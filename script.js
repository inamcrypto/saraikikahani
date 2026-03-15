// ============================================
// Saraiki Bal Kahani - JavaScript
// Children's Story Website Functionality
// ============================================

// Global State
let stories = [];
let currentStory = null;
let currentPage = 0;

// DOM Elements
const storiesGrid = document.getElementById('storiesGrid');
const storyModal = document.getElementById('storyModal');
const readerTitle = document.getElementById('readerTitle');
const readerContent = document.getElementById('readerContent');
const readerCategory = document.getElementById('readerCategory');
const pageIndicator = document.getElementById('pageIndicator');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const filterBtns = document.querySelectorAll('.filter-btn');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');

// Category Labels in Saraiki
const categoryLabels = {
    animal: 'جانور',
    moral: 'اخلاق',
    folk: 'لوک کہانی'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStories();
    setupEventListeners();
});

// Load Stories from JSON
async function loadStories() {
    try {
        const response = await fetch('stories.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        stories = data.stories;
    } catch (error) {
        console.error('Error loading stories:', error);

        if (window.STORIES_DATA?.stories?.length) {
            stories = window.STORIES_DATA.stories;
        } else {
            storiesGrid.innerHTML = '<p class="error">کہانیاں لود نہیں ہو سکیاں۔</p>';
            return;
        }
    }

    renderStories(stories);
}

// Render Stories to Grid
function renderStories(storiesToRender) {
    storiesGrid.innerHTML = '';

    if (storiesToRender.length === 0) {
        storiesGrid.innerHTML = '<p class="no-stories">ایہہ زمرے وچ کوئی کہانی نہیں۔</p>';
        return;
    }

    storiesToRender.forEach(story => {
        const card = createStoryCard(story);
        storiesGrid.appendChild(card);
    });
}

// Create Story Card Element
function createStoryCard(story) {
    const card = document.createElement('div');
    card.className = `story-card ${story.category}`;
    card.dataset.id = story.id;

    card.innerHTML = `
        <div class="story-cover">
            <span class="story-emoji">${story.emoji}</span>
        </div>
        <div class="story-info">
            <span class="story-category">${categoryLabels[story.category]}</span>
            <h3 class="story-title">${story.title}</h3>
            <p class="story-description">${story.description}</p>
            <button class="story-btn">
                <span>📖</span>
                <span>پڑھو</span>
            </button>
        </div>
    `;

    card.addEventListener('click', () => openStory(story));

    return card;
}

// Open Story Reader
function openStory(story) {
    currentStory = story;
    currentPage = 0;

    readerTitle.textContent = story.title;
    readerCategory.textContent = categoryLabels[story.category];

    updateReaderContent();
    storyModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Format story text with simple bold markup and visible line breaks.
function formatStoryText(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function getStoryPageImage(story, index) {
    if (!Array.isArray(story.pageImages)) {
        return null;
    }

    return story.pageImages[index] || null;
}

// Update Reader Content
function updateReaderContent() {
    const paragraphs = currentStory.content;

    // Create page elements with optional artwork.
    readerContent.innerHTML = paragraphs.map((text, index) => {
        const isCurrentPage = index === currentPage;
        const pageImage = getStoryPageImage(currentStory, index);
        const imageMarkup = pageImage ? `
            <figure class="reader-page-image">
                <img src="${pageImage.src}" alt="${pageImage.alt}">
            </figure>
        ` : '';
        const pageClass = pageImage ? 'reader-page has-image' : 'reader-page';

        return `
            <div class="${pageClass}" style="display: ${isCurrentPage ? 'block' : 'none'};">
                <p>${formatStoryText(text)}</p>
                ${imageMarkup}
            </div>
        `;
    }).join('');

    // Update page indicator
    pageIndicator.textContent = `${currentPage + 1} / ${paragraphs.length}`;

    // Update button states
    prevBtn.disabled = currentPage === 0;
    nextBtn.disabled = currentPage === paragraphs.length - 1;
}

// Close Story Reader
function closeStory() {
    storyModal.classList.remove('active');
    document.body.style.overflow = '';
    currentStory = null;
    currentPage = 0;
}

// Navigation Functions
function goToPrevPage() {
    if (currentPage > 0) {
        currentPage--;
        updateReaderContent();
    }
}

function goToNextPage() {
    if (currentStory && currentPage < currentStory.content.length - 1) {
        currentPage++;
        updateReaderContent();
    }
}

// Filter Stories by Category
function filterStories(category) {
    if (category === 'all') {
        renderStories(stories);
    } else {
        const filtered = stories.filter(story => story.category === category);
        renderStories(filtered);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Mobile Menu Toggle
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Filter Buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterStories(btn.dataset.category);
        });
    });

    // Modal Close
    document.querySelector('.modal-close').addEventListener('click', closeStory);
    document.querySelector('.modal-overlay').addEventListener('click', closeStory);

    // Navigation Buttons
    prevBtn.addEventListener('click', goToPrevPage);
    nextBtn.addEventListener('click', goToNextPage);

    // Keyboard Navigation
    document.addEventListener('keydown', (e) => {
        if (!storyModal.classList.contains('active')) return;

        if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
            goToPrevPage();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
            goToNextPage();
        } else if (e.key === 'Escape') {
            closeStory();
        }
    });

    // Smooth Scroll for Navigation Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }

            // Close mobile menu if open
            navLinks.classList.remove('active');

            // Update active nav link
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Navbar Scroll Effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        }
    });
}
