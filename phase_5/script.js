document.addEventListener('DOMContentLoaded', () => {
    // State management
    const state = {
        localities: [],
        cuisines: []
    };

    // DOM Elements
    const form = document.getElementById('recommendation-form');
    const priceRange = document.getElementById('price-range');
    const priceDisplay = document.getElementById('price-display');
    const minRating = document.getElementById('min-rating');
    const ratingDisplay = document.getElementById('rating-display');
    const localitySelect = document.getElementById('locality');
    const cuisineSelect = document.getElementById('cuisine');

    const resultsSection = document.getElementById('results-section');
    const resultsGrid = document.getElementById('results-grid');
    const resultsCount = document.getElementById('results-count');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');

    // Update range displays
    priceRange.addEventListener('input', () => {
        priceDisplay.textContent = `₹${priceRange.value}`;
    });

    minRating.addEventListener('input', () => {
        ratingDisplay.textContent = minRating.value;
    });

    // Initialize Metadata
    async function initMetadata() {
        try {
            const [locRes, cuiRes] = await Promise.all([
                fetch('/meta/localities'),
                fetch('/meta/cuisines')
            ]);

            const locData = await locRes.json();
            const cuiData = await cuiRes.json();

            state.localities = locData.localities;
            state.cuisines = cuiData.cuisines;

            populateSelect(localitySelect, state.localities);
            populateSelect(cuisineSelect, state.cuisines);
        } catch (error) {
            console.error('Failed to load metadata:', error);
        }
    }

    function populateSelect(selectEl, items) {
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            selectEl.appendChild(option);
        });
    }

    // Handle Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI States
        errorSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');

        const payload = {
            max_price: parseFloat(priceRange.value),
            min_rating: parseFloat(minRating.value),
            locality: localitySelect.value || null,
            desired_cuisines: cuisineSelect.value ? [cuisineSelect.value] : null
        };

        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to get recommendations');
            }

            const data = await response.json();
            renderResults(data.recommendations);
        } catch (error) {
            showError(error.message);
        } finally {
            loadingSection.classList.add('hidden');
        }
    });

    function renderResults(recommendations) {
        resultsGrid.innerHTML = '';

        if (!recommendations || recommendations.length === 0) {
            resultsCount.textContent = '0 restaurants found';
            showError('No restaurants found matching your criteria. Try adjusting the filters.');
            return;
        }

        resultsCount.textContent = `${recommendations.length} restaurants found`;

        recommendations.forEach(item => {
            const res = item.restaurant;
            const card = document.createElement('div');
            card.className = 'restaurant-card';

            const cuisinesList = res.cuisines.split(',').map(c => c.trim());
            const cuisineHtml = cuisinesList.map(c => `<span class="cuisine-pill">${c}</span>`).join('');

            card.innerHTML = `
                <div class="card-header">
                    <div>
                        <h3 class="res-name">${res.name}</h3>
                        <div class="res-location">
                            <i class="fa-solid fa-location-dot"></i> ${res.location}
                        </div>
                    </div>
                    <div class="rating-badge">
                        ${res.rating} <span style="font-size: 0.7em">★</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="res-cuisines-pills">
                        ${cuisineHtml}
                    </div>
                    <div class="res-stats">
                        <div class="stat-item">
                            <span class="stat-label">Price for two</span>
                            <span class="stat-value">₹${res.price_for_two}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Votes</span>
                            <span class="stat-value">${res.votes.toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="ai-reason">
                        "${item.reason}"
                    </div>
                </div>
            `;
            resultsGrid.appendChild(card);
        });

        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorSection.classList.remove('hidden');
    }

    // Run initialization
    initMetadata();
});
