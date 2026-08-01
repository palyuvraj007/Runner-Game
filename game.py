import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Pursuit Ultra", layout="centered", page_icon="🎮")

st.markdown("""
    <style>
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AI Pursuit: Ultra Edition")
st.caption("🎮 **Controls:** Use Arrow Keys / WASD on PC, or Touch D-Pad on Mobile!")

game_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * { 
        box-sizing: border-box; 
        touch-action: none; 
        user-select: none; 
        -webkit-user-select: none;
        -webkit-touch-callout: none;
    }
    body {
        margin: 0;
        padding: 0;
        background-color: #0e1117;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
        overflow: hidden;
    }
    #ui-panel {
        display: flex;
        justify-content: space-between;
        width: 100%;
        max-width: 500px;
        padding: 8px 12px;
        background: #161b22;
        border-radius: 8px 8px 0 0;
        border: 1px solid #30363d;
        border-bottom: none;
        font-size: 16px;
        font-weight: bold;
    }
    canvas {
        border: 1px solid #30363d;
        border-radius: 0 0 8px 8px;
        background-color: #0d1117;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.6);
        outline: none;
        max-width: 100%;
        touch-action: none;
        cursor: pointer;
    }

    #dpad {
        display: none;
        grid-template-columns: repeat(3, 55px);
        grid-template-rows: repeat(2, 55px);
        gap: 6px;
        margin-top: 12px;
    }

    @media (pointer: coarse) {
        #dpad {
            display: grid;
        }
    }

    .dbtn {
        background: #21262d;
        border: 2px solid #30363d;
        color: #58a6ff;
        font-size: 22px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .dbtn:active {
        background: #1f6feb;
        color: white;
        transform: scale(0.95);
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

<canvas id="canvas" width="500" height="360" tabindex="0"></canvas>

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

    canvas.focus();

    // Game States: "START", "PLAYING", "GAMEOVER"
    let gameState = "START";

    let score = 0;
    let particles = [];
    let aiTrail = [];

    let player = { x: 250, y: 180, radius: 10, speed: 5.5 };
    let ai = { x: 40, y: 40, radius: 12, speed: 2.2, baseSpeed: 2.2 };
    let coin = { x: 380, y: 120, radius: 7, pulse: 0 };

    const keys = {};

    // Unified Mobile & PC Tap/Click Handler
    function handleCanvasInteraction(e) {
        if (gameState === "PLAYING") return;

        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        let clientX = e.clientX;
        let clientY = e.clientY;

        if (e.changedTouches && e.changedTouches.length > 0) {
            clientX = e.changedTouches[0].clientX;
            clientY = e.changedTouches[0].clientY;
        }

        const mouseX = (clientX - rect.left) * scaleX;
        const mouseY = (clientY - rect.top) * scaleY;

        const btnX = canvas.width / 2 - 75;
        const btnY = canvas.height / 2 + 20;

        // Check button hit box
        if (mouseX >= btnX && mouseX <= btnX + 150 && mouseY >= btnY && mouseY <= btnY + 50) {
            resetGame();
        }
    }

    // Canvas Listeners
    canvas.addEventListener("click", handleCanvasInteraction);
    canvas.addEventListener("touchstart", function(e) {
        e.preventDefault();
        canvas.focus();
        handleCanvasInteraction(e);
    }, { passive: false });

    function resetGame() {
        score = 0;
        gameState = "PLAYING";
        player.x = 250; player.y = 180;
        ai.x = 40; ai.y = 40;
        ai.speed = ai.baseSpeed;
        coin.x = Math.random() * (canvas.width - 60) + 30;
        coin.y = Math.random() * (canvas.height - 60) + 30;
        particles = [];
        aiTrail = [];
        document.getElementById("score").innerText = "0";
        document.getElementById("speed").innerText = "1.0x";
    }

    // Keyboard Listeners (PC)
    document.addEventListener("keydown", function(e) {
        if(["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].indexOf(e.code) > -1) {
            e.preventDefault();
        }
        keys[e.code] = true;
        keys[e.key.toLowerCase()] = true;
    });

    document.addEventListener("keyup", function(e) {
        keys[e.code] = false;
        keys[e.key.toLowerCase()] = false;
    });

    // Touch D-Pad Controls (Mobile)
    function bindBtn(id, key) {
        const btn = document.getElementById(id);
        if (!btn) return;

        const start = (e) => { e.preventDefault(); keys[key] = true; };
        const end = (e) => { e.preventDefault(); keys[key] = false; };
        
        btn.addEventListener("touchstart", start, { passive: false });
        btn.addEventListener("touchend", end, { passive: false });
        btn.addEventListener("mousedown", start);
        btn.addEventListener("mouseup", end);
    }

    bindBtn("up", "ArrowUp");
    bindBtn("down", "ArrowDown");
    bindBtn("left", "ArrowLeft");
    bindBtn("right", "ArrowRight");

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

    function update() {
        if (gameState !== "PLAYING") return;

        let moveX = 0;
        let moveY = 0;

        if (keys["ArrowLeft"] || keys["KeyA"] || keys["a"]) moveX -= 1;
        if (keys["ArrowRight"] || keys["KeyD"] || keys["d"]) moveX += 1;
        if (keys["ArrowUp"] || keys["KeyW"] || keys["w"]) moveY -= 1;
        if (keys["ArrowDown"] || keys["KeyS"] || keys["s"]) moveY += 1;

        if (moveX !== 0 && moveY !== 0) {
            moveX *= 0.7071;
            moveY *= 0.7071;
        }

        player.x += moveX * player.speed;
        player.y += moveY * player.speed;

        player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x));
        player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y));

        let dx = player.x - ai.x;
        let dy = player.y - ai.y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > 0) {
            ai.x += (dx / dist) * ai.speed;
            ai.y += (dy / dist) * ai.speed;
        }

        let tailLength = Math.floor(6 + (ai.speed - ai.baseSpeed) * 8);
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
            
            ai.speed += 0.25;
            document.getElementById("speed").innerText = (ai.speed / ai.baseSpeed).toFixed(1) + "x";
        }

        particles.forEach((p, index) => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 0.05;
            if (p.life <= 0) particles.splice(index, 1);
        });

        if (dist < player.radius + ai.radius) {
            gameState = "GAMEOVER";
        }
    }

    function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (gameState === "START") {
            ctx.fillStyle = "#58a6ff";
            ctx.font = "bold 30px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("AI PURSUIT", canvas.width / 2, canvas.height / 2 - 30);

            ctx.fillStyle = "#8b949e";
            ctx.font = "14px sans-serif";
            ctx.fillText("Outrun the AI & Collect the Orbs!", canvas.width / 2, canvas.height / 2);

            const btnX = canvas.width / 2 - 75;
            const btnY = canvas.height / 2 + 20;
            
            ctx.fillStyle = "#1f6feb";
            ctx.beginPath();
            ctx.roundRect(btnX, btnY, 150, 45, 10);
            ctx.fill();

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 18px sans-serif";
            ctx.fillText("🚀 Start Game", canvas.width / 2, btnY + 28);
            requestAnimationFrame(render);
            return;
        }

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
            ctx.fillStyle = `rgba(248, 81, 73, ${ratio * 0.6})`;
            ctx.fill();
        });

        ctx.beginPath();
        ctx.arc(ai.x, ai.y, ai.radius, 0, Math.PI * 2);
        ctx.fillStyle = "#f85149";
        ctx.shadowBlur = 12 + (ai.speed * 2);
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

        update();

        if (gameState === "GAMEOVER") {
            ctx.fillStyle = "rgba(13, 17, 23, 0.88)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#f85149";
            ctx.font = "bold 32px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 25);

            ctx.fillStyle = "#8b949e";
            ctx.font = "16px sans-serif";
            ctx.fillText("Final Score: " + score, canvas.width / 2, canvas.height / 2 + 5);

            const btnX = canvas.width / 2 - 75;
            const btnY = canvas.height / 2 + 25;
            
            ctx.fillStyle = "#238636";
            ctx.beginPath();
            ctx.roundRect(btnX, btnY, 150, 42, 8);
            ctx.fill();

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 16px sans-serif";
            ctx.fillText("🔄 Play Again", canvas.width / 2, btnY + 26);
            requestAnimationFrame(render);
            return;
        }

        requestAnimationFrame(render);
    }

    render();
};
</script>
</body>
</html>
"""

components.html(game_code, height=560)
