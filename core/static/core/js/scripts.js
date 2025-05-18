document.addEventListener('DOMContentLoaded', function() {
    const commonImprovementStatusId = 'improvement-status';
    const commonTextareaId = 'id_description';

    // Helper function to setup improvement button listeners
    function setupImprovementButton(buttonId, handlerFunction, baseConfig) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                // Pass the buttonId in the config as it's used by the handlers
                const fullConfig = { ...baseConfig, buttonId: buttonId };
                handlerFunction(fullConfig);
            });
        }
    }

    setupImprovementButton('improve-description', improveEntityDescription_Interactive, {
        statusId: commonImprovementStatusId,
        textareaId: commonTextareaId,
        endpoint: '/ai/improve/place/',
        successProperty: 'improved_description',
        successMessage: 'Description improved successfully!',
        datasetKey: 'placeId' // Standardized
    });

    setupImprovementButton('improve-organization', improveEntityDescription_Interactive, {
        statusId: commonImprovementStatusId,
        textareaId: commonTextareaId,
        endpoint: '/ai/improve/organization/',
        successProperty: 'improved_description',
        successMessage: 'Description improved successfully!',
        datasetKey: 'organizationId' // Standardized
    });

    setupImprovementButton('improve-bio', improveEntityDescription_Interactive, {
        statusId: commonImprovementStatusId,
        textareaId: commonTextareaId, // Assuming same textarea for bio description
        endpoint: '/ai/improve/character/',
        successProperty: 'improved_bio',
        successMessage: 'Bio improved successfully!',
        datasetKey: 'characterId' // Standardized
    });

    setupImprovementButton('write-chapter', improveEntityDescription_Interactive, {
        statusId: 'chapter-writing-status',
        textareaId: 'id_content',
        endpoint: '/ai/improve/chapter/',
        successProperty: 'generated_content',
        successMessage: 'Chapter content generated successfully!',
        datasetKey: 'chapterId'
    });
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

// Helper function to get or create the proposal container
function _getOrCreateProposalContainer(statusId, statusDiv) {
    const proposalContainerId = statusId + '-proposal-container';
    let proposalContainer = document.getElementById(proposalContainerId);
    if (!proposalContainer) {
        proposalContainer = document.createElement('div');
        proposalContainer.id = proposalContainerId;
        proposalContainer.style.marginTop = '10px';
        statusDiv.parentNode.insertBefore(proposalContainer, statusDiv.nextSibling);
    }
    proposalContainer.innerHTML = ''; // Clear previous content
    return proposalContainer;
}

// Helper function to handle errors during API requests
function _handleRequestError(statusDiv, proposalContainer, buttonToReEnable, error, errorMessagePrefix = 'Error') {
    const message = error.message || 'An unknown error occurred.';
    statusDiv.textContent = `${errorMessagePrefix}: ${message}`;
    statusDiv.className = 'improvement-status error';
    if (proposalContainer) {
        proposalContainer.innerHTML = '';
    }
    if (buttonToReEnable) {
        buttonToReEnable.disabled = false;
    }
}

async function improveEntityDescription_Interactive(config) {
    const improveButton = document.getElementById(config.buttonId);
    const originalTextarea = document.getElementById(config.textareaId);
    const statusDiv = document.getElementById(config.statusId);
    const projectId = improveButton.dataset.projectId;
    const itemId = improveButton.dataset[config.datasetKey];

    if (!itemId) {
        _handleRequestError(statusDiv, null, improveButton, new Error(`Could not find item ID using data attribute 'data-${config.datasetKey}'.`), 'Configuration Error');
        return;
    }

    const proposalContainer = _getOrCreateProposalContainer(config.statusId, statusDiv);

    try {
        statusDiv.textContent = 'Fetching prompt...';
        statusDiv.className = 'improvement-status loading';
        improveButton.disabled = true;

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
                    _handleRequestError(statusDiv, proposalContainer, improveButton, execError, 'Error generating improvement');
                }
            };

            proposalContainer.appendChild(promptEditorTextarea);
            proposalContainer.appendChild(executeButton);

        } else {
            throw new Error(promptData.message || 'Failed to fetch prompt');
        }
    } catch (error) {
        _handleRequestError(statusDiv, proposalContainer, improveButton, error, 'Error fetching prompt');
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
    const improveButton = document.getElementById(config.buttonId);
    const textarea = document.getElementById(config.textareaId);
    const statusDiv = document.getElementById(config.statusId);
    const projectId = improveButton.dataset.projectId;
    const itemId = improveButton.dataset[config.datasetKey]; // Use standardized datasetKey

    if (!itemId) {
        _handleRequestError(statusDiv, null, improveButton, new Error(`Could not find item ID using data attribute 'data-${config.datasetKey}'.`), 'Configuration Error');
        return;
    }

    const proposalContainer = _getOrCreateProposalContainer(config.statusId, statusDiv);

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
        _handleRequestError(statusDiv, proposalContainer, improveButton, error, 'Error generating proposal');
    }
}
