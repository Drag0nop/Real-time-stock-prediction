// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const tickerInput = document.getElementById('ticker');
    const predictBtn = document.getElementById('predict-btn');
    const predictionBtns = document.querySelectorAll('.prediction-btn');
    const statusMessage = document.getElementById('status-message');
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    // Chart elements
    const tickerName = document.getElementById('ticker-name');
    const startPrice = document.getElementById('start-price');
    const endPrice = document.getElementById('end-price');
    const priceChange = document.getElementById('price-change');
    
    // Chart.js instance
    let predictionChart = null;
    
    // Default values
    let selectedDays = 30; // Default to 30 days
    
    // Setup prediction period buttons
    predictionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            predictionBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Update selected days
            selectedDays = parseInt(btn.dataset.days);
        });
    });
    
    // Setup predict button
    predictBtn.addEventListener('click', async () => {
        const ticker = tickerInput.value.trim().toUpperCase();
        
        if (!ticker) {
            showError('Please enter a stock ticker symbol');
            return;
        }
        
        // Reset UI
        hideError();
        showLoader('Fetching data and generating predictions...');
        hideResults();
        
        try {
            // Make API request to backend
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticker: ticker,
                    days: selectedDays
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get prediction');
            }
            
            const data = await response.json();
            
            // Process and display results
            processResults(data);
            
        } catch (error) {
            showError(error.message);
            hideLoader();
        }
    });
    
    // Function to process and display prediction results
    function processResults(data) {
        // Update ticker name
        tickerName.textContent = data.ticker;
        
        // Update summary cards
        const historicalLastPrice = data.historical[data.historical.length - 1].price;
        const predictedLastPrice = data.predictions[data.predictions.length - 1].price;
        
        startPrice.textContent = formatCurrency(historicalLastPrice);
        endPrice.textContent = formatCurrency(predictedLastPrice);
        
        // Calculate and format price change
        const changeAmount = predictedLastPrice - historicalLastPrice;
        const changePercent = (changeAmount / historicalLastPrice) * 100;
        
        priceChange.textContent = `${formatCurrency(changeAmount)} (${changePercent.toFixed(2)}%)`;
        priceChange.className = changeAmount >= 0 ? 'positive' : 'negative';
        
        // Create chart
        createChart(data);
        
        // Show results and hide loader
        hideLoader();
        showResults();
    }
    
    // Function to create the prediction chart
    function createChart(data) {
        // Format data for Chart.js
        const historicalDates = data.historical.map(item => item.date);
        const historicalPrices = data.historical.map(item => item.price);
        
        const predictionDates = data.predictions.map(item => item.date);
        const predictionPrices = data.predictions.map(item => item.price);
        
        // Create dates array for x-axis
        const allDates = [...historicalDates, ...predictionDates];
        
        // Create datasets
        const datasets = [
            {
                label: 'Historical',
                data: [...historicalPrices, null],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.1
            },
            {
                label: 'Predicted',
                data: [historicalPrices[historicalPrices.length - 1], ...predictionPrices],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.2)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.1
            }
        ];
        
        // Get chart canvas
        const ctx = document.getElementById('prediction-chart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (predictionChart) {
            predictionChart.destroy();
        }
        
        // Create new chart
        predictionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allDates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    },
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: `${data.ticker} Stock Price Prediction (${selectedDays} days)`
                    }
                }
            }
        });
    }
    
    // Helper functions
    function showLoader(message) {
        loader.style.display = 'block';
        statusMessage.textContent = message;
    }
    
    function hideLoader() {
        loader.style.display = 'none';
        statusMessage.textContent = '';
    }
    
    function showResults() {
        resultsDiv.style.display = 'block';
    }
    
    function hideResults() {
        resultsDiv.style.display = 'none';
    }
    
    function showError(message) {
        errorText.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    function hideError() {
        errorDiv.style.display = 'none';
    }
    
    function formatCurrency(value) {
        return '$' + value.toFixed(2);
    }
});