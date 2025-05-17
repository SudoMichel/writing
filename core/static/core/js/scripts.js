document.addEventListener('DOMContentLoaded', function() {
    // Place form improve description button
    const improveButton = document.getElementById('improve-description');
    if (improveButton) {
        improveButton.addEventListener('click', function() {
            improve({
                buttonId: 'improve-description',
                statusId: 'improvement-status',
                textareaId: 'id_description',
                endpoint: '/ai/improve/place/',
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
                textareaId: 'id_description',
                endpoint: '/ai/improve/organization/',
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
                textareaId: 'id_description',
                endpoint: '/ai/improve/character/',
                successProperty: 'improved_bio',
                successMessage: 'Bio improved successfully!'
            });
        });
    }

    // Chapter form write chapter button
    const writeChapterButton = document.getElementById('write-chapter');
    if (writeChapterButton) {
        writeChapterButton.addEventListener('click', function() {
            improve({
                buttonId: 'write-chapter',
                statusId: 'chapter-writing-status',
                textareaId: 'id_content', // Assuming the content textarea has id 'id_content'
                endpoint: '/ai/generate-chapter/',
                successProperty: 'generated_content',
                successMessage: 'Chapter content generated successfully!',
                itemIdProperty: 'chapterId' // To pick up data-chapter-id
            });
        });
    }
});

async function improve(config) {
    const statusDiv = document.getElementById(config.statusId);
    const improveButton = document.getElementById(config.buttonId);
    const textarea = document.getElementById(config.textareaId);
    const projectId = improveButton.dataset.projectId;
    const itemId = improveButton.dataset[config.itemIdProperty || 'placeId'] || improveButton.dataset.organizationId || improveButton.dataset.characterId; // Use general itemIdProperty

    let proposalContainerId = config.statusId + '-proposal-container';
    let proposalContainer = document.getElementById(proposalContainerId);
    if (!proposalContainer) {
        proposalContainer = document.createElement('div');
        proposalContainer.id = proposalContainerId;
        proposalContainer.style.marginTop = '10px'; // Add some space
        statusDiv.parentNode.insertBefore(proposalContainer, statusDiv.nextSibling);
    }
    proposalContainer.innerHTML = ''; // Clear previous proposals

    try {
        statusDiv.textContent = 'Generating proposal...';
        statusDiv.className = 'improvement-status loading';
        improveButton.disabled = true;

        const response = await fetch(`${config.endpoint}${projectId}/${itemId}/`);
        const data = await response.json();

        if (data.status === 'success') {
            const proposedText = data[config.successProperty];
            statusDiv.textContent = 'Proposal ready:';
            statusDiv.className = 'improvement-status info'; // A new class for neutral info

            const proposalPreview = document.createElement('div');
            proposalPreview.classList.add('proposal-preview');
            proposalPreview.style.border = '1px solid #ccc';
            proposalPreview.style.padding = '10px';
            proposalPreview.style.marginBottom = '10px';
            proposalPreview.style.maxHeight = '200px';
            proposalPreview.style.overflowY = 'auto';
            proposalPreview.style.backgroundColor = '#f9f9f9';
            proposalPreview.style.whiteSpace = 'pre-wrap'; // To respect newlines from AI
            proposalPreview.textContent = proposedText;

            const acceptButton = document.createElement('button');
            acceptButton.textContent = 'Accept';
            acceptButton.classList.add('btn', 'btn-success'); // Assuming btn-success is available or can be styled
            acceptButton.style.marginRight = '5px';
            acceptButton.onclick = () => {
                textarea.value = proposedText;
                statusDiv.textContent = config.successMessage;
                statusDiv.className = 'improvement-status success';
                proposalContainer.innerHTML = '';
                improveButton.disabled = false;
            };

            const cancelButton = document.createElement('button');
            cancelButton.textContent = 'Cancel';
            cancelButton.classList.add('btn', 'btn-secondary');
            cancelButton.onclick = () => {
                statusDiv.textContent = 'Improvement cancelled.';
                statusDiv.className = 'improvement-status info';
                proposalContainer.innerHTML = '';
                improveButton.disabled = false;
            };

            proposalContainer.appendChild(proposalPreview);
            proposalContainer.appendChild(acceptButton);
            proposalContainer.appendChild(cancelButton);

        } else {
            throw new Error(data.message || 'Failed to generate proposal');
        }
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'improvement-status error';
        proposalContainer.innerHTML = '';
        improveButton.disabled = false; // Re-enable button on error
    }
}
