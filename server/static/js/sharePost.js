document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const highlightPostId = urlParams.get('post_id');

    if (highlightPostId) {
        const postElement = document.querySelector(`[data-post-id="${highlightPostId}"]`);
        if (postElement) {
            postElement.scrollIntoView({ behavior: 'smooth' });
            postElement.classList.add('highlight');
            setTimeout(() => {
                postElement.classList.remove('highlight');
            }, 60000);

            // Update the URL without reloading the page
            const newUrl = `${window.location.origin}/posts/${highlightPostId}`;
            history.pushState(null, '', newUrl);
        }
    }
});

function sharePost(postId) {
    const url = `${window.location.origin}/posts/${postId}`;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).catch(err => {
            console.error('Failed to copy: ', err);
        });
    } else {
        // Fallback method
        const textArea = document.createElement("textarea");
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }
        document.body.removeChild(textArea);
    }
}