import os
import sys
import json
import time
import uuid
import asyncio
import threading
import subprocess
import webbrowser
import re
from typing import List, Dict, Optional
import ctypes

# Keep console window visible in taskbar on Windows
try:
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 1)  # SW_SHOW = 1
except Exception as e:
    print(f"Error showing console: {e}")


# Change working directory to the script's directory to ensure relative paths work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_startup_shortcut_path() -> str:
    startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    return os.path.join(startup_dir, "EiLight.lnk")

def set_startup(enable: bool):
    shortcut_path = get_startup_shortcut_path()
    if enable:
        workspace_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.normpath(os.path.join(workspace_dir, "start.bat"))
        
        # PowerShell command to create a shortcut
        ps_command = f"""
        $Shell = New-Object -ComObject WScript.Shell
        $Shortcut = $Shell.CreateShortcut('{shortcut_path}')
        $Shortcut.TargetPath = '{bat_path}'
        $Shortcut.WorkingDirectory = '{workspace_dir}'
        $Shortcut.Save()
        """
        try:
            subprocess.run(["powershell", "-Command", ps_command], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_message("Inicialização automática ativada no Windows.", "success")
        except Exception as e:
            log_message(f"Erro ao ativar inicialização automática: {e}", "error")
    else:
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
                log_message("Inicialização automática desativada no Windows.", "success")
            except Exception as e:
                log_message(f"Erro ao desativar inicialização automática: {e}", "error")


import numpy as np
import sounddevice as sd
import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Initialize FastAPI App
app = FastAPI(title="Ei Light Backend")

# Create required directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("audios", exist_ok=True)

# Mount static files, audio files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audios", StaticFiles(directory="audios"), name="audios")
templates = Jinja2Templates(directory="templates")

# Global State
CONFIG_FILE = "config.json"
is_listening = True
audio_stream = None
active_websockets: List[WebSocket] = []
websocket_loop = None
dev_mode_active = False
system_enabled = True
is_calibrating = False

# Mutex for thread safety on config operations
config_lock = threading.Lock()
config = {}

# Load Configuration
def load_config() -> dict:
    global config
    with config_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Check dynamic shortcut state on load
                    config.setdefault("settings", {})
                    config["settings"]["autostart"] = os.path.exists(get_startup_shortcut_path())
                    return config
            except Exception as e:
                print(f"Error reading config: {e}")
        
        # Default configuration if file doesn't exist
        config = {
            "settings": {
                "mic_index": None,
                "clap_threshold": 0.30,
                "clap_delay": 0.8,
                "clap_count_required": 2,
                "speech_language": "pt-PT",
                "speech_phrases": ["ei light"],
                "autostart": os.path.exists(get_startup_shortcut_path())
            },
            "actions": [
                {
                    "id": "action_default_1",
                    "name": "Ativar Ei Light",
                    "trigger": "speech",
                    "trigger_value": "ei light",
                    "steps": [
                        { "type": "url", "value": "https://github.com" },
                        { "type": "command", "value": "code ." },
                        { "type": "command", "value": "start cmd /k \"echo EI LIGHT ATIVADO! & echo Seu workspace esta pronto!\"" }
                    ]
                },
                {
                    "id": "action_default_2",
                    "name": "Abrir Calculadora",
                    "trigger": "clap",
                    "trigger_value": "2",
                    "steps": [
                        { "type": "app", "value": "calc.exe" }
                    ]
                }
            ]
        }
        save_config_unsafe()
        return config

def save_config_unsafe():
    try:
        # Sync speech phrases list based on current speech actions
        speech_phrases = []
        for action in config.get("actions", []):
            if action.get("trigger") == "speech" and action.get("trigger_value"):
                phrase = action["trigger_value"].lower().strip()
                if phrase not in speech_phrases:
                    speech_phrases.append(phrase)
        config["settings"]["speech_phrases"] = speech_phrases

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def save_config():
    with config_lock:
        save_config_unsafe()

# =============================================
#  Backup System
# =============================================
import shutil
from datetime import datetime

BACKUPS_DIR = "backups"

def ensure_backups_dir():
    if not os.path.exists(BACKUPS_DIR):
        os.makedirs(BACKUPS_DIR)

def create_backup():
    """Cria um backup do config.json com timestamp"""
    ensure_backups_dir()
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_backup_{timestamp}.json"
        backup_path = os.path.join(BACKUPS_DIR, backup_name)
        
        with config_lock:
            with open(CONFIG_FILE, "r", encoding="utf-8") as src:
                backup_content = src.read()
        
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(backup_content)
        
        log_message(f"Backup criado: {backup_name}", "system")
        return {"status": "success", "backup": backup_name}
    except Exception as e:
        log_message(f"Erro ao criar backup: {e}", "error")
        return {"status": "error", "detail": str(e)}

def get_backups():
    """Retorna lista de backups disponíveis"""
    ensure_backups_dir()
    try:
        backups = []
        for file in sorted(os.listdir(BACKUPS_DIR), reverse=True):
            if file.startswith("config_backup_") and file.endswith(".json"):
                file_path = os.path.join(BACKUPS_DIR, file)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_mtime).strftime("%d/%m/%Y %H:%M:%S")
                backups.append({
                    "name": file,
                    "date": file_date,
                    "size": f"{file_size} bytes"
                })
        return backups
    except Exception as e:
        log_message(f"Erro ao listar backups: {e}", "error")
        return []

def restore_backup(backup_name: str):
    """Restaura um backup anterior"""
    ensure_backups_dir()
    try:
        backup_path = os.path.join(BACKUPS_DIR, backup_name)
        
        # Validar que o ficheiro existe e está no diretório de backups
        if not os.path.exists(backup_path) or not backup_path.startswith(os.path.abspath(BACKUPS_DIR)):
            log_message(f"Backup inválido: {backup_name}", "error")
            return {"status": "error", "detail": "Backup não encontrado ou inválido"}
        
        # Criar um backup do estado atual antes de restaurar
        create_backup()
        
        # Restaurar
        with open(backup_path, "r", encoding="utf-8") as src:
            restored_config = json.load(src)
        
        with config_lock:
            global config
            config = restored_config
            save_config_unsafe()
        
        log_message(f"Backup restaurado: {backup_name}", "system")
        return {"status": "success", "detail": f"Backup {backup_name} restaurado com sucesso"}
    except Exception as e:
        log_message(f"Erro ao restaurar backup: {e}", "error")
        return {"status": "error", "detail": str(e)}

# Thread-safe logging and WebSocket broadcasting
def log_message(message: str, level: str = "info"):
    print(f"[{level.upper()}] {message}")
    if websocket_loop and active_websockets:
        asyncio.run_coroutine_threadsafe(
            broadcast_ws({"type": "log", "message": message, "level": level}),
            websocket_loop
        )

async def broadcast_ws(payload: dict):
    if not active_websockets:
        return
    
    # Clean up disconnected sockets on the fly
    disconnected = []
    for ws in active_websockets:
        try:
            await ws.send_json(payload)
        except Exception:
            disconnected.append(ws)
            
    for ws in disconnected:
        if ws in active_websockets:
            active_websockets.remove(ws)

def trigger_glow_effect():
    if websocket_loop and active_websockets:
        asyncio.run_coroutine_threadsafe(
            broadcast_ws({"type": "trigger_glow"}),
            websocket_loop
        )

# Step Executor
# DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP ensures launched processes
# are fully independent — they survive even if the terminal window is closed.
DETACH_FLAGS = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

def execute_step(step: dict, play_sounds: bool = True):
    stype = step.get("type")
    sval = step.get("value", "").strip()
    if not sval:
        return

    try:
        if stype == "url":
            webbrowser.open(sval)
            log_message(f"Passo Executado: Abrindo URL -> {sval}", "success")
        elif stype == "app":
            try:
                # os.startfile is always detached on Windows
                os.startfile(sval)
                log_message(f"Passo Executado: Abrindo App -> {sval}", "success")
            except Exception:
                # Fallback: fully detached subprocess so it survives terminal close
                subprocess.Popen(
                    sval, shell=True,
                    creationflags=DETACH_FLAGS,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                log_message(f"Passo Executado: Abrindo App (detached) -> {sval}", "success")
            if play_sounds:
                play_audio_step("app aberto.mp3")
        elif stype == "command":
            subprocess.Popen(
                sval, shell=True,
                creationflags=DETACH_FLAGS,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log_message(f"Passo Executado: Rodando comando (detached) -> {sval}", "success")
        elif stype == "audio":
            if play_sounds:
                play_audio_step(sval)
            log_message(f"Passo Executado: Tocando áudio -> {sval}", "success")
    except Exception as e:
        log_message(f"Erro ao executar passo ({stype} - {sval}): {e}", "error")

def play_audio_step(filename: str):
    if websocket_loop and active_websockets:
        asyncio.run_coroutine_threadsafe(
            broadcast_ws({"type": "play_audio", "filename": filename}),
            websocket_loop
        )
    else:
        play_audio_file(filename)


def play_audio_file(filename: str):
    # Determine the audio path dynamically
    audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", filename)
    if not os.path.exists(audio_path):
        log_message(f"Erro: Arquivo de áudio não encontrado em {audio_path}", "error")
        return

    log_message(f"Áudio será tocado no site: {filename}", "info")
    # Nota: O áudio é tocado apenas no navegador via WebSocket
    # Não abrimos ficheiros MP3 com aplicações externas
    return

def play_dev_mode_audio(active: bool):
    filename = "modo dev ativado.mp3" if active else "modo dev desativado.mp3"
    threading.Thread(target=play_audio_file, args=(filename,), daemon=True).start()


def close_dev_apps():
    # We scan the steps of action_default_2 (or any action with trigger_value == "2")
    # and find all "app" type steps.
    apps_to_close = ["Antigravity IDE.exe", "opera.exe", "Spotify.exe"]
    
    with config_lock:
        actions = list(config.get("actions", []))
    
    for action in actions:
        if action.get("trigger") == "clap" and action.get("trigger_value") == "2":
            for step in action.get("steps", []):
                if step.get("type") == "app":
                    val = step.get("value", "").strip()
                    if val.lower().endswith(".exe"):
                        exe_name = os.path.basename(val)
                        if exe_name not in apps_to_close:
                            apps_to_close.append(exe_name)
                    elif "spotify" in val.lower():
                        if "Spotify.exe" not in apps_to_close:
                            apps_to_close.append("Spotify.exe")
                    elif "opera" in val.lower():
                        if "opera.exe" not in apps_to_close:
                            apps_to_close.append("opera.exe")
                    elif "antigravity" in val.lower():
                        if "Antigravity IDE.exe" not in apps_to_close:
                            apps_to_close.append("Antigravity IDE.exe")

    log_message(f"Fechando aplicativos do Ei Light: {', '.join(apps_to_close)}", "info")
    for app in apps_to_close:
        try:
            subprocess.run(["taskkill", "/F", "/IM", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Erro ao fechar {app}: {e}")

def execute_action(action: dict, play_sounds: bool = True):
    log_message(f"Disparando Ação: '{action.get('name')}'", "success")
    trigger_glow_effect()
    
    # Execute steps in a separate thread to avoid blocking main loops
    def run():
        for step in action.get("steps", []):
            execute_step(step, play_sounds=play_sounds)
            time.sleep(0.3) # Slight delay between steps for visual progression
            
    threading.Thread(target=run, daemon=True).start()

def normalize_trigger_values(trigger_value: str) -> List[str]:
    return [v.lower().strip() for v in re.split(r"[,;]+", str(trigger_value)) if v.strip()]


def set_system_enabled(enabled: bool):
    global system_enabled
    system_enabled = enabled
    if websocket_loop and active_websockets:
        asyncio.run_coroutine_threadsafe(
            broadcast_ws({"type": "system_status", "enabled": enabled}),
            websocket_loop
        )
    log_message(f"Sistema {'ativado' if enabled else 'desativado'}.", "system")


def is_system_toggle_command(text: str, enable: bool) -> bool:
    text = text.lower()
    if enable:
        return bool(re.search(r"\b(ativar|ativado|ligar|ligado)\b.*\bsistema\b|\bsistema\b.*\b(ativar|ativado|ligar|ligado)\b", text))
    return bool(re.search(r"\b(desativar|desativado|desligar|desligado)\b.*\bsistema\b|\bsistema\b.*\b(desativar|desativado|desligar|desligado)\b", text))


def trigger_actions_by_type(trigger_type: str, trigger_value: str):
    """
    Looks for configured actions matching the trigger type and value.
    For 'speech', does a substring match.
    """
    global dev_mode_active
    triggered_any = False
    
    with config_lock:
        actions = list(config.get("actions", []))
        
    if trigger_type == "clap" and not system_enabled:
        return False

    if trigger_type == "speech":
        normalized_text = trigger_value.lower()
        if system_enabled and is_system_toggle_command(normalized_text, enable=False):
            set_system_enabled(False)
            return True
        if not system_enabled:
            if is_system_toggle_command(normalized_text, enable=True):
                set_system_enabled(True)
                return True
            return False

    for action in actions:
        if action.get("trigger") == trigger_type:
            possible_values = normalize_trigger_values(action.get("trigger_value", ""))
            if not possible_values:
                continue

            if trigger_type == "clap":
                if trigger_value in possible_values:
                    if trigger_value == "2":
                        # Toggle Ei Light state
                        if not dev_mode_active:
                            dev_mode_active = True
                            asyncio.run_coroutine_threadsafe(
                                broadcast_ws({"type": "dev_mode", "active": True}),
                                websocket_loop
                            )
                            execute_action(action, play_sounds=False)
                            if websocket_loop and active_websockets:
                                asyncio.run_coroutine_threadsafe(
                                    broadcast_ws({"type": "play_audio", "filename": "modo dev ativado.mp3"}),
                                    websocket_loop
                                )
                        else:
                            dev_mode_active = False
                            asyncio.run_coroutine_threadsafe(
                                broadcast_ws({"type": "dev_mode", "active": False}),
                                websocket_loop
                            )
                            log_message("Desativando Ei Light...", "warning")
                            def run_deactivate():
                                close_dev_apps()
                                if websocket_loop and active_websockets:
                                    asyncio.run_coroutine_threadsafe(
                                        broadcast_ws({"type": "play_audio", "filename": "modo dev desativado.mp3"}),
                                        websocket_loop
                                    )
                            threading.Thread(target=run_deactivate, daemon=True).start()
                    else:
                        execute_action(action)
                    triggered_any = True
            elif trigger_type == "speech":
                for phrase in possible_values:
                    if phrase and phrase in normalized_text:
                        execute_action(action)
                        triggered_any = True
                        break
                    
    if not triggered_any and trigger_type == "speech":
        log_message(f"Nenhum gatilho correspondente encontrado para a frase falada.", "system")
    return triggered_any

# Sound Monitor & Clap Detection
def audio_monitor_thread():
    global is_listening, audio_stream
    clap_times = []
    last_clap_time = 0.0
    block_count = 0
    
    def callback(indata, frames, time_info, status):
        nonlocal last_clap_time, clap_times, block_count
        if not is_listening:
            return
            
        if status:
            print(f"[Audio Stream Status] {status}")
            
        amplitude = float(np.max(np.abs(indata)))
        
        # Throttle volume level sending to frontend to avoid overloading WebSockets
        # callback is called ~43 times a second with blocksize 1024 at 44.1kHz.
        # Sending every 3rd block is ~14Hz, which is perfect for animations.
        block_count += 1
        if block_count % 3 == 0:
            if websocket_loop and active_websockets:
                asyncio.run_coroutine_threadsafe(
                    broadcast_ws({"type": "volume", "value": amplitude}),
                    websocket_loop
                )
        
        # Clap detection logic
        current_time = time.time()
        threshold = config["settings"]["clap_threshold"]
        delay = config["settings"]["clap_delay"]
        required_count = config["settings"]["clap_count_required"]
        
        # Debounce claps (at least 150ms between claps to reject waveform sub-spikes)
        if amplitude > threshold and (current_time - last_clap_time) > 0.15:
            last_clap_time = current_time
            clap_times.append(current_time)
            log_message(f"Clap detectado! Pico de amplitude: {amplitude:.2f}", "info")
            
            # Keep only claps within the time window
            clap_times = [t for t in clap_times if (current_time - t) <= delay]
            
            if len(clap_times) >= required_count:
                log_message(f"Sucesso: {required_count} Palmas detectadas dentro de {delay}s!", "success")
                trigger_actions_by_type("clap", str(required_count))
                clap_times.clear() # Reset window

    while True:
        if not is_listening or is_calibrating:
            if audio_stream is not None:
                try:
                    audio_stream.stop()
                    audio_stream.close()
                except Exception:
                    pass
                audio_stream = None
            time.sleep(0.3)
            continue
            
        if audio_stream is None:
            mic_idx = config["settings"]["mic_index"]
            try:
                # Open sounddevice stream
                audio_stream = sd.InputStream(
                    device=mic_idx,
                    channels=1,
                    samplerate=44100,
                    blocksize=1024,
                    callback=callback
                )
                audio_stream.start()
                log_message("Captura de Palmas iniciada com sucesso.", "system")
            except Exception as e:
                log_message(f"Erro ao abrir dispositivo de áudio para palmas: {e}", "error")
                is_listening = False
                if websocket_loop and active_websockets:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_ws({"type": "status", "listening": False}),
                        websocket_loop
                    )
                time.sleep(1.0)
                continue
                
        time.sleep(0.5)

# =============================================
# Speech Recognition Thread (continuous)
# =============================================
def speech_recognition_thread():
    """
    Continuously listens for voice commands using Google Speech Recognition.
    Runs in a background thread, independent of clap detection.
    Uses ambient noise calibration for better accuracy.
    """
    recognizer = sr.Recognizer()
    # More aggressive energy threshold — adapts automatically
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.6   # seconds of silence = end of phrase
    recognizer.phrase_threshold = 0.3

    log_message("Reconhecimento de voz iniciado. A calibrar ruído ambiente...", "system")

    while True:
        if not is_listening or is_calibrating:
            time.sleep(0.5)
            continue

        try:
            with sr.Microphone(device_index=config["settings"].get("mic_index")) as source:
                # Calibrate once per session block
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                log_message("Microfone de voz pronto. A escutar frases...", "system")

                while is_listening and not is_calibrating:
                    try:
                        audio = recognizer.listen(
                            source,
                            timeout=2.0,          # check for calibration flag every 2 seconds
                            phrase_time_limit=4.0  # max 4s per phrase
                        )
                    except sr.WaitTimeoutError:
                        continue
                    except OSError:
                        # Mic unplugged or device error — restart outer loop
                        break

                    # Transcribe in a thread so we don't block the mic
                    def transcribe(audio_data):
                        lang = config["settings"].get("speech_language", "pt-PT")
                        try:
                            text = recognizer.recognize_google(audio_data, language=lang)
                            log_message(f"Voz reconhecida: \"{text}\"", "info")
                            trigger_actions_by_type("speech", text.lower())
                        except sr.UnknownValueError:
                            pass  # Unintelligible — ignore silently
                        except sr.RequestError as e:
                            log_message(f"Erro na API de voz (sem internet?): {e}", "error")

                    threading.Thread(target=transcribe, args=(audio,), daemon=True).start()

        except OSError as e:
            log_message(f"Erro ao aceder ao microfone de voz: {e}", "error")
            time.sleep(3.0)  # Wait before retrying
        except Exception as e:
            log_message(f"Erro inesperado no reconhecimento de voz: {e}", "error")
            time.sleep(2.0)

# Models
class SettingsModel(BaseModel):
    mic_index: Optional[int]
    clap_threshold: float
    clap_delay: float
    clap_count_required: int
    speech_language: Optional[str] = "pt-PT"
    speech_phrases: Optional[List[str]] = []
    autostart: Optional[bool] = False

class StepModel(BaseModel):
    type: str # command, url, app
    value: str

class ActionModel(BaseModel):
    id: Optional[str]
    name: str
    trigger: str # clap, speech
    trigger_value: str
    steps: List[StepModel]

class CalibrateModel(BaseModel):
    action_id: str

# REST API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/config")
async def get_config():
    return config

@app.get("/api/mics")
async def get_mics():
    mics_list = []
    try:
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            # We only want input devices
            if dev['max_input_channels'] > 0:
                mics_list.append({
                    "index": idx,
                    "name": dev['name'],
                    "host_api": dev.get('hostapi_name', 'MME') if isinstance(dev.get('hostapi'), str) else sd.query_hostapis(dev['hostapi'])['name']
                })
    except Exception as e:
        print(f"Error querying mics: {e}")
    return mics_list

@app.get("/api/audios")
async def get_audios():
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios")
    os.makedirs(audio_dir, exist_ok=True)
    audio_files = []
    try:
        for file_name in os.listdir(audio_dir):
            full_path = os.path.join(audio_dir, file_name)
            if os.path.isfile(full_path) and file_name.lower().endswith((".mp3", ".wav", ".ogg", ".m4a")):
                audio_files.append(file_name)
    except Exception as e:
        print(f"Error reading audio files: {e}")

    return sorted(audio_files)

@app.post("/api/settings")
async def save_settings(settings: SettingsModel):
    global is_listening, audio_stream
    
    if settings.autostart is not None:
        set_startup(settings.autostart)
        
    with config_lock:
        config["settings"]["mic_index"] = settings.mic_index
        config["settings"]["clap_threshold"] = settings.clap_threshold
        config["settings"]["clap_delay"] = settings.clap_delay
        config["settings"]["clap_count_required"] = settings.clap_count_required
        config["settings"]["speech_language"] = settings.speech_language
        config["settings"]["autostart"] = settings.autostart
        save_config_unsafe()
        
    # Hot-reload audio stream if running
    if is_listening:
        log_message("Reiniciando stream de áudio com as novas configurações...", "system")
        if audio_stream is not None:
            try:
                audio_stream.stop()
                audio_stream.close()
            except Exception:
                pass
            audio_stream = None
            
    await broadcast_ws({"type": "config", "config": config})
    return config["settings"]

@app.post("/api/shutdown")
async def shutdown():
    log_message("Sinal de desligamento recebido. Encerrando o aplicativo...", "warning")
    def run_shutdown():
        time.sleep(1.0)
        os._exit(0)
    threading.Thread(target=run_shutdown, daemon=True).start()
    return {"status": "success", "message": "Desligando o servidor..."}

@app.post("/api/config/action")
async def save_action(action: ActionModel):
    action_dict = action.model_dump()
    
    with config_lock:
        if not action_dict.get("id"):
            action_dict["id"] = "action_" + str(uuid.uuid4())[:8]
            config["actions"].append(action_dict)
            log_message(f"Nova ação criada: '{action_dict['name']}'", "system")
        else:
            # Edit existing action
            found = False
            for idx, act in enumerate(config["actions"]):
                if act.get("id") == action_dict["id"]:
                    config["actions"][idx] = action_dict
                    found = True
                    log_message(f"Ação editada: '{action_dict['name']}'", "system")
                    break
            if not found:
                # If ID was sent but not found, append it
                config["actions"].append(action_dict)
                
        save_config_unsafe()
        
    await broadcast_ws({"type": "config", "config": config})
    return {"status": "success", "action": action_dict}

@app.delete("/api/config/action/{action_id}")
async def delete_action(action_id: str):
    with config_lock:
        actions = config.get("actions", [])
        # Use safe access in case some actions don't have an 'id' field
        new_actions = [act for act in actions if act.get("id") != action_id]
        if len(new_actions) == len(actions):
            raise HTTPException(status_code=404, detail="Action not found")
        config["actions"] = new_actions
        save_config_unsafe()
        
    log_message("Ação removida.", "system")
    await broadcast_ws({"type": "config", "config": config})
    return {"status": "success"}

# =============================================
#  Backup Routes
# =============================================
@app.post("/api/backup/create")
async def backup_create():
    result = create_backup()
    if result["status"] == "success":
        await broadcast_ws({"type": "log", "message": f"✅ Backup criado: {result['backup']}", "level": "success"})
    else:
        await broadcast_ws({"type": "log", "message": f"❌ Erro ao criar backup: {result['detail']}", "level": "error"})
    return result

@app.get("/api/backup/list")
async def backup_list():
    return {"backups": get_backups()}

@app.post("/api/backup/restore/{backup_name}")
async def backup_restore(backup_name: str):
    result = restore_backup(backup_name)
    if result["status"] == "success":
        await broadcast_ws({"type": "config", "config": config})
        await broadcast_ws({"type": "log", "message": f"✅ {result['detail']}", "level": "success"})
    else:
        await broadcast_ws({"type": "log", "message": f"❌ {result['detail']}", "level": "error"})
    return result

@app.post("/api/calibrate/start")
async def start_calibration(body: CalibrateModel):
    global is_calibrating
    action_id = body.action_id
        
    # Find the action to verify it exists
    action_to_calibrate = None
    with config_lock:
        for act in config.get("actions", []):
            if act.get("id") == action_id:
                action_to_calibrate = act
                break
                
    if not action_to_calibrate:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
        
    if action_to_calibrate.get("trigger") != "speech":
        raise HTTPException(status_code=400, detail="Apenas ações de voz podem ser calibradas")
    
    if is_calibrating:
        raise HTTPException(status_code=409, detail="Já existe uma calibração em curso")
        
    # Signal background threads to release the mic
    is_calibrating = True
    log_message("Modo de calibração ativo. A aguardar libertação do microfone...", "system")
    await broadcast_ws({"type": "log", "message": "🎙️ Microfone reservado para calibração. Fale agora!", "level": "system"})
    
    # Give background threads time to exit their mic context (they check flag every 2s)
    await asyncio.sleep(1.5)
    
    transcribed_text = ""
    error_msg = ""
    
    def record_and_transcribe():
        nonlocal transcribed_text, error_msg
        recognizer = sr.Recognizer()
        # Use fixed threshold so it doesn't auto-adjust and cut the recording short
        recognizer.dynamic_energy_threshold = False
        recognizer.energy_threshold = 250
        recognizer.pause_threshold = 0.8   # allow brief natural pauses
        
        mic_idx = config["settings"].get("mic_index")
        try:
            with sr.Microphone(device_index=mic_idx) as source:
                # Calibrate ambient noise before recording (crucial for accuracy)
                log_message("A calibrar ruído ambiente antes da gravação...", "system")
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                log_message("Pronto! Diga agora o comando de voz...", "system")
                # Wait up to 6s to start, allow up to 5s of speech
                audio_data = recognizer.listen(source, timeout=6.0, phrase_time_limit=5.0)
                
            log_message("Áudio capturado. A transcrever...", "system")
            lang = config["settings"].get("speech_language", "pt-PT")
            transcribed_text = recognizer.recognize_google(audio_data, language=lang)
            log_message(f"✅ Transcrição concluída: \"{transcribed_text}\"", "success")
        except sr.WaitTimeoutError:
            error_msg = "Tempo limite excedido. Nenhuma fala foi detetada."
            log_message(error_msg, "error")
        except sr.UnknownValueError:
            error_msg = "Não foi possível compreender o áudio. Tente falar mais perto do microfone."
            log_message(error_msg, "error")
        except sr.RequestError as e:
            error_msg = f"Erro de ligação à API Google Speech: {e}"
            log_message(error_msg, "error")
        except Exception as e:
            error_msg = f"Erro inesperado durante a calibração: {e}"
            log_message(error_msg, "error")
            
    # Run in executor thread to avoid blocking FastAPI event loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, record_and_transcribe)
    
    # Always release calibration mode, even on error
    is_calibrating = False
    log_message("Calibração terminada. Reconhecimento de voz retomado.", "system")
    
    if error_msg:
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {"status": "success", "text": transcribed_text}

@app.post("/api/listening/toggle")
async def toggle_listening_state():
    global is_listening
    is_listening = not is_listening
    state_str = "ATIVADO" if is_listening else "DESATIVADO"
    log_message(f"Monitoramento por áudio {state_str}.", "system")
    await broadcast_ws({"type": "status", "listening": is_listening})
    return {"listening": is_listening}

@app.post("/api/trigger-action/{action_id}")
async def trigger_action(action_id: str):
    action_to_run = None
    with config_lock:
        for act in config.get("actions", []):
            if act.get("id") == action_id:
                action_to_run = act
                break
                
    if not action_to_run:
        raise HTTPException(status_code=404, detail="Action not found")
        
    if action_to_run.get("trigger") == "clap" and action_to_run.get("trigger_value") == "2":
        trigger_actions_by_type("clap", "2")
    else:
        execute_action(action_to_run)
    return {"status": "triggered"}

# WebSocket Handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    
    # Send initial state
    try:
        await websocket.send_json({"type": "config", "config": config})
        await websocket.send_json({"type": "status", "listening": is_listening})
        await websocket.send_json({"type": "dev_mode", "active": dev_mode_active})
        await websocket.send_json({"type": "system_status", "enabled": system_enabled})
        log_message("Novo cliente conectado ao painel.", "system")
        
        while True:
            # Keep connection open, wait for close or message
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        print("Client disconnected from WebSocket.")
    except Exception as e:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        print(f"WebSocket error: {e}")

# Startup Tasks
@app.on_event("startup")
async def startup_event():
    global websocket_loop
    websocket_loop = asyncio.get_event_loop()
    
    # Load settings from file or initialize
    load_config()
    
    # Launch audio threads (clap detection)
    threading.Thread(target=audio_monitor_thread, daemon=True).start()
    threading.Thread(target=speech_recognition_thread, daemon=True).start()
    
    print("\n=======================================================")
    print(" APLICATIVO INICIADO! Acesse o painel em:")
    print(" http://localhost:8000")
    print("=======================================================\n")

if __name__ == "__main__":
    import uvicorn
    # Run server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
