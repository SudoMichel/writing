document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.getElementById('copy-llm-context-btn');
    const llmContextPre = document.getElementById('llm-context-pre');
    const saveButton = document.getElementById('save-llm-context-btn');

    if (copyButton && llmContextPre) {
        copyButton.addEventListener('click', function() {
            const textToCopy = llmContextPre.textContent;
            navigator.clipboard.writeText(textToCopy).then(function() {
                copyButton.textContent = 'Copied!';
                copyButton.disabled = true;
                setTimeout(function() {
                    copyButton.textContent = 'Copy JSON';
                    copyButton.disabled = false;
                }, 2000); // Reset button after 2 seconds
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                copyButton.textContent = 'Error Copying';
                setTimeout(function() {
                    copyButton.textContent = 'Copy JSON';
                }, 2000);
            });
        });
    }

    if (saveButton && llmContextPre) {
        saveButton.addEventListener('click', function() {
            const textToSave = llmContextPre.textContent;
            const projectTitleElement = document.querySelector('h1');
            let filename = 'llm_context.json';
            if (projectTitleElement) {
                const projectTitle = projectTitleElement.textContent.replace('LLM Context: ', '').trim();
                if (projectTitle) {
                    filename = `${projectTitle.toLowerCase().replace(/\s+/g, '_')}_llm_context.json`;
                }
            }

            const blob = new Blob([textToSave], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            saveButton.textContent = 'Saved!';
            saveButton.disabled = true;
            setTimeout(function() {
                saveButton.textContent = 'Save JSON';
                saveButton.disabled = false;
            }, 2000);
        });
    }
}); 