const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const currentUserSelect = document.getElementById('currentUser');
const toolList = document.getElementById('toolList');
const suggestions = document.querySelectorAll('.suggestion');
const clearChatBtn = document.getElementById('clearChat');

const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    if (sender === 'assistant' && typeof marked !== 'undefined') {
        msgDiv.innerHTML = marked.parse(text);
    } else {
        msgDiv.textContent = text;
    }
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateToolActivity(activities) {
    toolList.innerHTML = '';
    activities.forEach(act => {
        const li = document.createElement('li');
        li.textContent = act;
        toolList.appendChild(li);
    });
}

async function sendMessage(text) {
    if (!text.trim()) return;
    
    addMessage(text, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    
    const loadingId = 'loading_' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'assistant', 'loading');
    loadingDiv.id = loadingId;
    loadingDiv.textContent = 'Agent is thinking...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                current_user: currentUserSelect.value,
                session_id: sessionId
            })
        });
        
        const data = await res.json();
        document.getElementById(loadingId).remove();
        
        if (data.error) {
            addMessage('Error: ' + data.error, 'assistant');
        } else {
            addMessage(data.response, 'assistant');
        }
        
        if (data.tool_activity && data.tool_activity.length > 0) {
            updateToolActivity(data.tool_activity);
        }
    } catch (err) {
        document.getElementById(loadingId).remove();
        addMessage('Network error. Please try again.', 'assistant');
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', () => sendMessage(userInput.value));
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(userInput.value);
});

suggestions.forEach(s => {
    s.addEventListener('click', () => {
        userInput.value = s.textContent;
        sendMessage(s.textContent);
    });
});

clearChatBtn.addEventListener('click', async () => {
    await fetch('/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    chatBox.innerHTML = '<div class="message assistant">Hello! I am the ParcelPilot AI Agent. How can I help you today? (Chat cleared)</div>';
    toolList.innerHTML = '';
});
