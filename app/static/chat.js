document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const form = document.getElementById('research-form');
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const modelSelect = document.getElementById('model-select');
    
    // Discord config elements
    const saveDiscordBtn = document.getElementById('save-discord-btn');
    
    // 1. Fetch available models on load
    fetch('/api/models')
        .then(res => res.json())
        .then(models => {
            modelSelect.innerHTML = '';
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = m.name;
                modelSelect.appendChild(opt);
            });
        })
        .catch(err => console.error('Failed to load models', err));

    // 2. Save Discord Config
    saveDiscordBtn.addEventListener('click', async () => {
        const token = document.getElementById('discord-token').value;
        const channel = document.getElementById('discord-channel').value;
        if (!token || !channel) {
            alert('Please provide both Bot Token and Channel ID');
            return;
        }
        
        saveDiscordBtn.textContent = 'Saving...';
        try {
            const res = await fetch('/api/discord/configure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bot_token: token, channel_id: channel })
            });
            if (res.ok) {
                saveDiscordBtn.textContent = 'Saved!';
                setTimeout(() => saveDiscordBtn.textContent = 'Save Config', 2000);
            }
        } catch (e) {
            saveDiscordBtn.textContent = 'Error';
            console.error(e);
        }
    });

    // 3. Handle Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        // Add user message
        addMessage('user', query);
        input.value = '';
        sendBtn.disabled = true;

        // Add loading state
        const loadingId = 'loading-' + Date.now();
        const loadingHtml = `
            <div class="loading-indicator">
                <div class="spinner"></div>
                <span id="${loadingId}-text">Initiating research...</span>
            </div>
        `;
        const loadingNode = addMessage('assistant', loadingHtml, loadingId);
        
        // Progress text cycle
        const progressTexts = [
            "Searching for official website...",
            "Crawling website pages...",
            "Analyzing business model with AI...",
            "Identifying top competitors...",
            "Finalizing report..."
        ];
        let progressIdx = 0;
        const textEl = document.getElementById(`${loadingId}-text`);
        const progressInterval = setInterval(() => {
            if (textEl && progressIdx < progressTexts.length) {
                textEl.textContent = progressTexts[progressIdx];
                progressIdx++;
            }
        }, 4000); // Update every 4s

        try {
            const res = await fetch('/api/research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: query,
                    model: modelSelect.value
                })
            });

            clearInterval(progressInterval);
            
            if (!res.ok) {
                const err = await res.json();
                updateMessage(loadingNode, `<p style="color: var(--error)">Error: ${err.detail || 'Research failed'}</p>`);
                return;
            }

            const report = await res.json();
            
            // Format report HTML
            let html = `<div class="report-card">`;
            html += `<h2>${report.company_name}</h2>`;
            html += `<p><a href="${report.website}" target="_blank" style="color: var(--accent); text-decoration: none;">${report.website}</a></p>`;
            if (report.phone || report.address) {
                html += `<p style="color: var(--text-muted); font-size: 0.9em;">${report.phone || ''} | ${report.address || ''}</p>`;
            }
            
            html += `<h3>Executive Summary</h3>`;
            const summaryParts = report.summary.split('\n');
            summaryParts.forEach(part => {
                if (part.trim()) {
                    html += `<p style="margin-bottom: 12px;">${part.trim()}</p>`;
                }
            });
            
            html += `<h3>Products & Services</h3><ul>`;
            report.products_services.forEach(p => html += `<li>${p}</li>`);
            html += `</ul>`;
            
            html += `<h3>Key Pain Points</h3><ul>`;
            report.pain_points.forEach(p => html += `<li>${p}</li>`);
            html += `</ul>`;
            
            html += `<h3>Competitors</h3><ul>`;
            if (report.competitors && report.competitors.length > 0) {
                report.competitors.forEach(c => html += `<li><strong>${c.name}</strong> - <a href="${c.website}" target="_blank" style="color: var(--accent); text-decoration: none;">${c.website}</a></li>`);
            } else {
                html += `<li>No major competitors found.</li>`;
            }
            html += `</ul>`;
            
            // Store report in a dictionary to prevent state overwrite
            window.reports = window.reports || {};
            const reportId = 'report_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
            window.reports[reportId] = report;
            
            // Add buttons
            html += `<div class="action-buttons">
                <button class="primary-btn" onclick="downloadPdf('${reportId}')">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                    Download PDF
                </button>
                <button class="secondary-btn" style="width: auto;" onclick="sendToDiscord('${reportId}', this)">
                    Share to Discord
                </button>
            </div>`;
            
            html += `</div>`;
            
            updateMessage(loadingNode, html);

        } catch (e) {
            clearInterval(progressInterval);
            updateMessage(loadingNode, `<p style="color: var(--error)">Network error occurred.</p>`);
            console.error(e);
        } finally {
            sendBtn.disabled = false;
        }
    });

    function addMessage(role, content, id = null) {
        const div = document.createElement('div');
        div.className = `message ${role}-message`;
        if (id) div.id = id;
        
        div.innerHTML = `
            <div class="avatar">${role === 'user' ? 'U' : 'AI'}</div>
            <div class="message-content">${content}</div>
        `;
        
        chatLog.appendChild(div);
        chatLog.scrollTop = chatLog.scrollHeight;
        return div;
    }

    function updateMessage(node, newContent) {
        node.querySelector('.message-content').innerHTML = newContent;
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // Global functions for inline button clicks
    window.downloadPdf = async function(reportId) {
        const report = (window.reports && window.reports[reportId]) ? window.reports[reportId] : null;
        if (!report) return;
        try {
            const res = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(report)
            });
            if (!res.ok) throw new Error('PDF generation failed');
            
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${report.company_name.replace(/\s+/g, '_')}_Report.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (e) {
            alert(e.message);
        }
    };

    window.sendToDiscord = async function(reportId, btn) {
        const report = (window.reports && window.reports[reportId]) ? window.reports[reportId] : null;
        if (!report) return;
        const name = document.getElementById('applicant-name').value;
        const email = document.getElementById('applicant-email').value;
        
        if (!name || !email) {
            alert("Please enter Applicant Name and Email in the Discord Settings panel first.");
            return;
        }
        
        btn.textContent = "Sending...";
        btn.disabled = true;
        
        try {
            const res = await fetch('/api/discord/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    applicant_name: name,
                    applicant_email: email,
                    report: report
                })
            });
            
            if (res.ok) {
                btn.textContent = "Sent!";
                btn.style.backgroundColor = "var(--success)";
                btn.style.color = "white";
                btn.style.borderColor = "var(--success)";
            } else {
                const err = await res.json();
                throw new Error(err.detail || "Failed to send");
            }
        } catch (e) {
            alert(e.message);
            btn.textContent = "Share to Discord";
            btn.disabled = false;
        }
    };
});
