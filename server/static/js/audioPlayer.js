document.addEventListener('DOMContentLoaded', function() {
    const audioTracks = document.querySelectorAll('.audio-track');
    let currentlyPlaying = null;

    audioTracks.forEach((audio, index) => {
        audio.addEventListener('play', function() {
            if (currentlyPlaying && currentlyPlaying !== audio) {
                currentlyPlaying.pause();
                currentlyPlaying.currentTime = 0; // Reset the previous audio to the beginning
            }
            currentlyPlaying = audio; // Set the new playing audio
        });

        audio.addEventListener('ended', function() {
            currentlyPlaying = null; // Clear the reference when the audio ends
            const nextAudio = audioTracks[index + 1];
            if (nextAudio) {
                nextAudio.play();
            }
        });
    });
});