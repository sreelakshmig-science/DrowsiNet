const statusText = document.getElementById('status-text');
const statusCard = document.getElementById('status-card');

function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            statusText.innerText = data.status;
            
            // UI Logic for Alerts
            if (data.status === "SLEEPING !!!") {
                statusCard.classList.add('danger-alert');
                statusText.style.color = "#ef4444"; // Red
            } else {
                statusCasrd.classList.remove('danger-alert');
                statusText.style.color = "#4ade80"; // Green
            }
        });
}

// Poll the server for status updates every 1 second
setInterval(updateStatus, 1000);