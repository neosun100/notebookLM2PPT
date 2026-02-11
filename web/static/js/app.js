let selectedFiles = [];
let conversionTasks = {};

// File input handling
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');

fileInput.addEventListener('change', handleFiles);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
    addFiles(files);
});

function handleFiles(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function addFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    updateFileList();
}

function updateFileList() {
    const fileListSection = document.getElementById('fileListSection');
    const fileList = document.getElementById('fileList');
    
    if (selectedFiles.length === 0) {
        fileListSection.style.display = 'none';
        return;
    }
    
    fileListSection.style.display = 'block';
    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div>
                <div class="file-name">📄 ${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function startConversion() {
    if (selectedFiles.length === 0) return;
    
    const options = {
        pages: document.getElementById('pageRange').value || null,
        parallel: parseInt(document.getElementById('parallel').value),
        force: document.getElementById('force').checked,
        no_clean: document.getElementById('keepTemp').checked,
        remove_watermark: document.getElementById('removeWatermark').checked
    };
    
    // Show progress section
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    
    const progressList = document.getElementById('progressList');
    progressList.innerHTML = '';
    
    // Process each file
    for (const file of selectedFiles) {
        const taskId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Add progress item
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        progressItem.id = `progress-${taskId}`;
        progressItem.innerHTML = `
            <div style="flex: 1;">
                <div class="file-name">${file.name}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="bar-${taskId}" style="width: 0%"></div>
                </div>
            </div>
            <span class="status status-processing" id="status-${taskId}">Processing...</span>
        `;
        progressList.appendChild(progressItem);
        
        // Upload and convert
        try {
            await convertFile(file, taskId, options);
        } catch (error) {
            updateProgress(taskId, 100, 'error', error.message);
        }
    }
    
    // Show results
    showResults();
}

async function convertFile(file, taskId, options) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));
    
    const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Conversion failed: ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n').filter(l => l.trim());
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                if (data.progress !== undefined) {
                    updateProgress(taskId, data.progress, 'processing', data.message);
                }
                
                if (data.status === 'completed') {
                    updateProgress(taskId, 100, 'success', 'Completed');
                    conversionTasks[taskId] = {
                        filename: file.name,
                        output: data.output_file,
                        download_url: data.download_url
                    };
                }
                
                if (data.status === 'error') {
                    updateProgress(taskId, 100, 'error', data.error);
                }
            }
        }
    }
}

function updateProgress(taskId, progress, status, message) {
    const bar = document.getElementById(`bar-${taskId}`);
    const statusEl = document.getElementById(`status-${taskId}`);
    
    if (bar) bar.style.width = progress + '%';
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = `status status-${status}`;
    }
}

function showResults() {
    const resultsSection = document.getElementById('resultsSection');
    const resultsList = document.getElementById('resultsList');
    
    resultsSection.style.display = 'block';
    
    resultsList.innerHTML = Object.entries(conversionTasks).map(([taskId, task]) => `
        <div class="result-item">
            <div>
                <div class="file-name">✅ ${task.filename}</div>
                <div class="file-size">${task.output}</div>
            </div>
            <a href="${task.download_url}" class="download-btn" download>Download</a>
        </div>
    `).join('');
}
