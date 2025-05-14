function reorderPlotPoint(plotpointId, direction) {
    const csrfToken = '{{ csrf_token }}';
    
    fetch("{% url 'plotpoint_reorder' project.id %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `plotpoint_id=${plotpointId}&direction=${direction}`
    })
    .then(response => {
        if (response.ok) {
            // Reload only the plotpoints section
            const plotpointsSection = document.querySelector('.plotpoints-list').parentElement;
            fetch(window.location.href)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newPlotpointsSection = doc.querySelector('.plotpoints-list').parentElement;
                    plotpointsSection.innerHTML = newPlotpointsSection.innerHTML;
                });
        }
    });
}