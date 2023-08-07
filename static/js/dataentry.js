// Function to populate the dropdown with unique values from column 'A'
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

    // Re-initialize select2
    $dropdown.select2().trigger('change');
}

let headers = []; // Global variable to store headers

// Function to fetch and display data based on the selected value in the dropdown
function fetchData() {

    const valueA = document.getElementById('dropdown-a').value;
    const valueB = document.getElementById('dropdown-b').value;
    const valueC = document.getElementById('dropdown-c').value;

    if (!valueA || !valueB || !valueC) {
        return; // Exit if any value is not selected
    }

    fetch(`/get_table?value_a=${valueA}&value_b=${valueB}&value_c=${valueC}`)
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('data-table');
        // Create table headers based on object keys
        headers = Object.keys(data[0]);
        let headerRow = '<thead><tr>';
        headerRow += '<th>Complete</th>';
        headers.forEach(header => {
            headerRow += `<th>${header}</th>`;
        });
        headerRow += '</tr></thead>';
        table.innerHTML = headerRow;

        // Populate table rows based on data
        let dropdownsToPopulate = [];
        let rows = '<tbody>';
        return Promise.all(data.map(row => {
            rows += '<tr>';
            rows += '<td><input type="checkbox" class="task-completion"></td>'; // Checkbox for task completion
            return Promise.all(headers.map(header => {
                return fetch('/get_column_type?column_name=' + header)
                .then(response => response.json())
                .then(data => {
                    if (data.type === 'number') {
                        rows += `<td><input type="number" class="editable" value="${row[header]}" disabled></td>`;
                    } 
                    else if (data.type === 'categorical') {
                        rows += `<td><select class = "select2value" id="dropdown-${header}"><option value="" disabled </option></select></td>`;
                        console.log(`${data.values}`);
                        dropdownsToPopulate.push({dropdownId: 'dropdown-' + header, values: data.values});
                    }
                    else {
                        rows += `<td>${row[header]}</td>`;
                        console.log(`${row[header]}`);
                    }
                });
            }))
            .then(() => {
                rows += '</tr>';
                return rows;
            });
        }))
        .then(rows => {
            rows += '</tbody>';
            console.log(rows);
            table.innerHTML = headerRow + rows;

            // Here we populate the dropdowns
            dropdownsToPopulate.forEach(({dropdownId, values}) => {
                populateDropdown(dropdownId, values, values[0], false);
            });
            // Clear the array for the next fetchData call
            dropdownsToPopulate = [];

            // Display the table
            table.style.display = 'block';
        });
    });
}

// Initial population of the dropdown with unique values from column 'A'
fetch('/get_unique_values_a')
.then(response => response.json())
.then(data => populateDropdown('dropdown-a', data, 'Select a value for A'));

$('#dropdown-a').on('change', function() {
    const valueA = this.value;
    if (valueA) {
        fetch(`/get_unique_values_b?value_a=${valueA}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-b', data, 'Select a value for B');
            $('#dropdown-b').prop('disabled', false); // Enable dropdown B
        });
    } else {
        $('#dropdown-b').prop('disabled', true); // Disable dropdown B if no value is selected for A
    }
});

$('#dropdown-b').on('change', function() {
    const valueA = document.getElementById('dropdown-a').value;
    const valueB = this.value;
    if (valueA) {
        fetch(`/get_unique_values_c?value_a=${valueA}&value_b=${valueB}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-c', data, 'Select a value for C');
            $('#dropdown-c').prop('disabled', false); // Enable dropdown B
        });
    } else {
        $('#dropdown-b').prop('disabled', true); // Disable dropdown B if no value is selected for A
    }
});

// Populate dropdown A
fetch('/get_unique_values_a')
.then(response => response.json())
.then(data => populateDropdown('dropdown-a', data, 'Select a value for A'));


let recordedData = []; // This will store the recorded data

function recordData() {
    const tableRows = document.querySelectorAll('#data-table tbody tr');
    recordedData = []; // Clear the previously recorded data

    tableRows.forEach(row => {
        const rowData = {};
        const columns = row.querySelectorAll('td');

        headers.forEach((header, index) => {
            // +1 because the first column (index 0) is the checkbox
            const cell = columns[index + 1];
            if (cell.querySelector('input')) {
                rowData[header] = cell.querySelector('input').value;
            } else {
                rowData[header] = cell.textContent;
            }
        });

        recordedData.push(rowData);
    });

    // Reset filters and table
    document.getElementById('dropdown-a').selectedIndex = 0;
    document.getElementById('dropdown-b').selectedIndex = 0;
    document.getElementById('dropdown-c').selectedIndex = 0;
    document.getElementById('data-table').innerHTML = '';

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
    });
}


document.addEventListener('change', function(event) {
    if (event.target.classList.contains('task-completion')) {
        const row = event.target.closest('tr');
        const inputs = row.querySelectorAll('input.editable');
        //Dropdowns with class select2value
        const dropdowns = row.querySelectorAll('select.select2value');
        // Toggle editability based on checkbox state
        inputs.forEach(input => {
            input.disabled = !event.target.checked;
        });

        // Toggle editability based on checkbox state
        dropdowns.forEach(dropdown => {
            dropdown.disabled = !event.target.checked;
        });
    }
});

