document.addEventListener("DOMContentLoaded", function() {
    // 获取 DOM 元素
    const statusDisplay = document.getElementById("posture-indicator");
    const angleValue = document.getElementById("angle-value");
    const angleBar = document.getElementById("angle-bar");
    const logList = document.querySelector(".log-list");
    const cpuSpan = document.querySelector(".random-change");
    
    // 状态配置
    const CONFIG = {
        "Normal": { color: "#00ff41", text: "NORMAL // 正常", alert: false },
        "Warning: Slouching!": { color: "#ff3333", text: "WARNING // 驼背", alert: true }
    };

    let lastStatus = "";

    function updateSystem() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                // 1. 获取当前状态配置
                const state = CONFIG[data.status] || CONFIG["Normal"];
                
                // 2. 更新状态卡片
                statusDisplay.innerText = state.text;
                statusDisplay.style.color = state.color;
                statusDisplay.style.borderColor = state.alert ? state.color : "transparent";
                statusDisplay.style.textShadow = `0 0 10px ${state.color}`;

                // 3. 更新角度进度条
                angleValue.innerText = data.angle + "°";
                
                // 简单的归一化：假设 100度到 180度是有效区间
                let percentage = Math.max(0, Math.min(100, (data.angle - 100) / 0.8));
                angleBar.style.width = percentage + "%";
                angleBar.style.backgroundColor = state.color; // 进度条颜色也随状态变

                // 4. 记录日志
                if (data.status !== lastStatus && state.alert) {
                    addLog(`[ALERT] Angle dropped to ${data.angle}°`, "#ff3333");
                }
                lastStatus = data.status;

                // 5. 模拟 CPU 跳动
                if(Math.random() > 0.5) {
                    cpuSpan.innerText = Math.floor(Math.random() * 20 + 10) + "%";
                }
            })
            .catch(err => console.error("Link Error:", err));
    }

    function addLog(msg, color) {
        const li = document.createElement("li");
        li.innerHTML = `<span style="color:${color || '#888'}">> ${msg}</span>`;
        
        logList.prepend(li); // 新日志插在最上面
        if (logList.children.length > 6) {
            logList.removeChild(logList.lastChild);
        }
    }

    setInterval(updateSystem, 500);
});