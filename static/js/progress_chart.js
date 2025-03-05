// Progress Chart for WingFoil app
// Uses Chart.js to visualize user progress

class ProgressChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.chart = null;
        this.timeRange = 'month'; // Default time range
        this.chartData = {
            labels: [],
            datasets: []
        };
    }

    initialize(sessionsData) {
        if (!this.ctx) {
            console.error('Canvas context not available');
            return;
        }

        // Process the data
        this.processData(sessionsData);
        
        // Create the chart
        this.createChart();
        
        // Set up event listeners for filter buttons
        this.setupEventListeners();
    }
    
    processData(sessionsData) {
        // Group sessions by date
        const groupedSessions = this.groupSessionsByDate(sessionsData);
        
        // Generate labels and datasets based on time range
        this.generateChartData(groupedSessions);
    }
    
    groupSessionsByDate(sessions) {
        const grouped = {};
        
        sessions.forEach(session => {
            // Ensure date is in YYYY-MM-DD format
            let dateKey;
            try {
                const date = new Date(session.date);
                if (isNaN(date.getTime())) {
                    // If date is invalid, use the string directly
                    dateKey = session.date;
                } else {
                    // Format as YYYY-MM-DD
                    dateKey = date.toISOString().split('T')[0];
                }
            } catch (e) {
                // Fallback to using the string directly
                dateKey = session.date;
                console.error('Error parsing date:', e);
            }
            
            if (!grouped[dateKey]) {
                grouped[dateKey] = [];
            }
            
            grouped[dateKey].push(session);
        });
        
        return grouped;
    }
    
    generateChartData(groupedSessions) {
        // Get date range based on selected time range
        const { startDate, endDate } = this.getDateRange();
        
        // Generate all dates in the range
        const allDates = this.generateDateRange(startDate, endDate);
        
        // Prepare labels (dates)
        this.chartData.labels = allDates.map(date => {
            const d = new Date(date);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        // Prepare datasets
        const sessionCounts = allDates.map(date => {
            return groupedSessions[date] ? groupedSessions[date].length : 0;
        });
        
        const avgRatings = allDates.map(date => {
            if (!groupedSessions[date] || groupedSessions[date].length === 0) {
                return 0;
            }
            
            const sum = groupedSessions[date].reduce((acc, session) => acc + session.rating, 0);
            return sum / groupedSessions[date].length;
        });
        
        const skillCounts = allDates.map(date => {
            if (!groupedSessions[date] || groupedSessions[date].length === 0) {
                return 0;
            }
            
            let totalSkills = 0;
            groupedSessions[date].forEach(session => {
                if (session.skills) {
                    try {
                        const skills = typeof session.skills === 'string' 
                            ? JSON.parse(session.skills) 
                            : session.skills;
                        totalSkills += Object.keys(skills).length;
                    } catch (e) {
                        console.error('Error parsing skills:', e);
                    }
                }
            });
            
            return totalSkills;
        });
        
        // Create datasets
        this.chartData.datasets = [
            {
                label: 'Sessions',
                data: sessionCounts,
                backgroundColor: 'rgba(0, 150, 199, 0.2)',
                borderColor: 'rgba(0, 150, 199, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            },
            {
                label: 'Avg. Rating',
                data: avgRatings,
                backgroundColor: 'rgba(255, 183, 3, 0.2)',
                borderColor: 'rgba(255, 183, 3, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                hidden: true
            },
            {
                label: 'Skills Practiced',
                data: skillCounts,
                backgroundColor: 'rgba(255, 107, 53, 0.2)',
                borderColor: 'rgba(255, 107, 53, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }
        ];
    }
    
    getDateRange() {
        const now = new Date();
        let startDate = new Date();
        
        switch (this.timeRange) {
            case 'week':
                startDate.setDate(now.getDate() - 7);
                break;
            case 'month':
                startDate.setMonth(now.getMonth() - 1);
                break;
            case 'year':
                startDate.setFullYear(now.getFullYear() - 1);
                break;
            default:
                startDate.setMonth(now.getMonth() - 1);
        }
        
        return {
            startDate: startDate.toISOString().split('T')[0],
            endDate: now.toISOString().split('T')[0]
        };
    }
    
    generateDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const dates = [];
        
        let current = new Date(start);
        
        while (current <= end) {
            dates.push(current.toISOString().split('T')[0]);
            current.setDate(current.getDate() + 1);
        }
        
        return dates;
    }
    
    createChart() {
        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Create new chart
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: this.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                
                                if (context.parsed.y !== null) {
                                    if (label.includes('Rating')) {
                                        label += context.parsed.y.toFixed(1) + ' / 5';
                                    } else {
                                        label += context.parsed.y;
                                    }
                                }
                                
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 5
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        const timeRangeButtons = document.querySelectorAll('.time-range-btn');
        
        timeRangeButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active state
                timeRangeButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update time range
                this.timeRange = button.getAttribute('data-range');
                
                // Fetch new data or update existing data
                const sessionsData = this.getSessionsData();
                this.processData(sessionsData);
                
                // Update chart
                this.chart.data = this.chartData;
                this.chart.update();
            });
        });
    }
    
    getSessionsData() {
        // This function should be overridden to get the actual sessions data
        // For demo purposes, we'll return the data that was passed to initialize()
        return window.sessionsData || [];
    }
    
    // Method to update chart with new data
    updateData(sessionsData) {
        this.processData(sessionsData);
        if (this.chart) {
            this.chart.data = this.chartData;
            this.chart.update();
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const progressChartCanvas = document.getElementById('progress-chart');
    if (progressChartCanvas && typeof Chart !== 'undefined') {
        // Check if we have sessions data in the global scope
        if (window.sessionsData) {
            const chart = new ProgressChart('progress-chart');
            chart.initialize(window.sessionsData);
            
            // Expose chart to global scope for debugging
            window.progressChart = chart;
        }
    }
});
