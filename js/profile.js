document.addEventListener("DOMContentLoaded", function () {

    // Resume upload
    var uploadForm = document.getElementById("resume-upload-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", function (e) {
            e.preventDefault();
            var statusText = document.getElementById("upload-status");
            var fileInput = document.getElementById("resume-file");

            statusText.style.color = "#4ecdc4";
            statusText.textContent = "Uploading...";

            var formData = new FormData();
            formData.append("resume", fileInput.files[0]);

            fetch("/upload_resume", { method: "POST", body: formData })
                .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
                .then(function (res) {
                    statusText.style.color = res.ok ? "#4ecdc4" : "#ff6b6b";
                    statusText.textContent = res.data.message;
                    if (res.ok) fileInput.value = "";
                });
        });
    }

    // Career preferences
    var prefForm = document.getElementById("preferences-form");
    if (prefForm) {
        prefForm.addEventListener("submit", function (e) {
            e.preventDefault();
            var statusText = document.getElementById("preferences-status");

            statusText.style.color = "#4ecdc4";
            statusText.textContent = "Saving...";

            fetch("/api/update_profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    years_exp: document.getElementById("years_exp").value,
                    preferred_mode: document.getElementById("preferred_mode").value,
                    preferred_loc: document.getElementById("preferred_loc").value
                })
            })
                .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
                .then(function (res) {
                    statusText.style.color = res.ok ? "#4ecdc4" : "#ff6b6b";
                    statusText.textContent = res.data.message;
                    if (res.ok) setTimeout(function () { statusText.textContent = ""; }, 3000);
                });
        });
    }

});
