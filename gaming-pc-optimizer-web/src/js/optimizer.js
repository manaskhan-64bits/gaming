function formatBytes(size) {
    const units = ["B", "KB", "MB", "GB", "TB"];
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

async function deleteContents(folder) {
    let deletedSize = 0;
    let deletedFiles = 0;

    try {
        const entries = await fetch(`/api/contents?folder=${encodeURIComponent(folder)}`).then(res => res.json());

        for (const entry of entries) {
            const path = `${folder}/${entry.name}`;

            if (entry.type === 'file') {
                deletedSize += entry.size;
                await fetch(`/api/delete?path=${encodeURIComponent(path)}`, { method: 'DELETE' });
                deletedFiles++;
            } else if (entry.type === 'directory') {
                const folderSize = await getFolderSize(path);
                await fetch(`/api/delete?path=${encodeURIComponent(path)}`, { method: 'DELETE' });
                deletedSize += folderSize;
                deletedFiles++;
            }
        }
    } catch (error) {
        console.error(`Error deleting contents of ${folder}:`, error);
    }

    return { deletedSize, deletedFiles };
}

async function cleanTempFiles() {
    const tempLocations = [
        '/temp',
        '/tmp',
        '/windows/temp'
    ];

    let totalSize = 0;
    let totalFiles = 0;

    for (const location of tempLocations) {
        const { deletedSize, deletedFiles } = await deleteContents(location);
        totalSize += deletedSize;
        totalFiles += deletedFiles;
    }

    return { totalSize, totalFiles };
}

async function emptyRecycleBin() {
    try {
        await fetch('/api/recycle-bin/empty', { method: 'POST' });
        console.log("Recycle Bin emptied.");
    } catch (error) {
        console.error("Could not empty Recycle Bin:", error);
    }
}

async function enableGameMode() {
    try {
        await fetch('/api/game-mode/enable', { method: 'POST' });
        console.log("Windows Game Mode enabled.");
    } catch (error) {
        console.error("Could not enable Windows Game Mode:", error);
    }
}

async function setHighPerformancePowerPlan() {
    try {
        await fetch('/api/power-plan/high-performance', { method: 'POST' });
        console.log("High Performance power plan selected.");
    } catch (error) {
        console.error("Could not change the power plan:", error);
    }
}

async function launchGame(gamePath) {
    if (!gamePath) {
        alert("Please select a game executable first.");
        return;
    }

    try {
        await fetch(`/api/launch-game?path=${encodeURIComponent(gamePath)}`, { method: 'POST' });
        console.log(`Launching game: ${gamePath}`);
    } catch (error) {
        console.error("Launch error:", error);
    }
}