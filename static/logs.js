function updateLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs');
            logsContainer.innerHTML = '';

            // Sort logs from newest to oldest
            data.logs.sort((a, b) => {
                const timestampA = new Date(a.split(" ", 1)[0]);
                const timestampB = new Date(b.split(" ", 1)[0]);
                return timestampB - timestampA;
            });

            data.logs.forEach(log => {
                const log_parts = log.split(" ", 3);
                const timestamp = log_parts[0];
                const level = log_parts[1].replace("[", "").replace("]:", "");
                const message = log_parts[2];

                const logElement = document.createElement('div');
                logElement.innerHTML = `<strong>${timestamp} [${level}]:</strong> ${message}`;
                logsContainer.appendChild(logElement);
            });
        })
        .catch(error => console.error('Error fetching logs:', error));
}

// Initial logs update
updateLogs();

// Update logs every 5 seconds (5000 milliseconds)
setInterval(updateLogs, 5000);
