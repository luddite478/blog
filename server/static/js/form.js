// Disable auto-discovery of Dropzone instances.
Dropzone.autoDiscover = false;

document.addEventListener('DOMContentLoaded', function() {
  const createPostForm = document.getElementById('create-post-form');
  const createPostButton = document.getElementById('create-post-button');

  // Initialize Dropzone on the dropzone-area div.
  const dropzone = new Dropzone("#dropzone-area", {
    url: '/api/create-post', // The endpoint for file uploads.
    paramName: 'file',       // The name of the file parameter.
    maxFilesize: 10000,      // Maximum file size in MB.
    autoProcessQueue: false, // We'll trigger the processing manually.
    addRemoveLinks: true,
    uploadMultiple: true,
    parallelUploads: 10,     // Adjust according to your needs.
    init: function() {
      const dz = this;
      
      // Append additional form fields when sending each file.
      dz.on('sending', function(file, xhr, formData) {
        const title = document.querySelector('input[name="title"]').value;
        const words = document.querySelector('textarea[name="words"]').value;
        formData.append('title', title);
        formData.append('words', words);
        console.log('Appending form data:', { title, words });
      });

      // When all files have been processed, handle the response.
      dz.on('successmultiple', function(files, response) {
        console.log('Success:', response);
        if (response.message === "Post created") {
          location.reload(); // Refresh the page
        } else {
          alert('Error creating post');
        }
      });

      dz.on('errormultiple', function(files, response) {
        console.error('Error:', response);
        alert('Error uploading files');
      });
    }
  });

  // Handle the click on our custom button.
  createPostButton.addEventListener('click', function() {
    // If no files are added, do not process the queue.
    if (dropzone.files.length === 0) {
      alert('Please upload at least one file.');
      return;
    }

    // Manually process the Dropzone queue.
    dropzone.processQueue();
  });
});