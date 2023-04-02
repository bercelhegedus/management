function updateLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            logsContainer.innerHTML = '';
            data.logs.forEach(log => {
                const logElement = document.createElement('pre');
                logElement.textContent = log;
                logsContainer.prepend(logElement);
            });
        })
        .catch(error => console.error('Error fetching logs:', error));
}

// Initial logs update
updateLogs();
