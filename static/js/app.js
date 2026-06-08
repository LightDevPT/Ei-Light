// =============================================
//  Ei Light — App Logic v2
//  WebSocket fixo: ws://localhost:8000/ws
// =============================================

// Application State
let config = {
    settings: {
        mic_index: null,
        clap_threshold: 0.3,
        clap_delay: 0.8,
        clap_count_required: 2,
        speech_language: "pt-PT",
        speech_phrases: [],
        autostart: false
    },
    actions: []
};

let ws = null;
let reconnectTimer = null;
let currentMicDevices = [];
let audioFiles = [];

// --- Fixed base URL ---
const BASE_URL  = 'http://localhost:8000';
const WS_URL    = 'ws://localhost:8000/ws';

// DOM Elements
const connectionStatus  = document.getElementById('connection-status');
const listeningStatus   = document.getElementById('listening-status');
const listeningToggle   = document.getElementById('listening-toggle');
const micSelect         = document.getElementById('mic-select');
const clapThreshold     = document.getElementById('clap-threshold');
const clapThresholdVal  = document.getElementById('clap-threshold-val');
const clapCount         = document.getElementById('clap-count');
const clapDelay         = document.getElementById('clap-delay');
const clapDelayVal      = document.getElementById('clap-delay-val');
const micLevelBar       = document.getElementById('mic-level-bar');
const micLevelText      = document.getElementById('mic-level-text');
const visualizerCore    = document.getElementById('visualizer-core');
const pulseRing         = document.getElementById('pulse-ring');
const actionsList       = document.getElementById('actions-list');
const consoleLogs       = document.getElementById('console-logs');
const clearLogsBtn      = document.getElementById('clear-logs');
const systemStatus      = document.getElementById('system-status');
const devmodeStatus     = document.getElementById('devmode-status');
const autostartToggle   = document.getElementById('autostart-toggle');
const btnShutdown       = document.getElementById('btn-shutdown');
const shutdownOverlay   = document.getElementById('shutdown-overlay');

const audioPlayer       = new Audio();
audioPlayer.preload = 'auto';
audioPlayer.volume = 0.85;

// Modal Elements
const actionModal         = document.getElementById('action-modal');
const btnAddAction        = document.getElementById('btn-add-action');
const btnCloseModal       = document.getElementById('btn-close-modal');
const btnCancelModal      = document.getElementById('btn-cancel-modal');
const actionForm          = document.getElementById('action-form');
const stepsList           = document.getElementById('steps-list');
const btnAddStep          = document.getElementById('btn-add-step');
const actionTrigger       = document.getElementById('action-trigger');
const triggerValueContainer = document.getElementById('trigger-value-container');

// Backup Elements
const backupModal        = document.getElementById('backup-modal');
const btnBackupCreate    = document.getElementById('btn-backup-create');
const btnBackupList      = document.getElementById('btn-backup-list');
const btnCloseBackupModal = document.getElementById('btn-close-backup-modal');
const btnCloseBackupModalFooter = document.getElementById('btn-close-backup-modal-footer');
const backupListContainer = document.getElementById('backup-list');

// =============================================
//  Init
// =============================================
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    setupEventListeners();
    fetchConfig();
    fetchMics();
    fetchAudioFiles();
});

// =============================================
//  Event Listeners
// =============================================
function setupEventListeners() {
    listeningToggle.addEventListener('click', toggleListening);

    clapThreshold.addEventListener('input', (e) => {
        clapThresholdVal.textContent = parseFloat(e.target.value).toFixed(2);
    });
    clapThreshold.addEventListener('change', () => {
        saveSettings({ clap_threshold: parseFloat(clapThreshold.value) });
    });

    clapDelay.addEventListener('input', (e) => {
        clapDelayVal.textContent = parseFloat(e.target.value).toFixed(1) + 's';
    });
    clapDelay.addEventListener('change', () => {
        saveSettings({ clap_delay: parseFloat(clapDelay.value) });
    });

    clapCount.addEventListener('change', () => {
        saveSettings({ clap_count_required: parseInt(clapCount.value) });
    });

    micSelect.addEventListener('change', () => {
        const val = micSelect.value === 'default' ? null : parseInt(micSelect.value);
        saveSettings({ mic_index: val });
    });

    autostartToggle.addEventListener('change', () => {
        saveSettings({ autostart: autostartToggle.checked });
    });

    clearLogsBtn.addEventListener('click', () => {
        consoleLogs.innerHTML = '';
    });

    // Shutdown
    btnShutdown.addEventListener('click', async () => {
        if (!confirm('Tens a certeza que queres desligar o servidor?')) return;
        btnShutdown.disabled = true;
        try {
            await fetch(`${BASE_URL}/api/shutdown`, { method: 'POST' });
        } catch (_) {}
        if (ws) { try { ws.close(); } catch (_) {} }
        shutdownOverlay.classList.add('visible');
        logToConsole('[SISTEMA] Servidor desligado. Pode fechar esta aba.', 'warning');
    });

    // Backup
    btnBackupCreate.addEventListener('click', createBackup);
    btnBackupList.addEventListener('click', showBackupList);
    btnCloseBackupModal.addEventListener('click', hideBackupModal);
    btnCloseBackupModalFooter.addEventListener('click', hideBackupModal);
    backupModal.addEventListener('click', (e) => {
        if (e.target === backupModal) hideBackupModal();
    });

    // Modal
    btnAddAction.addEventListener('click', () => showModal());
    btnCloseModal.addEventListener('click', hideModal);
    btnCancelModal.addEventListener('click', hideModal);
    actionForm.addEventListener('submit', handleFormSubmit);
    btnAddStep.addEventListener('click', () => addStepRow());
    actionTrigger.addEventListener('change', updateTriggerValueField);

    // Close modal on overlay click
    actionModal.addEventListener('click', (e) => {
        if (e.target === actionModal) hideModal();
    });
}

// =============================================
//  REST API
// =============================================
async function fetchConfig() {
    try {
        const res = await fetch(`${BASE_URL}/api/config`);
        config = await res.json();
        console.log('Config carregada:', config);
        updateSettingsUI();
        renderActions();
    } catch (err) {
        logToConsole(`[ERRO] Falha ao carregar config: ${err.message}`, 'error');
        console.error('Erro fetchConfig:', err);
    }
}

async function fetchMics() {
    try {
        const res = await fetch(`${BASE_URL}/api/mics`);
        currentMicDevices = await res.json();
        micSelect.innerHTML = '<option value="default">Microfone Padrão do Sistema</option>';
        currentMicDevices.forEach(mic => {
            const opt = document.createElement('option');
            opt.value = mic.index;
            opt.textContent = `${mic.name} (${mic.host_api})`;
            if (config.settings.mic_index === mic.index) opt.selected = true;
            micSelect.appendChild(opt);
        });
    } catch (err) {
        logToConsole(`[ERRO] Falha ao carregar microfones: ${err.message}`, 'error');
    }
}

async function fetchAudioFiles() {
    try {
        const res = await fetch(`${BASE_URL}/api/audios`);
        if (res.ok) {
            audioFiles = await res.json();
        } else {
            audioFiles = [];
        }
    } catch (err) {
        audioFiles = [];
        logToConsole(`[ERRO] Falha ao carregar áudios: ${err.message}`, 'error');
    }
    updateAudioDatalist();
    updateAudioFilesPanel();
}

function updateAudioFilesPanel() {
    const listContainer = document.getElementById('audio-files-list');
    if (!listContainer) return;
    if (!audioFiles || audioFiles.length === 0) {
        listContainer.innerHTML = '<span class="hint">Nenhum áudio disponível.</span>';
        return;
    }
    listContainer.innerHTML = audioFiles
        .map(name => `<button type="button" class="audio-file-tag" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.08); padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.82rem; color: inherit; cursor: pointer;">${name}</button>`)
        .join('');
    listContainer.querySelectorAll('.audio-file-tag').forEach(btn => {
        btn.addEventListener('click', () => setAudioFileIntoStep(btn.textContent));
    });
}

function setAudioFileIntoStep(filename) {
    if (!filename) return;
    const audioRows = Array.from(stepsList.querySelectorAll('.step-edit-item'))
        .filter(row => row.querySelector('.step-type-select').value === 'audio');
    const targetRow = audioRows.find(row => row.querySelector('.step-value-input').value.trim() === '') || audioRows[audioRows.length - 1];
    if (!targetRow) return;
    const input = targetRow.querySelector('.step-value-input');
    input.value = filename;
    input.focus();
}

async function saveSettings(newSettings) {
    try {
        const updated = { ...config.settings, ...newSettings };
        const res = await fetch(`${BASE_URL}/api/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updated)
        });
        config.settings = await res.json();
        logToConsole('[SISTEMA] Configurações guardadas.', 'system');
    } catch (err) {
        logToConsole(`[ERRO] Falha ao guardar: ${err.message}`, 'error');
    }
}

async function toggleListening() {
    try {
        const res = await fetch(`${BASE_URL}/api/listening/toggle`, { method: 'POST' });
        const data = await res.json();
        updateListeningStatusUI(data.listening);
    } catch (err) {
        logToConsole(`[ERRO] Falha ao alternar escuta: ${err.message}`, 'error');
    }
}

// =============================================
//  WebSocket — Fixed to localhost:8000
// =============================================
function initWebSocket() {
    logToConsole('[SISTEMA] A conectar ao WebSocket...', 'system');

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        connectionStatus.className = 'status-item status-online';
        connectionStatus.querySelector('.status-text').textContent = 'Conectado';
        logToConsole('[SISTEMA] Conectado ao servidor!', 'success');
        if (reconnectTimer) { clearInterval(reconnectTimer); reconnectTimer = null; }
    };

    ws.onclose = () => {
        connectionStatus.className = 'status-item status-offline';
        connectionStatus.querySelector('.status-text').textContent = 'Desconectado';
        updateListeningStatusUI(false);
        logToConsole('[AVISO] Conexão perdida. A reconectar em 3s...', 'warning');
        if (!reconnectTimer) reconnectTimer = setInterval(initWebSocket, 3000);
    };

    ws.onerror = () => {
        logToConsole('[ERRO] Erro na ligação WebSocket.', 'error');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if      (data.type === 'volume')       updateAudioVisualizer(data.value);
        else if (data.type === 'log')          logToConsole(data.message, data.level);
        else if (data.type === 'status')       updateListeningStatusUI(data.listening);
        else if (data.type === 'dev_mode')     updateDevModeStatusUI(data.active);
        else if (data.type === 'system_status') updateSystemStatusUI(data.enabled);
        else if (data.type === 'config')       { config = data.config; updateSettingsUI(); renderActions(); }
        else if (data.type === 'trigger_glow') triggerVisualGlow();
        else if (data.type === 'play_audio')   playAudioOnPage(data.filename);
    };
}

// =============================================
//  UI Updates
// =============================================
function updateSettingsUI() {
    clapThreshold.value    = config.settings.clap_threshold;
    clapThresholdVal.textContent = parseFloat(config.settings.clap_threshold).toFixed(2);

    clapDelay.value        = config.settings.clap_delay;
    clapDelayVal.textContent = parseFloat(config.settings.clap_delay).toFixed(1) + 's';

    clapCount.value        = config.settings.clap_count_required;

    if (config.settings.mic_index !== null && config.settings.mic_index !== undefined) {
        micSelect.value = config.settings.mic_index;
    } else {
        micSelect.value = 'default';
    }

    if (config.settings.autostart !== undefined) {
        autostartToggle.checked = !!config.settings.autostart;
    }
}

function updateSystemStatusUI(isEnabled) {
    if (!systemStatus) return;
    systemStatus.className = isEnabled ? 'status-item status-online' : 'status-item status-offline';
    systemStatus.querySelector('.status-text').textContent = `Sistema: ${isEnabled ? 'Ativado' : 'Desativado'}`;
}

function updateListeningStatusUI(isListening) {
    const iconWrapper = document.getElementById('toggle-icon-wrapper');

    if (isListening) {
        listeningStatus.className = 'status-item status-listening';
        listeningStatus.querySelector('.status-text').textContent = 'A Escutar';
        listeningToggle.className = 'btn-listen listening';
        listeningToggle.querySelector('span:last-child').textContent = 'Parar Escuta';
        if (iconWrapper) iconWrapper.innerHTML = '<i data-lucide="square"></i>';
        visualizerCore.classList.add('active');

        // Animate rings when active
        document.querySelectorAll('.ring').forEach(r => r.style.borderColor = 'rgba(0,212,255,0.15)');
    } else {
        listeningStatus.className = 'status-item';
        listeningStatus.querySelector('.status-text').textContent = 'Parado';
        listeningToggle.className = 'btn-listen';
        listeningToggle.querySelector('span:last-child').textContent = 'Iniciar Escuta';
        if (iconWrapper) iconWrapper.innerHTML = '<i data-lucide="play"></i>';
        visualizerCore.classList.remove('active');
        updateAudioVisualizer(0);

        document.querySelectorAll('.ring').forEach(r => r.style.borderColor = '');
    }
    lucide.createIcons();
}

function updateDevModeStatusUI(isActive) {
    if (!devmodeStatus) return;
    if (isActive) {
        devmodeStatus.className = 'status-item status-active';
        devmodeStatus.querySelector('.status-text').textContent = 'Ei Light: ON';
    } else {
        devmodeStatus.className = 'status-item';
        devmodeStatus.querySelector('.status-text').textContent = 'Ei Light: Off';
    }
}

function updateAudioVisualizer(volume) {
    volume = Math.max(0, Math.min(1, volume));

    micLevelBar.style.width = (volume * 100) + '%';
    micLevelText.textContent = `Volume: ${Math.round(volume * 100)}%`;

    const scale = 1 + (volume * 0.45);
    visualizerCore.style.transform = `scale(${scale})`;

    // Animate rings based on volume
    const r1 = document.getElementById('ring-1');
    const r2 = document.getElementById('ring-2');
    const r3 = document.getElementById('ring-3');
    if (r1 && volume > 0.02) {
        r1.style.transform = `scale(${1 + volume * 0.15})`;
        r2.style.transform = `scale(${1 + volume * 0.1})`;
        r3.style.transform = `scale(${1 + volume * 0.05})`;
        r1.style.borderColor = `rgba(0,212,255,${0.3 + volume * 0.5})`;
        r2.style.borderColor = `rgba(0,212,255,${0.15 + volume * 0.3})`;
        r3.style.borderColor = `rgba(0,212,255,${0.07 + volume * 0.15})`;
    } else if (r1) {
        r1.style.transform = r2.style.transform = r3.style.transform = 'scale(1)';
        if (!visualizerCore.classList.contains('active')) {
            r1.style.borderColor = r2.style.borderColor = r3.style.borderColor = '';
        }
    }

    // Pulse ring
    if (volume > 0.02) {
        const ringScale = 1 + (volume * 1.8);
        pulseRing.style.transform = `scale(${ringScale})`;
        pulseRing.style.opacity   = Math.max(0, 0.8 - volume * 1.2);
    } else {
        pulseRing.style.transform = 'scale(1)';
        pulseRing.style.opacity   = 0;
    }
}

function triggerVisualGlow() {
    visualizerCore.classList.add('glowing-trigger');
    setTimeout(() => visualizerCore.classList.remove('glowing-trigger'), 800);
}

function playAudioOnPage(filename) {
    if (!filename) return;
    const url = `${BASE_URL}/audios/${encodeURIComponent(filename)}`;
    audioPlayer.pause();
    audioPlayer.src = url;
    audioPlayer.load();
    audioPlayer.play().catch((err) => {
        logToConsole(`[AVISO] Não foi possível reproduzir áudio no browser: ${err.message}`, 'warning');
    });
}

function logToConsole(message, level = 'info') {
    const line = document.createElement('div');
    line.className = `log-line ${level}`;

    const now = new Date();
    const time = [now.getHours(), now.getMinutes(), now.getSeconds()]
        .map(n => n.toString().padStart(2, '0')).join(':');

    line.textContent = `[${time}] ${message}`;
    consoleLogs.appendChild(line);
    consoleLogs.scrollTop = consoleLogs.scrollHeight;

    if (consoleLogs.children.length > 300) {
        consoleLogs.removeChild(consoleLogs.firstChild);
    }
}

// =============================================
//  Actions Render
// =============================================
function renderActions() {
    actionsList.innerHTML = '';

    if (!config.actions || config.actions.length === 0) {
        actionsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon"><i data-lucide="sparkles"></i></div>
                <p>Nenhuma ação configurada.</p>
                <span>Cria a tua primeira ação com o botão acima.</span>
            </div>`;
        lucide.createIcons();
        return;
    }

    config.actions.forEach(action => {
        const card = document.createElement('div');
        card.className = 'action-card';
        card.dataset.id = action.id;

        const isSpeech = action.trigger === 'speech';
        const triggerIcon  = isSpeech ? 'mic' : 'hand';
        const triggerValues = action.trigger_value.split(/[,;]+/).map(v => v.trim()).filter(Boolean);
        const triggerLabel = isSpeech
            ? `Voz: "${triggerValues.join('" / "')}"`
            : triggerValues.length > 1
                ? `${triggerValues.join(' / ')} Palmas`
                : (triggerValues[0] === '1' ? '1 Palma' : `${triggerValues[0]} Palmas`);
        const triggerClass = isSpeech ? 'speech-trigger' : 'clap-trigger';

        let stepsHtml = '<div class="action-steps-summary">';
        if (action.steps && action.steps.length > 0) {
            action.steps.forEach(step => {
                const icon = step.type === 'url' ? 'globe' : step.type === 'app' ? 'file-code' : step.type === 'audio' ? 'music' : 'terminal';
                const typeLabel = step.type === 'url' ? 'URL' : step.type === 'app' ? 'APP' : step.type === 'audio' ? 'SOM' : 'CMD';
                stepsHtml += `
                    <div class="step-item">
                        <i data-lucide="${icon}"></i>
                        <span class="step-type-badge">${typeLabel}</span>
                        <span class="step-val" title="${step.value}">${step.value}</span>
                    </div>`;
            });
        } else {
            stepsHtml += `<div class="step-item"><span class="hint">Sem passos configurados.</span></div>`;
        }
        stepsHtml += '</div>';

        card.innerHTML = `
            <div class="action-card-header">
                <div class="action-info">
                    <h3>${action.name}</h3>
                    <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 0.15rem;">
                        <span class="trigger-badge ${triggerClass}">
                            <i data-lucide="${triggerIcon}" style="width:10px;height:10px;"></i>
                            ${triggerLabel}
                        </span>
                        ${isSpeech ? `
                            <button class="btn-badge-calibrate" onclick="openCalibrationModal('${action.id}', '${action.name}')" title="Gravar voz para calibrar comando">
                                <i data-lucide="mic" style="width:10px;height:10px;"></i>
                                Gravar Voz
                            </button>
                        ` : ''}
                    </div>
                </div>
                <div class="action-btns">
                    <button class="btn-icon test" title="Testar" onclick="testAction('${action.id}')">
                        <i data-lucide="play"></i>
                    </button>
                    <button class="btn-icon edit" title="Editar" onclick="editAction('${action.id}')">
                        <i data-lucide="edit-2"></i>
                    </button>
                    <button class="btn-icon delete" title="Eliminar" onclick="deleteAction('${action.id}')">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
            ${stepsHtml}`;

        actionsList.appendChild(card);
    });

    lucide.createIcons();
}

// =============================================
//  Action CRUD
// =============================================
async function deleteAction(id) {
    if (!confirm('Eliminar esta ação?')) return;
    try {
        const res = await fetch(`${BASE_URL}/api/config/action/${id}`, { method: 'DELETE' });
        if (res.ok) { logToConsole('[SISTEMA] Ação eliminada.', 'system'); fetchConfig(); }
        else { const e = await res.json(); logToConsole(`[ERRO] ${e.detail}`, 'error'); }
    } catch (err) { logToConsole(`[ERRO] ${err.message}`, 'error'); }
}

async function testAction(id) {
    logToConsole('[TESTE] A disparar ação manualmente...', 'info');
    try {
        const res = await fetch(`${BASE_URL}/api/trigger-action/${id}`, { method: 'POST' });
        if (res.ok) logToConsole('[TESTE] Ação executada com sucesso.', 'success');
        else { const e = await res.json(); logToConsole(`[ERRO] ${e.detail}`, 'error'); }
    } catch (err) { logToConsole(`[ERRO] ${err.message}`, 'error'); }
}

function editAction(id) {
    const action = config.actions.find(a => a.id === id);
    if (action) showModal(action);
}

// =============================================
//  Modal
// =============================================
function showModal(action = null) {
    actionForm.reset();
    stepsList.innerHTML = '';

    if (action) {
        document.getElementById('modal-title').textContent = 'Editar Ação';
        document.getElementById('action-id').value = action.id;
        document.getElementById('action-name').value = action.name;
        document.getElementById('action-trigger').value = action.trigger;
        updateTriggerValueField();
        document.getElementById('action-trigger-value').value = action.trigger_value;
        (action.steps && action.steps.length > 0)
            ? action.steps.forEach(s => addStepRow(s.type, s.value))
            : addStepRow();
    } else {
        document.getElementById('modal-title').textContent = 'Nova Ação';
        document.getElementById('action-id').value = '';
        updateTriggerValueField();
        addStepRow();
    }

    updateAudioFilesPanel();
    actionModal.classList.add('open');
    lucide.createIcons();
}

function hideModal() {
    actionModal.classList.remove('open');
}

function updateTriggerValueField() {
    const type = actionTrigger.value;
    triggerValueContainer.innerHTML = '';

    const label = document.createElement('label');
    label.htmlFor = 'action-trigger-value';
    label.id = 'trigger-value-label';
    label.className = '';
    label.style = 'font-size:0.78rem;font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:0.04em;';

    if (type === 'clap') {
        label.textContent = 'Número(s) de Palmas';
        triggerValueContainer.appendChild(label);
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'action-trigger-value';
        input.required = true;
        input.placeholder = 'Ex: 2 ou 1,2';
        triggerValueContainer.appendChild(input);
    } else {
        label.textContent = 'Frase(s) de Gatilho';
        triggerValueContainer.appendChild(label);
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'action-trigger-value';
        input.required = true;
        input.placeholder = 'Ex: ei light, ativar ei light';
        triggerValueContainer.appendChild(input);
    }
}

function updateAudioDatalist() {
    let dataList = document.getElementById('audio-file-list');
    if (!dataList) {
        dataList = document.createElement('datalist');
        dataList.id = 'audio-file-list';
        document.body.appendChild(dataList);
    }
    dataList.innerHTML = audioFiles
        .map(name => `<option value="${name}"></option>`)
        .join('');
}

function addStepRow(type = 'command', value = '') {
    const row = document.createElement('div');
    row.className = 'step-edit-item';

    const select = document.createElement('select');
    select.className = 'step-type-select';
    [
        { val: 'command', text: 'Rodar Comando' },
        { val: 'url',     text: 'Abrir URL' },
        { val: 'app',     text: 'Abrir App' },
        { val: 'audio',   text: 'Tocar Áudio' }
    ].forEach(o => {
        const opt = document.createElement('option');
        opt.value = o.val; opt.textContent = o.text;
        if (o.val === type) opt.selected = true;
        select.appendChild(opt);
    });

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'step-value-input';
    input.required = true;
    input.value = value;

    const setPlaceholder = () => {
        if (select.value === 'url') {
            input.placeholder = 'https://...';
            input.removeAttribute('list');
        } else if (select.value === 'app') {
            input.placeholder = 'calc.exe ou code .';
            input.removeAttribute('list');
        } else if (select.value === 'audio') {
            input.placeholder = audioFiles.length > 0 ? 'Escolhe um ficheiro de áudio da pasta audios' : 'app aberto.mp3';
            input.setAttribute('list', 'audio-file-list');
            updateAudioDatalist();
        } else {
            input.placeholder = 'npm run dev';
            input.removeAttribute('list');
        }
    };

    select.addEventListener('change', () => {
        setPlaceholder();
        if (select.value === 'audio' && !input.value) {
            input.value = audioFiles.length > 0 ? audioFiles[0] : '';
        }
    });
    setPlaceholder();

    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'btn-icon delete';
    delBtn.innerHTML = '<i data-lucide="trash-2"></i>';
    delBtn.addEventListener('click', () => {
        row.remove();
        if (stepsList.children.length === 0) addStepRow();
        lucide.createIcons();
    });

    row.appendChild(select);
    row.appendChild(input);
    row.appendChild(delBtn);
    stepsList.appendChild(row);
    lucide.createIcons();
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const id            = document.getElementById('action-id').value;
    const name          = document.getElementById('action-name').value;
    const trigger       = document.getElementById('action-trigger').value;
    const trigger_value = document.getElementById('action-trigger-value').value;

    const steps = [];
    stepsList.querySelectorAll('.step-edit-item').forEach(row => {
        const type  = row.querySelector('.step-type-select').value;
        const value = row.querySelector('.step-value-input').value.trim();
        if (value) steps.push({ type, value });
    });

    if (steps.length === 0) { alert('Adiciona pelo menos um passo.'); return; }

    try {
        const res = await fetch(`${BASE_URL}/api/config/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id || null, name, trigger, trigger_value, steps })
        });
        if (res.ok) {
            logToConsole('[SISTEMA] Ação guardada.', 'success');
            hideModal();
            fetchConfig();
        } else {
            const err = await res.json();
            logToConsole(`[ERRO] ${err.detail}`, 'error');
        }
    } catch (err) { logToConsole(`[ERRO] ${err.message}`, 'error'); }
}

// =============================================
//  Voice Calibration System
// =============================================
let activeCalibrationActionId = null;
let activeCalibrationActionName = "";
let calibrationTimeout = null;

const calibrationModal = document.getElementById('calibration-modal');
const btnCloseCalibration = document.getElementById('btn-close-calibration');
const btnCancelCalibration = document.getElementById('btn-cancel-calibration');
const btnStartCalibration = document.getElementById('btn-start-calibration');
const btnConfirmCalibration = document.getElementById('btn-confirm-calibration');

const calRing1 = document.getElementById('cal-ring-1');
const calRing2 = document.getElementById('cal-ring-2');
const calRing3 = document.getElementById('cal-ring-3');
const calVisualizerCore = document.getElementById('cal-visualizer-core');

const calStateText = document.getElementById('calibration-state-text');
const calHintText = document.getElementById('calibration-hint-text');
const calResultContainer = document.getElementById('calibration-result-container');
const calResultText = document.getElementById('calibration-result-text');

function openCalibrationModal(actionId, actionName) {
    activeCalibrationActionId = actionId;
    activeCalibrationActionName = actionName;
    
    // Reset modal UI state
    calStateText.textContent = "Pronto para iniciar";
    calStateText.style.color = "var(--text-1)";
    calHintText.textContent = `Vais gravar o comando de voz para a ação "${actionName}".`;
    calResultContainer.style.display = "none";
    calResultText.textContent = "";
    btnStartCalibration.style.display = "flex";
    btnConfirmCalibration.style.display = "none";
    
    // Reset animation styles
    calRing1.style.transform = calRing2.style.transform = calRing3.style.transform = 'scale(1)';
    calRing1.style.borderColor = calRing2.style.borderColor = calRing3.style.borderColor = '';
    calVisualizerCore.style.transform = 'scale(1)';
    calVisualizerCore.style.boxShadow = '';
    
    calibrationModal.classList.add('open');
    setTimeout(() => lucide.createIcons(), 50);
}

function closeCalibrationModal() {
    calibrationModal.classList.remove('open');
    activeCalibrationActionId = null;
    activeCalibrationActionName = "";
    if (calibrationTimeout) {
        clearTimeout(calibrationTimeout);
        calibrationTimeout = null;
    }
}

// Add event listeners for calibration modal
if (btnCloseCalibration) btnCloseCalibration.addEventListener('click', closeCalibrationModal);
if (btnCancelCalibration) btnCancelCalibration.addEventListener('click', closeCalibrationModal);
if (btnStartCalibration) btnStartCalibration.addEventListener('click', startVoiceRecordingFlow);
if (btnConfirmCalibration) btnConfirmCalibration.addEventListener('click', confirmCalibrationResult);

// Handle calibration modal overlay click to close
if (calibrationModal) {
    calibrationModal.addEventListener('click', (e) => {
        if (e.target === calibrationModal) closeCalibrationModal();
    });
}

async function startVoiceRecordingFlow() {
    btnStartCalibration.style.display = "none";
    calStateText.textContent = "A preparar microfone...";
    calHintText.textContent = "Por favor, aguarda que as escutas em segundo plano sejam pausadas.";
    
    // Pulse animation during preparation
    calRing1.style.borderColor = "rgba(124, 58, 237, 0.4)";
    calRing2.style.borderColor = "rgba(0, 212, 255, 0.2)";
    
    // Pulse rings loop
    let step = 0;
    const pulseInterval = setInterval(() => {
        if (!activeCalibrationActionId || calStateText.textContent.includes("Gravação Concluída") || calStateText.textContent.includes("Erro")) {
            clearInterval(pulseInterval);
            return;
        }
        step = (step + 1) % 4;
        if (step === 0) {
            calRing1.style.transform = 'scale(1.1)';
            calRing2.style.transform = 'scale(1.05)';
            calVisualizerCore.style.transform = 'scale(1.05)';
        } else if (step === 2) {
            calRing1.style.transform = 'scale(1)';
            calRing2.style.transform = 'scale(1)';
            calVisualizerCore.style.transform = 'scale(1)';
        }
    }, 250);

    try {
        // Phase 1 (0→1.5s): backend is waiting for mic threads to exit
        setTimeout(() => {
            if (activeCalibrationActionId && !calStateText.textContent.includes("Erro")) {
                calStateText.textContent = "A calibrar ruído...";
                calStateText.style.color = "var(--yellow)";
                calHintText.textContent = "O sistema está a medir o ruído de fundo do ambiente.";
                calRing1.style.borderColor = "rgba(246, 201, 14, 0.4)";
                calRing2.style.borderColor = "rgba(246, 201, 14, 0.2)";
            }
        }, 1500);

        // Phase 2 (0→2.5s): ambient noise calibration done, now listening
        setTimeout(() => {
            if (activeCalibrationActionId && !calStateText.textContent.includes("Erro")) {
                calStateText.textContent = "FALE AGORA!";
                calStateText.style.color = "var(--green)";
                calHintText.textContent = "Diz a frase do comando de voz com clareza. (5s restantes)";
                calRing1.style.borderColor = "var(--green)";
                calRing2.style.borderColor = "rgba(16, 245, 154, 0.3)";
                calRing3.style.borderColor = "rgba(16, 245, 154, 0.15)";
                calVisualizerCore.style.boxShadow = "0 0 30px rgba(16, 245, 154, 0.5)";
                
                let secondsLeft = 5;
                const countdown = setInterval(() => {
                    secondsLeft--;
                    if (secondsLeft <= 0 || !activeCalibrationActionId || calStateText.textContent.includes("Concluída")) {
                        clearInterval(countdown);
                        calVisualizerCore.style.boxShadow = "";
                    } else {
                        calHintText.textContent = `Diz a frase do comando de voz com clareza. (${secondsLeft}s restantes)`;
                    }
                }, 1000);
            }
        }, 2500);

        const response = await fetch(`${BASE_URL}/api/calibrate/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action_id: activeCalibrationActionId })
        });
        
        clearInterval(pulseInterval);
        
        if (response.ok) {
            const data = await response.json();
            calStateText.textContent = "Gravação Concluída!";
            calStateText.style.color = "var(--primary)";
            calHintText.textContent = "Gostarias de definir a frase ouvida pelo sistema como o gatilho desta ação?";
            calResultText.textContent = `"${data.text}"`;
            calResultContainer.style.display = "block";
            btnConfirmCalibration.style.display = "flex";
            calRing1.style.borderColor = "var(--primary)";
            calRing2.style.borderColor = "rgba(255, 215, 0, 0.3)";
            calRing3.style.borderColor = "rgba(255, 215, 0, 0.15)";
        } else {
            const err = await response.json();
            calStateText.textContent = "Erro na Gravação";
            calStateText.style.color = "var(--red)";
            calHintText.textContent = err.detail || "Não foi possível calibrar. Tenta novamente.";
            btnStartCalibration.style.display = "flex";
            calRing1.style.borderColor = "var(--red)";
            calRing2.style.borderColor = "";
            calRing3.style.borderColor = "";
        }
    } catch (err) {
        clearInterval(pulseInterval);
        calStateText.textContent = "Erro de Ligação";
        calStateText.style.color = "var(--red)";
        calHintText.textContent = `Não foi possível comunicar com o servidor: ${err.message}`;
        btnStartCalibration.style.display = "flex";
        calRing1.style.borderColor = "var(--red)";
        calRing2.style.borderColor = "";
        calRing3.style.borderColor = "";
    }
}

async function confirmCalibrationResult() {
    if (!activeCalibrationActionId) return;
    
    const transcribedText = calResultText.textContent.replace(/"/g, '').trim();
    if (!transcribedText) {
        alert("Nenhum texto transcrevido para guardar.");
        return;
    }
    
    // Fetch the original action to update its trigger_value
    const action = config.actions.find(a => a.id === activeCalibrationActionId);
    if (!action) {
        alert("Ação original não encontrada.");
        return;
    }
    
    const updatedAction = {
        ...action,
        trigger_value: transcribedText
    };
    
    try {
        const res = await fetch(`${BASE_URL}/api/config/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedAction)
        });
        
        if (res.ok) {
            logToConsole(`[SISTEMA] Comando de voz calibrado com sucesso: "${transcribedText}"`, 'success');
            closeCalibrationModal();
            fetchConfig();
        } else {
            const err = await res.json();
            alert(`Erro ao guardar calibragem: ${err.detail}`);
        }
    } catch (err) {
        alert(`Erro de rede ao guardar calibragem: ${err.message}`);
    }
}

// =============================================
//  Backup System
// =============================================
async function createBackup() {
    try {
        const res = await fetch(`${BASE_URL}/api/backup/create`, { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            logToConsole(`✅ Backup criado: ${data.backup}`, 'success');
        } else {
            logToConsole(`❌ Erro ao criar backup: ${data.detail}`, 'error');
        }
    } catch (err) {
        logToConsole(`❌ Erro: ${err.message}`, 'error');
    }
}

function hideBackupModal() {
    backupModal.classList.remove('open');
}

async function showBackupList() {
    backupModal.classList.add('open');
    backupListContainer.innerHTML = '<div style="text-align: center; color: var(--text-2); padding: 2rem;"><i data-lucide="loader" style="animation: spin 1s linear infinite;"></i><p>A carregar backups...</p></div>';
    lucide.createIcons();
    
    try {
        const res = await fetch(`${BASE_URL}/api/backup/list`);
        const data = await res.json();
        const backups = data.backups;
        
        if (!backups || backups.length === 0) {
            backupListContainer.innerHTML = '<div style="text-align: center; color: var(--text-2); padding: 2rem;"><p>Nenhum backup encontrado.</p></div>';
            lucide.createIcons();
            return;
        }
        
        backupListContainer.innerHTML = backups.map((backup, idx) => `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius); padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 0.9rem;">${backup.name}</div>
                    <div style="font-size: 0.8rem; color: var(--text-2); margin-top: 0.25rem;">${backup.date} • ${backup.size}</div>
                </div>
                <button type="button" class="btn-icon" onclick="restoreBackup('${backup.name}')" title="Restaurar este backup" style="color: var(--primary);">
                    <i data-lucide="rotate-ccw"></i>
                </button>
            </div>
        `).join('');
        lucide.createIcons();
    } catch (err) {
        backupListContainer.innerHTML = `<div style="text-align: center; color: var(--red); padding: 2rem;"><p>Erro ao carregar backups: ${err.message}</p></div>`;
        lucide.createIcons();
    }
}

async function restoreBackup(backupName) {
    if (!confirm(`Tens a certeza que queres restaurar o backup "${backupName}"? As ações atuais serão guardadas como backup.`)) return;
    
    try {
        const res = await fetch(`${BASE_URL}/api/backup/restore/${encodeURIComponent(backupName)}`, { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            logToConsole(`✅ Backup restaurado com sucesso!`, 'success');
            fetchConfig();
            hideBackupModal();
        } else {
            logToConsole(`❌ ${data.detail}`, 'error');
        }
    } catch (err) {
        logToConsole(`❌ Erro: ${err.message}`, 'error');
    }
}
