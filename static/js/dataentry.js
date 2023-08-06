// Function to populate the dropdown with unique values from column 'A'
function populateDropdown(dropdownId, values) {
    const dropdown = document.getElementById(dropdownId);
    let options = `<option value="" disabled selected>Select a value for ${dropdownId.split('-')[1].toUpperCase()}</option>`;
    values.forEach(value => {
        options += `<option value="${value}">${value}</option>`;
    });
    dropdown.innerHTML = options;
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
        let rows = '<tbody>';
        data.forEach(row => {
            rows += '<tr>';
            rows += '<td><input type="checkbox" class="task-completion"></td>'; // Checkbox for task completion
            headers.forEach(header => {
                if (header === 'D' || header === 'E') {
                    rows += `<td><input type="text" class="editable" value="${row[header]}" disabled></td>`;
                } else {
                    rows += `<td>${row[header]}</td>`;
                }
            });
            rows += '</tr>';
        });
        rows += '</tbody>';
        table.innerHTML = headerRow + rows;

        // Display the table
        table.style.display = 'block';
    });
}

// Initial population of the dropdown with unique values from column 'A'
fetch('/get_unique_values_a')
.then(response => response.json())
.then(data => populateDropdown(data));

document.getElementById('dropdown-a').addEventListener('change', function() {
    const valueA = this.value;
    if (valueA) {
        fetch(`/get_unique_values_b?value_a=${valueA}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-b', data);
            document.getElementById('dropdown-b').disabled = false; // Enable dropdown B
        });
    } else {
        document.getElementById('dropdown-b').disabled = true; // Disable dropdown B if no value is selected for A
    }
});

document.getElementById('dropdown-b').addEventListener('change', function() {
    const valueA = document.getElementById('dropdown-a').value;
    const valueB = this.value;
    if (valueB) {
        fetch(`/get_unique_values_c?value_a=${valueA}&value_b=${valueB}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown('dropdown-c', data);
            document.getElementById('dropdown-c').disabled = false; // Enable dropdown C
        });
    } else {
        document.getElementById('dropdown-c').disabled = true; // Disable dropdown C if no value is selected for B
    }
});


// Populate dropdown A
fetch('/get_unique_values_a')
.then(response => response.json())
.then(data => populateDropdown('dropdown-a', data));


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
        
        // Toggle editability based on checkbox state
        inputs.forEach(input => {
            input.disabled = !event.target.checked;
        });
    }
});
