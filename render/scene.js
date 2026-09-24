// 3D-сцена хозблока по model/model.json (three.js, ось Z — вверх, мм).
import * as THREE from 'three';

const DEG = Math.PI / 180;

// ------------------------------------------------------------ процедурные текстуры
function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

function canvasTex(size, draw, repeatMM) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  t.userData.tile = repeatMM;
  return t;
}

const TEX = {};
function textures() {
  if (TEX.osb) return TEX;
  TEX.osb = canvasTex(1024, (g, n) => {
    const r = rng(7);
    g.fillStyle = '#c9a36a'; g.fillRect(0, 0, n, n);
    for (let i = 0; i < 2600; i++) {
      const w = 20 + r() * 70, h = 6 + r() * 18, a = r() * Math.PI;
      const tone = 150 + r() * 70;
      g.save(); g.translate(r() * n, r() * n); g.rotate(a);
      g.fillStyle = `rgb(${tone + 30},${tone * 0.78 + 20},${tone * 0.45})`;
      g.globalAlpha = 0.55; g.fillRect(-w / 2, -h / 2, w, h); g.restore();
    }
  }, 1250);
  const wood = (base, seed) => canvasTex(512, (g, n) => {
    const r = rng(seed);
    g.fillStyle = base; g.fillRect(0, 0, n, n);
    for (let i = 0; i < 90; i++) {
      const y = r() * n;
      g.strokeStyle = `rgba(120,70,30,${0.05 + r() * 0.12})`;
      g.lineWidth = 1 + r() * 3;
      g.beginPath(); g.moveTo(0, y);
      for (let x = 0; x <= n; x += 32) g.lineTo(x, y + Math.sin(x / 60 + i) * 3 + (r() - 0.5) * 2);
      g.stroke();
    }
    for (let i = 0; i < 6; i++) {
      g.fillStyle = 'rgba(110,60,20,0.35)';
      g.beginPath(); g.ellipse(r() * n, r() * n, 5 + r() * 6, 3 + r() * 3, 0, 0, 7); g.fill();
    }
  }, 800);
  TEX.timber = wood('#dcb57a', 3);
  TEX.board = wood('#cfa56a', 5);
  TEX.plywood = wood('#e3c48f', 9);
  TEX.deck = wood('#9a6a3e', 13);
  TEX.grass = canvasTex(512, (g, n) => {
    const r = rng(21);
    g.fillStyle = '#5d7f33'; g.fillRect(0, 0, n, n);
    for (let i = 0; i < 9000; i++) {
      const v = r();
      g.fillStyle = v < 0.5 ? `rgba(70,105,35,0.5)` : v < 0.85 ? `rgba(120,150,60,0.45)` : 'rgba(150,140,80,0.35)';
      g.fillRect(r() * n, r() * n, 2 + r() * 3, 2 + r() * 6);
    }
  }, 2500);
  TEX.gravel = canvasTex(512, (g, n) => {
    const r = rng(33);
    g.fillStyle = '#9d9a92'; g.fillRect(0, 0, n, n);
    for (let i = 0; i < 6000; i++) {
      const t = 110 + r() * 110;
      g.fillStyle = `rgb(${t},${t - 4},${t - 12})`;
      g.beginPath(); g.arc(r() * n, r() * n, 1 + r() * 4, 0, 7); g.fill();
    }
  }, 900);
  TEX.pegboard = canvasTex(512, (g, n) => {
    g.fillStyle = '#9ea6ad'; g.fillRect(0, 0, n, n);
    g.fillStyle = '#3b4046';
    for (let x = 16; x < n; x += 32) for (let y = 16; y < n; y += 32) {
      g.beginPath(); g.arc(x, y, 5, 0, 7); g.fill();
    }
  }, 400);
  TEX.concrete = canvasTex(256, (g, n) => {
    const r = rng(44);
    g.fillStyle = '#a9a8a2'; g.fillRect(0, 0, n, n);
    for (let i = 0; i < 1500; i++) {
      g.fillStyle = `rgba(${r() < 0.5 ? 60 : 200},${r() < 0.5 ? 60 : 200},60,0.15)`;
      g.fillRect(r() * n, r() * n, 2, 2);
    }
  }, 400);
  return TEX;
}

// UV в мировых мм, выбор плоскости по нормали — текстуры не растягиваются
function worldUV(geom, tile) {
  const p = geom.attributes.position, nrm = geom.attributes.normal;
  const uv = new Float32Array(p.count * 2);
  for (let i = 0; i < p.count; i++) {
    const nx = Math.abs(nrm.getX(i)), ny = Math.abs(nrm.getY(i)), nz = Math.abs(nrm.getZ(i));
    let u, v;
    if (nx >= ny && nx >= nz) { u = p.getY(i); v = p.getZ(i); }
    else if (ny >= nz) { u = p.getX(i); v = p.getZ(i); }
    else { u = p.getX(i); v = p.getY(i); }
    uv[2 * i] = u / tile; uv[2 * i + 1] = v / tile;
  }
  geom.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  return geom;
}

export function buildMaterials(opts = {}) {
  const T = textures();
  const std = (o) => new THREE.MeshStandardMaterial(o);
  const wall = opts.wallColor || '#2c5f4a';          // RAL 6005 «зелёный мох» (с учётом тонмаппинга)
  return {
    concrete: std({ map: T.concrete, roughness: 0.95 }),
    ruberoid: std({ color: '#1d1d1d', roughness: 0.9 }),
    timber: std({ map: T.timber, roughness: 0.8 }),
    wood: std({ map: T.timber, roughness: 0.75 }),
    board: std({ map: T.board, roughness: 0.8 }),
    board_rough: std({ map: T.board, color: '#bbbbbb', roughness: 0.9 }),
    plywood: std({ map: T.plywood, roughness: 0.6 }),
    osb: std({ map: T.osb, roughness: 0.8 }),
    insulation: std({ color: '#e8d27a', roughness: 1 }),
    deck: std({ map: T.deck, roughness: 0.8 }),
    wall_sheet: std({ color: wall, roughness: 0.5, metalness: 0.2 }),
    trim: std({ color: '#f1f0ea', roughness: 0.5, metalness: 0.2 }),
    roof_sheet: std({ color: '#c3c8cc', roughness: 0.32, metalness: 0.75 }),
    pvc: std({ color: '#f7f7f4', roughness: 0.35 }),
    glass: new THREE.MeshPhysicalMaterial({ color: '#bcd7e6', roughness: 0.05, metalness: 0,
      transmission: 0.0, transparent: true, opacity: 0.28, depthWrite: false }),
    door: std({ color: '#5a3a26', roughness: 0.55, metalness: 0.45 }),
    steel: std({ color: '#7d858c', roughness: 0.4, metalness: 0.8 }),
    dark: std({ color: '#2a2c2e', roughness: 0.6, metalness: 0.3 }),
    black: std({ color: '#111', roughness: 0.7 }),
    rubber: std({ color: '#1c1c1c', roughness: 0.95 }),
    pegboard: std({ map: T.pegboard, roughness: 0.5, metalness: 0.5 }),
    grass: std({ map: T.grass, roughness: 1 }),
    gravel: std({ map: T.gravel, roughness: 1 }),
    lamp: std({ color: '#ffffff', emissive: '#fff6e0', emissiveIntensity: 2.2 }),
    red: std({ color: '#c0392b', roughness: 0.45 }),
    orange: std({ color: '#e67e22', roughness: 0.45 }),
    green: std({ color: '#3c8d40', roughness: 0.45 }),
    blue: std({ color: '#2e6da4', roughness: 0.45 }),
    yellow: std({ color: '#e8b923', roughness: 0.45 }),
    grey: std({ color: '#8c8f93', roughness: 0.6 }),
  };
}

// ------------------------------------------------------------ примитивы
function meshBox(mat, x0, y0, z0, x1, y1, z1, tile) {
  const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
  g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  if (mat.map) worldUV(g, mat.map.userData.tile || 1000);
  const m = new THREE.Mesh(g, mat);
  m.castShadow = m.receiveShadow = true;
  return m;
}
function cyl(mat, r, h, axis = 'z', seg = 20) {
  const g = new THREE.CylinderGeometry(r, r, h, seg);
  if (axis === 'z') g.rotateX(Math.PI / 2);
  if (axis === 'x') g.rotateZ(Math.PI / 2);
  const m = new THREE.Mesh(g, mat);
  m.castShadow = m.receiveShadow = true;
  return m;
}
function at(obj, x, y, z) { obj.position.set(x, y, z); return obj; }

// Плоскость в вертикальной плоскости XZ с отверстиями, толщина t вглубь +Y от y0
function slabXZ(mat, x0, x1, z0, z1, holes, y0, t) {
  const s = new THREE.Shape();
  s.moveTo(x0, z0); s.lineTo(x1, z0); s.lineTo(x1, z1); s.lineTo(x0, z1); s.closePath();
  for (const [hx0, hz0, hx1, hz1] of holes) {
    const h = new THREE.Path();
    h.moveTo(hx0, hz0); h.lineTo(hx0, hz1); h.lineTo(hx1, hz1); h.lineTo(hx1, hz0); h.closePath();
    s.holes.push(h);
  }
  const g = new THREE.ExtrudeGeometry(s, { depth: t, bevelEnabled: false });
  g.rotateX(Math.PI / 2);            // (x, zShape) -> (x, z); глубина -> -y
  g.translate(0, y0 + t, 0);
  g.computeVertexNormals();
  if (mat.map) worldUV(g, mat.map.userData.tile || 1000);
  const m = new THREE.Mesh(g, mat);
  m.castShadow = m.receiveShadow = true;
  return m;
}

// ------------------------------------------------------------ здание
export function buildHouse(model, M, opts = {}) {
  const root = new THREE.Group();
  const groups = {};
  const G = (name) => (groups[name] ||= (() => { const g = new THREE.Group(); g.name = name; root.add(g); return g; })());
  const lv = model.levels, P = model.params, L = P.L, W = P.W;
  const tan = Math.tan(P.roof_pitch * DEG);
  const roofZ = (y) => lv.ridge - tan * Math.abs(y - W / 2);

  for (const e of model.elements) {
    if (e.kind === 'box') {
      if (e.section_only && !opts.showHidden) continue;
      const [x0, y0, z0, x1, y1, z1] = e.b;
      let m;
      if (e.holes) {
        m = slabXZ(M[e.mat], x0, x1, z0, z1, e.holes, y0, y1 - y0);
      } else m = meshBox(M[e.mat], x0, y0, z0, x1, y1, z1);
      m.name = e.id;
      G(groupOf(e)).add(m);
    } else if (e.kind === 'rbox') {
      const g = new THREE.BoxGeometry(...e.s);
      const mat = M[e.mat];
      if (mat.map) worldUV(g, mat.map.userData.tile || 1000);
      const m = new THREE.Mesh(g, mat);
      m.castShadow = m.receiveShadow = true;
      m.position.set(...e.c);
      m.rotation.set(e.rx * DEG, e.ry * DEG, 0);
      m.name = e.id;
      G(groupOf(e)).add(m);
    } else if (e.kind === 'item') {
      const o = buildItem(e, model, M, roofZ);
      if (o) { o.name = e.id; G(groupOf(e)).add(o); }
    }
  }
  return { root, groups };
}

function groupOf(e) {
  if (e.group === 'frame') {
    if (/^(wf_|br_f)/.test(e.id)) return 'frame_front';
    if (/^(chord|rafter|kingpost)/.test(e.id)) return 'frame_roof';
    return 'frame';
  }
  if (e.group === 'finish') return e.id === 'osb_front' ? 'finish_front' : e.id === 'osb_ceiling' ? 'ceiling' : 'finish';
  if (e.group === 'cladding') return e.face === 'front' ? 'clad_front' : 'cladding';
  if (e.group === 'opening') return 'openings';
  return e.group;
}

function ribsXZ(M, x0, x1, z0, z1, holes, y, dir, pitch = 115, depth = 10, w = 36, zTop = null) {
  // вертикальные рёбра профлиста на фасаде (плоскость XZ, dir: -1 наружу к -Y)
  const g = new THREE.Group();
  for (let x = x0 + pitch / 2; x < x1 - w / 2; x += pitch) {
    const top = zTop ? zTop(x) : z1;
    let segs = [[z0, top]];
    for (const [hx0, hz0, hx1, hz1] of holes) {
      if (x + w / 2 > hx0 - 20 && x - w / 2 < hx1 + 20) {
        const out = [];
        for (const [a, b] of segs) {
          if (b <= hz0 - 20 || a >= hz1 + 20) out.push([a, b]);
          else { if (a < hz0 - 20) out.push([a, hz0 - 20]); if (b > hz1 + 20) out.push([hz1 + 20, b]); }
        }
        segs = out;
      }
    }
    for (const [a, b] of segs) if (b - a > 5)
      g.add(meshBox(M.wall_sheet, x - w / 2, Math.min(y, y + dir * depth), a, x + w / 2, Math.max(y, y + dir * depth), b));
  }
  return g;
}

function buildItem(e, model, M, roofZ) {
  const lv = model.levels, P = model.params, L = P.L, W = P.W, C = lv.clad;
  const g = new THREE.Group();
  switch (e.type) {
    case 'wall_sheet': {
      const out = e.face === 'front' ? -1 : 1;
      const y0 = e.face === 'front' ? e.y : e.y - 2;
      const holes = e.holes.map(([x0, z0, x1, z1]) => [x0 - 10, z0 - 10, x1 + 10, z1 + 10]);
      g.add(slabXZ(M.wall_sheet, e.x0, e.x1, e.z0, e.z1, holes, y0, 2));
      g.add(ribsXZ(M, e.x0, e.x1, e.z0, e.z1, holes, e.face === 'front' ? e.y : e.y, out));
      // наличники проёмов, отливы
      for (const [x0, z0, x1, z1] of e.holes) {
        const yy = e.y + out * 12, yi = e.y;
        const tr = (a, b, c, d) => g.add(meshBox(M.trim, a, Math.min(yy, yi), b, c, Math.max(yy, yi), d));
        tr(x0 - 70, z1, x1 + 70, z1 + 60);
        tr(x0 - 70, z0 - (z0 > 200 ? 60 : 0), x0, z1);
        tr(x1, z0 - (z0 > 200 ? 60 : 0), x1 + 70, z1);
        if (z0 > 200) g.add(meshBox(M.trim, x0 - 40, e.y - 120, z0 - 25, x1 + 40, e.y, z0));
      }
      // цокольный отлив
      g.add(meshBox(M.trim, e.x0 - 3, Math.min(e.y, e.y + out * 45), e.z0 - 20, e.x1 + 3,
        Math.max(e.y, e.y + out * 45), e.z0 + 25));
      // угловые планки
      for (const x of [e.x0, e.x1])
        g.add(meshBox(M.trim, x - 30, Math.min(e.y, e.y + out * 30), e.z0, x + 30, Math.max(e.y, e.y + out * 30), e.z1));
      break;
    }
    case 'gable_sheet': {
      const out = e.face === 'left' ? -1 : 1;
      const x = e.x;
      // контур стены + фронтон
      const s = new THREE.Shape();
      const top = (y) => roofZ(y) - 20 - 30;
      s.moveTo(e.y0, e.z0); s.lineTo(e.y1, e.z0); s.lineTo(e.y1, top(e.y1));
      s.lineTo(W / 2, top(W / 2)); s.lineTo(e.y0, top(e.y0)); s.closePath();
      const m4 = new THREE.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1);
      const geo2 = new THREE.ExtrudeGeometry(s, { depth: 2, bevelEnabled: false });
      geo2.applyMatrix4(m4); // (sx, sy, sz) -> (x=sz, y=sx, z=sy)
      geo2.translate(out < 0 ? x : x - 2, 0, 0);
      geo2.computeVertexNormals();
      const wm = new THREE.Mesh(geo2, M.wall_sheet); wm.castShadow = wm.receiveShadow = true;
      g.add(wm);
      for (let y = e.y0 + 57; y < e.y1 - 18; y += 115) {
        const zt = top(y) - 10;
        g.add(meshBox(M.wall_sheet, Math.min(x, x + out * 10), y - 18, e.z0, Math.max(x, x + out * 10), y + 18, zt));
      }
      g.add(meshBox(M.trim, Math.min(x, x + out * 45), e.y0 - 3, e.z0 - 20, Math.max(x, x + out * 45), e.y1 + 3, e.z0 + 25));
      break;
    }
    case 'roof_sheet': {
      const sl = (e.ridge_y - e.y0) / Math.cos(e.pitch * DEG);
      for (const sg of [1, -1]) {
        const sub = new THREE.Group();
        const len = e.x1 - e.x0;
        sub.add(meshBox(M.roof_sheet, -len / 2, -sl / 2, -e.t + 3, len / 2, sl / 2, -e.t + 5));
        for (let x = -len / 2 + 60; x < len / 2 - 20; x += 137.5)
          sub.add(meshBox(M.roof_sheet, x - 25, -sl / 2, -e.t + 3, x + 25, sl / 2, 0));
        const yc = e.ridge_y - sg * (e.ridge_y - e.y0) / 2;
        sub.position.set((e.x0 + e.x1) / 2, yc, roofZ(yc));
        sub.rotation.x = sg * e.pitch * DEG;
        g.add(sub);
      }
      // ветровые планки по торцам скатов
      for (const x of [e.x0, e.x1]) for (const sg of [1, -1]) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(22, sl + 20, 140), M.trim);
        const yc = e.ridge_y - sg * (e.ridge_y - e.y0) / 2;
        b.position.set(x + (x < e.x0 + 1 ? -11 : 11), yc, roofZ(yc) - 45);
        b.rotation.x = sg * e.pitch * DEG; b.castShadow = true; g.add(b);
      }
      // конёк
      for (const sg of [1, -1]) {
        const r = meshBox(M.roof_sheet, e.x0 - 10, -100, -2, e.x1 + 10, 100, 2);
        const sub = new THREE.Group(); sub.add(r);
        sub.position.set(0, e.ridge_y - sg * 95, e.ridge_z + 22 - 95 * Math.tan(e.pitch * DEG));
        sub.rotation.x = sg * e.pitch * DEG;
        g.add(sub);
      }
      break;
    }
    case 'window': {
      const { x0, x1, z0, z1 } = e, y = 20, d = 70, f = 62;
      const fr = (a, b, c, dd) => g.add(meshBox(M.pvc, a, y, b, c, y + d, dd));
      fr(x0 + 10, z0 + 10, x1 - 10, z0 + 10 + f); fr(x0 + 10, z1 - 10 - f, x1 - 10, z1 - 10);
      fr(x0 + 10, z0 + 10, x0 + 10 + f, z1 - 10); fr(x1 - 10 - f, z0 + 10, x1 - 10, z1 - 10);
      // створка
      const s = 55;
      const sa = (a, b, c, dd) => g.add(meshBox(M.pvc, a, y + 5, b, c, y + d - 5, dd));
      sa(x0 + 72, z0 + 72, x1 - 72, z0 + 72 + s); sa(x0 + 72, z1 - 72 - s, x1 - 72, z1 - 72);
      sa(x0 + 72, z0 + 72, x0 + 72 + s, z1 - 72); sa(x1 - 72 - s, z0 + 72, x1 - 72, z1 - 72);
      const gl = meshBox(M.glass, x0 + 120, y + 30, z0 + 120, x1 - 120, y + 36, z1 - 120);
      gl.castShadow = false; g.add(gl);
      g.add(meshBox(M.pvc, x1 - 110, y + d, (z0 + z1) / 2 - 10, x1 - 90, y + d + 40, (z0 + z1) / 2 + 110)); // ручка
      // подоконник внутри + откосы
      g.add(meshBox(M.pvc, x0 - 30, y + d, z0 - 20, x1 + 30, 240, z0 + 10));
      for (const xx of [[x0 - 10, x0], [x1, x1 + 10]]) g.add(meshBox(M.pvc, xx[0], y + d, z0, xx[1], 118, z1));
      g.add(meshBox(M.pvc, x0, y + d, z1, x1, 118, z1 + 10));
      break;
    }
    case 'door': {
      const { x0, x1, z0, z1 } = e;
      const y = 0;
      g.add(meshBox(M.door, x0 + 5, y, z0, x0 + 55, y + 70, z1 - 5));
      g.add(meshBox(M.door, x1 - 55, y, z0, x1 - 5, y + 70, z1 - 5));
      g.add(meshBox(M.door, x0 + 5, y, z1 - 55, x1 - 5, y + 70, z1 - 5));
      g.add(meshBox(M.door, x0 + 55, y + 5, z0, x1 - 55, y + 65, z0 + 25));
      const lx0 = x0 + 55, lx1 = x1 - 55, lz0 = z0 + 25, lz1 = z1 - 55;
      g.add(meshBox(M.door, lx0, y + 8, lz0, lx1, y + 60, lz1));
      // декор-филёнки снаружи
      for (const [a, b] of [[lz0 + 120, lz0 + 900], [lz0 + 1020, lz1 - 120]])
        g.add(meshBox(M.door, lx0 + 110, y + 2, a, lx1 - 110, y + 8, b));
      // ручки и замок
      for (const yy of [[y - 50, y], [y + 60, y + 110]]) {
        g.add(meshBox(M.steel, lx1 - 90, yy[0], 1050, lx1 - 70, yy[1], 1070));
        g.add(meshBox(M.steel, lx1 - 250, yy[0] + (yy[0] < 0 ? -10 : 40), 1050, lx1 - 80, yy[0] + (yy[0] < 0 ? 10 : 60), 1072));
      }
      g.add(meshBox(M.steel, lx1 - 100, y - 3, 1200, lx1 - 60, y, 1250));
      break;
    }
    case 'vise': {
      g.add(meshBox(M.blue, e.x - 80, e.y - 150, e.z, e.x + 80, e.y + 20, e.z + 60));
      g.add(meshBox(M.blue, e.x - 70, e.y - 10, e.z + 60, e.x + 70, e.y + 40, e.z + 170));
      g.add(meshBox(M.blue, e.x - 70, e.y - 110, e.z + 60, e.x + 70, e.y - 60, e.z + 170));
      g.add(at(cyl(M.steel, 12, 320, 'y'), e.x, e.y + 60, e.z + 100));
      g.add(at(cyl(M.steel, 8, 200, 'x'), e.x, e.y + 210, e.z + 100));
      break;
    }
    case 'bench_stuff': {
      const z = e.z;
      g.add(meshBox(M.red, e.x0 + 150, e.y0 + 60, z, e.x0 + 650, e.y0 + 260, z + 220));   // ящик с инструментом
      g.add(meshBox(M.black, e.x0 + 150, e.y0 + 140, z + 220, e.x0 + 650, e.y0 + 180, z + 250));
      g.add(meshBox(M.green, e.x0 + 760, e.y0 + 60, z, e.x0 + 1160, e.y0 + 380, z + 110));  // кейс шуруповерта
      g.add(meshBox(M.yellow, e.x0 + 1250, e.y0 + 90, z, e.x0 + 1550, e.y0 + 300, z + 120)); // кейс
      g.add(meshBox(M.board, e.x0 + 900, e.y0 + 430, z, e.x0 + 1500, e.y0 + 520, z + 40));   // заготовка
      // настольная лампа
      g.add(at(cyl(M.dark, 60, 20), e.x0 + 1700, e.y0 + 120, z + 10));
      const arm = at(cyl(M.dark, 8, 420), e.x0 + 1700, e.y0 + 120, z + 220); g.add(arm);
      g.add(at(cyl(M.dark, 55, 90, 'z'), e.x0 + 1700, e.y0 + 220, z + 420));
      break;
    }
    case 'drawer_unit': {
      g.add(meshBox(M.grey, e.x0, e.y0, e.z0, e.x1, e.y1, e.z1));
      const n = 4, h = (e.z1 - e.z0 - 40) / n;
      for (let i = 0; i < n; i++) {
        const z = e.z0 + 20 + i * h;
        g.add(meshBox(M.red, e.x0 + 15, e.y1, z + 6, e.x1 - 15, e.y1 + 12, z + h - 6));
        g.add(meshBox(M.steel, (e.x0 + e.x1) / 2 - 60, e.y1 + 12, z + h / 2 - 8, (e.x0 + e.x1) / 2 + 60, e.y1 + 30, z + h / 2 + 8));
      }
      break;
    }
    case 'pegboard': {
      const x = e.x;
      g.add(meshBox(M.pegboard, x, e.y0, e.z0, x + 12, e.y1, e.z1));
      const tl = (mat, y0, z0, y1, z1, d = 25) => g.add(meshBox(mat, x + 20, y0, z0, x + 20 + d, y1, z1));
      const w = e.y1 - e.y0;
      // молотки, отвёртки, ножовка, ключи, рулетка, угольник
      for (let i = 0; i < 2; i++) {
        tl(M.wood, e.y0 + 60 + i * 70, e.z1 - 380, e.y0 + 85 + i * 70, e.z1 - 80);
        tl(M.steel, e.y0 + 30 + i * 70, e.z1 - 110, e.y0 + 115 + i * 70, e.z1 - 70, 35);
      }
      for (let i = 0; i < 6; i++) tl(i % 2 ? M.red : M.yellow, e.y0 + 230 + i * 45, e.z1 - 260, e.y0 + 250 + i * 45, e.z1 - 120, 30);
      tl(M.steel, e.y0 + 540, e.z1 - 500, e.y0 + 720, e.z1 - 130, 3);                   // ножовка
      tl(M.black, e.y0 + 660, e.z1 - 150, e.y0 + 720, e.z1 - 90, 40);
      for (let i = 0; i < 8; i++) tl(M.steel, e.y0 + 60 + i * 55, e.z0 + 330, e.y0 + 78 + i * 55, e.z0 + 480 + i * 12, 10);
      tl(M.yellow, e.y0 + 560, e.z0 + 380, e.y0 + 650, e.z0 + 470, 50);                  // рулетка
      tl(M.steel, e.y0 + 80, e.z0 + 80, e.y0 + 380, e.z0 + 110, 4);                      // угольник
      tl(M.steel, e.y0 + 80, e.z0 + 80, e.y0 + 110, e.z0 + 260, 4);
      tl(M.blue, e.y0 + 460, e.z0 + 60, e.y0 + 700, e.z0 + 260, 60);                     // органайзер
      break;
    }
    case 'rack_stuff': {
      const r = rng(5);
      const pal = [M.blue, M.grey, M.green, M.orange, M.red, M.yellow, M.black];
      e.levels.forEach((z, li) => {
        const topLimit = li < e.levels.length - 1 ? e.levels[li + 1] - 18 - 60 : z + 250;
        for (let s = 0; s < e.seps.length - 1; s++) {
          let x = e.seps[s] + 45;
          const xe = e.seps[s + 1] - 25;
          while (x < xe - 150) {
            const w = Math.min(180 + r() * 280, xe - x - 10);
            const h = Math.min(120 + r() * 300, topLimit - z);
            const d = 300 + r() * 170;
            const t = r();
            if (t < 0.18 && li < 3) {        // банки / вёдра
              for (let k = 0; k < 2 && x + 130 < xe; k++) {
                g.add(at(cyl(pal[(r() * 7) | 0], 80, Math.min(190, h)), x + 85, e.y1 - 160, z + Math.min(190, h) / 2));
                x += 170;
              }
              continue;
            }
            if (t < 0.3 && li === 0) {       // мешки с грунтом/удобрениями
              g.add(meshBox(new THREE.MeshStandardMaterial({ color: r() < 0.5 ? '#6d8b3a' : '#8a5a2c', roughness: 0.9 }),
                x, e.y1 - 40 - d, z, x + w, e.y1 - 40, z + Math.min(h, 160)));
            } else {
              const m = pal[(r() * pal.length) | 0];
              g.add(meshBox(m, x, e.y1 - 30 - d, z, x + w, e.y1 - 30, z + h));
              if (r() < 0.6) g.add(meshBox(M.black, x + 5, e.y1 - 30 - d - 3, z + h - 20, x + w - 5, e.y1 - 30 - d, z + h - 5));
            }
            x += w + 25 + r() * 40;
          }
        }
      });
      break;
    }
    case 'tool_wall': {
      const n = e.tools.length, step = (e.x1 - e.x0) / (n - 1);
      const y = e.y - 60;
      e.tools.forEach((t, i) => {
        const x = e.x0 + i * step;
        // держатель на рейке
        g.add(meshBox(M.dark, x - 30, y + 20, e.z_hook - 50, x + 30, e.y, e.z_hook - 20));
        g.add(meshBox(M.dark, x - 30, y + 20, e.z_hook - 450, x + 30, e.y, e.z_hook - 420));
        if (['axe', 'sledge', 'crowbar', 'pruner'].includes(t)) {
          const len = t === 'pruner' ? 650 : t === 'crowbar' ? 1100 : 800;
          g.add(at(cyl(t === 'crowbar' ? M.dark : M.wood, 16, len), x, y, e.z_hook + 100 - len / 2));
          if (t === 'axe') g.add(meshBox(M.steel, x - 20, y - 90, e.z_hook + 40, x + 20, y + 40, e.z_hook + 150));
          if (t === 'sledge') g.add(meshBox(M.dark, x - 40, y - 60, e.z_hook + 80, x + 40, y + 60, e.z_hook + 160));
          if (t === 'pruner') g.add(meshBox(M.red, x - 30, y - 15, e.z_hook + 80, x + 30, y + 15, e.z_hook + 220));
          return;
        }
        const top = e.z_hook + 120, bot = model.levels.floor + 330;
        g.add(at(cyl(M.wood, 18, top - bot), x, y, (top + bot) / 2));
        const head = { shovel: [M.dark, 230, 300], shovel2: [M.steel, 220, 330], fork: [M.steel, 200, 300],
          rake: [M.green, 420, 60], rake_fan: [M.orange, 420, 380], hoe: [M.steel, 160, 120],
          broom: [M.yellow, 320, 170], scoop: [M.blue, 300, 360] }[t];
        const [mat, hw, hh] = head;
        g.add(meshBox(mat, x - hw / 2, y - 25, bot - hh, x + hw / 2, y + 10, bot));
      });
      break;
    }
    case 'brackets': {
      const n = e.count;
      for (let i = 0; i < n; i++) {
        const x = e.x0 + 60 + i * (e.x1 - e.x0 - 120) / (n - 1);
        if (e.wall === 'front') {
          g.add(meshBox(M.dark, x - 15, e.y0, e.z - 200, x + 15, e.y0 + 20, e.z));
          g.add(meshBox(M.dark, x - 15, e.y0, e.z - 25, x + 15, e.y1 - 20, e.z));
        } else {
          g.add(meshBox(M.dark, x - 15, e.y1 - 20, e.z - 250, x + 15, e.y1, e.z));
          g.add(meshBox(M.dark, x - 15, e.y0 + 20, e.z - 25, x + 15, e.y1, e.z));
        }
      }
      break;
    }
    case 'shelf_stuff': {
      const r = rng(e.seed || 1);
      let x = e.x0 + 40;
      const pal = [M.blue, M.grey, M.green, M.orange, M.red, M.yellow];
      while (x < e.x1 - 120) {
        if (e.kind === 'bottles') {
          const h = 150 + r() * Math.min(150, e.hmax - 150);
          g.add(at(cyl(pal[(r() * 6) | 0], 35 + r() * 25, h), x + 50, (e.y0 + e.y1) / 2, e.z + h / 2));
          x += 110 + r() * 40;
        } else {
          const w = 250 + r() * 300, h = Math.min(120 + r() * 220, e.hmax);
          g.add(meshBox(pal[(r() * 6) | 0], x, e.y1 - 30 - 340, e.z, x + w, e.y1 - 30, e.z + h));
          x += w + 40;
        }
      }
      break;
    }
    case 'hook_wall': {
      const x = e.x;
      g.add(meshBox(M.wood, x - 25, e.y0, e.z - 50, x, e.y1, e.z + 50));
      // катушка шланга
      const hose = new THREE.Mesh(new THREE.TorusGeometry(170, 45, 12, 32), M.green);
      hose.rotation.y = Math.PI / 2; hose.position.set(x - 90, e.y0 + 230, e.z - 150); hose.castShadow = true; g.add(hose);
      g.add(meshBox(M.dark, x - 150, e.y0 + 210, e.z - 10, x - 25, e.y0 + 250, e.z + 20));
      // удлинитель
      const ext = at(cyl(M.orange, 150, 110, 'x'), x - 90, e.y0 + 620, e.z - 140); g.add(ext);
      g.add(at(cyl(M.black, 40, 130, 'x'), x - 90, e.y0 + 620, e.z - 140));
      // триммер
      g.add(meshBox(M.dark, x - 90, e.y0 + 900, e.z - 850, x - 60, e.y0 + 930, e.z + 450));
      g.add(meshBox(M.orange, x - 170, e.y0 + 860, e.z + 250, x - 40, e.y0 + 1000, e.z + 450));
      g.add(meshBox(M.dark, x - 150, e.y0 + 830, e.z - 900, x - 40, e.y0 + 1000, e.z - 830));
      // кусторез
      g.add(meshBox(M.green, x - 140, e.y1 - 150, e.z - 380, x - 40, e.y1 - 60, e.z + 20));
      g.add(meshBox(M.steel, x - 100, e.y1 - 120, e.z - 800, x - 80, e.y1 - 90, e.z - 380));
      break;
    }
    case 'mower': {
      const { x, y, z } = e;
      g.add(meshBox(M.red, x, y, z + 60, x + 540, y + 520, z + 280));
      g.add(meshBox(M.black, x + 120, y + 130, z + 280, x + 420, y + 380, z + 420));
      for (const [wx, wy] of [[x - 5, y + 90], [x + 545, y + 90], [x - 5, y + 430], [x + 545, y + 430]])
        g.add(at(cyl(M.rubber, 95, 45, 'x'), wx, wy, z + 95));
      g.add(meshBox(M.green, x + 70, y + 520, z + 120, x + 470, y + 900, z + 380));    // травосборник
      for (const hx of [x + 60, x + 480]) {
        const h = new THREE.Mesh(new THREE.CylinderGeometry(12, 12, 900, 10), M.black);
        h.position.set(hx, y + 700, z + 620); h.rotation.x = -35 * DEG - Math.PI / 2 + Math.PI / 2; h.rotation.x = 55 * DEG;
        h.castShadow = true; g.add(h);
      }
      g.add(at(cyl(M.black, 12, 440, 'x'), x + 270, y + 960, z + 980));
      break;
    }
    case 'tiller': {
      const { x, y, z } = e;
      for (const wx of [x, x + 560]) g.add(at(cyl(M.rubber, 200, 150, 'x'), wx + 20, y + 260, z + 200));
      g.add(at(cyl(M.dark, 30, 560, 'x'), x + 300, y + 260, z + 200));
      g.add(meshBox(M.red, x + 150, y + 330, z + 250, x + 450, y + 700, z + 620));      // двигатель
      g.add(meshBox(M.dark, x + 170, y + 360, z + 620, x + 430, y + 600, z + 720));
      g.add(meshBox(M.dark, x + 200, y + 150, z + 150, x + 400, y + 350, z + 380));      // редуктор
      g.add(meshBox(M.grey, x + 260, y + 700, z + 120, x + 340, y + 1150, z + 220));      // рама/сошник
      for (const hx of [x + 120, x + 480]) {
        const h = new THREE.Mesh(new THREE.CylinderGeometry(15, 15, 800, 10), M.dark);
        h.position.set(hx, y + 1000, z + 750); h.rotation.x = 60 * DEG; h.castShadow = true; g.add(h);
        g.add(at(cyl(M.black, 20, 150), hx, y + 1340, z + 950));
      }
      g.add(meshBox(M.red, x + 30, y - 30, z + 180, x + 570, y + 60, z + 330));          // крыло/бампер
      break;
    }
    case 'barrow': {
      const { x, y, z } = e;
      const tray = new THREE.Mesh(new THREE.CylinderGeometry(330, 250, 260, 4, 1), M.green);
      tray.rotation.y = Math.PI / 4; tray.scale.set(1, 1, 1);
      const tg = new THREE.Group(); tg.add(tray);
      tray.rotation.set(Math.PI / 2, Math.PI / 4, 0);
      tg.scale.set(0.85, 1.35, 1); tg.position.set(x + 280, y + 520, z + 480);
      tray.castShadow = true; g.add(tg);
      g.add(at(cyl(M.rubber, 190, 90, 'x'), x + 280, y + 120, z + 190));
      for (const hx of [x + 80, x + 480]) {
        g.add(meshBox(M.dark, hx - 15, y + 100, z + 330, hx + 15, y + 1350, z + 370));
        g.add(meshBox(M.dark, hx - 15, y + 950, z, hx + 15, y + 990, z + 340));
      }
      break;
    }
    case 'canisters': {
      for (let i = 0; i < 2; i++) {
        const x = e.x + i * 200;
        g.add(meshBox(M.red, x, e.y, e.z, x + 170, e.y + 350, e.z + 470));
        g.add(meshBox(M.red, x + 40, e.y + 60, e.z + 470, x + 130, e.y + 200, e.z + 510));
      }
      g.add(at(cyl(M.blue, 110, 330), e.x + 520, e.y + 150, e.z + 165));
      break;
    }
    case 'floor_mat':
      g.add(meshBox(M.rubber, e.x0, e.y0, e.z, e.x1, e.y1, e.z + 6));
      break;
    case 'lamp': {
      const m = meshBox(M.lamp, e.x - 600, e.y - 40, e.z - 45, e.x + 600, e.y + 40, e.z);
      m.castShadow = false; g.add(m);
      break;
    }
    default: return null;
  }
  return g;
}

// ------------------------------------------------------------ окружение
export function buildSite(model, M) {
  const g = new THREE.Group();
  const gz = model.levels.ground;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(60000, 60000), M.grass);
  worldUV(ground.geometry, 2500);
  ground.position.z = gz; ground.receiveShadow = true; g.add(ground);
  // отсыпка под хозблок и дорожка к крыльцу
  const pad = meshBox(M.gravel, -500, -700, gz - 5, model.params.L + 500, model.params.W + 500, gz + 8);
  g.add(pad);
  const dx = model.params.door.x_c;
  g.add(meshBox(M.gravel, dx - 500, -6000, gz - 5, dx + 500, -700, gz + 6));
  // кусты и деревья
  const bush = new THREE.MeshStandardMaterial({ color: '#3f6b2a', roughness: 1 });
  const leaf = new THREE.MeshStandardMaterial({ color: '#4d7d2f', roughness: 1 });
  const bark = new THREE.MeshStandardMaterial({ color: '#e8e4dc', roughness: 0.9 });
  const r = rng(99);
  const addBush = (x, y, s) => {
    for (let i = 0; i < 4; i++) {
      const m = new THREE.Mesh(new THREE.IcosahedronGeometry(s * (0.6 + r() * 0.5), 1), bush);
      m.position.set(x + (r() - 0.5) * s, y + (r() - 0.5) * s, gz + s * 0.5);
      m.castShadow = m.receiveShadow = true; g.add(m);
    }
  };
  addBush(-1100, 400, 550); addBush(-1000, 1800, 450); addBush(model.params.L + 1100, 1500, 600);
  addBush(1200, -1500, 380); addBush(4800, -1400, 420);
  const addTree = (x, y, h) => {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(90, 140, h, 10), bark);
    t.rotation.x = Math.PI / 2; t.position.set(x, y, gz + h / 2); t.castShadow = true; g.add(t);
    for (let i = 0; i < 6; i++) {
      const m = new THREE.Mesh(new THREE.IcosahedronGeometry(900 + r() * 600, 1), leaf);
      m.position.set(x + (r() - 0.5) * 1600, y + (r() - 0.5) * 1600, gz + h + (r() - 0.3) * 1200);
      m.castShadow = true; g.add(m);
    }
  };
  addTree(-3500, 4500, 4200); addTree(12500, 5200, 5200); addTree(-5200, -2000, 3600);
  // забор на заднем плане
  const fence = new THREE.MeshStandardMaterial({ color: '#8b6b4a', roughness: 0.9 });
  for (let x = -9000; x < 15000; x += 150) g.add(meshBox(fence, x, 7000, gz, x + 110, 7020, gz + 1700));
  return g;
}

export function addLights(scene, opts = {}) {
  const hemi = new THREE.HemisphereLight('#dfefff', '#6b5d45', opts.hemi ?? 0.9);
  hemi.position.set(0, 0, 1); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff3dd', opts.sun ?? 3.2);
  const sp = opts.sunPos || [-6000, -9000, 9000];
  sun.position.set(...sp); sun.target.position.set(2900, 1100, 0);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  const c = sun.shadow.camera; c.left = -7000; c.right = 7000; c.top = 7000; c.bottom = -7000;
  c.near = 100; c.far = 40000; sun.shadow.bias = -0.0004; sun.shadow.normalBias = 2;
  scene.add(sun); scene.add(sun.target);
  return { hemi, sun };
}

export function skyTexture() {
  const c = document.createElement('canvas'); c.width = 16; c.height = 512;
  const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, '#6f9fd8'); gr.addColorStop(0.6, '#b9d3ee'); gr.addColorStop(1, '#e9f1f7');
  g.fillStyle = gr; g.fillRect(0, 0, 16, 512);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
