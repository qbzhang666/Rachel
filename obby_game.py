import json
import random
from string import Template


DIFFICULTIES = {
    "Chill": {
        "speed": 1.0,
        "time_limit": 240,
        "hazard_speed": 0.9,
        "gravity": 0.82,
    },
    "Challenge": {
        "speed": 1.12,
        "time_limit": 180,
        "hazard_speed": 1.18,
        "gravity": 0.86,
    },
    "Tower Mode": {
        "speed": 1.25,
        "time_limit": 135,
        "hazard_speed": 1.45,
        "gravity": 0.9,
    },
}

HEIGHTS = {
    "Short": 5,
    "Classic": 7,
    "Tall": 9,
}


def build_game_html(config: dict[str, object]) -> str:
    config_json = json.dumps(config)
    template = Template(
        r"""
<div class="obby-shell">
    <canvas id="obbyCanvas" width="980" height="640" tabindex="0" aria-label="Tower obby game"></canvas>
    <div class="obby-controls" aria-hidden="true">
        <button id="btnLeft">A</button>
        <button id="btnJump">JUMP</button>
        <button id="btnRight">D</button>
        <button id="btnReset">R</button>
    </div>
</div>

<style>
    .obby-shell {
        width: min(100%, 1080px);
        margin: 0 auto;
        border: 1px solid #d8dee9;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
        padding: 14px;
    }
    #obbyCanvas {
        width: 100%;
        aspect-ratio: 49 / 32;
        display: block;
        border-radius: 8px;
        background: #111827;
        outline: none;
        touch-action: none;
    }
    .obby-controls {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
    }
    .obby-controls button {
        border: 0;
        border-radius: 8px;
        background: #172033;
        color: #ffffff;
        min-height: 48px;
        font: 800 0.9rem Arial, sans-serif;
        cursor: pointer;
        box-shadow: 0 8px 16px rgba(15, 23, 42, 0.15);
    }
    .obby-controls button:active {
        transform: translateY(1px);
        background: #2563eb;
    }
    @media (min-width: 900px) {
        .obby-controls {
            display: none;
        }
    }
</style>

<script>
(() => {
    const CONFIG = $config_json;
    const canvas = document.getElementById("obbyCanvas");
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;
    const worldW = 980;
    const sectionH = 520;
    const floorH = 70;
    const sections = Number(CONFIG.sections || 7);
    const totalH = sections * sectionH + floorH + 200;
    const keys = Object.create(null);
    const palette = CONFIG.palette || "Neon";

    let seed = Number(CONFIG.seed || 2026);
    let cameraY = totalH - H;
    let deaths = 0;
    let started = false;
    let won = false;
    let expired = false;
    let startTime = 0;
    let finishTime = 0;
    let lastTime = performance.now();
    let checkpoint = { x: 74, y: totalH - floorH - 50 };
    let bestHeight = 0;

    const colours = {
        Neon: {
            skyTop: "#0f172a",
            skyBottom: "#172033",
            platform: "#e2e8f0",
            platformEdge: "#38bdf8",
            player: "#facc15",
            playerDark: "#f97316",
            hazard: "#ef4444",
            hazardGlow: "rgba(239, 68, 68, 0.34)",
            moving: "#34d399",
            goal: "#a78bfa",
            text: "#f8fafc",
            muted: "#cbd5e1",
        },
        Candy: {
            skyTop: "#1e1b4b",
            skyBottom: "#312e81",
            platform: "#fff7ed",
            platformEdge: "#fb7185",
            player: "#67e8f9",
            playerDark: "#06b6d4",
            hazard: "#f43f5e",
            hazardGlow: "rgba(244, 63, 94, 0.34)",
            moving: "#bef264",
            goal: "#f9a8d4",
            text: "#ffffff",
            muted: "#e0e7ff",
        },
        Mint: {
            skyTop: "#042f2e",
            skyBottom: "#134e4a",
            platform: "#ecfeff",
            platformEdge: "#2dd4bf",
            player: "#fde68a",
            playerDark: "#f59e0b",
            hazard: "#fb7185",
            hazardGlow: "rgba(251, 113, 133, 0.34)",
            moving: "#93c5fd",
            goal: "#c4b5fd",
            text: "#f8fafc",
            muted: "#ccfbf1",
        },
    }[palette];

    const player = {
        x: checkpoint.x,
        y: checkpoint.y,
        w: 30,
        h: 38,
        vx: 0,
        vy: 0,
        onGround: false,
        face: 1,
        coyote: 0,
    };

    const platforms = [];
    const hazards = [];
    const spinners = [];
    const goal = {
        x: 388,
        y: 84,
        w: 204,
        h: 26,
    };

    function rand() {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 4294967296;
    }

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function rectsOverlap(a, b) {
        return a.x < b.x + b.w &&
            a.x + a.w > b.x &&
            a.y < b.y + b.h &&
            a.y + a.h > b.y;
    }

    function stageColour(index) {
        const colours = ["#2563eb", "#0f766e", "#d97706", "#7c3aed", "#be123c", "#0891b2"];
        return colours[index % colours.length];
    }

    function addPlatform(platform) {
        platforms.push({
            type: "solid",
            x: platform.x,
            y: platform.y,
            w: platform.w,
            h: platform.h || 18,
            baseX: platform.x,
            range: platform.range || 0,
            speed: platform.speed || 0,
            phase: platform.phase || 0,
            dx: 0,
            colour: platform.colour || colours.platform,
            edge: platform.edge || colours.platformEdge,
        });
    }

    function addHazard(hazard) {
        hazards.push({
            x: hazard.x,
            y: hazard.y,
            w: hazard.w,
            h: hazard.h,
            baseX: hazard.x,
            baseY: hazard.y,
            rangeX: hazard.rangeX || 0,
            rangeY: hazard.rangeY || 0,
            speed: hazard.speed || 0,
            phase: hazard.phase || 0,
        });
    }

    function addSpinner(spinner) {
        spinners.push({
            cx: spinner.cx,
            cy: spinner.cy,
            len: spinner.len,
            thickness: spinner.thickness,
            speed: spinner.speed,
            phase: spinner.phase,
        });
    }

    function buildTower() {
        addPlatform({ x: 0, y: totalH - floorH, w: worldW, h: floorH, edge: "#64748b" });

        for (let s = 0; s < sections; s += 1) {
            const top = totalH - floorH - (s + 1) * sectionH;
            const base = top + sectionH;
            const edge = stageColour(s);
            const pattern = s % 4;
            const wobble = 30 + rand() * 60;

            if (pattern === 0) {
                addPlatform({ x: 82, y: base - 88, w: 220, edge });
                addPlatform({ x: 356, y: base - 168, w: 190, edge, range: 90, speed: 1.1, phase: rand() * 6 });
                addPlatform({ x: 650, y: base - 248, w: 230, edge });
                addPlatform({ x: 426, y: base - 340, w: 180, edge });
                addPlatform({ x: 132, y: base - 430, w: 240, edge, range: 70, speed: 1.4, phase: rand() * 6 });
                addHazard({ x: 318, y: base - 72, w: 36, h: 28, rangeX: 260, speed: 1.5, phase: rand() * 6 });
                addHazard({ x: 0, y: base - 304, w: worldW, h: 16, rangeY: wobble, speed: 0.7, phase: rand() * 6 });
            } else if (pattern === 1) {
                addPlatform({ x: 688, y: base - 82, w: 200, edge });
                addPlatform({ x: 444, y: base - 158, w: 160, edge });
                addPlatform({ x: 174, y: base - 242, w: 180, edge, range: 110, speed: 1.2, phase: rand() * 6 });
                addPlatform({ x: 480, y: base - 328, w: 190, edge });
                addPlatform({ x: 742, y: base - 422, w: 156, edge });
                addSpinner({ cx: 490, cy: base - 244, len: 220, thickness: 14, speed: 1.1, phase: rand() * 6 });
                addHazard({ x: 104, y: base - 384, w: 44, h: 34, rangeX: 360, speed: 1.35, phase: rand() * 6 });
            } else if (pattern === 2) {
                addPlatform({ x: 114, y: base - 80, w: 180, edge });
                addPlatform({ x: 350, y: base - 150, w: 170, edge });
                addPlatform({ x: 598, y: base - 220, w: 180, edge });
                addPlatform({ x: 360, y: base - 310, w: 160, edge, range: 130, speed: 1.55, phase: rand() * 6 });
                addPlatform({ x: 110, y: base - 414, w: 190, edge });
                addHazard({ x: 0, y: base - 118, w: 280, h: 16, rangeX: 620, speed: 1.0, phase: rand() * 6 });
                addSpinner({ cx: 678, cy: base - 338, len: 170, thickness: 14, speed: -1.25, phase: rand() * 6 });
            } else {
                addPlatform({ x: 396, y: base - 84, w: 170, edge, range: 150, speed: 1.25, phase: rand() * 6 });
                addPlatform({ x: 146, y: base - 176, w: 180, edge });
                addPlatform({ x: 654, y: base - 260, w: 176, edge });
                addPlatform({ x: 440, y: base - 348, w: 178, edge });
                addPlatform({ x: 222, y: base - 430, w: 190, edge, range: 80, speed: 1.4, phase: rand() * 6 });
                addHazard({ x: 590, y: base - 134, w: 48, h: 36, rangeX: 220, speed: 1.4, phase: rand() * 6 });
                addSpinner({ cx: 418, cy: base - 276, len: 210, thickness: 14, speed: 1.35, phase: rand() * 6 });
            }

            addHazard({ x: 0, y: top + 10, w: worldW, h: 12, rangeX: 0, speed: 0 });
        }

        addPlatform({ x: 322, y: goal.y + 46, w: 336, h: 20, edge: colours.goal });
    }

    buildTower();

    function resetPlayer(useCheckpoint) {
        const target = useCheckpoint ? checkpoint : { x: 74, y: totalH - floorH - 50 };
        player.x = target.x;
        player.y = target.y;
        player.vx = 0;
        player.vy = 0;
        player.onGround = false;
        player.coyote = 0;
        if (!useCheckpoint) {
            checkpoint = { x: 74, y: totalH - floorH - 50 };
        }
    }

    function die() {
        deaths += 1;
        resetPlayer(Boolean(CONFIG.practice));
    }

    function jump() {
        if (player.onGround || player.coyote > 0) {
            player.vy = -17.2;
            player.onGround = false;
            player.coyote = 0;
        }
    }

    function handleKey(event, value) {
        const code = event.code;
        if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Space"].includes(code)) {
            event.preventDefault();
        }
        keys[code] = value;
        if (value && (code === "Space" || code === "ArrowUp" || code === "KeyW")) {
            if (!started) startRun();
            jump();
        }
        if (value && code === "KeyR") {
            deaths += 1;
            resetPlayer(false);
            expired = false;
            won = false;
            startRun();
        }
    }

    function startRun() {
        if (!started || expired || won) {
            started = true;
            won = false;
            expired = false;
            startTime = performance.now();
            finishTime = 0;
            resetPlayer(false);
        }
    }

    window.addEventListener("keydown", (event) => handleKey(event, true), { passive: false });
    window.addEventListener("keyup", (event) => {
        keys[event.code] = false;
    });
    canvas.addEventListener("pointerdown", () => {
        canvas.focus();
        if (!started) startRun();
    });

    function bindButton(id, codes) {
        const button = document.getElementById(id);
        const setCodes = (value) => {
            codes.forEach((code) => {
                keys[code] = value;
            });
            if (value && codes.includes("Space")) {
                if (!started) startRun();
                jump();
            }
            if (value && codes.includes("KeyR")) {
                deaths += 1;
                resetPlayer(false);
                startRun();
            }
        };
        button.addEventListener("pointerdown", (event) => {
            event.preventDefault();
            setCodes(true);
            canvas.focus();
        });
        button.addEventListener("pointerup", () => setCodes(false));
        button.addEventListener("pointerleave", () => setCodes(false));
        button.addEventListener("pointercancel", () => setCodes(false));
    }

    bindButton("btnLeft", ["ArrowLeft", "KeyA"]);
    bindButton("btnRight", ["ArrowRight", "KeyD"]);
    bindButton("btnJump", ["Space"]);
    bindButton("btnReset", ["KeyR"]);

    function updateMovingObjects(time) {
        const hazardSpeed = Number(CONFIG.hazard_speed || 1);
        platforms.forEach((platform) => {
            const oldX = platform.x;
            if (platform.range) {
                platform.x = platform.baseX + Math.sin(time * platform.speed * 0.001 * hazardSpeed + platform.phase) * platform.range;
            }
            platform.dx = platform.x - oldX;
        });
        hazards.forEach((hazard) => {
            hazard.x = hazard.baseX + Math.sin(time * hazard.speed * 0.001 * hazardSpeed + hazard.phase) * hazard.rangeX;
            hazard.y = hazard.baseY + Math.sin(time * hazard.speed * 0.001 * hazardSpeed + hazard.phase) * hazard.rangeY;
        });
    }

    function updatePlayer(dt) {
        const speed = 6.2 * Number(CONFIG.speed || 1);
        const left = keys.ArrowLeft || keys.KeyA;
        const right = keys.ArrowRight || keys.KeyD;
        const desired = (right ? 1 : 0) - (left ? 1 : 0);

        if (desired !== 0) {
            player.face = desired;
        }

        player.vx += desired * 1.1;
        player.vx *= player.onGround ? 0.77 : 0.88;
        player.vx = clamp(player.vx, -speed, speed);
        player.vy += Number(CONFIG.gravity || 0.86);
        player.vy = clamp(player.vy, -22, 22);

        const previous = { x: player.x, y: player.y, w: player.w, h: player.h };

        player.x += player.vx * dt;
        player.x = clamp(player.x, 8, worldW - player.w - 8);

        player.y += player.vy * dt;
        player.onGround = false;

        for (const platform of platforms) {
            const p = { x: platform.x, y: platform.y, w: platform.w, h: platform.h };
            const fallingOnto = previous.y + previous.h <= p.y + 4 && player.y + player.h >= p.y && player.vy >= 0;
            if (fallingOnto && player.x + player.w > p.x && player.x < p.x + p.w) {
                player.y = p.y - player.h;
                player.vy = 0;
                player.onGround = true;
                player.x += platform.dx || 0;
            }
        }

        if (player.onGround) {
            player.coyote = 8;
        } else {
            player.coyote = Math.max(0, player.coyote - 1);
        }

        if (player.y > totalH + 160) {
            die();
        }

        const heightNow = Math.max(0, Math.round((totalH - floorH - player.y) / 10));
        bestHeight = Math.max(bestHeight, heightNow);

        if (CONFIG.practice) {
            const currentSection = Math.floor((totalH - floorH - player.y) / sectionH);
            if (currentSection > Math.floor((totalH - floorH - checkpoint.y) / sectionH)) {
                checkpoint = { x: player.x, y: player.y };
            }
        }
    }

    function hitSpinner(spinner) {
        const time = performance.now();
        const angle = time * spinner.speed * 0.001 * Number(CONFIG.hazard_speed || 1) + spinner.phase;
        const ax = spinner.cx - Math.cos(angle) * spinner.len / 2;
        const ay = spinner.cy - Math.sin(angle) * spinner.len / 2;
        const bx = spinner.cx + Math.cos(angle) * spinner.len / 2;
        const by = spinner.cy + Math.sin(angle) * spinner.len / 2;
        const px = player.x + player.w / 2;
        const py = player.y + player.h / 2;
        const abx = bx - ax;
        const aby = by - ay;
        const apx = px - ax;
        const apy = py - ay;
        const ab2 = abx * abx + aby * aby;
        const t = clamp((apx * abx + apy * aby) / ab2, 0, 1);
        const cx = ax + abx * t;
        const cy = ay + aby * t;
        const dx = px - cx;
        const dy = py - cy;
        return Math.sqrt(dx * dx + dy * dy) < spinner.thickness + 16;
    }

    function updateHazards() {
        const body = { x: player.x + 4, y: player.y + 4, w: player.w - 8, h: player.h - 8 };
        for (const hazard of hazards) {
            if (rectsOverlap(body, hazard)) {
                die();
                return;
            }
        }
        for (const spinner of spinners) {
            if (hitSpinner(spinner)) {
                die();
                return;
            }
        }
        if (rectsOverlap(player, goal)) {
            won = true;
            finishTime = performance.now();
        }
    }

    function remainingSeconds(now) {
        if (!started) return Number(CONFIG.time_limit || 180);
        if (won) {
            return Math.max(0, Math.ceil((Number(CONFIG.time_limit || 180) * 1000 - (finishTime - startTime)) / 1000));
        }
        return Math.max(0, Math.ceil((Number(CONFIG.time_limit || 180) * 1000 - (now - startTime)) / 1000));
    }

    function drawRoundedRect(x, y, w, h, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + w - radius, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
        ctx.lineTo(x + w, y + h - radius);
        ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
        ctx.lineTo(x + radius, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
        ctx.fill();
    }

    function drawBackground() {
        const sky = ctx.createLinearGradient(0, 0, 0, H);
        sky.addColorStop(0, colours.skyTop);
        sky.addColorStop(1, colours.skyBottom);
        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, W, H);

        ctx.save();
        ctx.translate(0, -cameraY);
        for (let s = 0; s < sections; s += 1) {
            const y = totalH - floorH - (s + 1) * sectionH;
            ctx.fillStyle = s % 2 === 0 ? "rgba(255,255,255,0.035)" : "rgba(255,255,255,0.065)";
            ctx.fillRect(0, y, worldW, sectionH);
            ctx.fillStyle = stageColour(s);
            ctx.globalAlpha = 0.28;
            ctx.fillRect(0, y + 4, worldW, 5);
            ctx.globalAlpha = 1;
        }

        ctx.strokeStyle = "rgba(255,255,255,0.06)";
        ctx.lineWidth = 1;
        for (let x = 0; x <= worldW; x += 70) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, totalH);
            ctx.stroke();
        }
        ctx.restore();
    }

    function drawPlatforms() {
        ctx.save();
        ctx.translate(0, -cameraY);
        for (const p of platforms) {
            ctx.shadowColor = "rgba(0,0,0,0.18)";
            ctx.shadowBlur = 10;
            ctx.fillStyle = p.colour;
            drawRoundedRect(p.x, p.y, p.w, p.h, 8);
            ctx.shadowBlur = 0;
            ctx.fillStyle = p.edge;
            ctx.fillRect(p.x, p.y, p.w, 5);
            if (p.range) {
                ctx.fillStyle = colours.moving;
                ctx.globalAlpha = 0.22;
                ctx.fillRect(p.baseX - p.range, p.y + p.h + 7, p.range * 2 + p.w, 4);
                ctx.globalAlpha = 1;
            }
        }
        ctx.restore();
    }

    function drawHazards(now) {
        ctx.save();
        ctx.translate(0, -cameraY);
        for (const h of hazards) {
            ctx.fillStyle = colours.hazardGlow;
            drawRoundedRect(h.x - 6, h.y - 6, h.w + 12, h.h + 12, 10);
            ctx.fillStyle = colours.hazard;
            drawRoundedRect(h.x, h.y, h.w, h.h, 6);
        }
        for (const s of spinners) {
            const angle = now * s.speed * 0.001 * Number(CONFIG.hazard_speed || 1) + s.phase;
            const ax = s.cx - Math.cos(angle) * s.len / 2;
            const ay = s.cy - Math.sin(angle) * s.len / 2;
            const bx = s.cx + Math.cos(angle) * s.len / 2;
            const by = s.cy + Math.sin(angle) * s.len / 2;
            ctx.lineCap = "round";
            ctx.strokeStyle = colours.hazardGlow;
            ctx.lineWidth = s.thickness + 12;
            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(bx, by);
            ctx.stroke();
            ctx.strokeStyle = colours.hazard;
            ctx.lineWidth = s.thickness;
            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(bx, by);
            ctx.stroke();
            ctx.fillStyle = "#ffffff";
            ctx.globalAlpha = 0.9;
            ctx.beginPath();
            ctx.arc(s.cx, s.cy, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;
        }
        ctx.restore();
    }

    function drawPlayer() {
        ctx.save();
        ctx.translate(0, -cameraY);
        ctx.shadowColor = "rgba(250, 204, 21, 0.55)";
        ctx.shadowBlur = 18;
        ctx.fillStyle = colours.player;
        drawRoundedRect(player.x, player.y, player.w, player.h, 8);
        ctx.shadowBlur = 0;
        ctx.fillStyle = colours.playerDark;
        drawRoundedRect(player.x + 7, player.y + 8, player.w - 14, 7, 4);
        ctx.fillStyle = "#172033";
        const eyeX = player.face > 0 ? player.x + 20 : player.x + 8;
        ctx.fillRect(eyeX, player.y + 10, 4, 4);
        ctx.restore();
    }

    function drawGoal(now) {
        ctx.save();
        ctx.translate(0, -cameraY);
        const pulse = 0.75 + Math.sin(now * 0.006) * 0.25;
        ctx.fillStyle = "rgba(167, 139, 250, " + (0.22 + pulse * 0.18) + ")";
        drawRoundedRect(goal.x - 18, goal.y - 20, goal.w + 36, goal.h + 44, 12);
        ctx.fillStyle = colours.goal;
        drawRoundedRect(goal.x, goal.y, goal.w, goal.h, 10);
        ctx.fillStyle = colours.text;
        ctx.font = "800 18px Arial";
        ctx.textAlign = "center";
        ctx.fillText("FINISH", goal.x + goal.w / 2, goal.y - 8);
        ctx.restore();
    }

    function drawHud(now) {
        const remaining = remainingSeconds(now);
        const level = Math.min(sections, Math.max(1, Math.floor((totalH - floorH - player.y) / sectionH) + 1));
        const chips = [
            "Stage " + level + "/" + sections,
            "Time " + remaining + "s",
            "Falls " + deaths,
            "Height " + bestHeight,
        ];
        ctx.font = "800 15px Arial";
        ctx.textAlign = "left";
        let x = 18;
        for (const chip of chips) {
            const width = ctx.measureText(chip).width + 26;
            ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
            drawRoundedRect(x, 18, width, 34, 10);
            ctx.fillStyle = colours.text;
            ctx.fillText(chip, x + 13, 40);
            x += width + 10;
        }

        const progress = clamp((totalH - floorH - player.y) / (totalH - floorH - goal.y), 0, 1);
        ctx.fillStyle = "rgba(255,255,255,0.16)";
        drawRoundedRect(W - 34, 74, 12, H - 140, 999);
        ctx.fillStyle = colours.goal;
        drawRoundedRect(W - 34, 74 + (H - 140) * (1 - progress), 12, (H - 140) * progress, 999);

        if (remaining <= 0 && started && !won) {
            expired = true;
            started = false;
            deaths += 1;
            resetPlayer(false);
        }
    }

    function drawOverlay(now) {
        if (started && !won && !expired) return;
        ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
        ctx.fillRect(0, 0, W, H);
        ctx.textAlign = "center";
        ctx.fillStyle = colours.text;
        ctx.font = "900 44px Arial";
        let title = "Tower Rush Obby";
        if (won) title = "Tower cleared";
        if (expired) title = "Time reset";
        ctx.fillText(title, W / 2, H / 2 - 64);

        ctx.font = "700 18px Arial";
        ctx.fillStyle = colours.muted;
        let subtitle = "A D to move, Space to jump, R to reset";
        if (won) {
            const elapsed = Math.round((finishTime - startTime) / 1000);
            subtitle = "Clear time " + elapsed + "s with " + deaths + " falls";
        }
        if (expired) {
            subtitle = "Start again before the timer runs out";
        }
        ctx.fillText(subtitle, W / 2, H / 2 - 24);

        ctx.fillStyle = colours.goal;
        drawRoundedRect(W / 2 - 110, H / 2 + 14, 220, 52, 14);
        ctx.fillStyle = "#111827";
        ctx.font = "900 17px Arial";
        ctx.fillText(won ? "RUN AGAIN" : "START RUN", W / 2, H / 2 + 47);
    }

    canvas.addEventListener("click", (event) => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = W / rect.width;
        const scaleY = H / rect.height;
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
        if (!started || won || expired) {
            if (x >= W / 2 - 130 && x <= W / 2 + 130 && y >= H / 2 && y <= H / 2 + 86) {
                startRun();
            }
        }
    });

    function loop(now) {
        const dt = Math.min(1.6, (now - lastTime) / 16.67);
        lastTime = now;

        if (started && !won && !expired) {
            updateMovingObjects(now);
            updatePlayer(dt);
            updateHazards();
        } else {
            updateMovingObjects(now);
        }

        const targetCamera = clamp(player.y - 400, 0, totalH - H);
        cameraY += (targetCamera - cameraY) * 0.08;

        drawBackground();
        drawGoal(now);
        drawPlatforms();
        drawHazards(now);
        drawPlayer();
        drawHud(now);
        drawOverlay(now);
        requestAnimationFrame(loop);
    }

    requestAnimationFrame(loop);
})();
</script>
"""
    )
    return template.safe_substitute(config_json=config_json)


def main() -> None:
    import streamlit as st
    import streamlit.components.v1 as components

    st.set_page_config(
        page_title="Tower Rush Obby",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(90deg, rgba(37, 99, 235, 0.09), rgba(15, 118, 110, 0.09), rgba(217, 119, 6, 0.09)),
                #f8fafc;
        }
        .block-container {
            max-width: 1180px;
            padding-top: 1.2rem;
        }
        .game-topbar {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }
        .game-topbar h1 {
            margin: 0;
            color: #172033;
            font-size: 2rem;
            letter-spacing: 0;
        }
        .game-topbar span {
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            border-radius: 999px;
            background: #ffffff;
            border: 1px solid #d9e2ec;
            color: #334155;
            padding: 0 0.9rem;
            font-weight: 800;
        }
        div.stButton > button[kind="primary"] {
            min-height: 44px;
            font-weight: 800;
            background: linear-gradient(135deg, #2563eb, #0f766e);
            border: 0;
        }
        @media (max-width: 720px) {
            .game-topbar {
                align-items: flex-start;
                flex-direction: column;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "obby_seed" not in st.session_state:
        st.session_state.obby_seed = random.randint(10_000, 999_999)

    with st.sidebar:
        st.header("Tower setup")
        difficulty_name = st.selectbox("Difficulty", list(DIFFICULTIES), index=1)
        height_name = st.selectbox("Tower height", list(HEIGHTS), index=1)
        palette = st.selectbox("Style", ["Neon", "Candy", "Mint"], index=0)
        practice = st.toggle("Practice checkpoints", value=False)
        if st.button("Build new tower", type="primary", use_container_width=True):
            st.session_state.obby_seed = random.randint(10_000, 999_999)

    difficulty = DIFFICULTIES[difficulty_name]
    config = {
        **difficulty,
        "sections": HEIGHTS[height_name],
        "palette": palette,
        "practice": practice,
        "seed": st.session_state.obby_seed,
    }

    st.markdown(
        f"""
        <div class="game-topbar">
            <h1>Tower Rush Obby</h1>
            <span>{difficulty_name} | {height_name} tower</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components.html(build_game_html(config), height=760, scrolling=False)


if __name__ == "__main__":
    main()
