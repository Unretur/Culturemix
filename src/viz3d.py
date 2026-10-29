"""3D view of the Qloo evidence network. It draws only the data it is given."""
import json
import math

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; height: 100%; overflow: hidden;
    background: radial-gradient(ellipse at center, #1e1b4b 0%, #0b0f1a 70%);
    font-family: Helvetica, Arial, sans-serif; }
  #info { position: absolute; left: 14px; bottom: 12px; color: #cbd5e1; font-size: 12px;
    background: rgba(15, 23, 42, 0.6); padding: 6px 10px; border-radius: 8px; }
  .lbl { position: absolute; pointer-events: none; color: #e2e8f0; font-size: 12px;
    background: rgba(15, 23, 42, 0.75); padding: 2px 7px; border-radius: 6px;
    white-space: nowrap; transform: translate(-50%, -170%); }
</style>
<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
} }
</script>
</head>
<body>
<div id="info">Drag to rotate, scroll to zoom. Green lines: shared Qloo tags.</div>
<div id="labels"></div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const DATA = __DATA__;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 2, 9);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(devicePixelRatio);
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.6;

scene.add(new THREE.AmbientLight(0xffffff, 0.8));
const light = new THREE.PointLight(0x7dd3fc, 40);
light.position.set(6, 6, 6);
scene.add(light);

const centre = new THREE.Mesh(
  new THREE.SphereGeometry(0.35, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0x60a5fa, emissive: 0x1e3a8a })
);
scene.add(centre);

const COLOURS = { qloo: 0x34d399, mock: 0x94a3b8 };
const meshes = DATA.nodes.map((n) => {
  const m = new THREE.Mesh(
    new THREE.SphereGeometry(0.22, 24, 24),
    new THREE.MeshStandardMaterial({ color: COLOURS[n.source] ?? 0x94a3b8, emissive: 0x111827 })
  );
  m.position.set(...n.pos);
  scene.add(m);
  const spoke = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), m.position]);
  scene.add(new THREE.Line(spoke, new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.5 })));
  return m;
});

DATA.links.forEach((l) => {
  const geo = new THREE.BufferGeometry().setFromPoints([meshes[l.a].position, meshes[l.b].position]);
  scene.add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x059669 })));
});

const labelBox = document.getElementById("labels");
const labels = DATA.nodes.map((n) => {
  const d = document.createElement("div");
  d.className = "lbl";
  d.textContent = n.name;
  labelBox.appendChild(d);
  return d;
});

const v = new THREE.Vector3();
function placeLabels() {
  meshes.forEach((m, i) => {
    v.copy(m.position).project(camera);
    labels[i].style.left = (v.x * 0.5 + 0.5) * innerWidth + "px";
    labels[i].style.top = (-v.y * 0.5 + 0.5) * innerHeight + "px";
    labels[i].style.opacity = v.z < 1 ? 1 : 0;
  });
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  placeLabels();
}
animate();

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
"""


def _fibonacci_sphere(n: int, radius: float = 3.0) -> list[list[float]]:
    """Spread n points evenly over a sphere, so nodes don't overlap."""
    golden = math.pi * (3 - math.sqrt(5))
    points = []
    for i in range(n):
        y = 1 - (i / max(n - 1, 1)) * 2
        r = math.sqrt(max(0.0, 1 - y * y))
        theta = golden * i
        points.append([
            round(radius * math.cos(theta) * r, 3),
            round(radius * y, 3),
            round(radius * math.sin(theta) * r, 3),
        ])
    return points


def network_3d_html(evidence: list[dict], links: list[dict]) -> str:
    """evidence: rows with name and source. links: rows with a, b (names) and shared (tags)."""
    positions = _fibonacci_sphere(len(evidence))
    index = {e["name"]: i for i, e in enumerate(evidence)}
    payload = {
        "nodes": [
            {"name": e["name"], "source": e["source"], "pos": p}
            for e, p in zip(evidence, positions)
        ],
        "links": [
            {"a": index[l["a"]], "b": index[l["b"]]}
            for l in links
            if l["a"] in index and l["b"] in index
        ],
    }
    # Escape "</" so the JSON can't close the script tag early.
    data = json.dumps(payload).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__DATA__", data)