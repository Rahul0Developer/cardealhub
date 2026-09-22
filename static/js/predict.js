document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('prediction-form');
    const companySelect = document.getElementById('company');
    const carModelSelect = document.getElementById('car_model');
    const yearSelect = document.getElementById('year');
    const kmsInput = document.getElementById('kms_driven');
    const fuelTypeSelect = document.getElementById('fuel_type');
    const resultContainer = document.getElementById('prediction-result');
    const submitButton = document.getElementById('submit-prediction');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Update car models based on selected company
    if (companySelect && carModelSelect) {
        companySelect.addEventListener('change', function() {
            const selectedCompany = companySelect.value;
            
            // Clear current options
            carModelSelect.innerHTML = '<option value="">Select Model</option>';
            
            if (selectedCompany) {
                // Show loading state
                carModelSelect.disabled = true;
                
                // Fetch car models for selected company
                fetch(`/api/car-models?brand=${selectedCompany}`)
                    .then(response => response.json())
                    .then(models => {
                        // Add new options
                        models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            carModelSelect.appendChild(option);
                        });
                        
                        // Enable select
                        carModelSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching car models:', error);
                        carModelSelect.disabled = false;
                    });
            }
        });
    }
    
    // Handle form submission
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (!validatePredictionForm()) {
                return;
            }
            
            // Show loading state
            if (submitButton && loadingIndicator) {
                submitButton.disabled = true;
                loadingIndicator.classList.remove('hidden');
            }
            
            // Get form data
            const formData = new FormData(predictionForm);
            
            // Send prediction request
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    // Hide loading state
                    if (submitButton && loadingIndicator) {
                        submitButton.disabled = false;
                        loadingIndicator.classList.add('hidden');
                    }
                    
                    // Display prediction result
                    displayPredictionResult(data);
                })
                .catch(error => {
                    console.error('Error making prediction:', error);
                    
                    // Hide loading state
                    if (submitButton && loadingIndicator) {
                        submitButton.disabled = false;
                        loadingIndicator.classList.add('hidden');
                    }
                    
                    // Show error message
                    if (resultContainer) {
                        resultContainer.innerHTML = `
                            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                                <p>Sorry, there was an error making your prediction. Please try again.</p>
                            </div>
                        `;
                        resultContainer.classList.remove('hidden');
                    }
                });
        });
    }
    
    // Validate prediction form
    function validatePredictionForm() {
        let isValid = true;
        const errorMessages = document.querySelectorAll('.error-message');
        
        // Clear previous error messages
        errorMessages.forEach(message => message.remove());
        
        // Validate company
        if (!companySelect.value) {
            showError(companySelect, 'Please select a car brand');
            isValid = false;
        }
        
        // Validate car model
        if (!carModelSelect.value) {
            showError(carModelSelect, 'Please select a car model');
            isValid = false;
        }
        
        // Validate year
        if (!yearSelect.value) {
            showError(yearSelect, 'Please select a year');
            isValid = false;
        }
        
        // Validate kilometers driven
        if (!kmsInput.value) {
            showError(kmsInput, 'Please enter kilometers driven');
            isValid = false;
        } else if (isNaN(kmsInput.value) || parseInt(kmsInput.value) < 0) {
            showError(kmsInput, 'Please enter a valid number for kilometers driven');
            isValid = false;
        }
        
        // Validate fuel type
        if (!fuelTypeSelect.value) {
            showError(fuelTypeSelect, 'Please select a fuel type');
            isValid = false;
        }
        
        return isValid;
    }
    
    // Show error message for form field
    function showError(element, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        element.parentNode.appendChild(errorDiv);
    }
    
    // Display prediction result
    function displayPredictionResult(data) {
        if (resultContainer) {
            const predictedPrice = data.predicted_price;
            const carDetails = data.car_details;
            const modelPredictions = data.model_predictions || {};
            const chartData = data.chart_data || {};
            const availableModels = data.available_models || [];
            const modelUsed = data.model_used || 'xgboost';
            
            // Create model comparison HTML
            let modelComparisonHTML = '';
            if (Object.keys(modelPredictions).length > 0) {
                modelComparisonHTML = `
                    <div class="mt-6">
                        <h4 class="text-lg font-semibold mb-3">Model Comparison</h4>
                        <div class="grid grid-cols-1 md:grid-cols-${Math.min(4, availableModels.length)} gap-4">
                `;
                
                // Add current model
                modelComparisonHTML += `
                    <div class="bg-primary bg-opacity-10 border border-primary rounded p-3 text-center">
                        <p class="text-sm font-medium">${modelUsed.replace('_', ' ').toUpperCase()}</p>
                        <p class="text-lg font-bold">₹${predictedPrice.toLocaleString('en-IN')}</p>
                        <p class="text-xs">(Selected)</p>
                    </div>
                `;
                
                // Add other models
                for (const [name, price] of Object.entries(modelPredictions)) {
                    modelComparisonHTML += `
                        <div class="bg-gray-50 border rounded p-3 text-center">
                            <p class="text-sm font-medium">${name.replace('_', ' ').toUpperCase()}</p>
                            <p class="text-lg font-bold">₹${price.toLocaleString('en-IN')}</p>
                        </div>
                    `;
                }
                
                modelComparisonHTML += `
                        </div>
                    </div>
                `;
            }
            
            // Create charts HTML
            const chartsHTML = `
                <div class="mt-6">
                    <h4 class="text-lg font-semibold mb-3">Price Analysis</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 class="text-sm font-medium mb-2">Average Price by Year</h5>
                            <div class="bg-white border rounded p-3 h-64">
                                <canvas id="yearPriceChart"></canvas>
                            </div>
                        </div>
                        <div>
                            <h5 class="text-sm font-medium mb-2">Price Comparison by Model</h5>
                            <div class="bg-white border rounded p-3 h-64">
                                <canvas id="modelPriceChart"></canvas>
                            </div>
                        </div>
                        <div class="md:col-span-2">
                            <h5 class="text-sm font-medium mb-2">Kilometers vs Price (Scatter Plot)</h5>
                            <div class="bg-white border rounded p-3 h-64">
                                <canvas id="scatterChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            resultContainer.innerHTML = `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 prediction-result">
                    <h3 class="text-xl font-bold text-gray-900 mb-4">Estimated Price</h3>
                    <div class="flex justify-center mb-6">
                        <div class="text-3xl md:text-4xl font-bold text-primary">₹${predictedPrice.toLocaleString('en-IN')}</div>
                    </div>
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div>
                            <p class="text-sm text-gray-500">Brand</p>
                            <p class="font-medium">${carDetails.company}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Model</p>
                            <p class="font-medium">${carDetails.model}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Year</p>
                            <p class="font-medium">${carDetails.year}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Kilometers Driven</p>
                            <p class="font-medium">${carDetails.kms_driven.toLocaleString('en-IN')} km</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Fuel Type</p>
                            <p class="font-medium">${carDetails.fuel_type}</p>
                        </div>
                    </div>
                    
                    ${modelComparisonHTML}
                    
                    ${Object.keys(chartData).length > 0 ? chartsHTML : ''}
                    
                    <div class="mt-6">
                        <p class="text-sm text-gray-500 mb-4">This is an estimated market value based on similar cars in our database. Actual selling price may vary based on additional factors like car condition, features, and market demand.</p>
                        <div class="flex gap-4">
                            <button class="bg-primary text-white px-4 py-2 rounded-button" onclick="window.print()">Print Report</button>
                            <button class="bg-white text-primary border border-primary px-4 py-2 rounded-button" onclick="document.getElementById('prediction-form').reset()">New Prediction</button>
                        </div>
                    </div>
                </div>
            `;
            
            resultContainer.classList.remove('hidden');
            resultContainer.scrollIntoView({ behavior: 'smooth' });
            
            // Initialize charts if chart data is available
            if (chartData && Object.keys(chartData).length > 0) {
                setTimeout(() => {
                    initializeCharts(chartData);
                }, 100);
            }
        }
    }
    
    // Initialize charts with the provided data
    function initializeCharts(chartData) {
        // Year Price Line Chart
        if (chartData.year_price && document.getElementById('yearPriceChart')) {
            const ctx = document.getElementById('yearPriceChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.year_price.categories,
                    datasets: [{
                        label: 'Average Price (₹)',
                        data: chartData.year_price.values,
                        borderColor: '#4F46E5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return '₹' + context.parsed.y.toLocaleString('en-IN');
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + (value/1000) + 'K';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Model Price Bar Chart
        if (chartData.model_price && document.getElementById('modelPriceChart')) {
            const ctx = document.getElementById('modelPriceChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.model_price.categories,
                    datasets: [{
                        label: 'Average Price (₹)',
                        data: chartData.model_price.values,
                        backgroundColor: 'rgba(79, 70, 229, 0.7)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return '₹' + context.parsed.y.toLocaleString('en-IN');
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + (value/1000) + 'K';
                                }
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    }
                }
            });
        }
        
        // Scatter Plot (Kilometers vs Price)
        if (chartData.scatter_data && document.getElementById('scatterChart')) {
            const ctx = document.getElementById('scatterChart').getContext('2d');
            const scatterData = [];
            
            // Prepare scatter plot data points
            for (let i = 0; i < chartData.scatter_data.x.length; i++) {
                scatterData.push({
                    x: chartData.scatter_data.x[i],
                    y: chartData.scatter_data.y[i],
                    name: chartData.scatter_data.names[i]
                });
            }
            
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Kilometers vs Price',
                        data: scatterData,
                        backgroundColor: 'rgba(79, 70, 229, 0.7)',
                        borderColor: '#4F46E5',
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const point = context.raw;
                                    return [
                                        point.name,
                                        'Price: ₹' + point.y.toLocaleString('en-IN'),
                                        'Kilometers: ' + point.x.toLocaleString('en-IN')
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Price (₹)'
                            },
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + (value/1000) + 'K';
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Kilometers Driven'
                            },
                            ticks: {
                                callback: function(value) {
                                    return (value/1000) + 'K';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
});
