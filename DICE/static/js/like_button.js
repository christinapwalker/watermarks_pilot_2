// === Reactions Script (Fully Global) ===
console.log("Reactions script loaded!");

// --- Global arrays ---
window.likesData = [];
window.retweetsData = [];
window.repliesData = [];

// --- Helper: ensure DOM ready ---
function onDOMReady(callback) {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", callback);
    } else {
        callback();
    }
}

// --- Global collection functions ---
window.collectLikes = function() {
    window.likesData = [];
    document.querySelectorAll('.like-button').forEach(button => {
        const docId = button.id.replace('like_button_', '');
        const icon = button.querySelector('.like-icon');
        const isLiked = icon && icon.classList.contains('bi-heart-fill');
        window.likesData.push({ doc_id: docId, liked: isLiked });
    });
    console.log("Likes data:", window.likesData);
};

// FIXED: Updated collectRetweets to check for 'retweeted' class on button
window.collectRetweets = function() {
    window.retweetsData = [];
    document.querySelectorAll('.retweet-button').forEach(button => {
        const docId = button.id.replace('retweet_button_', '');
        const icon = button.querySelector('.retweet-icon');

        // Check multiple ways a retweet might be indicated
        const hasTextSuccess = icon && icon.classList.contains('text-success');
        const buttonHasRetweeted = button.classList.contains('retweeted');

        // A retweet is indicated by text-success OR by the button having 'retweeted' class
        const isRetweeted = hasTextSuccess || buttonHasRetweeted;

        window.retweetsData.push({ doc_id: docId, retweeted: isRetweeted });
    });
    console.log("Retweets data:", window.retweetsData);
};

window.collectData = function() {
    window.collectLikes();
    window.collectRetweets();
    console.log("=== COLLECTED DATA ===");
    console.log("Likes:", window.likesData);
    console.log("Retweets:", window.retweetsData);
    console.log("Replies:", window.repliesData);
};

// --- Toggle functions with auto-updating arrays ---
window.toggleLike = function(button) {
    const icon = button.querySelector('.like-icon');
    const count = button.querySelector('.like-count');
    let n = parseInt(count.textContent);

    if (icon.classList.contains('bi-heart')) {
        icon.classList.replace('bi-heart', 'bi-heart-fill');
        n++;
    } else {
        icon.classList.replace('bi-heart-fill', 'bi-heart');
        n--;
    }
    count.textContent = n;

    const docId = button.id.replace('like_button_', '');
    const index = window.likesData.findIndex(x => x.doc_id === docId);
    const isLiked = icon.classList.contains('bi-heart-fill');

    if (index !== -1) {
        window.likesData[index].liked = isLiked;
    } else {
        window.likesData.push({ doc_id: docId, liked: isLiked });
    }
};

// UPDATED: toggleRetweet to match the detection logic
window.toggleRetweet = function(button) {
    const icon = button.querySelector('.retweet-icon');
    const count = button.querySelector('.retweet-count');
    let n = parseInt(count.textContent);

    // Check current state using the same logic as collectRetweets
    const hasTextSuccess = icon.classList.contains('text-success');
    const buttonHasRetweeted = button.classList.contains('retweeted');
    const isCurrentlyRetweeted = hasTextSuccess || buttonHasRetweeted;

    if (!isCurrentlyRetweeted) {
        // Add retweet
        icon.classList.add('text-success');
        button.classList.add('retweeted');
        n++;
    } else {
        // Remove retweet
        icon.classList.remove('text-success');
        button.classList.remove('retweeted');
        n--;
    }

    count.textContent = n;

    const docId = button.id.replace('retweet_button_', '');
    const index = window.retweetsData.findIndex(x => x.doc_id === docId);
    const isRetweeted = icon.classList.contains('text-success') || button.classList.contains('retweeted');

    if (index !== -1) {
        window.retweetsData[index].retweeted = isRetweeted;
    } else {
        window.retweetsData.push({ doc_id: docId, retweeted: isRetweeted });
    }
};

// --- Reply tracking ---
window.addReply = function(docId, replyText) {
    if (!replyText.trim()) return;
    const index = window.repliesData.findIndex(x => x.doc_id === docId);
    if (index !== -1) {
        window.repliesData[index].reply = replyText;
    } else {
        window.repliesData.push({ doc_id: docId, reply: replyText });
    }
    console.log("Replies updated:", window.repliesData);
};

// --- Attach listeners after DOM is ready ---
onDOMReady(() => {
    // --- Event Listeners for Tweet Buttons ---
    document.querySelectorAll('.like-button').forEach(btn =>
        btn.addEventListener('click', () => window.toggleLike(btn))
    );
    document.querySelectorAll('.retweet-button').forEach(btn =>
        btn.addEventListener('click', () => window.toggleRetweet(btn))
    );
    document.querySelectorAll('.reply-modal-button').forEach(btn =>
        btn.addEventListener('click', function() {
            const docId = this.id.replace('reply_modal_button_', '');
            const replyField = document.getElementById(`reply_to_item_${docId}`);
            if (replyField) window.addReply(docId, replyField.value.trim());
        })
    );

    // --- Submission Logic ---
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function(event) {
            // Collect final data
            window.collectLikes();
            window.collectRetweets();

            // Prepare data for submission
            const likesToSave = window.likesData.filter(item => item.liked).map(item => item.doc_id);
            const retweetsToSave = window.retweetsData.filter(item => item.retweeted).map(item => item.doc_id);

            // Populate the hidden input fields
            const likesField = document.querySelector('input[name="likes_data"]');
            const retweetsField = document.querySelector('input[name="retweets_data"]');

            if (likesField) {
                likesField.value = JSON.stringify(likesToSave);
            }

            if (retweetsField) {
                retweetsField.value = JSON.stringify(retweetsToSave);
            }

            console.log("Submitting - Likes:", likesToSave);
            console.log("Submitting - Retweets:", retweetsToSave);
        });
    }

    // --- Initialize arrays with current page state ---
    window.collectLikes();
    window.collectRetweets();
});