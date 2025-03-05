// Weather API integration for WingFoil app
// Uses the OpenWeatherMap API to fetch wind and wave conditions

class WeatherWidget {
    constructor(apiKey = null, defaultLocation = 'Barcelona,es') {
        this.apiKey = apiKey || '3b8ec3499a7dda8d5a7a0c1a96d1d0d5'; // Demo key with limited usage
        this.defaultLocation = defaultLocation;
        this.container = null;
        this.currentLocation = defaultLocation;
    }

    async initialize(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Weather widget container not found');
            return;
        }

        // Create widget structure
        this.container.innerHTML = `
            <div class="weather-widget">
                <div class="weather-header">
                    <div class="location-info">
                        <i class="bi bi-geo-alt"></i>
                        <span class="location-name">Loading...</span>
                    </div>
                    <div class="weather-refresh">
                        <button class="btn btn-sm refresh-btn">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>
                </div>
                <div class="weather-body">
                    <div class="weather-loading">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                    <div class="weather-content" style="display: none;">
                        <div class="weather-main">
                            <div class="weather-icon">
                                <i class="bi bi-cloud"></i>
                            </div>
                            <div class="weather-temp">--°C</div>
                        </div>
                        <div class="weather-details">
                            <div class="weather-detail wind">
                                <i class="bi bi-wind"></i>
                                <span class="wind-speed">-- km/h</span>
                                <div class="wind-direction">
                                    <i class="bi bi-arrow-up"></i>
                                </div>
                            </div>
                            <div class="weather-detail waves">
                                <i class="bi bi-water"></i>
                                <span class="wave-height">-- m</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="weather-footer">
                    <span class="weather-updated">Updated: --</span>
                </div>
            </div>
        `;

        // Add event listeners
        const refreshBtn = this.container.querySelector('.refresh-btn');
        refreshBtn.addEventListener('click', () => this.fetchWeatherData());

        // Initial data fetch
        await this.fetchWeatherData();
    }

    async fetchWeatherData() {
        const loadingEl = this.container.querySelector('.weather-loading');
        const contentEl = this.container.querySelector('.weather-content');
        
        // Show loading
        loadingEl.style.display = 'flex';
        contentEl.style.display = 'none';
        
        try {
            // Fetch current weather
            const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?q=${this.currentLocation}&units=metric&appid=${this.apiKey}`;
            const weatherResponse = await fetch(weatherUrl);
            const weatherData = await weatherResponse.json();
            
            if (weatherData.cod !== 200) {
                throw new Error(weatherData.message || 'Error fetching weather data');
            }
            
            // For demo purposes, generate some wave data (OpenWeatherMap free tier doesn't include wave data)
            const waveHeight = (Math.random() * 2 + 0.2).toFixed(1);
            
            // Update UI
            this.updateWeatherUI(weatherData, waveHeight);
            
            // Hide loading, show content
            loadingEl.style.display = 'none';
            contentEl.style.display = 'block';
        } catch (error) {
            console.error('Weather API error:', error);
            
            // Show error in widget
            this.showErrorState(error.message);
            
            // Hide loading
            loadingEl.style.display = 'none';
        }
    }
    
    updateWeatherUI(data, waveHeight) {
        // Location
        this.container.querySelector('.location-name').textContent = data.name;
        
        // Temperature
        this.container.querySelector('.weather-temp').textContent = `${Math.round(data.main.temp)}°C`;
        
        // Wind
        const windSpeed = Math.round(data.wind.speed * 3.6); // Convert m/s to km/h
        this.container.querySelector('.wind-speed').textContent = `${windSpeed} km/h`;
        
        // Wind direction
        const windDirEl = this.container.querySelector('.wind-direction i');
        windDirEl.style.transform = `rotate(${data.wind.deg}deg)`;
        
        // Wave height (simulated)
        this.container.querySelector('.wave-height').textContent = `${waveHeight} m`;
        
        // Weather icon
        const iconEl = this.container.querySelector('.weather-icon i');
        const weatherCode = data.weather[0].id;
        
        // Map OpenWeatherMap icon codes to Bootstrap icons
        if (weatherCode >= 200 && weatherCode < 300) {
            iconEl.className = 'bi bi-lightning';
        } else if (weatherCode >= 300 && weatherCode < 400) {
            iconEl.className = 'bi bi-cloud-drizzle';
        } else if (weatherCode >= 500 && weatherCode < 600) {
            iconEl.className = 'bi bi-cloud-rain';
        } else if (weatherCode >= 600 && weatherCode < 700) {
            iconEl.className = 'bi bi-snow';
        } else if (weatherCode >= 700 && weatherCode < 800) {
            iconEl.className = 'bi bi-cloud-haze';
        } else if (weatherCode === 800) {
            iconEl.className = 'bi bi-sun';
        } else {
            iconEl.className = 'bi bi-cloud';
        }
        
        // Update time
        const now = new Date();
        this.container.querySelector('.weather-updated').textContent = 
            `Updated: ${now.toLocaleTimeString()}`;
    }
    
    showErrorState(message) {
        const contentEl = this.container.querySelector('.weather-content');
        contentEl.style.display = 'block';
        contentEl.innerHTML = `
            <div class="weather-error">
                <i class="bi bi-exclamation-triangle text-warning"></i>
                <p>${message || 'Unable to load weather data'}</p>
                <button class="btn btn-sm btn-primary mt-2 retry-btn">Try Again</button>
            </div>
        `;
        
        // Add retry button handler
        const retryBtn = contentEl.querySelector('.retry-btn');
        retryBtn.addEventListener('click', () => this.fetchWeatherData());
    }
    
    setLocation(location) {
        this.currentLocation = location;
        this.fetchWeatherData();
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const weatherWidgetContainer = document.getElementById('weather-widget-container');
    if (weatherWidgetContainer) {
        const widget = new WeatherWidget();
        widget.initialize('weather-widget-container');
        
        // Expose widget to global scope for debugging/manual location changes
        window.weatherWidget = widget;
    }
});
