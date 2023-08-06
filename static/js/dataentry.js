// Function to populate the dropdown with unique values from column 'A'
function populateDropdown(dropdownId, values) {
    const dropdown = document.getElementById(dropdownId);
    let options = `<option value="" disabled selected>Select a value for ${dropdownId.split('-')[1].toUpperCase()}</option>`;
    values.forEach(value => {
        options += `<option value="${value}">${value}</option>`;
    });
    dropdown.innerHTML = options;
}


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
        const headers = Object.keys(data[0]);
        let headerRow = '<thead><tr>';
        headers.forEach(header => {
            headerRow += `<th>${header}</th>`;
        });
        headerRow += '</tr></thead>';
        table.innerHTML = headerRow;

        // Populate table rows based on data
        let rows = '<tbody>';
        data.forEach(row => {
            rows += '<tr>';
            headers.forEach(header => {
                rows += `<td>${row[header]}</td>`;
            });
            rows += '</tr>';
        });
        rows += '</tbody>';
        table.innerHTML += rows;

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


