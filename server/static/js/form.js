document.addEventListener('DOMContentLoaded', function() {
    const createPostForm = document.getElementById('create-post-form');
    createPostForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(createPostForm);

        fetch('/api/create-post', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});