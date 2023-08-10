document.addEventListener('DOMContentLoaded', function() {
    var forms = document.getElementsByTagName('form');
    for (var i = 0; i < forms.length; i++) {
      forms[i].addEventListener('submit', showSpinner);
    }
  });

  function showSpinner(event) {
    event.preventDefault();
    var spinner = document.getElementById('spinner');
    spinner.style.display = 'block';
    
    // Use FormData to send the form data in the request
    var formData = new FormData(event.target);
    
fetch(event.target.action, {
  method: event.target.method,
  body: formData
    }).then(function(response) {
      if (response.ok) {
        if (response.headers.get('Content-Type') === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
          var inputFilename = response.headers.get('X-Input-Filename');
          var outputFilename = inputFilename;
          response.blob().then(function(blob) {
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = outputFilename;
            document.body.appendChild(a);
            a.click();
            a.remove();
          });
        } else {
          return response.json();
        }
      } else {
        throw new Error('An error occurred while processing the request.');
      }
    }).then(function(json) {
      if (json) {
        alert(json.message);
      }
    }).catch(function(error) {
      alert(error.message);
    }).finally(function() {
      spinner.style.display = 'none';
    });
  }