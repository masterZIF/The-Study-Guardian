document.addEventListener("DOMContentLoaded", function() {
    const statusCard = document.getElementById("status-card-bg");
    const emojiFace = document.getElementById("emoji-face");
    const statusText = document.getElementById("status-text");
    const subText = document.getElementById("sub-text");
    const angleValue = document.getElementById("angle-value");

    function updateSystem() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                angleValue.innerText = data.angle + "°";

                if (data.status.includes("Warning")) {
                    setBadState();
                } else {
                    setGoodState();
                }
            })
            .catch(err => console.error("Error:", err));
    }

    function setGoodState() {
        statusCard.style.backgroundColor = "var(--state-good-bg)";
        statusText.style.color = "var(--state-good-text)";
        subText.style.color = "var(--state-good-text)";
        
        emojiFace.innerText = "🥰";
        statusText.innerText = "坐姿很棒！";
        subText.innerText = "保持这个状态，继续加油哦";
    }

    function setBadState() {
        statusCard.style.backgroundColor = "var(--state-bad-bg)";
        statusText.style.color = "var(--state-bad-text)";
        subText.style.color = "var(--state-bad-text)";
        
        emojiFace.innerText = "🥺";
        statusText.innerText = "脖子酸了吗？";
        subText.innerText = "稍微抬起头，休息一下吧";
    }

    setInterval(updateSystem, 500);
});