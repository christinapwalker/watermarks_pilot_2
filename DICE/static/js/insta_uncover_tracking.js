// Track Instagram "uncover photo" button clicks
var instaUncoverData = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('Instagram uncover tracking initialized');

    // Find all "Uncover Photo" elements (they are <p> tags with class "click-to-see-box")
    const uncoverElements = document.querySelectorAll('.click-to-see-box');

    console.log('Found uncover elements:', uncoverElements.length);

    // Log each element found
    uncoverElements.forEach((el, index) => {
        console.log(`Uncover element ${index}:`, {
            text: el.textContent.trim(),
            onclick: el.getAttribute('onclick')
        });
    });

    uncoverElements.forEach(function(element) {
        element.addEventListener('click', function(e) {
            const clickTime = Date.now();
            const row = this.closest('tr');
            const docId = row ? row.id : 'unknown';

            console.log('✅ Uncover Photo clicked on doc_id:', docId, 'at', new Date(clickTime).toISOString());

            instaUncoverData.push({
                doc_id: docId,
                event: 'uncover_click',
                timestamp: clickTime,
                button_text: this.textContent.trim()
            });

            // Update the hidden field immediately
            const uncoverField = document.getElementById('insta_uncover_clicks');
            if (uncoverField) {
                uncoverField.value = JSON.stringify(instaUncoverData);
                console.log('📝 Updated field with data:', instaUncoverData);
            } else {
                console.error('❌ insta_uncover_clicks field not found!');
            }
        });
    });
});