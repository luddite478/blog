document.addEventListener('DOMContentLoaded', function() {
    const audioTracks = document.querySelectorAll('.audio-track');
    const videoTracks = document.querySelectorAll('.video-track');
    const repeatButtons = document.querySelectorAll('.repeat-button');
    let currentlyPlaying = null;

    function handlePlay(media) {
        if (currentlyPlaying && currentlyPlaying !== media) {
            currentlyPlaying.pause();
            currentlyPlaying.currentTime = 0; // Reset the previous media to the beginning
        }
        currentlyPlaying = media; // Set the new playing media
    }

    function handleEnded(media, index, mediaTracks) {
        if (media.loop) {
            media.play(); // Replay the media if loop is enabled
        } else {
            currentlyPlaying = null; // Clear the reference when the media ends
            const nextMedia = mediaTracks[index + 1];
            if (nextMedia) {
                nextMedia.play();
            }
        }
    }

    audioTracks.forEach((audio, index) => {
        audio.addEventListener('play', function() {
            handlePlay(audio);
        });

        audio.addEventListener('ended', function() {
            handleEnded(audio, index, audioTracks);
        });
    });

    videoTracks.forEach((video, index) => {
        video.addEventListener('play', function() {
            handlePlay(video);
        });

        video.addEventListener('ended', function() {
            handleEnded(video, index, videoTracks);
        });
    });

    repeatButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('active');
            const post = this.closest('.post');
            const mediaTracks = post.querySelectorAll('.audio-track, .video-track');
            mediaTracks.forEach(media => {
                media.loop = this.classList.contains('active');
            });
        });
    });
});