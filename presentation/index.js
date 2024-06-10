document.addEventListener("DOMContentLoaded", function() {
    const getCardButton = document.getElementById("getCard");
    const getCardsButton = document.getElementById("getCards"); 
    const getUserButton = document.getElementById("getUser"); 
    const uploadCSVButton = document.getElementById("uploadCSVBtn");

    const dropZone = document.getElementById('drop-zone');
    const output = document.getElementById('output');

    const loadingSpinner = document.querySelector('.loading-spinner');

    function fetchDataAndProcess(url) {
        showLoadingSpinner();

        return fetch(url)
            .then(response => {
                hideLoadingSpinner();

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Data fetched:', data);
                 // Process the fetched data as needed
                return data; // Return the fetched data
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                hideLoadingSpinner();
                throw error; // Rethrow the error to handle it outside this function
            });
      }

      function sendCSVToAPI(data) {
        const apiEndpoint = '';
        fetch(apiEndpoint,{
            method:'POST',
            headers: {
                'Content-type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            output.textContent += '\n\nAPI Response:\n' + JSON.stringify(data, null, 2);
        })
        .catch((error) => {
            console.error('Error:', error)
        });
      }

    async function getCard() {
        //GET DATA
        const apiUrl = 'https://httpbin.org/get';
        let fetchData; 
        try {
            fetchedData = await fetchDataAndProcess(apiUrl);
            console.log("Data received:", fetchedData);
          } catch (error) {
            // Handle errors
          }

        // Display Data

        showContentDiv("cardDetails");

    }

    async function getCards() {
        //GET DATA
        const apiUrl = 'https://api.example.com/data';
        let fetchData; 
        try {
            fetchedData = await fetchDataAndProcess(apiUrl);
            console.log("Data received:", fetchedData);
          } catch (error) {
            // Handle errors
          }

        // Process Data
        var test = "<tr><td>someCard</td><td>someUrl</td><td>100.00</td></tr>";
        
        // Update the table body with the new data
        document.getElementById('cardTable').getElementsByTagName('tbody')[0].innerHTML = test;

        showContentDiv("cardList");
    }

    async function getUser() {
        //GET DATA
        const apiUrl = 'https://api.example.com/data';
        let fetchData; 
        try {
            fetchedData = await fetchDataAndProcess(apiUrl);
            console.log("Data received:", fetchedData);
          } catch (error) {
            // Handle errors
          }

        // Process Data

        // Display Data

        showContentDiv("userDetails");
    }

    function getDropZone() {
        showContentDiv("uploadCSV");
    }

    function handleFileDrop(event) {
        event.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            readFileAsText(file);
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        dropZone.classList.add('dragover');
    }

    function handleDragLeave() {
        dropZone.classList.remove('dragover');
    }

    function parseCSV(text) {
        const lines = text.split('\n');
        const result = [];
        const headers = lines[0].split(',');

        for (let i = 1; i < lines.length; i++) {
            const obj = {};
            const currentline = lines[i].split(',');

            for (let j = 0; j < headers.length; j++) {
                obj[headers[j]] = currentline[j];
            }
            result.push(obj);
        }

        return result;
    }

    function readFileAsText(file) {
        const reader = new FileReader();
        reader.onload = () => {
            const fileText = reader.result;
            output.textContent = fileText;
            const csvData = parseCSV(fileText);
            sendCSVToAPI(csvData);
        };
        reader.readAsText(file);
    }

    function showLoadingSpinner() {
        hideContentDivs();
        
        loadingSpinner.classList.remove("hidden");
    }
    
    function hideLoadingSpinner() {
        hideContentDivs();

        loadingSpinner.classList.add("hidden");
    }

    function hideContentDivs(){
        document.getElementById("cardDetails").classList.add("hidden");
        document.getElementById("cardList").classList.add("hidden");
        document.getElementById("userDetails").classList.add("hidden");
        document.getElementById("uploadCSV").classList.add("hidden");
    }

    function showContentDiv(div){
        hideContentDivs();

        if(div == "cardDetails"){
            document.getElementById("cardDetails").classList.remove("hidden");
        }else if (div == "cardList") {
            document.getElementById("cardList").classList.remove("hidden");
        }else if (div == "userDetails") {
            document.getElementById("userDetails").classList.remove("hidden");
        }else if (div == "uploadCSV") {
            document.getElementById("uploadCSV").classList.remove("hidden");
        }
    }

    function onStart() {
        getCardButton.addEventListener("click", getCard);
        getCardsButton.addEventListener("click", getCards);
        getUserButton.addEventListener("click", getUser);
        uploadCSVButton.addEventListener("click", getDropZone);

        dropZone.addEventListener("drop", handleFileDrop);
        dropZone.addEventListener("dragleave", handleDragLeave);
        dropZone.addEventListener("dragover", handleDragOver);
    }

    onStart();
});