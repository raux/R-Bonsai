const MODES = {
  0: {
    name: "Classic Bonsai",
    axiom: "X",
    rules: { X: "F+[[X]-X]-F[-FX]+X", F: "FF" },
    angle: 25,
    iterations: 5,
  },
  1: {
    name: "Koch Snowflake",
    axiom: "F++F++F",
    rules: { F: "F-F++F-F" },
    angle: 60,
    iterations: 4,
  },
};

const form = document.getElementById("configForm");
const modeSelect = document.getElementById("modeSelect");
const iterationsInput = document.getElementById("iterations");
const axiomInput = document.getElementById("axiom");
const rulesInput = document.getElementById("rules");
const angleInput = document.getElementById("angle");
const statusEl = document.getElementById("status");
const outputEl = document.getElementById("lsysOutput");
const canvas = document.getElementById("bonsaiCanvas");
const ctx = canvas.getContext("2d");

let displayWidth = canvas.clientWidth || canvas.width;
let displayHeight = canvas.clientHeight || canvas.height;

function resizeCanvas() {
  const ratio = window.devicePixelRatio || 1;
  displayWidth = canvas.clientWidth || canvas.width;
  displayHeight = displayWidth * 0.72;
  canvas.width = displayWidth * ratio;
  canvas.height = displayHeight * ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

function populateFromMode(modeId) {
  const mode = MODES[modeId];
  if (!mode) {
    return;
  }
  axiomInput.value = mode.axiom;
  rulesInput.value = JSON.stringify(mode.rules, null, 0);
  angleInput.value = mode.angle;
  iterationsInput.value = mode.iterations;
  statusEl.textContent = `${mode.name} preset loaded.`;
}

async function generateSequence(payload) {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  if (!response.ok) {
    const detail = data?.detail || "Generation failed";
    throw new Error(detail);
  }
  return data;
}

function calculateStep(length, iterations, modeId) {
  const span = Math.min(displayWidth, displayHeight);
  if (modeId === 1) {
    return Math.max(2, (span * 0.8) / (iterations + 3) / 3);
  }
  return Math.max(2, (span * 0.5) / (10 + iterations * 3 + Math.sqrt(length) * 0.3));
}

function animateSequence(sequence, angleDeg, modeId, iterations) {
  ctx.clearRect(0, 0, displayWidth, displayHeight);
  const angle = (angleDeg * Math.PI) / 180;
  const stack = [];
  const step = calculateStep(sequence.length, iterations, modeId);
  const start =
    modeId === 1
      ? { x: displayWidth * 0.12, y: displayHeight * 0.6, heading: 0 }
      : { x: displayWidth / 2, y: displayHeight * 0.95, heading: -Math.PI / 2 };

  let x = start.x;
  let y = start.y;
  let heading = start.heading;
  let index = 0;

  ctx.lineWidth = 2;
  ctx.strokeStyle = modeId === 1 ? "#7ae1b1" : "#37c7f4";
  ctx.lineCap = "round";

  const batchSize = 14;

  function tick() {
    ctx.beginPath();
    let processed = 0;
    while (index < sequence.length && processed < batchSize) {
      const symbol = sequence[index++];
      switch (symbol) {
        case "F": {
          const nextX = x + Math.cos(heading) * step;
          const nextY = y + Math.sin(heading) * step;
          ctx.moveTo(x, y);
          ctx.lineTo(nextX, nextY);
          x = nextX;
          y = nextY;
          break;
        }
        case "+":
          heading += angle;
          break;
        case "-":
          heading -= angle;
          break;
        case "[":
          stack.push({ x, y, heading });
          break;
        case "]": {
          const state = stack.pop();
          if (state) {
            ({ x, y, heading } = state);
          }
          break;
        }
        default:
          break;
      }
      processed += 1;
    }
    ctx.stroke();

    if (index < sequence.length) {
      requestAnimationFrame(tick);
    } else {
      statusEl.textContent = `Animation complete. ${sequence.length} symbols rendered.`;
    }
  }

  tick();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const modeId = Number(modeSelect.value);
    const iterations = Number(iterationsInput.value);
    const angle = Number(angleInput.value);
    const axiom = axiomInput.value.trim();
    const rules = JSON.parse(rulesInput.value);

    if (!axiom) {
      throw new Error("Axiom is required.");
    }

    statusEl.textContent = "Generating...";

    const payload = { mode: modeId, iterations, axiom, rules, angle };
    const data = await generateSequence(payload);

    outputEl.textContent = data.result;
    statusEl.textContent = `Generated ${data.result.length} symbols @ ${data.angle}°. Animating...`;

    animateSequence(data.result, data.angle, modeId, iterations);
  } catch (error) {
    statusEl.textContent = error.message || "Failed to generate.";
    console.error(error);
  }
});

modeSelect.addEventListener("change", () => {
  populateFromMode(Number(modeSelect.value));
});

populateFromMode(Number(modeSelect.value));
