// Load the header
window.addEventListener('DOMContentLoaded', (event) => {
    fetch('/static/templates/header.html')
        .then(response => response.text())
        .then(data => {
            document.body.insertAdjacentHTML('afterbegin', data);
            document.getElementById("page-name").innerText = pageName;

            // TODO: Fetch current user info and set it
            // For the sake of this example, I'm setting a dummy user
            
    // Fetch the current user's name from the server and set it in the header
    fetch('/get_current_username')
        .then(response => response.json())
        .then(data => {
            document.getElementById("current-user").innerText = data.username;
        });
    
        });
});
