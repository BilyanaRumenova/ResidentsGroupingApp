document.getElementById('inputForm').onsubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');
    const textInput = document.getElementById('textInput');

    if (fileInput.files[0]) {
        formData.append('csv_file', fileInput.files[0]);
    }
    if (textInput.value) {
        formData.append('text_input', textInput.value);
    }

    const response = await fetch('/process-data', {
        method: 'POST',
        body: formData
    });

    const responseData = await response.json();
    const resultDisplay = document.getElementById('resultDisplay');
    const downloadLink = document.getElementById('downloadLink');

    if (response.ok) {
        const lines = responseData.processed_data.split('\n');
        const formattedData = lines.map(line => {
            const names = line.split(', ');
            return `<p>${names.join(', ')}</p>`;
        }).join('');

        resultDisplay.innerHTML = formattedData;
        downloadLink.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(responseData.processed_data);
        downloadLink.style.display = 'block';
    } else {
        resultDisplay.textContent = "No data provided";
    }
};
document.getElementById("clearButton").onclick = () => {
    const fileInput = document.getElementById("fileInput");
    fileInput.value = ''
    const textInput = document.getElementById("textInput");
    textInput.value = ''
    const resultDisplay = document.getElementById("resultDisplay");
    resultDisplay.textContent = ''
    const downloadLink = document.getElementById("downloadLink");
    downloadLink.style.display = 'none';
};