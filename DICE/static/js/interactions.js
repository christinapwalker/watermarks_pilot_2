console.log("🚀 Clean interactions script loading...");

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
        console.log("Processing like button:", button.id);
        const docId = button.id.replace('like_button_', '');
        const icon = button.querySelector('.like-icon');
        const isLiked = icon && icon.classList.contains('bi-heart-fill');
        console.log(`Like - Doc ID: "${docId}", Liked: ${isLiked}`);
        window.likesData.push({ doc_id: docId, liked: isLiked });
    });
    console.log("Likes data:", window.likesData);
};

window.collectRetweets = function() {
    window.retweetsData = [];
    document.querySelectorAll('.retweet-button').forEach(button => {
        console.log("Processing retweet button:", button);

        // Since retweet buttons don't have IDs, find the doc_id from parent row
        let docId = '';

        // Look for parent <tr> element with ID
        let parentRow = button.closest('tr');
        if (parentRow && parentRow.id) {
            docId = parentRow.id; // This should be just the number like "26", "105", etc.
            console.log(`Found parent row ID: "${docId}"`);
        }

        // If no parent row ID, try to find a nearby like button to get the doc_id
        if (!docId) {
            const nearbyLikeButton = button.closest('tr')?.querySelector('.like-button');
            if (nearbyLikeButton && nearbyLikeButton.id) {
                docId = nearbyLikeButton.id.replace('like_button_', '');
                console.log(`Extracted doc_id from nearby like button: "${docId}"`);
            }
        }

        const icon = button.querySelector('.retweet-icon');
        const isRetweeted = button.classList.contains('retweeted') || (icon && icon.classList.contains('text-primary'));

        console.log(`Retweet - Extracted Doc ID: "${docId}", Retweeted: ${isRetweeted}`);

        if (docId) {  // Only add if we have a valid doc_id
            window.retweetsData.push({ doc_id: docId, retweeted: isRetweeted });
        } else {
            console.warn("⚠️ Could not extract doc_id for retweet button");
        }
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

// --- Toggle functions ---
window.toggleLike = function(button) {
    console.log("🎯 toggleLike called for:", button.id);
    const icon = button.querySelector('.like-icon');
    const count = button.querySelector('.like-count');
    let n = parseInt(count.textContent);

    if (icon.classList.contains('bi-heart')) {
        icon.classList.replace('bi-heart', 'bi-heart-fill');
        icon.classList.replace('text-secondary', 'text-danger');
        n++;
        console.log("✅ Liked!");
    } else {
        icon.classList.replace('bi-heart-fill', 'bi-heart');
        icon.classList.replace('text-danger', 'text-secondary');
        n--;
        console.log("❌ Unliked!");
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

// --- Handle like click for Instagram overlay posts ---
window.handleLikeClick = function(docId, event) {
    console.log("🎯 handleLikeClick called for docId:", docId);

    // Prevent event bubbling
    if (event) {
        event.stopPropagation();
    }

    // Find the like button for this docId
    const likeButton = document.getElementById('like_button_' + docId);
    if (likeButton) {
        window.toggleLike(likeButton);
    } else {
        console.error("❌ Like button not found for docId:", docId);
    }
};

window.toggleRetweet = function(button) {
    console.log("🎯 toggleRetweet called for:", button);
    const icon = button.querySelector('.retweet-icon');
    const count = button.querySelector('.retweet-count');
    let n = parseInt(count.textContent);

    const isCurrentlyRetweeted = button.classList.contains('retweeted') || (icon && icon.classList.contains('text-primary'));

    if (!isCurrentlyRetweeted) {
        // Retweet it
        button.classList.add('retweeted');
        icon.classList.remove('text-secondary');
        icon.classList.add('text-primary');
        icon.style.webkitTextStroke = "0.5px";
        icon.style.color = "#17bf63";
        n++;
        console.log("✅ Retweeted!");
    } else {
        // Un-retweet it
        button.classList.remove('retweeted');
        icon.classList.remove('text-primary');
        icon.classList.add('text-secondary');
        icon.style.webkitTextStroke = "";
        icon.style.color = "gray";
        n--;
        console.log("❌ Un-retweeted!");
    }
    count.textContent = n;

    // Update data array - get doc_id same way as collection function
    let docId = '';
    let parentRow = button.closest('tr');
    if (parentRow && parentRow.id) {
        docId = parentRow.id;
    } else {
        const nearbyLikeButton = button.closest('tr')?.querySelector('.like-button');
        if (nearbyLikeButton && nearbyLikeButton.id) {
            docId = nearbyLikeButton.id.replace('like_button_', '');
        }
    }

    if (docId) {
        const index = window.retweetsData.findIndex(x => x.doc_id === docId);
        const isRetweeted = button.classList.contains('retweeted');

        if (index !== -1) {
            window.retweetsData[index].retweeted = isRetweeted;
        } else {
            window.retweetsData.push({ doc_id: docId, retweeted: isRetweeted });
        }
        console.log("Updated retweetsData for doc_id:", docId);
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

// --- Setup functions ---
function setupShareButtons() {
    console.log("Setting up share buttons...");
    const shareButtons = document.querySelectorAll(".share-button");
    shareButtons.forEach(function(shareButton) {
        const shareIcon = shareButton.querySelector(".share-icon");
        shareButton.addEventListener("click", function() {
            if (shareButton.classList.contains("shared")) {
                shareButton.classList.remove("shared");
                shareIcon.className = "bi bi-upload text-secondary share-icon";
                shareIcon.removeAttribute("style");
            } else {
                shareButton.classList.add("shared");
                shareIcon.className = "bi bi-upload text-primary share-icon";
                shareIcon.style.webkitTextStroke = "0.5px";
            }
        });
    });
    console.log(`Share buttons setup complete (${shareButtons.length} buttons)`);
}

function setupReplyModals() {
    console.log("Setting up reply modals...");
    const replyButtons = document.querySelectorAll('.reply-button');
    replyButtons.forEach(function(replyButton) {
        replyButton.addEventListener("click", function() {
            const docId = replyButton.id.replace('reply_button_', '');
            const replyingTweet = document.getElementById("replying_tweet_" + docId);
            const originalTweet = document.getElementById("tweet_" + docId);
            if (replyingTweet && originalTweet) {
                replyingTweet.innerHTML = originalTweet.innerHTML;
            }
        });
    });
    console.log(`Reply modals setup complete (${replyButtons.length} buttons)`);
}

function setupInteractionButtons() {
    console.log("Setting up interaction buttons...");

    // Like buttons - handle both regular and Instagram overlay posts
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(btn => {
        // Remove any existing onclick attributes to avoid conflicts
        btn.removeAttribute('onclick');

        btn.addEventListener('click', (event) => {
            // Check if this like button has a handleLikeClick onclick
            const docId = btn.id.replace('like_button_', '');
            const hasOnclick = btn.getAttribute('onclick');

            if (hasOnclick && hasOnclick.includes('handleLikeClick')) {
                // For Instagram overlay posts, use handleLikeClick
                window.handleLikeClick(docId, event);
            } else {
                // For regular posts, use toggleLike
                window.toggleLike(btn);
            }
        });
    });

    // Retweet buttons
    const retweetButtons = document.querySelectorAll('.retweet-button');
    retweetButtons.forEach(btn => {
        btn.addEventListener('click', () => window.toggleRetweet(btn));
    });

    // Reply modal buttons
    const replyModalButtons = document.querySelectorAll('.reply-modal-button');
    replyModalButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const docId = this.id.replace('reply_modal_button_', '');
            const replyField = document.getElementById(`reply_to_item_${docId}`);
            if (replyField) window.addReply(docId, replyField.value.trim());
        });
    });

    console.log(`Interaction buttons setup: ${likeButtons.length} likes, ${retweetButtons.length} retweets, ${replyModalButtons.length} replies`);
}

function setupSubmitButton() {
    console.log("Setting up submit button...");
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function(event) {
            console.log("🚀 Submit button clicked - collecting ALL data...");

            // Collect final interaction data
            window.collectLikes();
            window.collectRetweets();

            // 🔥 NEW: Also collect any replies that might not have been captured yet
            // This catches replies where users typed but didn't click the modal Reply button
            document.querySelectorAll('[id^="reply_to_item_"]').forEach(textarea => {
                const docId = textarea.id.replace('reply_to_item_', '');
                const replyText = textarea.value.trim();

                if (replyText) {
                    // Check if this reply is already in our data
                    const existingIndex = window.repliesData.findIndex(x => x.doc_id === docId);
                    if (existingIndex !== -1) {
                        // Update existing reply
                        window.repliesData[existingIndex].reply = replyText;
                    } else {
                        // Add new reply
                        window.repliesData.push({ doc_id: docId, reply: replyText });
                    }
                    console.log(`📝 Collected reply for ${docId}: "${replyText}"`);
                }
            });

            // Prepare data for submission
            const allLikesData = window.likesData;
            const allRetweetsData = window.retweetsData;
            const allRepliesData = window.repliesData; // 🔥 NEW: Include replies data

            console.log("📊 Final data to save:");
            console.log("  - Likes:", allLikesData);
            console.log("  - Retweets:", allRetweetsData);
            console.log("  - Replies:", allRepliesData); // 🔥 NEW: Log replies

            // Find hidden input fields
            const likesField = document.querySelector('input[name="likes_data"]');
            const retweetsField = document.querySelector('input[name="retweets_data"]');
            const repliesField = document.querySelector('input[name="replies_data"]'); // 🔥 NEW: Find replies field

            console.log("Hidden fields found:");
            console.log("  - Likes field:", !!likesField);
            console.log("  - Retweets field:", !!retweetsField);
            console.log("  - Replies field:", !!repliesField); // 🔥 NEW: Check replies field

            // Populate the hidden input fields
            if (likesField) {
                likesField.value = JSON.stringify(allLikesData);
                console.log("✅ Likes field populated");
            } else {
                console.error("❌ Likes field not found!");
            }

            if (retweetsField) {
                retweetsField.value = JSON.stringify(allRetweetsData);
                console.log("✅ Retweets field populated");
            } else {
                console.error("❌ Retweets field not found!");
            }

            // 🔥 NEW: Handle replies data
            if (repliesField) {
                repliesField.value = JSON.stringify(allRepliesData);
                console.log("✅ Replies field populated with:", repliesField.value);
            } else {
                console.error("❌ Replies field not found! Make sure you have: <input type='hidden' name='replies_data' id='replies_data'>");
            }

            console.log("✅ Complete data submission preparation complete!");
        });
        console.log("✅ Enhanced submit button event listener attached");
    } else {
        console.error("❌ Submit button not found!");
    }
}

// --- Main initialization ---
onDOMReady(() => {
    console.log("🚀 DOM ready - initializing interactions...");

    setupShareButtons();
    setupReplyModals();
    setupInteractionButtons();
    setupSubmitButton();

    // Initialize data collection
    window.collectLikes();
    window.collectRetweets();

    console.log("✅ All interactions initialized successfully!");
});

console.log("interactions ready!");