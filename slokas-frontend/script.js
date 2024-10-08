function performFuzzySearch(language) {
    // Get the query from the respective input field
    const queryId = language === 'English' ? 'queryEnglish' : 'querySanskrit';
    const query = document.getElementById(queryId).value;
    // Display loading message
    document.getElementById('loading-message').style.display = 'block';

    // Clear previous results
    document.getElementById('results-container').innerHTML = '';

    // Fetch data from the API based on the selected language
    let apiUrl;
    if (language === 'English') {
        apiUrl = `http://127.0.0.1:5000/api/ramayanam/slokas/fuzzy-search?query=${query}`;
    } else {
        apiUrl = `http://127.0.0.1:5000/api/ramayanam/slokas/fuzzy-search-sanskrit?query=${query}`;
    }

    fetch(apiUrl)
        .then(response => response.json())
        .then(results => {
            // Hide loading message
            document.getElementById('loading-message').style.display = 'none';

            // Display search results
            displayResults(results);
        })
        .catch(error => {
           // Hide loading message
           document.getElementById('loading-message').style.display = 'none';

            console.error('Error fetching data:', error);
        });
}

function displayResults(results) {
    const resultsContainer = document.getElementById('results-container');

    // Clear previous results
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
    } else {
        // Display each result
        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.classList.add('result');
            resultElement.innerHTML = `
                <p>Sloka Number: ${result.sloka_number}</p>
                <p>Ratio: ${result.ratio}</p>
                <p>Sloka: ${result.sloka}</p>
                <p>Meaning: ${result.meaning}</p>
                <p>Translation: ${result.translation}</p>
                <p>Link: <a href="${generateSlokaLink(result)}" target="_blank">Go to Sloka at valmiki.iitk.ac.in</a></p>
            `;
            resultsContainer.appendChild(resultElement);
        });
    }
}
function generateSlokaLink(result) {
        const baseLink = 'https://www.valmiki.iitk.ac.in/content';
        const language = 'dv';  // Assuming 'dv' is the desired language
        const kanda = result.sloka_number.split('.')[0];
        const sarga = result.sloka_number.split('.')[1];
        const sloka = result.sloka_number.split('.')[2];

        return `${baseLink}?language=${language}&field_kanda_tid=${kanda}&field_sarga_value=${sarga}&field_sloka_value=${sloka}`;
    }
// Add event listeners for the "Enter" key press on both input fields
document.getElementById('queryEnglish').addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        performFuzzySearch('English');
    }
});

document.getElementById('querySanskrit').addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        performFuzzySearch('Sanskrit');
    }
});