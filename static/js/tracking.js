function populateDropdown(dropdownId, values, startingValue, disableStartingValue = true) {
    const $dropdown = $(`#${dropdownId}`);

    // Clear existing options
    $dropdown.empty();

    // Add placeholder
    if (disableStartingValue) {
        const placeholder = `<option value="" disabled selected>${startingValue}</option>`;
        $dropdown.append(placeholder);
    }
    else {
        const placeholder = `<option value="" selected>${startingValue}</option>`;
        $dropdown.append(placeholder);
    }
    
    // Append new options, do not add starting value to the list of options

    values.forEach(value => {
        if (value !== startingValue) {
            const option = new Option(value, value, false, false);
            $dropdown.append(option);
        }
    });

    $dropdown.select2(
        {
            width: '300px',
        }
    ).trigger('change');
}

let headers = []; // Global variable to store headers

// Function to fetch and display data based on the selected value in the dropdown
function fetchData() {
    const izometria = document.getElementById('dropdown-izometria').value;
    const lap = document.getElementById('dropdown-lap').value;
    const kategoria = document.getElementById('dropdown-kategoria').value;

    if (!izometria || !lap || !kategoria) {
        return; // Exit if any value is not selected
    }

    fetch(`/get_table?izometria=${izometria}&lap=${lap}&kategoria=${kategoria}`)
    .then(response => response.json())
    .then(data => {
        headers = Object.keys(data[0]);
        
        console.log(data);

        // Fetch column data types for all headers in a single request
        const headersString = headers.join(',');
        fetch(`/get_column_priority?column_names=${headersString}&kategoria=${kategoria}`)
        .then(response => response.json())
        .then(headerTypeMap => {
            headers.sort((a, b) => {
                const priorityA = headerTypeMap[a] !== undefined ? headerTypeMap[a] : Infinity;
                const priorityB = headerTypeMap[b] !== undefined ? headerTypeMap[b] : Infinity;
                return priorityA - priorityB;
            });
                        
            // Filter out headers with type 'exclude'
            const validHeaders = headers.filter(header => headerTypeMap[header].type !== 'exclude');

            // Create table headers based on validHeaders
            let headerRow = '<thead><tr>';
            headerRow += '<th>Modositas</th>';
            validHeaders.forEach(header => {
                headerRow += `<th>${header}</th>`;
            });
            headerRow += '</tr></thead>';
            
            // Process rows with the fetched header types
            let rows = '<tbody>';
            data.forEach((row, rowIndex) => {
                rows += '<tr>';
                rows += '<td class="checkbox-cell"><input type="checkbox" class="task-completion"></td>';                
                validHeaders.forEach(header => {
                    if (row[header]['type'] === 'number') {
                        rows += `<td class="numeric-cell"><input type="number" class="editable" value="${row[header]['value']}" disabled>`;
                        rows += `<button class="set-max" max-value="${row[header]['max']}" disabled>Befejezve</button></td>`;
                    } else if (row[header]['type'] === 'categorical') {
                        rows += `<td><select class="select2value" id="dropdown-${header}-${rowIndex}" disabled><option value="${row[header]['value']}" disabled selected></option></select></td>`;
                    } else if (row[header]['type'] === 'date') {
                        rows += `<td><input type="date" class="editable" value="${row[header]['value']}" disabled></td>`;
                    } else {
                        rows += `<td>${row[header]['value']}</td>`;
                    }
                });
                rows += '</tr>';
            });
            rows += '</tbody>';
            
            const table = document.getElementById('data-table');
            table.innerHTML = headerRow + rows;

            // Populate dropdowns
            const tableDropdowns = document.querySelectorAll('#data-table select.select2value');
            tableDropdowns.forEach(dropdown => {
                const header = dropdown.id.split('-')[1]
                const rowid = dropdown.id.split('-')[2]
                // get possible values from data by row index and header (accepted_values in data)
                const values = data[rowid][header]["accepted_values"];
                const startingValue = dropdown.value ? dropdown.value : header;
                const disableStartingValue = dropdown.value ? false : true;
                populateDropdown(dropdown.id, values, startingValue, disableStartingValue);
            });

            table.style.display = 'block';
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
}

// Initial population of the dropdown with unique values from column 'A'
fetch('/get_unique_values_izometria')
.then(response => response.json())
.then(data => {
    populateDropdown('dropdown-izometria', data, 'Izometria');
});




$('#dropdown-izometria').on('change', function() {
    const izometria = this.value;
    if (izometria) {
        fetch(`/get_unique_values_lap?izometria=${izometria}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-lap', data, 'Lap');
            $('#dropdown-lap').prop('disabled', false); // Enable dropdown B
            //Disable dropdown C
            $('#dropdown-kategoria').prop('disabled', true);
            //Reset dropdown C
            $('#dropdown-kategoria').val(null).trigger('change');
        });
    } else {
        $('#dropdown-lap').prop('disabled', true); // Disable dropdown B if no value is selected for A
    }
});

$('#dropdown-lap').on('change', function() {
    const izometria = document.getElementById('dropdown-izometria').value;
    const lap = this.value;
    if (lap) {
        fetch(`/get_unique_values_kategoria?izometria=${izometria}&lap=${lap}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-kategoria', data, 'Kategoria');
            $('#dropdown-kategoria').prop('disabled', false); // Enable dropdown B
        });
    } else {
        $('#dropdown-lap').prop('disabled', true); // Disable dropdown B if no value is selected for A
    }
});

$('#dropdown-kategoria').on('change', function() {
    fetchData();
});

let recordedData = []; // This will store the recorded data

function recordData() {
    const tableRows = document.querySelectorAll('#data-table tbody tr');
    recordedData = []; // Clear the previously recorded data

    tableRows.forEach(row => {
        const rowData = {};
        const columns = row.querySelectorAll('td');
    
        headers.forEach((header, index) => {
            const cell = columns[index + 1];
            if (cell) {
                if (cell.querySelector('input[type="number"]')) {
                    rowData[header] = cell.querySelector('input[type="number"]').value;
                } else if (cell.querySelector('.select2value')) {
                    rowData[header] = cell.querySelector('.select2value').value;
                } else if (cell.querySelector('input[type="date"]')) {
                    rowData[header] = cell.querySelector('input[type="date"]').value;
                } else {
                    rowData[header] = cell.textContent;
                }
            }
        });
        recordedData.push(rowData);
    });

    // Reset filters and table
    //document.getElementById('data-table').innerHTML = '';

    fetch('/save_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(recordedData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        showToast(data.message);
    });
}


document.addEventListener('change', function(event) {
    if (event.target.classList.contains('task-completion')) {
        const row = event.target.closest('tr');
        const inputs = row.querySelectorAll('input.editable');
        //set max button
        const setMaxButtons = row.querySelector('button.set-max');
        //Dropdowns with class select2value
        const dropdowns = row.querySelectorAll('select.select2value');
        // Toggle editability based on checkbox state
        inputs.forEach(input => {
            input.disabled = !event.target.checked;
        });
        
        if (event.target.checked) {
            row.classList.remove('inactive-row'); // Remove the 'inactive-row' class when the checkbox is checked
        } else {
            row.classList.add('inactive-row'); // Add the 'inactive-row' class when the checkbox is unchecked
        }        

        // Toggle editability based on checkbox state
        setMaxButtons.disabled = !event.target.checked;

        // Toggle editability based on checkbox state
        dropdowns.forEach(dropdown => {
            dropdown.disabled = !event.target.checked;
            // Reset dropdown value
            if (!event.target.checked) {
                dropdown.selectedIndex = 0;
                $(dropdown).trigger('change');
            }         
        });

        // Set date input to today's date if checkbox is checked
        if (event.target.checked) {
            const dateInput = row.querySelector('input[type="date"]');
            if (!dateInput.value){
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        }
        // Clear date input if checkbox is unchecked
        else {
            const dateInput = row.querySelector('input[type="date"]');
            dateInput.value = '';
        }
        // Reset number input to original value if checkbox is unchecked
        if (!event.target.checked) {
            const numberInput = row.querySelector('input[type="number"]');
            numberInput.value = numberInput.defaultValue;
        }
    }
});

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    
    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000); // The toast will disappear after 3 seconds
}


document.addEventListener('click', function(event) {
    if (event.target.classList.contains('set-max')) {
        const maxVal = event.target.getAttribute('max-value');
        const inputElem = event.target.previousSibling;
        inputElem.value = maxVal;
    }
});