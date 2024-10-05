document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.closest('.post').getAttribute('data-post-id');
            const isConfirmed = confirm('Are you sure you want to delete this post?');

            if (isConfirmed) {
                fetch(`/api/delete-posts`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ids: [postId] })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    window.location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });
});