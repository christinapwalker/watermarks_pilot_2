// Track CR watermark hover events
var watermarkHoverData = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Watermark hover tracking initialized');

    // Wait a bit for the page to fully render
    setTimeout(function() {
        console.log('🔍 Searching for watermark elements...');

        // Find all CR watermark div elements (the "CR" badge that shows the tooltip)
        const watermarkElements = document.querySelectorAll('.watermark');

        console.log('📊 Found watermark elements:', watermarkElements.length);

        if (watermarkElements.length === 0) {
            console.warn('⚠️ No watermark elements found! Checking alternative selectors...');

            // Try finding by data-bs-toggle attribute
            const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            console.log('Found elements with tooltip:', tooltipElements.length);

            // Try finding divs with "CR" text
            const allDivs = document.querySelectorAll('div');
            const crDivs = Array.from(allDivs).filter(div => div.textContent.trim() === 'CR');
            console.log('Found divs with "CR" text:', crDivs.length);

            // Log the watermark container
            const containers = document.querySelectorAll('.watermark-container');
            console.log('Found watermark containers:', containers.length);
        }

        // Log each watermark found
        watermarkElements.forEach((el, index) => {
            const row = el.closest('tr');
            const docId = row ? row.id : 'unknown';
            console.log(`Watermark ${index}:`, {
                docId: docId,
                className: el.className,
                text: el.textContent.trim(),
                tooltip: el.getAttribute('title') || el.getAttribute('data-bs-original-title')
            });
        });

        watermarkElements.forEach(function(element, idx) {
            let hoverStartTime = null;

            console.log(`📌 Attaching hover listeners to watermark ${idx}`);

            element.addEventListener('mouseenter', function(e) {
                hoverStartTime = Date.now();
                const row = this.closest('tr');
                const docId = row ? row.id : 'unknown';

                console.log('✅ Watermark MOUSEENTER detected on doc_id:', docId, 'at', new Date(hoverStartTime).toISOString());
                console.log('Element that triggered:', this.className, this.textContent.trim());

                watermarkHoverData.push({
                    doc_id: docId,
                    event: 'hover_start',
                    timestamp: hoverStartTime
                });

                console.log('Current hover data array:', watermarkHoverData);
            }, true); // Use capture phase

            element.addEventListener('mouseleave', function(e) {
                if (hoverStartTime) {
                    const hoverEndTime = Date.now();
                    const duration = (hoverEndTime - hoverStartTime) / 1000;
                    const row = this.closest('tr');
                    const docId = row ? row.id : 'unknown';

                    console.log('✅ Watermark MOUSELEAVE detected on doc_id:', docId, 'Duration:', duration, 'seconds');

                    watermarkHoverData.push({
                        doc_id: docId,
                        event: 'hover_end',
                        timestamp: hoverEndTime,
                        duration: duration
                    });

                    console.log('Current hover data array:', watermarkHoverData);

                    hoverStartTime = null;
                } else {
                    console.warn('⚠️ Mouseleave without mouseenter');
                }
            }, true); // Use capture phase
        });

        console.log('✅ Hover listeners attached to', watermarkElements.length, 'watermark elements');

    }, 1000); // Wait 1 second for page to render

    // Update hidden field before submission
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            console.log('💾 Saving watermark hover data:', watermarkHoverData);
            const hoverField = document.getElementById('watermark_hover_events');
            if (hoverField) {
                hoverField.value = JSON.stringify(watermarkHoverData);
                console.log('📝 Watermark hover data saved to field:', hoverField.value);
            } else {
                console.error('❌ watermark_hover_events field not found!');
            }
        });
    } else {
        console.error('❌ Submit button not found!');
    }
});


// Update hidden field before submission
document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            console.log('Submit clicked - saving hover data:', watermarkHoverData);
            const hoverField = document.getElementById('watermark_hover_events');
            if (hoverField) {
                hoverField.value = JSON.stringify(watermarkHoverData);
                console.log('Hover data saved to field');
            } else {
                console.error('watermark_hover_events field not found!');
            }
        });
    }
});