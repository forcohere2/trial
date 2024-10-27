// Initialize Split.js for the viewer and editor with a draggable divider
Split(['.viewer', '.editor'], {
    sizes: [37, 63],  // Initial split size percentages
    minSize: 200,     // Minimum size of each pane
    gutterSize: 5,    // Size of the draggable divider
    cursor: 'col-resize'  // Cursor style when hovering over the divider
});

// Toggle sidebar visibility
function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("active");
}

// File upload functionality
document.getElementById('upload-button').addEventListener('click', async () => {
    const fileInput = document.getElementById('file-upload');
    const ocrCheckbox = document.getElementById('ocr-checkbox').checked;
    const formData = new FormData();

    // Check if file is selected
    if (fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }

    // Append the file to the form data
    formData.append('file', fileInput.files[0]);

    // Append OCR option and selected languages
    formData.append('ocrCheckbox', ocrCheckbox ? 'on' : 'off');
    if (document.getElementById('lang-eng').checked) formData.append('lang-eng', 'on');
    if (document.getElementById('lang-guj').checked) formData.append('lang-guj', 'on');
    if (document.getElementById('lang-san').checked) formData.append('lang-san', 'on');
    if (document.getElementById('lang-hin').checked) formData.append('lang-hin', 'on');

    // Send file and options to the server
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            // Display the converted HTML in the viewer without removing the hamburger menu
            const viewer = document.querySelector('.viewer');

            // Check if an iframe already exists; if so, update its src, otherwise create one
            let iframe = viewer.querySelector('iframe');
            if (!iframe) {
                iframe = document.createElement('iframe');
                iframe.setAttribute('frameborder', '0');
                iframe.setAttribute('width', '100%');
                iframe.setAttribute('height', '100%');
                viewer.appendChild(iframe);
            }
            iframe.src = result.html_url;

            // Save the viewer content URL to local storage
            localStorage.setItem('viewerContentUrl', result.html_url);
        } else {
            alert(result.error || "Failed to upload and process the document.");
        }
    } catch (error) {
        console.error("Error uploading file:", error);
        alert("An error occurred while uploading the file. Please try again.");
    }
});

// Load saved viewer content on page load
window.addEventListener('load', () => {
    const savedViewerContentUrl = localStorage.getItem('viewerContentUrl');
    if (savedViewerContentUrl) {
        const viewer = document.querySelector('.viewer');
        let iframe = viewer.querySelector('iframe');
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.setAttribute('frameborder', '0');
            iframe.setAttribute('width', '100%');
            iframe.setAttribute('height', '100%');
            viewer.appendChild(iframe);
        }
        iframe.src = savedViewerContentUrl;
    }
});

// Function to clear the editor content
function clearEditorContent() {
    if (editorInstance) {
        const confirmClear = confirm("Are you sure you want to clear the content?");
        if (confirmClear) {
            editorInstance.setData(''); // Clears the content
            localStorage.removeItem('editorContent'); // Clear the saved content
        }
    }
}