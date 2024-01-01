document.addEventListener('DOMContentLoaded', function () {
    const slokaContainer = document.getElementById('sloka-container');

    // Replace 'http://127.0.0.1:5000/api/ramayanam/kandas/BalaKanda/sargas/1/slokas' with your actual API endpoint
    fetch('http://127.0.0.1:5000/api/ramayanam/kandas/BalaKanda/sargas/1/slokas')
        .then(response => response.json())
        .then(data => {
            // Assuming your API response has a 'slokaText' property
            slokaContainer.innerHTML = `<div>${data.slokaText}</div>`;
        })
        .catch(error => console.error('Error fetching sloka:', error));
});
