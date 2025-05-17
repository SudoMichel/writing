document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.getElementById('copy-llm-context-btn');
    const llmContextPre = document.getElementById('llm-context-pre');

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
}); 