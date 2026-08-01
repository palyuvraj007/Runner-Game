import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="THE RUNNER", layout="centered", page_icon="🎮")

st.markdown("""
    <style>
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("I WILL KILL YOU!")
st.caption("🎮 **Controls:** WASD / Arrow Keys on PC • Touch D-Pad on Mobile!")

game_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * { 
        box-sizing: border-box; 
        user-select: none; 
        -webkit-user-select: none;
        -webkit-touch-callout: none;
    }
    body {
        margin: 0;
        padding: 0 0 20px 0;
        background-color: #0e1117;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
    }
    #ui-panel {
        display: flex;
        justify-content: space-between;
        width: 100%;
        max-width: 500px;
        padding: 10px 14px;
        background: #161b22;
        border-radius: 8px 8px 0 0;
        border: 1px solid #30363d;
        border-bottom: none;
        font-size: 16px;
        font-weight: bold;
    }
    #game-container {
        position: relative;
        width: 100%;
        max-width: 500px;
    }
    canvas {
        display: block;
        width: 100%;
        height: auto;
        aspect-ratio: 500 / 360;
        border: 1px solid #30363d;
        border-radius: 0 0 8px 8px;
        background-color: #0d1117;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.6);
        outline: none;
        touch-action: none;
    }

    #overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(13, 17, 23, 0.94);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 0 0 8px 8px;
        z-index: 10;
    }

    .action-btn {
        background: #1f6feb;
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        cursor: pointer;
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.4);
        touch-action: manipulation;
    }
    .action-btn:active {
        transform: scale(0.95);
        background: #388bfd;
    }

    #dpad {
        display: grid;
        grid-template-columns: repeat(3, 65px);
        grid-template-rows: repeat(2, 65px);
        gap: 12px;
        margin-top: 20px;
        margin-bottom: 20px;
        padding: 10px;
        touch-action: none;
    }

    .dbtn {
        background: #21262d;
        border: 2px solid #30363d;
        color: #58a6ff;
        font-size: 26px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        touch-action: none;
    }
    .dbtn:active {
        background: #1f6feb;
        color: white;
        transform: scale(0.92);
    }
    #up { grid-column: 2; grid-row: 1; }
    #left { grid-column: 1; grid-row: 2; }
    #down { grid-column: 2; grid-row: 2; }
    #right { grid-column: 3; grid-row: 2; }
</style>
</head>
<body>

<div id="ui-panel">
    <div>🪙 Score: <span id="score" style="color:#e3b341;">0</span></div>
    <div>⚡ AI Speed: <span id="speed" style="color:#f85149;">1.0x</span></div>
</div>

<div id="game-container">
    <canvas id="canvas" width="500" height="360" tabindex="0"></canvas>
    
    <div id="overlay">
        <h2 id="overlay-title" style="margin:0; color:#58a6ff; font-size:28px;">AI PURSUIT</h2>
        <p id="overlay-desc" style="margin:8px 0 0 0; color:#8b949e; font-size:14px;">Outrun the AI & Collect the Orbs!</p>
        <button id="start-btn" class="action-btn">🚀 Start Game</button>
    </div>
</div>

<div id="dpad">
    <div class="dbtn" id="up">▲</div>
    <div class="dbtn" id="left">◀</div>
    <div class="dbtn" id="down">▼</div>
    <div class="dbtn" id="right">▶</div>
</div>

<script>
window.onload = function() {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const overlay = document.getElementById("overlay");
    const overlayTitle = document.getElementById("overlay-title");
    const overlayDesc = document.getElementById("overlay-desc");
    const startBtn = document.getElementById("start-btn");

    let gameState = "START";

    let score = 0;
    let particles = [];
    let aiTrail = [];
    let lastTime = 0;

    // Base multiplier for normalized delta-time speed
    const SPEED_MULT = 60;

    // Red AI starts at 1.0, Blue Player starts at 2.0
    let player = { x: 250, y: 180, radius: 10, speedVal: 2.0, baseSpeedVal: 2.0 };
    let ai = { x: 40, y: 40, radius: 12, speedVal: 1.0, baseSpeedVal: 1.0 };
    let coin = { x: 380, y: 120, radius: 7, pulse: 0 };

    const keys = { up: false, down: false, left: false, right: false };

    function startGame() {
        score = 0;
        gameState = "PLAYING";
        overlay.style.display = "none";
        
        player.x = 250; player.y = 180;
        player.speedVal = player.baseSpeedVal;
        
        ai.x = 40; ai.y = 40;
        ai.speedVal = ai.baseSpeedVal;
        
        coin.x = Math.random() * (canvas.width - 60) + 30;
        coin.y = Math.random() * (canvas.height - 60) + 30;
        particles = [];
        aiTrail = [];

        keys.up = false; keys.down = false;
        keys.left = false; keys.right = false;

        document.getElementById("score").innerText = "0";
        document.getElementById("speed").innerText = "1.0x";
        
        lastTime = performance.now();
        window.focus();
        canvas.focus();
    }

    startBtn.addEventListener("click", startGame);
    startBtn.addEventListener("pointerdown", function(e) {
        e.preventDefault();
        startGame();
    });

    function triggerGameOver() {
        gameState = "KILLED💀";
        overlayTitle.innerText = "KILLED💀";
        overlayTitle.style.color = "#f85149";
        overlayDesc.innerText = "Final Score: " + score;
        startBtn.innerText = "🔄 Play Again";
        overlay.style.display = "flex";
    }

    function handleKey(e, isPressed) {
        const k = e.key ? e.key.toLowerCase() : "";
        const code = e.code || "";

        if (k === "w" || k === "arrowup" || code === "KeyW" || code === "ArrowUp") {
            keys.up = isPressed;
            if (e.cancelable) e.preventDefault();
        }
        if (k === "s" || k === "arrowdown" || code === "KeyS" || code === "ArrowDown") {
            keys.down = isPressed;
            if (e.cancelable) e.preventDefault();
        }
        if (k === "a" || k === "arrowleft" || code === "KeyA" || code === "ArrowLeft") {
            keys.left = isPressed;
            if (e.cancelable) e.preventDefault();
        }
        if (k === "d" || k === "arrowright" || code === "KeyD" || code === "ArrowRight") {
            keys.right = isPressed;
            if (e.cancelable) e.preventDefault();
        }
    }

    window.addEventListener("keydown", (e) => handleKey(e, true));
    window.addEventListener("keyup", (e) => handleKey(e, false));

    document.body.addEventListener("click", () => { canvas.focus(); });

    function bindBtn(id, dir) {
        const btn = document.getElementById(id);
        if (!btn) return;

        const press = (e) => { e.preventDefault(); keys[dir] = true; };
        const release = (e) => { e.preventDefault(); keys[dir] = false; };

        btn.addEventListener("pointerdown", press);
        btn.addEventListener("pointerup", release);
        btn.addEventListener("pointercancel", release);
        btn.addEventListener("pointerleave", release);
        
        btn.addEventListener("touchstart", press, { passive: false });
        btn.addEventListener("touchend", release, { passive: false });
    }

    bindBtn("up", "up");
    bindBtn("down", "down");
    bindBtn("left", "left");
    bindBtn("right", "right");

    function createBurst(x, y) {
        for (let i = 0; i < 12; i++) {
            particles.push({
                x: x, y: y,
                vx: (Math.random() - 0.5) * 8,
                vy: (Math.random() - 0.5) * 8,
                life: 1.0
            });
        }
    }

    function update(dt) {
        if (gameState !== "PLAYING") return;

        let moveX = 0;
        let moveY = 0;

        if (keys.left) moveX -= 1;
        if (keys.right) moveX += 1;
        if (keys.up) moveY -= 1;
        if (keys.down) moveY += 1;

        if (moveX !== 0 && moveY !== 0) {
            moveX *= 0.7071;
            moveY *= 0.7071;
        }

        player.x += moveX * (player.speedVal * SPEED_MULT) * dt;
        player.y += moveY * (player.speedVal * SPEED_MULT) * dt;

        player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x));
        player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y));

        let dx = player.x - ai.x;
        let dy = player.y - ai.y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > 0) {
            ai.x += (dx / dist) * (ai.speedVal * SPEED_MULT) * dt;
            ai.y += (dy / dist) * (ai.speedVal * SPEED_MULT) * dt;
        }

        let tailLength = Math.floor(4 + (score / 10) * 3);
        aiTrail.push({ x: ai.x, y: ai.y });
        while (aiTrail.length > tailLength) {
            aiTrail.shift();
        }

        let cDx = player.x - coin.x;
        let cDy = player.y - coin.y;
        if (Math.sqrt(cDx * cDx + cDy * cDy) < player.radius + coin.radius) {
            score += 10;
            createBurst(coin.x, coin.y);
            document.getElementById("score").innerText = score;
            
            coin.x = Math.random() * (canvas.width - 60) + 30;
            coin.y = Math.random() * (canvas.height - 60) + 30;
            
            // Speed increases exactly by +0.1 for both
            ai.speedVal += 0.1;
            player.speedVal += 0.1;

            document.getElementById("speed").innerText = (ai.speedVal / ai.baseSpeedVal).toFixed(2) + "x";
        }

        particles.forEach((p, index) => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 0.05;
            if (p.life <= 0) particles.splice(index, 1);
        });

        if (dist < player.radius + ai.radius) {
            triggerGameOver();
        }
    }

    function render(timestamp) {
        if (!lastTime) lastTime = timestamp;
        let dt = (timestamp - lastTime) / 1000;
        if (dt > 0.1) dt = 0.1; 
        lastTime = timestamp;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (gameState === "PLAYING") {
            particles.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(227, 179, 65, ${p.life})`;
                ctx.fill();
            });

            coin.pulse += 0.08;
            let currentRadius = coin.radius + Math.sin(coin.pulse) * 1.5;
            ctx.beginPath();
            ctx.arc(coin.x, coin.y, currentRadius, 0, Math.PI * 2);
            ctx.fillStyle = "#e3b341";
            ctx.shadowBlur = 10;
            ctx.shadowColor = "#e3b341";
            ctx.fill();
            ctx.shadowBlur = 0;

            aiTrail.forEach((t, idx) => {
                let ratio = idx / aiTrail.length;
                ctx.beginPath();
                ctx.arc(t.x, t.y, ai.radius * ratio, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(248, 81, 73, ${ratio * 0.65})`;
                ctx.fill();
            });

            ctx.beginPath();
            ctx.arc(ai.x, ai.y, ai.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#f85149";
            ctx.shadowBlur = 10 + ((ai.speedVal / ai.baseSpeedVal) * 3);
            ctx.shadowColor = "#f85149";
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#58a6ff";
            ctx.shadowBlur = 10;
            ctx.shadowColor = "#58a6ff";
            ctx.fill();
            ctx.shadowBlur = 0;

            update(dt);
        }

        requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
};
</script>
</body>
</html>
"""

components.html(game_code, height=670, scrolling=True)
