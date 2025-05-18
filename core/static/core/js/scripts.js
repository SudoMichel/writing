document.addEventListener('DOMContentLoaded', function() {
    // Place form improve description button
    const improvePlaceButton = document.getElementById('improve-description');
    if (improvePlaceButton) {
        improvePlaceButton.addEventListener('click', function() {
            improveEntityDescription_Interactive({
                buttonId: 'improve-description',
                statusId: 'improvement-status',
                textareaId: 'id_description',
                endpoint: '/ai/improve/place/',
                successProperty: 'improved_description',
                successMessage: 'Description improved successfully!',
                entityType: 'place'
            });
        });
    }
    
    // Organization form improve purpose button
    const improveOrgButton = document.getElementById('improve-organization');
    if (improveOrgButton) {
        improveOrgButton.addEventListener('click', function() {
            improveEntityDescription_Interactive({
                buttonId: 'improve-organization',
                statusId: 'improvement-status',
                textareaId: 'id_description',
                endpoint: '/ai/improve/organization/',
                successProperty: 'improved_description',
                successMessage: 'Description improved successfully!',
                entityType: 'organization'
            });
        });
    }
    
    // Character form improve bio button
    const improveBioButton = document.getElementById('improve-bio');
    if (improveBioButton) {
        improveBioButton.addEventListener('click', function() {
            improveEntityDescription_Interactive({
                buttonId: 'improve-bio',
                statusId: 'improvement-status',
                textareaId: 'id_description',
                endpoint: '/ai/improve/character/',
                successProperty: 'improved_bio',
                successMessage: 'Bio improved successfully!',
                entityType: 'character'
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

// Helper function to get CSRF token (needed for POST requests in Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function improveEntityDescription_Interactive(config) {
    const statusDiv = document.getElementById(config.statusId);
    const improveButton = document.getElementById(config.buttonId);
    const originalTextarea = document.getElementById(config.textareaId);
    const projectId = improveButton.dataset.projectId;

    let itemId;
    if (config.entityType === 'character') itemId = improveButton.dataset.characterId;
    else if (config.entityType === 'place') itemId = improveButton.dataset.placeId;
    else if (config.entityType === 'organization') itemId = improveButton.dataset.organizationId;
    
    if (!itemId) {
        statusDiv.textContent = 'Error: Could not identify the item.';
        statusDiv.className = 'improvement-status error';
        if (improveButton) improveButton.disabled = false;
        return;
    }

    let proposalContainerId = config.statusId + '-proposal-container';
    let proposalContainer = document.getElementById(proposalContainerId);
    if (!proposalContainer) {
        proposalContainer = document.createElement('div');
        proposalContainer.id = proposalContainerId;
        proposalContainer.style.marginTop = '10px';
        statusDiv.parentNode.insertBefore(proposalContainer, statusDiv.nextSibling);
    }
    proposalContainer.innerHTML = '';

    try {
        statusDiv.textContent = 'Fetching prompt...';
        statusDiv.className = 'improvement-status loading';
        if (improveButton) improveButton.disabled = true;

        const getPromptResponse = await fetch(`${config.endpoint}${projectId}/${itemId}/`);
        const promptData = await getPromptResponse.json();

        if (promptData.status === 'success' && promptData.prompt) {
            statusDiv.textContent = 'Review and edit the prompt below:';
            statusDiv.className = 'improvement-status info';

            const promptEditorTextarea = document.createElement('textarea');
            promptEditorTextarea.style.width = '100%';
            promptEditorTextarea.style.minHeight = '150px';
            promptEditorTextarea.style.marginBottom = '10px';
            promptEditorTextarea.value = promptData.prompt;

            const executeButton = document.createElement('button');
            executeButton.textContent = 'Generate Improvement with this Prompt';
            executeButton.classList.add('btn', 'btn-primary');
            executeButton.onclick = async () => {
                const editedPrompt = promptEditorTextarea.value;
                statusDiv.textContent = 'Generating proposal with your prompt...';
                statusDiv.className = 'improvement-status loading';
                executeButton.disabled = true;
                promptEditorTextarea.disabled = true;

                try {
                    const executeResponse = await fetch(`${config.endpoint}${projectId}/${itemId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ prompt: editedPrompt })
                    });
                    const improvementData = await executeResponse.json();

                    if (improvementData.status === 'success') {
                        const proposedText = improvementData[config.successProperty]; 
                        _displayProposalUI(statusDiv, proposalContainer, originalTextarea, improveButton, proposedText, config.successMessage);
                    } else {
                        throw new Error(improvementData.message || 'Failed to generate proposal');
                    }
                } catch (execError) {
                    statusDiv.textContent = `Error generating improvement: ${execError.message}`;
                    statusDiv.className = 'improvement-status error';
                    proposalContainer.innerHTML = '';
                    if (improveButton) improveButton.disabled = false;
                }
            };

            proposalContainer.appendChild(promptEditorTextarea);
            proposalContainer.appendChild(executeButton);

        } else {
            throw new Error(promptData.message || 'Failed to fetch prompt');
        }
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'improvement-status error';
        proposalContainer.innerHTML = '';
        if (improveButton) improveButton.disabled = false;
    }
}

function _displayProposalUI(statusDiv, proposalContainer, originalTextarea, improveButton, proposedText, successMessage) {
    statusDiv.textContent = 'Proposal ready:';
    statusDiv.className = 'improvement-status info';
    
    proposalContainer.innerHTML = ''; // Clear previous content like prompt editor

    const proposalPreview = document.createElement('div');
    proposalPreview.classList.add('proposal-preview');
    proposalPreview.style.border = '1px solid #ccc';
    proposalPreview.style.padding = '10px';
    proposalPreview.style.marginBottom = '10px';
    proposalPreview.style.maxHeight = '200px';
    proposalPreview.style.overflowY = 'auto';
    proposalPreview.style.backgroundColor = '#f9f9f9';
    proposalPreview.style.whiteSpace = 'pre-wrap';
    proposalPreview.textContent = proposedText;

    const acceptButton = document.createElement('button');
    acceptButton.textContent = 'Accept';
    acceptButton.classList.add('btn', 'btn-success');
    acceptButton.style.marginRight = '5px';
    acceptButton.onclick = () => {
        originalTextarea.value = proposedText;
        statusDiv.textContent = successMessage;
        statusDiv.className = 'improvement-status success';
        proposalContainer.innerHTML = '';
        if (improveButton) improveButton.disabled = false;
    };

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.classList.add('btn', 'btn-secondary');
    cancelButton.onclick = () => {
        statusDiv.textContent = 'Improvement cancelled.';
        statusDiv.className = 'improvement-status info';
        proposalContainer.innerHTML = '';
        if (improveButton) improveButton.disabled = false;
    };
    
    proposalContainer.appendChild(proposalPreview);
    proposalContainer.appendChild(acceptButton);
    proposalContainer.appendChild(cancelButton);
}

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
            _displayProposalUI(statusDiv, proposalContainer, textarea, improveButton, proposedText, config.successMessage);
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
