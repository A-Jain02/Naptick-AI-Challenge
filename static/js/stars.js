const canvas = document.getElementById("stars");
const ctx = canvas.getContext("2d");

let w, h;
function resize() {
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

// Star twinkles
const numStars = 100;
const stars = [];
for (let i = 0; i < numStars; i++) {
  stars.push({
    x: Math.random() * w,
    y: Math.random() * h,
    r: Math.random() * 1.2,
    alpha: Math.random(),
    direction: Math.random() < 0.5 ? 1 : -1
  });
}

// Define small constellations with fixed layouts
const constellations = [
  {
    name: "Orion",
    points: [
      { x: 150, y: 180 },
      { x: 165, y: 200 },
      { x: 180, y: 220 },
      { x: 200, y: 200 },
      { x: 215, y: 180 },
      { x: 190, y: 170 }
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5]]
  },
  {
    name: "Ursa Minor",
    points: [
      { x: w - 180, y: 120 },
      { x: w - 160, y: 130 },
      { x: w - 140, y: 140 },
      { x: w - 120, y: 150 },
      { x: w - 100, y: 160 },
      { x: w - 80, y: 165 },
      { x: w - 60, y: 170 }
    ],
    links: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]]
  }
];

// Comet system
let comets = [];
function createComet() {
  const size = 3 + Math.random() * 2;
  const angle = Math.PI / 6;
  comets.push({
    x: -60,
    y: Math.random() * h * 0.6,
    dx: 4 + Math.random(),
    dy: 1.5 + Math.random(),
    size,
    trail: [],
    life: 1
  });
}
setInterval(createComet, 7000);

// Animation loop
function animate() {
  ctx.clearRect(0, 0, w, h);

  // Draw twinkling stars
  for (const s of stars) {
    s.alpha += 0.01 * s.direction;
    if (s.alpha <= 0.3 || s.alpha >= 1) s.direction *= -1;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
    ctx.fill();
  }

  // Draw constellations
  ctx.strokeStyle = "rgba(255,255,255,0.4)";
  ctx.lineWidth = 0.6;
  for (const group of constellations) {
    for (const [i, j] of group.links) {
      const a = group.points[i];
      const b = group.points[j];
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }

    // Draw stars in constellation
    for (const p of group.points) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = "white";
      ctx.fill();
    }
  }

  // Animate comets
  // for (let i = comets.length - 1; i >= 0; i--) {
  //   const comet = comets[i];
  //   comet.x += comet.dx;
  //   comet.y += comet.dy;
  //   comet.trail.unshift({ x: comet.x, y: comet.y, alpha: comet.life });

  //   if (comet.trail.length > 40) comet.trail.pop();
  //   comet.life -= 0.005;

  //   // Draw comet trail
  //   for (let j = 0; j < comet.trail.length; j++) {
  //     const t = comet.trail[j];
  //     ctx.beginPath();
  //     ctx.arc(t.x, t.y, comet.size - j * 0.1, 0, Math.PI * 2);
  //     ctx.fillStyle = `rgba(255, 255, 255, ${t.alpha * 0.2})`;
  //     ctx.fill();
  //   }

  //   // Comet head glow
  //   ctx.beginPath();
  //   const glow = ctx.createRadialGradient(comet.x, comet.y, 0, comet.x, comet.y, comet.size * 2);
  //   glow.addColorStop(0, "rgba(255,255,255,0.9)");
  //   glow.addColorStop(1, "rgba(255,255,255,0)");
  //   ctx.fillStyle = glow;
  //   ctx.arc(comet.x, comet.y, comet.size, 0, Math.PI * 2);
  //   ctx.fill();

  //   if (comet.x > w + 100 || comet.y > h + 100 || comet.life <= 0) {
  //     comets.splice(i, 1);
  //   }
  // }

  requestAnimationFrame(animate);
}
animate();

const toggle = document.createElement('button');
toggle.innerText = "🌓";
toggle.style.position = 'fixed';
toggle.style.top = '20px';
toggle.style.right = '20px';
toggle.style.padding = '10px 16px';
toggle.style.backgroundColor = '#394b61';
toggle.style.color = '#fff';
toggle.style.border = 'none';
toggle.style.cursor = 'pointer';
toggle.style.borderRadius = '4px';
toggle.style.zIndex = 10;
document.body.appendChild(toggle);

toggle.onclick = () => {
  document.body.classList.toggle('light-theme');
};
