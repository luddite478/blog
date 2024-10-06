document.addEventListener('DOMContentLoaded', function() {
    const posts = document.querySelectorAll('.post');
    let currentlyPlaying = null;

    function handlePlay(media) {
        if (currentlyPlaying && currentlyPlaying !== media) {
            currentlyPlaying.pause();
            currentlyPlaying.currentTime = 0; // Reset the previous media to the beginning
        }
        currentlyPlaying = media; // Set the new playing media
    }

    function handleEnded(media, index, mediaTracks, postIndex) {
        const post = posts[postIndex];
        const repeatButton = post.querySelector('.repeat-button');

        currentlyPlaying = null; // Clear the reference when the media ends
        const nextMedia = mediaTracks[index + 1];
        if (nextMedia) {
            nextMedia.play();
        } else if (repeatButton.classList.contains('active')) {
            // If repeat button is active, cycle back to the first media in the current post
            mediaTracks[0].play();
        } else {
            const nextPost = posts[postIndex + 1];
            if (nextPost) {
                const nextPostMediaTracks = nextPost.querySelectorAll('.audio-track, .video-track');
                if (nextPostMediaTracks.length > 0) {
                    nextPostMediaTracks[0].play();
                }
            }
        }
    }

    posts.forEach((post, postIndex) => {
        const mediaTracks = post.querySelectorAll('.audio-track, .video-track');

        mediaTracks.forEach((media, index) => {
            media.addEventListener('play', function() {
                handlePlay(media);
            });

            media.addEventListener('ended', function() {
                handleEnded(media, index, mediaTracks, postIndex);
            });
        });

        const repeatButton = post.querySelector('.repeat-button');
        repeatButton.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });
});