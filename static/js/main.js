// Add a from_json filter to Jinja2
if (typeof JSON.parse !== 'function') {
    JSON.parse = function(str) {
        return eval('(' + str + ')');
    };
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
