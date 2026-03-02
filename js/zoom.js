function updateZoom(value) {
    const zoomContent = document.getElementById('zoom-content');
    const zoomValueDisplay = document.getElementById('zoomValue');
    
    // Update the CSS transform
    zoomContent.style.transform = `scale(${value})`;
    
    // Update the percentage text display
    zoomValueDisplay.textContent = `${Math.round(value * 100)}%`;
    
}