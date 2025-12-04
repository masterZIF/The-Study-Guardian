document.addEventListener("DOMContentLoaded", function() {
    const statusIndicator = document.getElementById("posture-indicator");
    const logList = document.querySelector(".log-list");
    const cpuSpan = document.querySelector(".random-change"); // 简单模拟
    
    // 状态映射：定义不同状态下的样式
    const STATUS_MAP = {
        "Normal": { color: "#00ff41", text: "NORMAL", alert: false },
        "Warning: Slouching!": { color: "#ff3333", text: "CRITICAL: SLOUCHING", alert: true }
    };

    let lastStatus = "";

    function updateSystem() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                const config = STATUS_MAP[data.status] || STATUS_MAP["Normal"];
                
                // 1. 更新大状态指示灯
                statusIndicator.innerText = config.text;
                statusIndicator.style.borderColor = config.color;
                statusIndicator.style.color = config.color;
                statusIndicator.style.textShadow = `0 0 10px ${config.color}`;

                // 2. 触发报警特效 (页面边框变红)
                if (config.alert) {
                    document.body.style.boxShadow = "inset 0 0 50px #ff0000";
                } else {
                    document.body.style.boxShadow = "none";
                }

                // 3. 记录日志 (只有状态改变时才记录)
                if (data.status !== lastStatus && data.status.includes("Warning")) {
                    addLog(`[ALERT] Posture deviation detected! Angle: ${data.angle}°`, "warning-text");
                }
                lastStatus = data.status;

                // 4. 模拟 CPU 波动 (增加一点极客感)
                if(Math.random() > 0.7) {
                    cpuSpan.innerText = Math.floor(Math.random() * 30 + 10) + "%";
                }
            })
            .catch(err => console.error("Data link severed:", err));
    }

    function addLog(message, className) {
        const li = document.createElement("li");
        li.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
        if (className) li.classList.add(className);
        
        // 保持日志只有最新的 8 条
        if (logList.children.length > 8) {
            logList.removeChild(logList.firstChild);
        }
        logList.appendChild(li);
    }

    // 每 500 毫秒轮询一次后端状态
    setInterval(updateSystem, 500);
});