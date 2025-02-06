Dropzone.autoDiscover = false; // Ensure Dropzone does not auto-discover

document.addEventListener('DOMContentLoaded', function() {
    const createPostForm = document.getElementById('create-post-form');

    // Initialize Dropzone
    const dropzone = new Dropzone("#dropzone-area", {
        url: '/api/create-post', // Your file upload API URL
        paramName: 'file', // The name that will be used to transfer the file
        maxFilesize: 10000, // MB
        autoProcessQueue: false, // Disable auto upload
        addRemoveLinks: true,
        uploadMultiple: true,
        parallelUploads: 10, // Adjust based on how many files you expect to handle
        init: function() {
            const dz = this;

            // Append form data to Dropzone request
            dz.on('sending', function(file, xhr, formData) {
                const title = document.querySelector('input[name="title"]').value;
                const words = document.querySelector('textarea[name="words"]').value;
                formData.append('title', title);
                formData.append('words', words);
                console.log('Form Data:', { title, words });
                console.log('Files:', dz.files);
            });

            // On form submission, process Dropzone files
            createPostForm.addEventListener('submit', function(event) {
                event.preventDefault();

                // If no files in Dropzone, do nothing
                if (dz.files.length === 0) {
                    alert('Please upload at least one file.');
                    return;
                }

                dz.processQueue(); // Manually process the queue
            });

            // On success, show success message
            dz.on('successmultiple', function(files, response) {
                console.log('Success:', response);
                if (response.message === "Post created") {
                    alert('Post created successfully!');
                    // Optionally, you can reload the page or reset the form here
                    // window.location.reload(); // Reload the page on success
                } else {
                    alert('Error creating post');
                }
            });

            // On error, show error message
            dz.on('errormultiple', function(files, response) {
                console.error('Error:', response);
                alert('Error uploading files');
            });

            // Handle file removal
            dz.on('removedfile', function(file) {
                console.log('Removed file:', file);
            });
        }
    });
});