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