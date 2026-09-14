function formatBytes(size) {
    const units = ["B", "KB", "MB", "GB", "TB"];
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

function getFolderSize(folderPath) {
    // Placeholder for folder size calculation logic
    // This would typically involve making an API call to the backend
    return 0; // Return 0 for now
}

function deleteContents(folderPath) {
    // Placeholder for delete contents logic
    // This would typically involve making an API call to the backend
    return { deletedSize: 0, deletedFiles: 0 }; // Return dummy data for now
}

function logMessage(message) {
    const logArea = document.getElementById('log');
    logArea.value += `[${new Date().toLocaleTimeString()}] ${message}\n`;
    logArea.scrollTop = logArea.scrollHeight; // Auto-scroll to the bottom
}