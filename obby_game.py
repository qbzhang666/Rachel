import json
import random
from string import Template


DIFFICULTIES = {
    "Easy Flow": {
        "speed": 1.0,
        "time_limit": 300,
        "hazard_speed": 0.7,
        "gravity": 0.62,
        "jump": 15.8,
    },
    "Red Rush": {
        "speed": 1.06,
        "time_limit": 240,
        "hazard_speed": 0.9,
        "gravity": 0.66,
        "jump": 16.0,
    },
    "Challenge": {
        "speed": 1.12,
        "time_limit": 210,
        "hazard_speed": 1.05,
        "gravity": 0.7,
        "jump": 16.2,
    },
}

HEIGHTS = {
    "Mini": 4,
    "Classic": 6,
    "Big": 8,
}

PALETTES = {
    "Neon": {
        "sky_a": "#111827",
        "sky_b": "#172033",
        "sky_c": "#312e81",
        "platform": "#f8fafc",
        "edge": "#38bdf8",
        "player": "#facc15",
        "player_shadow": "#f97316",
        "goal": "#a78bfa",
        "accent": "#22d3ee",
    },
    "Arcade": {
        "sky_a": "#1e1b4b",
        "sky_b": "#831843",
        "sky_c": "#0f766e",
        "platform": "#fff7ed",
        "edge": "#fb7185",
        "player": "#67e8f9",
        "player_shadow": "#0891b2",
        "goal": "#bef264",
        "accent": "#f9a8d4",
    },
    "Street": {
        "sky_a": "#0f172a",
        "sky_b": "#3b0764",
        "sky_c": "#064e3b",
        "platform": "#e2e8f0",
        "edge": "#f59e0b",
        "player": "#a7f3d0",
        "player_shadow": "#10b981",
        "goal": "#f0abfc",
        "accent": "#fbbf24",
    },
}


def build_game_html(config: dict[str, object]) -> str:
    config_json = json.dumps(config)
    template = Template(
        r"""
<div class="obby-card">
    <div class="game-toolbar">
        <button id="playButton" type="button">Play</button>
        <button id="musicButton" type="button">Music Off</button>
        <button id="resetButton" type="button">Reset</button>
    </div>
    <canvas id="obbyCanvas" width="980" height="640" tabindex="0" aria-label="Red obstacle tower game"></canvas>
    <div class="mobile-controls" aria-hidden="true">
        <button id="leftButton" type="button">A</button>
        <button id="jumpButton" type="button">Jump</button>
        <button id="rightButton" type="button">D</button>
    </div>
</div>

<style>
    .obby-card {
        width: min(100%, 1080px);
        margin: 0 auto;
        padding: 14px;
        border: 1px solid #d9e2ec;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
    }
    .game-toolbar {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-bottom: 12px;
    }
    .game-toolbar button,
    .mobile-controls button {
        border: 0;
        border-radius: 8px;
        min-height: 46px;
        color: #ffffff;
        background: linear-gradient(135deg, #172033, #2563eb);
        font: 800 0.94rem Arial, sans-serif;
        cursor: pointer;
        box-shadow: 0 8px 16px rgba(15, 23, 42, 0.15);
    }
    #musicButton {
        background: linear-gradient(135deg, #be123c, #7c3aed);
    }
    #playButton {
        background: linear-gradient(135deg, #0f766e, #2563eb);
    }
    #resetButton {
        background: linear-gradient(135deg, #d97706, #be123c);
    }
    .game-toolbar button:active,
    .mobile-controls button:active {
        transform: translateY(1px);
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
    .mobile-controls {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
    }
    .mobile-controls button {
        min-height: 54px;
        font-size: 1rem;
    }
    @media (min-width: 900px) {
        .mobile-controls {
            display: none;
        }
    }
</style>

<script>
(() => {
    const CONFIG = $config_json;
    const canvas = document.getElementById("obbyCanvas");
    const ctx = canvas.getContext("2d");
    const playButton = document.getElementById("playButton");
    const musicButton = document.getElementById("musicButton");
    const resetButton = document.getElementById("resetButton");
    const W = canvas.width;
    const H = canvas.height;
    const worldW = 980;
    const sectionH = 430;
    const floorH = 76;
    const sections = Number(CONFIG.sections || 6);
    const totalH = sections * sectionH + floorH + 180;
    const palette = CONFIG.palette || {};
    const keys = Object.create(null);
    const hazards = [];
    const platforms = [];
    const particles = [];
    const confetti = [];

    let seed = Number(CONFIG.seed || 2026);
    let cameraY = totalH - H;
    let deaths = 0;
    let started = false;
    let won = false;
    let expired = false;
    let startTime = 0;
    let finishTime = 0;
    let lastTime = performance.now();
    let checkpoint = { x: 82, y: totalH - floorH - 48 };
    let bestHeight = 0;
    let messageTimer = 0;
    let audioContext = null;
    let musicTimer = null;
    let musicStep = 0;
    let musicTrack = 0;

    const player = {
        x: checkpoint.x,
        y: checkpoint.y,
        w: 34,
        h: 42,
        vx: 0,
        vy: 0,
        onGround: false,
        jumpsLeft: 2,
        jumpBuffer: 0,
        coyote: 0,
        face: 1,
    };

    const goal = {
        x: 340,
        y: 80,
        w: 300,
        h: 30,
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

    function roundedRect(x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
        ctx.fill();
    }

    function addPlatform(x, y, w, h, edge) {
        platforms.push({ x, y, w, h, edge });
    }

    function addHazard(x, y, w, h, options) {
        hazards.push({
            x,
            y,
            w,
            h,
            baseX: x,
            baseY: y,
            rangeX: options.rangeX || 0,
            rangeY: options.rangeY || 0,
            speed: options.speed || 0,
            phase: options.phase || 0,
        });
    }

    function buildTower() {
        addPlatform(0, totalH - floorH, worldW, floorH, "#64748b");

        for (let s = 0; s < sections; s += 1) {
            const top = totalH - floorH - (s + 1) * sectionH;
            const base = top + sectionH;
            const edge = ["#38bdf8", "#fb7185", "#f59e0b", "#a78bfa", "#22c55e"][s % 5];
            const rightFirst = s % 2 === 1;
            const xs = rightFirst ? [620, 360, 95, 415, 650] : [80, 350, 625, 405, 120];
            const widths = [300, 280, 310, 260, 300];

            addPlatform(xs[0], base - 82, widths[0], 20, edge);
            addPlatform(xs[1], base - 158, widths[1], 20, edge);
            addPlatform(xs[2], base - 238, widths[2], 20, edge);
            addPlatform(xs[3], base - 318, widths[3], 20, edge);
            addPlatform(xs[4], base - 394, widths[4], 20, edge);

            if (s % 3 === 0) {
                addHazard(410, base - 124, 150, 18, { rangeX: 210, speed: 0.8, phase: rand() * 6 });
                addHazard(0, base - 282, 250, 18, { rangeX: 540, speed: 0.65, phase: rand() * 6 });
            } else if (s % 3 === 1) {
                addHazard(260, base - 202, 520, 18, { rangeY: 24, speed: 0.7, phase: rand() * 6 });
                addHazard(700, base - 366, 68, 48, { rangeX: 110, speed: 0.9, phase: rand() * 6 });
            } else {
                addHazard(185, base - 128, 68, 48, { rangeX: 120, speed: 0.75, phase: rand() * 6 });
                addHazard(520, base - 286, 340, 18, { rangeX: 0, speed: 0 });
            }

            addHazard(0, top + 10, worldW, 12, { speed: 0 });
        }

        addPlatform(300, goal.y + 54, 380, 22, palette.goal);
    }

    function makeParticles() {
        for (let i = 0; i < 88; i += 1) {
            particles.push({
                x: rand() * worldW,
                y: rand() * totalH,
                r: 1 + rand() * 2.4,
                speed: 0.08 + rand() * 0.22,
                alpha: 0.18 + rand() * 0.45,
            });
        }
    }

    buildTower();
    makeParticles();

    function resetPlayer(toCheckpoint) {
        const spawn = toCheckpoint ? checkpoint : { x: 82, y: totalH - floorH - 48 };
        player.x = spawn.x;
        player.y = spawn.y;
        player.vx = 0;
        player.vy = 0;
        player.onGround = false;
        player.jumpsLeft = 2;
        player.jumpBuffer = 0;
        player.coyote = 0;
        if (!toCheckpoint) {
            checkpoint = { x: 82, y: totalH - floorH - 48 };
        }
    }

    function startRun() {
        if (!started || won || expired) {
            const wasFinished = won || expired;
            started = true;
            won = false;
            expired = false;
            startTime = performance.now();
            finishTime = 0;
            if (wasFinished) {
                deaths = 0;
                bestHeight = 0;
            }
            resetPlayer(false);
            messageTimer = 80;
        }
        canvas.focus();
    }

    function respawn() {
        deaths += 1;
        resetPlayer(Boolean(CONFIG.checkpoints));
        messageTimer = 90;
    }

    function queueJump() {
        player.jumpBuffer = 10;
    }

    function performJump() {
        player.vy = -Number(CONFIG.jump || 16);
        player.onGround = false;
        player.coyote = 0;
        player.jumpBuffer = 0;
        if (player.jumpsLeft > 0) {
            player.jumpsLeft -= 1;
        }
    }

    function resetRun() {
        deaths += 1;
        started = true;
        won = false;
        expired = false;
        startTime = performance.now();
        finishTime = 0;
        resetPlayer(false);
        canvas.focus();
    }

    function setKey(code, value) {
        keys[code] = value;
    }

    window.addEventListener("keydown", (event) => {
        if (["ArrowLeft", "ArrowRight", "ArrowUp", "Space", "KeyA", "KeyD", "KeyW", "KeyR"].includes(event.code)) {
            event.preventDefault();
        }
        setKey(event.code, true);
        if (event.code === "Space" || event.code === "ArrowUp" || event.code === "KeyW") {
            if (!started || won || expired) startRun();
            queueJump();
        }
        if (event.code === "KeyR") {
            resetRun();
        }
    }, { passive: false });

    window.addEventListener("keyup", (event) => {
        setKey(event.code, false);
    });

    function bindButton(button, down, up) {
        button.addEventListener("pointerdown", (event) => {
            event.preventDefault();
            down();
            canvas.focus();
        });
        button.addEventListener("pointerup", up);
        button.addEventListener("pointerleave", up);
        button.addEventListener("pointercancel", up);
    }

    bindButton(document.getElementById("leftButton"), () => {
        setKey("ArrowLeft", true);
        startRun();
    }, () => setKey("ArrowLeft", false));
    bindButton(document.getElementById("rightButton"), () => {
        setKey("ArrowRight", true);
        startRun();
    }, () => setKey("ArrowRight", false));
    bindButton(document.getElementById("jumpButton"), () => {
        startRun();
        queueJump();
    }, () => {});

    playButton.addEventListener("click", startRun);
    resetButton.addEventListener("click", resetRun);
    canvas.addEventListener("pointerdown", () => {
        if (!started || won || expired) startRun();
        canvas.focus();
    });

    function ensureAudio() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === "suspended") {
            audioContext.resume();
        }
    }

    function beep(time, frequency, duration, type, gainValue) {
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(frequency, time);
        gain.gain.setValueAtTime(gainValue, time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + duration);
        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.start(time);
        osc.stop(time + duration);
    }

    function noiseHit(time, duration, gainValue) {
        const bufferSize = Math.max(1, Math.floor(audioContext.sampleRate * duration));
        const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i += 1) {
            data[i] = Math.random() * 2 - 1;
        }
        const source = audioContext.createBufferSource();
        const gain = audioContext.createGain();
        const filter = audioContext.createBiquadFilter();
        filter.type = "highpass";
        filter.frequency.value = 1700;
        gain.gain.setValueAtTime(gainValue, time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + duration);
        source.buffer = buffer;
        source.connect(filter);
        filter.connect(gain);
        gain.connect(audioContext.destination);
        source.start(time);
        source.stop(time + duration);
    }

    function playMusicStep() {
        if (!audioContext || musicTrack === 0) return;
        const time = audioContext.currentTime + 0.02;
        const step = musicStep % 16;
        const tracks = [
            null,
            { bass: [55, 55, 65, 55, 73, 65, 55, 49], hat: [2, 6, 10, 14], kick: [0, 4, 8, 12], snare: [4, 12] },
            { bass: [49, 49, 58, 65, 49, 44, 49, 58], hat: [1, 3, 6, 9, 11, 14], kick: [0, 3, 8, 10], snare: [4, 12] },
            { bass: [65, 62, 55, 49, 55, 49, 44, 49], hat: [2, 4, 6, 10, 12, 14], kick: [0, 6, 8, 13], snare: [4, 12] },
        ];
        const track = tracks[musicTrack];

        if (track.kick.includes(step)) {
            beep(time, 94, 0.09, "sine", 0.4);
            beep(time + 0.01, 46, 0.14, "sine", 0.34);
        }
        if (track.snare.includes(step)) {
            noiseHit(time, 0.08, 0.18);
        }
        if (track.hat.includes(step)) {
            noiseHit(time, 0.035, 0.08);
        }
        if (step % 2 === 0) {
            const note = track.bass[Math.floor(step / 2) % track.bass.length];
            beep(time, note, 0.16, "sawtooth", 0.16);
            beep(time, note / 2, 0.18, "triangle", 0.12);
        }

        musicStep += 1;
    }

    function updateMusicButton() {
        const labels = ["Music Off", "Phonk 1", "Phonk 2", "Phonk 3"];
        musicButton.textContent = labels[musicTrack];
    }

    musicButton.addEventListener("click", () => {
        ensureAudio();
        musicTrack = (musicTrack + 1) % 4;
        musicStep = 0;
        if (musicTrack === 0) {
            if (musicTimer) {
                clearInterval(musicTimer);
                musicTimer = null;
            }
        } else if (!musicTimer) {
            playMusicStep();
            musicTimer = setInterval(playMusicStep, 125);
        }
        updateMusicButton();
    });

    function updateHazards(now) {
        const speed = Number(CONFIG.hazard_speed || 1);
        hazards.forEach((hazard) => {
            hazard.x = hazard.baseX + Math.sin(now * hazard.speed * 0.001 * speed + hazard.phase) * hazard.rangeX;
            hazard.y = hazard.baseY + Math.sin(now * hazard.speed * 0.001 * speed + hazard.phase) * hazard.rangeY;
        });
    }

    function updatePlayer(dt) {
        if (player.jumpBuffer > 0) player.jumpBuffer -= 1;
        if (player.coyote > 0) player.coyote -= 1;

        const left = keys.ArrowLeft || keys.KeyA;
        const right = keys.ArrowRight || keys.KeyD;
        const direction = (right ? 1 : 0) - (left ? 1 : 0);
        const maxSpeed = 7.4 * Number(CONFIG.speed || 1);

        if (direction !== 0) {
            player.face = direction;
            player.vx += direction * (player.onGround ? 1.45 : 1.02);
        } else {
            player.vx *= player.onGround ? 0.72 : 0.9;
        }

        player.vx = clamp(player.vx, -maxSpeed, maxSpeed);
        player.vy += Number(CONFIG.gravity || 0.66);
        player.vy = clamp(player.vy, -22, 20);

        if (player.jumpBuffer > 0 && (player.onGround || player.coyote > 0 || player.jumpsLeft > 0)) {
            performJump();
        }

        const previous = { x: player.x, y: player.y, w: player.w, h: player.h };
        player.x += player.vx * dt;
        player.x = clamp(player.x, 8, worldW - player.w - 8);
        player.y += player.vy * dt;
        player.onGround = false;

        for (const platform of platforms) {
            const landed = previous.y + previous.h <= platform.y + 6 &&
                player.y + player.h >= platform.y &&
                player.vy >= 0 &&
                player.x + player.w > platform.x &&
                player.x < platform.x + platform.w;
            if (landed) {
                player.y = platform.y - player.h;
                player.vy = 0;
                player.onGround = true;
                player.jumpsLeft = 2;
                player.coyote = 10;
            }
        }

        if (!player.onGround && previous.y + previous.h <= player.y + player.h) {
            player.coyote = Math.max(0, player.coyote);
        }

        if (player.y > totalH + 120) {
            respawn();
        }

        const climb = Math.max(0, totalH - floorH - player.y);
        bestHeight = Math.max(bestHeight, Math.round(climb / 10));

        if (CONFIG.checkpoints) {
            const currentStage = Math.floor(climb / sectionH);
            const checkpointStage = Math.floor(Math.max(0, totalH - floorH - checkpoint.y) / sectionH);
            if (currentStage > checkpointStage && player.onGround) {
                checkpoint = { x: player.x, y: player.y };
                messageTimer = 80;
            }
        }
    }

    function updateCollisions() {
        const body = {
            x: player.x + 7,
            y: player.y + 6,
            w: player.w - 14,
            h: player.h - 12,
        };
        for (const hazard of hazards) {
            if (rectsOverlap(body, hazard)) {
                respawn();
                return;
            }
        }
        if (rectsOverlap(player, goal)) {
            won = true;
            started = false;
            finishTime = performance.now();
            for (let i = 0; i < 80; i += 1) {
                confetti.push({
                    x: goal.x + goal.w / 2,
                    y: goal.y,
                    vx: -7 + Math.random() * 14,
                    vy: -9 + Math.random() * 6,
                    life: 70 + Math.random() * 60,
                    colour: ["#facc15", "#22d3ee", "#fb7185", "#a78bfa", "#34d399"][i % 5],
                });
            }
        }
    }

    function remainingSeconds(now) {
        const total = Number(CONFIG.time_limit || 240);
        if (!started) return total;
        return Math.max(0, Math.ceil((total * 1000 - (now - startTime)) / 1000));
    }

    function updateTimers(now) {
        if (messageTimer > 0) messageTimer -= 1;
        if (started && remainingSeconds(now) <= 0) {
            expired = true;
            started = false;
            respawn();
        }
    }

    function drawBackground(now) {
        const gradient = ctx.createLinearGradient(0, 0, 0, H);
        gradient.addColorStop(0, palette.sky_a);
        gradient.addColorStop(0.55, palette.sky_b);
        gradient.addColorStop(1, palette.sky_c);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, W, H);

        ctx.save();
        ctx.translate(0, -cameraY);
        for (const particle of particles) {
            particle.y += particle.speed;
            if (particle.y > totalH) particle.y = 0;
            ctx.globalAlpha = particle.alpha;
            ctx.fillStyle = palette.accent;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;

        for (let s = 0; s < sections; s += 1) {
            const y = totalH - floorH - (s + 1) * sectionH;
            ctx.fillStyle = s % 2 === 0 ? "rgba(255,255,255,0.035)" : "rgba(255,255,255,0.065)";
            ctx.fillRect(0, y, worldW, sectionH);
        }
        ctx.restore();

        ctx.fillStyle = "rgba(255,255,255,0.08)";
        for (let i = 0; i < 7; i += 1) {
            const x = (i * 170 + (now * 0.018)) % (W + 200) - 100;
            roundedRect(x, 90 + i * 72, 120, 10, 999);
        }
    }

    function drawPlatforms() {
        ctx.save();
        ctx.translate(0, -cameraY);
        for (const platform of platforms) {
            ctx.shadowColor = "rgba(0, 0, 0, 0.22)";
            ctx.shadowBlur = 10;
            ctx.fillStyle = palette.platform;
            roundedRect(platform.x, platform.y, platform.w, platform.h, 8);
            ctx.shadowBlur = 0;
            ctx.fillStyle = platform.edge || palette.edge;
            ctx.fillRect(platform.x, platform.y, platform.w, 5);
        }
        ctx.restore();
    }

    function drawHazards(now) {
        ctx.save();
        ctx.translate(0, -cameraY);
        for (const hazard of hazards) {
            const pulse = 0.55 + Math.sin(now * 0.01 + hazard.phase) * 0.18;
            ctx.fillStyle = "rgba(239, 68, 68, " + pulse + ")";
            roundedRect(hazard.x - 7, hazard.y - 7, hazard.w + 14, hazard.h + 14, 10);
            ctx.fillStyle = "#ef4444";
            roundedRect(hazard.x, hazard.y, hazard.w, hazard.h, 7);
            ctx.fillStyle = "rgba(255,255,255,0.36)";
            ctx.fillRect(hazard.x + 8, hazard.y + 4, Math.max(8, hazard.w - 16), 3);
        }
        ctx.restore();
    }

    function drawGoal(now) {
        ctx.save();
        ctx.translate(0, -cameraY);
        const pulse = 0.28 + Math.sin(now * 0.006) * 0.08;
        ctx.fillStyle = "rgba(167, 139, 250, " + pulse + ")";
        roundedRect(goal.x - 24, goal.y - 24, goal.w + 48, goal.h + 58, 14);
        ctx.fillStyle = palette.goal;
        roundedRect(goal.x, goal.y, goal.w, goal.h, 12);
        ctx.fillStyle = "#111827";
        ctx.font = "900 18px Arial";
        ctx.textAlign = "center";
        ctx.fillText("FINISH", goal.x + goal.w / 2, goal.y + 21);
        ctx.restore();
    }

    function drawPlayer() {
        ctx.save();
        ctx.translate(0, -cameraY);
        ctx.shadowColor = palette.player;
        ctx.shadowBlur = 20;
        ctx.fillStyle = palette.player;
        roundedRect(player.x, player.y, player.w, player.h, 9);
        ctx.shadowBlur = 0;
        ctx.fillStyle = palette.player_shadow;
        roundedRect(player.x + 7, player.y + 28, player.w - 14, 8, 5);
        ctx.fillStyle = "#111827";
        const eyeX = player.face > 0 ? player.x + 22 : player.x + 9;
        ctx.fillRect(eyeX, player.y + 11, 5, 5);
        ctx.restore();
    }

    function drawConfetti() {
        ctx.save();
        ctx.translate(0, -cameraY);
        for (const bit of confetti) {
            bit.x += bit.vx;
            bit.y += bit.vy;
            bit.vy += 0.22;
            bit.life -= 1;
            ctx.globalAlpha = clamp(bit.life / 80, 0, 1);
            ctx.fillStyle = bit.colour;
            ctx.fillRect(bit.x, bit.y, 9, 9);
        }
        ctx.globalAlpha = 1;
        ctx.restore();
        for (let i = confetti.length - 1; i >= 0; i -= 1) {
            if (confetti[i].life <= 0) confetti.splice(i, 1);
        }
    }

    function drawHud(now) {
        const remaining = remainingSeconds(now);
        const stage = Math.min(sections, Math.max(1, Math.floor(Math.max(0, totalH - floorH - player.y) / sectionH) + 1));
        const chips = [
            "Stage " + stage + "/" + sections,
            "Time " + remaining,
            "Falls " + deaths,
            "Height " + bestHeight,
        ];
        ctx.font = "900 15px Arial";
        ctx.textAlign = "left";
        let x = 18;
        for (const chip of chips) {
            const width = ctx.measureText(chip).width + 26;
            ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
            roundedRect(x, 18, width, 34, 10);
            ctx.fillStyle = "#ffffff";
            ctx.fillText(chip, x + 13, 40);
            x += width + 10;
        }

        const progress = clamp((totalH - floorH - player.y) / (totalH - floorH - goal.y), 0, 1);
        ctx.fillStyle = "rgba(255,255,255,0.16)";
        roundedRect(W - 32, 78, 12, H - 150, 999);
        ctx.fillStyle = palette.goal;
        roundedRect(W - 32, 78 + (H - 150) * (1 - progress), 12, (H - 150) * progress, 999);

        if (messageTimer > 0 && CONFIG.checkpoints) {
            ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
            roundedRect(W / 2 - 130, 68, 260, 38, 10);
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "center";
            ctx.font = "900 15px Arial";
            ctx.fillText("Checkpoint saved", W / 2, 93);
        }
    }

    function drawOverlay() {
        if (started && !won && !expired) return;
        ctx.fillStyle = "rgba(15, 23, 42, 0.68)";
        ctx.fillRect(0, 0, W, H);
        ctx.textAlign = "center";
        ctx.fillStyle = "#ffffff";
        ctx.font = "900 46px Arial";
        let title = "Red Rush Tower";
        if (won) title = "Tower cleared";
        if (expired) title = "Time reset";
        ctx.fillText(title, W / 2, H / 2 - 58);

        ctx.font = "800 18px Arial";
        ctx.fillStyle = "#e2e8f0";
        const detail = won ? "Clear time " + Math.round((finishTime - startTime) / 1000) + "s" : "Tap Play when ready";
        ctx.fillText(detail, W / 2, H / 2 - 20);

        ctx.fillStyle = palette.goal;
        roundedRect(W / 2 - 112, H / 2 + 18, 224, 54, 14);
        ctx.fillStyle = "#111827";
        ctx.font = "900 18px Arial";
        ctx.fillText(won ? "PLAY AGAIN" : "PLAY", W / 2, H / 2 + 52);
    }

    canvas.addEventListener("click", (event) => {
        const rect = canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) * (W / rect.width);
        const y = (event.clientY - rect.top) * (H / rect.height);
        if (!started || won || expired) {
            if (x > W / 2 - 130 && x < W / 2 + 130 && y > H / 2 + 4 && y < H / 2 + 90) {
                startRun();
            }
        }
    });

    function loop(now) {
        const dt = Math.min(1.7, (now - lastTime) / 16.67);
        lastTime = now;

        updateHazards(now);
        if (started && !won && !expired) {
            updatePlayer(dt);
            updateCollisions();
            updateTimers(now);
        }

        const targetCamera = clamp(player.y - 405, 0, totalH - H);
        cameraY += (targetCamera - cameraY) * 0.09;

        drawBackground(now);
        drawGoal(now);
        drawPlatforms();
        drawHazards(now);
        drawPlayer();
        drawConfetti();
        drawHud(now);
        drawOverlay();
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
        page_title="Red Rush Tower",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(90deg, rgba(37, 99, 235, 0.09), rgba(15, 118, 110, 0.09), rgba(190, 18, 60, 0.09)),
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
            background: linear-gradient(135deg, #be123c, #2563eb);
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
        st.header("Game setup")
        difficulty_name = st.selectbox("Difficulty", list(DIFFICULTIES), index=0)
        height_name = st.selectbox("Tower height", list(HEIGHTS), index=1)
        palette_name = st.selectbox("Style", list(PALETTES), index=0)
        checkpoints = st.toggle("Checkpoints", value=True)
        if st.button("Build new tower", type="primary", use_container_width=True):
            st.session_state.obby_seed = random.randint(10_000, 999_999)

    config = {
        **DIFFICULTIES[difficulty_name],
        "sections": HEIGHTS[height_name],
        "palette": PALETTES[palette_name],
        "checkpoints": checkpoints,
        "seed": st.session_state.obby_seed,
    }

    st.markdown(
        f"""
        <div class="game-topbar">
            <h1>Red Rush Tower</h1>
            <span>Ages 12-15 | {difficulty_name} | {height_name}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components.html(build_game_html(config), height=760, scrolling=False)


if __name__ == "__main__":
    main()
