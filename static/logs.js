// static/logs.js
function updateLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            logsContainer.innerHTML = '';
            data.logs.forEach(log => {
                const logElement = document.createElement('pre');
                logElement.textContent = log;
                logsContainer.appendChild(logElement);
            });
        })
        .catch(error => console.error('Error fetching logs:', error));
}

// Update logs every 5 seconds (5000 milliseconds)
setInterval(updateLogs, 5000);

// Initial logs update
updateLogs();
