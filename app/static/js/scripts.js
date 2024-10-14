
const uploadFormSubmit = document.getElementById('upload-form');
const fileInfo = document.getElementById('file-info');
const sensitiveColumn = document.getElementById('sensitive-column');
const labelColumn = document.getElementById('label-column');
const detectButton = document.getElementById('detect-button');
const taskStatus = document.getElementById('task-status');
const allowedExtensions = ['csv', 'xls', 'xlsx'];
const allowedMimeTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
const plotContainer = document.getElementById('plot-container');
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
const createBarChart = (id,x,y,sum,xlabel,ylabel) => {
 // Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
var ctx = document.getElementById(`myBarChart${id}`);

var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: x,
    datasets: [{

      backgroundColor: "rgba(2,117,216,1)",
      borderColor: "rgba(2,117,216,1)",
      data: y.map((value)=>value/sum),
    }],
  },
  options: {
    scales: {
      xAxes: [{
        
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 6
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 1,
          maxTicksLimit: 5
        },
        gridLines: {
          display: true
        },
        scaleLabel: {
            display: true,
            labelString: ylabel
          }
      }],
      xAxes: [{
        scaleLabel: {
            display: true,
            labelString: xlabel
          }
      }],
    },
    legend: {
      display: false
    }
  }
});

};
const addBarChart = (id,x,y,sum,xlabel,ylabel,callback) => {
    
    const newCol=document.createElement('div');
    newCol.classList.add('col');
    const newDiv=document.createElement('div');
    newDiv.classList.add('p-3');
    
    const newCanvas=document.createElement('canvas');
    newCanvas.id=`myBarChart${id}`;
    newDiv.appendChild(newCanvas);
    newCol.appendChild(newDiv);
    plotContainer.appendChild(newCol);
    // console.log(document.getElementById(`myBarChart${id}`));
    callback(id,x,y,sum,xlabel,ylabel);
};
//Delete the file from S3 
const deleteFile = async (file_key) => {
    const formData = new FormData();
    formData.append('file_key', file_key);
    const response = await fetch('/delete-file', {
        method: 'POST',
        body: formData
    });
    return response.json();
}
const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/async-upload', {
        method: 'POST',
        body: formData
    });
    return response.json();
}


const progressTracker = (task_id) => {
    const interval = setInterval(async () => {
        const response = await fetch(`/check-task/${task_id}`);
        const data = await response.json();
        
        taskStatus.style.display = 'block';
        taskStatus.querySelector('h5').innerText = 'Data processing...';
        console.log(data);
        if (data.task_status == "SUCCESS") {
            clearInterval(interval);
            taskStatus.querySelector('h5').innerText = 'Data processing complete';
            let table=data.task_result['contingency_table'];
            let pValue=data.task_result['p_value'];
            if (pValue<0.05){
                taskStatus.innerHTML+=`<p>The p-value is ${pValue}. The sensitive and label columns are dependent with p-value 0.05 according to chi-square test.</p>`;
                
            
            }

            let newTable={};
            let total=0;
            let ylabel=sessionStorage.getItem('labelColumn');
            let groups=[];
            let totalSamples=[];
            Object.keys(table).forEach((key)=>{
                total+=Object.values(table[key]).reduce((a,b)=>a+b)
                newTable[key]={'total':Object.values(table[key]).reduce((a,b)=>a+b)}
                groups.push(key);
                totalSamples.push(Object.values(table[key]).reduce((a,b)=>a+b));

            });
           
           addBarChart(0,groups,totalSamples,total,'','Probability',createBarChart); 
            
           
            Object.keys(table).forEach((key,index)=>{
                // addBarChart(index,createBarChart);
                let x=Object.keys(table[key]);
                let y=Object.values(table[key]);
                let sum=y.reduce((a,b)=>a+b);
                let xlabel=`${key} being ${sessionStorage.getItem('labelColumn')}`;
                addBarChart(index+1,x,y,total,ylabel,xlabel,createBarChart);
            });


        }
    }, 1000);
}
const detect = async (file_key,sensitiveColumn, labelColumn) => {
    const formData = new FormData();
    formData.append('file_key', file_key);
    formData.append('sensitive_column', sensitiveColumn);
    formData.append('label_column', labelColumn);
   
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
    const sensitiveColumnValue = sensitiveColumn.value;
    const labelColumnValue = labelColumn.value;
    detectButton.disabled =false;
   
    if (sensitiveColumnValue === labelColumnValue) {
        detectButton.disabled = true;
    } else {
        sessionStorage.setItem('sensitiveColumn', sensitiveColumnValue);
        sessionStorage.setItem('labelColumn', labelColumnValue);
        detectButton.disabled = false;
    }
};



window.addEventListener('DOMContentLoaded', event => {

sensitiveColumn.addEventListener('change', storeAndCompareValues);

labelColumn.addEventListener('change', storeAndCompareValues);

detectButton.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Detect button clicked');
    const url=sessionStorage.getItem('url');
    const sensitiveColumn=sessionStorage.getItem('sensitiveColumn');
    const labelColumn=sessionStorage.getItem('labelColumn');
    try{
        const data=await detect(url,sensitiveColumn, labelColumn);
        const task_id=data.task_id;
        console.log(data);
        progressTracker(task_id);
    }
    catch(error){
        console.error(error);
    }
    
});

    
    uploadFormSubmit.onclick = async (e) => {
        
        if (sessionStorage.getItem('url')) {
           const url=sessionStorage.getItem('url');
           const deleteResponse=await deleteFile(url);
         
        }
        sessionStorage.clear();
        const fileInput = e.target.previousElementSibling;
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
            complete: async function(results) {
                const columnNames = results.meta.fields;
                if (columnNames.length>1) {
                    
                    columnNames.forEach((columnName) => {
                        sensitiveColumn.appendChild(createOption(columnName, columnName));
                        labelColumn.appendChild(createOption(columnName, columnName));
                    });
                    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2); // Convert to MB
                    fileInfo.innerText = `File size: ${sizeInMB} MB`;
                    
                    try{
                        const response =await uploadFile(file);
                        console.log(response);
                        sessionStorage.setItem('url', response.key);
                    }
                    catch(error){
                        console.error(error);
                    }
                    
                }
                
                else {
                    return;
                    alert('The file must have more than one column');
                }
            }});

        }
     
    });


 

    
    

