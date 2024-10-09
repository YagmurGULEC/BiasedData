const uploadForm = document.getElementById('upload');
const allowedExtensions = ['csv','xls','xlsx'];
const allowedMimeTypes = ['text/csv','application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
const sensitiveColumn=document.getElementById('sensitive-column');
const labelColumn=document.getElementById('label-column');
const fileInfo=document.getElementById('file-info');
const detectButton=document.getElementById('detect');
//create an option element with the given value and text
const createOption = (value, text) => {
    const option = document.createElement('option');
    option.value = value;
    option.innerText = text;
    return option;
};

const sanitizeFilename = (filename) => {
    return filename
    .replace(/[^a-zA-Z0-9.\-_ ]/g, "")   // Remove illegal characters
    .replace(/\s+/g, "_")                // Replace spaces with underscores
    .toLowerCase(); 
};

const uploadFile = async (file,columns) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('size', file.size);
    formData.append('filename', sanitizeFilename(file.name));
    formData.append('columns', JSON.stringify(columns));
    const response = await fetch('/async-upload', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    return data;
}

const detect = async (file_key,sensitiveColumn, labelColumn) => {
    const formData = new FormData();
    formData.append('file_key', file_key);
    formData.append('sensitive_column', sensitiveColumn);
    formData.append('label_column', labelColumn);
    console.log(formData);
    const response = await fetch('/detect-bias', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    return data;
}
//Check if the file type is valid and return true if it is
const validateFile = (file) => {
    const { name: fileName, type: fileType } = file;
    const fileExtension = fileName.split('.').pop();
    if (!allowedExtensions.includes(fileExtension)) {
        alert('Invalid file type. Only CSV, XLS and XLSX files are allowed');
        return false;
    }
    if (!allowedMimeTypes.includes(fileType)) {
        alert('Invalid file type. Only CSV, XLS and XLSX files are allowed');
        return false;
    }
    if (file.size > 1024 * 1024 * 10) {
        alert('File size must be less than 10MB');
        return false;
    }
    return true;
};
const storeAndCompareValues = () => {
   sensitiveColumn.querySelectorAll('option').forEach((option) => {
        if(option.selected){
            sessionStorage.setItem('sensitiveColumn', option.value);
        }
    })
   labelColumn.querySelectorAll('option').forEach((option) => {
        if(option.selected){
            sessionStorage.setItem('labelColumn', option.value);
        }
    })  

    if(sessionStorage.getItem('sensitiveColumn')===sessionStorage.getItem('labelColumn')){
        alert('Sensitive column and Label column must be different');
      
    }
    else{
        if (sessionStorage.getItem('url') && sessionStorage.getItem('columns') ) {
            detectButton.disabled = false;
        }
    }
    
};

uploadForm.addEventListener('submit', (e) => {
    e.preventDefault();
    e.stopPropagation();
    sessionStorage.clear();

    const fileInput = e.target.querySelector('input[type="file"]');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }
    if (!validateFile(file)) {
        alert('Invalid file type. Only CSV, XLS and XLSX files are allowed');
        return;
    }
    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            const columnNames = results.meta.fields;
            if (columnNames.length>1) {
                
                columnNames.forEach((columnName) => {
                    sensitiveColumn.appendChild(createOption(columnName, columnName));
                    labelColumn.appendChild(createOption(columnName, columnName));
                });
                const sizeInMB = (file.size / (1024 * 1024)).toFixed(2); // Convert to MB
                fileInfo.innerText = `File size: ${sizeInMB} MB`;
                
                uploadFile(file, columnNames)
                    .then((data) => {
                       
                        sessionStorage.setItem('url', data.url);
                        sessionStorage.setItem('columns', JSON.stringify(data.columns));
                    })
                    .catch((error) => {
                        console.error(error);
                       
                    });
            }
            
            else {
                return;
                alert('The file must have more than one column');
            }
        }}  
    );
    
});

sensitiveColumn.addEventListener('change', storeAndCompareValues);

labelColumn.addEventListener('change', storeAndCompareValues);

detectButton.addEventListener('click', (e) => {
    let sensitiveColumn=sessionStorage.getItem('sensitiveColumn');
    let labelColumn=sessionStorage.getItem('labelColumn');
    let url=sessionStorage.getItem('url');

    detect(url,sensitiveColumn, labelColumn)
        .then((data) => {
            console.log(data);
        })
        .catch((error) => {
            console.error(error);
        })
  
    
});