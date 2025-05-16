document.addEventListener('DOMContentLoaded', function() {
    // Place form improve description button
    const improveButton = document.getElementById('improve-description');
    if (improveButton) {
        improveButton.addEventListener('click', function() {
            improve({
                buttonId: 'improve-description',
                statusId: 'improvement-status',
                textareaId: 'description',
                endpoint: '/ai/improve-place-description/',
                successProperty: 'improved_description',
                successMessage: 'Description improved successfully!'
            });
        });
    }
    
    // Organization form improve purpose button
    const improveOrgButton = document.getElementById('improve-organization');
    if (improveOrgButton) {
        improveOrgButton.addEventListener('click', function() {
            improve({
                buttonId: 'improve-organization',
                statusId: 'improvement-status',
                textareaId: 'notes',
                endpoint: '/ai/improve-organization-description/',
                successProperty: 'improved_description',
                successMessage: 'Notes improved successfully!'
            });
        });
    }
    
    // Character form improve bio button
    const improveBioButton = document.getElementById('improve-bio');
    if (improveBioButton) {
        improveBioButton.addEventListener('click', function() {
            improve({
                buttonId: 'improve-bio',
                statusId: 'improvement-status',
                textareaId: 'bio',
                endpoint: '/ai/improve-character-bio/',
                successProperty: 'improved_bio',
                successMessage: 'Bio improved successfully!'
            });
        });
    }
});

async function improve(config) {
    const statusDiv = document.getElementById(config.statusId);
    const improveButton = document.getElementById(config.buttonId);
    const textarea = document.getElementById(config.textareaId);
    const projectId = improveButton.dataset.projectId;
    const itemId = improveButton.dataset.placeId || improveButton.dataset.organizationId || improveButton.dataset.characterId;
    
    try {
        statusDiv.textContent = 'Improving...';
        statusDiv.className = 'improvement-status loading';
        improveButton.disabled = true;
        
        const response = await fetch(`${config.endpoint}${projectId}/${itemId}/`);
        const data = await response.json();
        
        if (data.status === 'success') {
            textarea.value = data[config.successProperty];
            statusDiv.textContent = config.successMessage;
            statusDiv.className = 'improvement-status success';
        } else {
            throw new Error(data.message || 'Failed to improve content');
        }
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'improvement-status error';
    } finally {
        improveButton.disabled = false;
    }
}
