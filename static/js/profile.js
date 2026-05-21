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
    const prefForm = document.getElementById('preferences-form');
    if (prefForm) {
        prefForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const statusText = document.getElementById('preferences-status');
            const yearsExp = document.getElementById('years_exp').value;
            const preferredMode = document.getElementById('preferred_mode').value;
            const preferredLoc = document.getElementById('preferred_loc').value;

            statusText.style.color = "#4ecdc4";
            statusText.textContent = "Saving preferences...";

            fetch('/api/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    years_exp: yearsExp,
                    preferred_mode: preferredMode,
                    preferred_loc: preferredLoc
                })
            })
            .then(response => {
                if (!response.ok) throw response;
                return response.json();
            })
            .then(data => {
                statusText.style.color = "#4ecdc4";
                statusText.textContent = data.message;
                
                // Clear the status message after 3 seconds
                setTimeout(() => { statusText.textContent = ""; }, 3000);
            })
            .catch(async (errorResponse) => {
                const errorData = await errorResponse.json().catch(() => ({}));
                statusText.style.color = "#ff6b6b";
                statusText.textContent = errorData.message || "An error occurred while saving.";
            });
        });
    }

});
