document.getElementById('create-post-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var form = this;
    var errorMessage = document.getElementById('error-message');

    fetch('/api/health', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            form.submit();
        } else {
            errorMessage.style.display = 'block';
        }
    })
    .catch(error => {
        errorMessage.style.display = 'block';
    });
});

// Function to perform health check
function performHealthCheck() {
    fetch('/api/health', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            console.log('API is reachable');
        } else {
            console.error('API is not reachable');
        }
    })
    .catch(error => {
        console.error('API is not reachable');
    });
}

// Run health check every 1 minute (60000 milliseconds)
setInterval(performHealthCheck, 60000);

// Initial health check on page load
performHealthCheck();