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
const modalContent = document.querySelector('.modal-content');
const readerTitle = document.getElementById('readerTitle');
const readerContent = document.getElementById('readerContent');
const readerCategory = document.getElementById('readerCategory');
const pageIndicator = document.getElementById('pageIndicator');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const filterBtns = document.querySelectorAll('.filter-btn');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');
const storiesSchema = document.getElementById('storiesSchema');

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

    updateStoriesSchema(stories);
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
    const card = document.createElement('article');
    const categoryLabel = categoryLabels[story.category] || story.category;
    const storyTitleId = `story-title-${story.id}`;
    const storyDescriptionId = `story-description-${story.id}`;

    card.className = `story-card ${story.category}`;
    card.dataset.id = story.id;
    card.setAttribute('aria-labelledby', storyTitleId);
    card.setAttribute('aria-describedby', storyDescriptionId);

    card.innerHTML = `
        <div class="story-cover">
            <span class="story-emoji">${story.emoji}</span>
        </div>
        <div class="story-info">
            <span class="story-category">${categoryLabel}</span>
            <h3 class="story-title" id="${storyTitleId}">${story.title}</h3>
            <p class="story-description" id="${storyDescriptionId}">${story.description}</p>
            <button class="story-btn" type="button" aria-label="Read ${story.title}">
                <span>📖</span>
                <span>پڑھو</span>
            </button>
        </div>
    `;

    card.addEventListener('click', () => openStory(story));

    return card;
}

function updateStoriesSchema(storiesToDescribe) {
    if (!storiesSchema) {
        return;
    }

    const schema = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'CollectionPage',
                name: 'Saraiki Kids Stories',
                description: 'Read Saraiki kids stories, Saraiki bedtime stories, and moral stories for children.',
                inLanguage: ['skr', 'en'],
                about: [
                    'Saraiki kids stories',
                    'Saraiki bedtime stories',
                    'Saraiki moral stories',
                    'Saraiki folk stories'
                ],
                numberOfItems: storiesToDescribe.length,
                hasPart: storiesToDescribe.map((story, index) => ({
                    '@type': 'CreativeWork',
                    position: index + 1,
                    name: story.title,
                    description: story.description,
                    genre: categoryLabels[story.category] || story.category,
                    inLanguage: 'skr'
                }))
            },
            {
                '@type': 'FAQPage',
                inLanguage: 'en',
                mainEntity: [
                    {
                        '@type': 'Question',
                        name: 'What kind of Saraiki kids stories can I read here?',
                        acceptedAnswer: {
                            '@type': 'Answer',
                            text: 'You can read Saraiki bedtime stories, folk stories, and moral stories for children, all written in a simple and friendly style.'
                        }
                    },
                    {
                        '@type': 'Question',
                        name: 'Are these Saraiki children stories good for bedtime reading?',
                        acceptedAnswer: {
                            '@type': 'Answer',
                            text: 'Yes. The current collection is short, gentle, and easy for parents to read aloud during bedtime or quiet reading time.'
                        }
                    },
                    {
                        '@type': 'Question',
                        name: 'Does the site include Saraiki moral stories for kids?',
                        acceptedAnswer: {
                            '@type': 'Answer',
                            text: 'Yes. Some stories focus on friendship, kindness, courage, and small life lessons that work well for young readers.'
                        }
                    },
                    {
                        '@type': 'Question',
                        name: 'Who are Saraiki kids stories on this site for?',
                        acceptedAnswer: {
                            '@type': 'Answer',
                            text: 'The site is designed for children, parents, and teachers who want simple Saraiki reading material and enjoyable story time.'
                        }
                    }
                ]
            }
        ]
    };

    storiesSchema.textContent = JSON.stringify(schema);
}

// Open Story Reader
function openStory(story) {
    currentStory = story;
    currentPage = 0;
    modalContent.dataset.storyId = String(story.id);

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
        const useEnhancedStoryLayout = true;
        const imageMarkup = pageImage ? `
            <figure class="reader-page-image">
                <img src="${pageImage.src}" alt="${pageImage.alt}">
            </figure>
        ` : '';
        const pageClass = [
            'reader-page',
            pageImage ? 'has-image' : '',
            useEnhancedStoryLayout ? 'mobile-story-page' : ''
        ].filter(Boolean).join(' ');
        const textMarkup = `
            <div class="reader-page-text-wrap">
                ${useEnhancedStoryLayout ? `<span class="reader-page-chip">صفحہ ${index + 1}</span>` : ''}
                <p>${formatStoryText(text)}</p>
            </div>
        `;

        return `
            <div class="${pageClass}" style="display: ${isCurrentPage ? 'block' : 'none'};">
                ${imageMarkup}${textMarkup}
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
    delete modalContent.dataset.storyId;
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




