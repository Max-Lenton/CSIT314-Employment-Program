document.addEventListener('DOMContentLoaded', function () {
    const summary = document.getElementById('summary-text');
    if (summary) {
        summary.textContent = 'Profile page loaded from profile.html with its own profile.js file.';
    }
    const uploadForm = document.getElementById('resume-upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const statusText = document.getElementById('upload-status');
            const fileInput = document.getElementById('resume-file');
            
            statusText.style.color = "#4ecdc4";
            statusText.innerText = "Uploading...";

            const formData = new FormData();
            formData.append("resume", fileInput.files[0]);

            fetch('/upload_resume', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw response; 
                }
                return response.json();
            })
            .then(data => {
                statusText.style.color = "#4ecdc4";
                statusText.innerText = data.message;
                
                fileInput.value = ""; 
            })
            .catch(async (errorResponse) => {
                const errorData = await errorResponse.json();
                statusText.style.color = "#4ecdc4";
                statusText.innerText = errorData.message || "An error occurred during upload.";
            });
        });
    }
});
