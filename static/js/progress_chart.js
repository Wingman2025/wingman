// Progress Chart for WingFoil app
// Uses Chart.js to visualize user progress

class ProgressChart {
    constructor(canvasId, skillContainerId) {
        this.canvas = document.getElementById(canvasId);
        this.skillContainer = document.getElementById(skillContainerId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.chart = null;
        this.timeRange = 'month'; // Default time range
        this.chartData = {
            labels: [],
            datasets: []
        };
        this.mockData = this.generateMockData();
    }

    initialize() {
        if (!this.ctx) {
            console.error('Canvas context not available');
            return;
        }

        // Process the data
        this.processData(this.mockData);
        
        // Create the chart
        this.createChart();
        
        // Set up event listeners for filter buttons
        this.setupEventListeners();
        
        // Update skill progress bars
        this.updateSkillProgress();
    }
    
    generateMockData() {
        // Generate mock data for demonstration
        const now = new Date();
        const mockData = [];
        
        // Generate sessions for the past 30 days
        for (let i = 0; i < 15; i++) {
            const date = new Date();
            date.setDate(now.getDate() - Math.floor(Math.random() * 30));
            
            mockData.push({
                id: i + 1,
                date: date.toISOString().split('T')[0],
                duration: Math.floor(Math.random() * 90) + 30,
                rating: Math.floor(Math.random() * 5) + 1,
                skills: JSON.stringify(['Water Start', 'Tack', 'Jibe'].slice(0, Math.floor(Math.random() * 3) + 1)),
                skill_ratings: JSON.stringify({
                    'Water Start': Math.floor(Math.random() * 5) + 1,
                    'Tack': Math.floor(Math.random() * 5) + 1,
                    'Jibe': Math.floor(Math.random() * 5) + 1
                })
            });
        }
        
        return mockData;
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
                        totalSkills += Array.isArray(skills) ? skills.length : Object.keys(skills).length;
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
            case 'quarter':
                startDate.setMonth(now.getMonth() - 3);
                break;
            case 'year':
                startDate.setFullYear(now.getFullYear() - 1);
                break;
            case 'all':
                startDate.setFullYear(now.getFullYear() - 3);
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
                    title: {
                        display: true,
                        text: 'Training Progress'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Add event listeners to time range buttons
        const timeRangeButtons = document.querySelectorAll('.time-range-btn');
        
        timeRangeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Remove active class from all buttons
                timeRangeButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                e.target.classList.add('active');
                
                // Update time range
                this.timeRange = e.target.dataset.range;
                
                // Update chart
                this.processData(this.mockData);
                this.createChart();
            });
        });
    }
    
    updateSkillProgress() {
        if (!this.skillContainer) return;
        
        // Calculate skill progress from mock data
        const skillProgress = this.calculateSkillProgress(this.mockData);
        
        // Sort skills by progress
        const sortedSkills = Object.entries(skillProgress)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);
        
        // Clear container
        this.skillContainer.innerHTML = '';
        
        // Add skill progress bars
        sortedSkills.forEach(([skill, progress]) => {
            const progressPercentage = Math.min(100, Math.round(progress * 20)); // Scale 1-5 rating to percentage
            
            const colorClass = progressPercentage >= 80 ? 'bg-success' : 
                              progressPercentage >= 60 ? 'bg-info' : 
                              progressPercentage >= 40 ? 'bg-primary' : 
                              progressPercentage >= 20 ? 'bg-warning' : 'bg-danger';
            
            const skillElement = document.createElement('div');
            skillElement.className = 'skill-progress';
            skillElement.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>${skill}</span>
                    <span>${progressPercentage}%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar ${colorClass}" role="progressbar" 
                         style="width: ${progressPercentage}%" 
                         aria-valuenow="${progressPercentage}" 
                         aria-valuemin="0" 
                         aria-valuemax="100"></div>
                </div>
            `;
            
            this.skillContainer.appendChild(skillElement);
        });
    }
    
    calculateSkillProgress(sessionsData) {
        const skillProgress = {};
        
        sessionsData.forEach(session => {
            if (session.skill_ratings) {
                try {
                    const ratings = typeof session.skill_ratings === 'string' 
                        ? JSON.parse(session.skill_ratings) 
                        : session.skill_ratings;
                    
                    Object.entries(ratings).forEach(([skill, rating]) => {
                        if (!skillProgress[skill]) {
                            skillProgress[skill] = 0;
                        }
                        
                        // Accumulate ratings
                        skillProgress[skill] += rating;
                    });
                } catch (e) {
                    console.error('Error parsing skill ratings:', e);
                }
            }
        });
        
        // Calculate average ratings
        Object.keys(skillProgress).forEach(skill => {
            skillProgress[skill] = skillProgress[skill] / sessionsData.length;
        });
        
        return skillProgress;
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const progressChartCanvas = document.getElementById('progress-chart');
    const skillContainer = document.getElementById('skill-progress-container');
    if (progressChartCanvas && skillContainer && typeof Chart !== 'undefined') {
        // Check if we have sessions data in the global scope
        if (window.sessionsData) {
            const chart = new ProgressChart('progress-chart', 'skill-progress-container');
            chart.initialize();
            
            // Expose chart to global scope for debugging
            window.progressChart = chart;
        }
    }
});
