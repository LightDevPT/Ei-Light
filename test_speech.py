import speech_recognition as sr

def test_speech_recognition():
    r = sr.Recognizer()
    print("=== TESTANDO RECONHECIMENTO DE VOZ ===")
    print("Por favor, certifique-se de que seu microfone está conectado e você tem acesso à internet.")
    
    try:
        with sr.Microphone() as source:
            print("\n1. Calibrando ruído de fundo (silêncio por 1 segundo)...")
            r.adjust_for_ambient_noise(source, duration=1.0)
            print("Calibração concluída.")
            
            print("\n2. Gravando! Fale algo agora (ex: 'Ei Light')...")
            try:
                audio = r.listen(source, timeout=5.0, phrase_time_limit=3.0)
                print("Gravação finalizada. Enviando para transcrição...")
                
                # Google Speech Recognition
                try:
                    text = r.recognize_google(audio, language="pt-BR")
                    print(f"\n=> SUCESSO! Você disse: \"{text}\"")
                except sr.UnknownValueError:
                    print("\n=> Não foi possível entender o áudio (sem palavras reconhecidas).")
                except sr.RequestError as e:
                    print(f"\n=> ERRO na requisição da API: {e}")
            except sr.WaitTimeoutError:
                print("\n=> Tempo esgotado (nenhum som foi capturado nos 5 segundos).")
    except Exception as e:
        print(f"\n=> ERRO Crítico ao acessar o microfone: {e}")

if __name__ == "__main__":
    test_speech_recognition()
