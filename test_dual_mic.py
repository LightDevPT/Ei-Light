import sounddevice as sd
import speech_recognition as sr
import threading
import time
import numpy as np

# Test flags
sd_ok = False
sr_ok = False

def run_sounddevice():
    global sd_ok
    print("[sounddevice] Iniciando captura...")
    def callback(indata, frames, time, status):
        if status:
            print(f"[sounddevice] Status: {status}")
        # Just check amplitude
        amp = np.max(np.abs(indata))
        # Keep it quiet but print occasionally
        # print(f"[sounddevice] Amp: {amp:.4f}")
    
    try:
        with sd.InputStream(channels=1, callback=callback, samplerate=16000, blocksize=1024):
            print("[sounddevice] Captura ativa! Ouvindo por 5 segundos...")
            sd_ok = True
            time.sleep(5)
        print("[sounddevice] Captura finalizada.")
    except Exception as e:
        print(f"[sounddevice] ERRO: {e}")

def run_speech():
    global sr_ok
    print("[speech_rec] Iniciando microphone...")
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("[speech_rec] Ajustando para ruído ambiente...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("[speech_rec] Microfone ativo! Fale algo nos próximos 4 segundos...")
            sr_ok = True
            try:
                audio = r.listen(source, timeout=4, phrase_time_limit=3)
                print("[speech_rec] Áudio capturado. Tentando reconhecer...")
                text = r.recognize_google(audio, language="pt-BR")
                print(f"[speech_rec] Reconhecido: {text}")
            except sr.WaitTimeoutError:
                print("[speech_rec] Tempo esgotado, nenhuma fala detectada.")
            except Exception as e:
                print(f"[speech_rec] Erro no reconhecimento: {e}")
    except Exception as e:
        print(f"[speech_rec] ERRO ao abrir microfone: {e}")

# Run both in threads
t1 = threading.Thread(target=run_sounddevice)
t2 = threading.Thread(target=run_speech)

t1.start()
time.sleep(1) # Start sounddevice first
t2.start()

t1.join()
t2.join()

print(f"\n=== RESULTADOS DO TESTE DUAL-MIC ===")
print(f"sounddevice OK: {sd_ok}")
print(f"speech_recognition OK: {sr_ok}")
