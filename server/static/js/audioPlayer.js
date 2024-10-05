document.addEventListener('DOMContentLoaded', function() {
    const audioTracks = document.querySelectorAll('.audio-track');
    const repeatButtons = document.querySelectorAll('.repeat-button');
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
            if (audio.loop) {
                audio.play(); // Replay the audio if loop is enabled
            } else {
                currentlyPlaying = null; // Clear the reference when the audio ends
                const nextAudio = audioTracks[index + 1];
                if (nextAudio) {
                    nextAudio.play();
                }
            }
        });
    });

    repeatButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const audio = audioTracks[index];
            audio.loop = !audio.loop; // Toggle the loop property
            button.querySelector('i').classList.toggle('active'); // Toggle active class
        });
    });
});