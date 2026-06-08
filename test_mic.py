import sounddevice as sd

try:
    print("=== DISPOSITIVOS DE ÁUDIO DETECTADOS ===")
    devices = sd.query_devices()
    print(devices)
    
    default_input = sd.default.device[0]
    default_output = sd.default.device[1]
    
    print("\n=== PADRÕES ===")
    print(f"Entrada Padrão (Mic): {default_input} - {devices[default_input]['name'] if default_input >= 0 else 'Nenhum'}")
    print(f"Saída Padrão: {default_output} - {devices[default_output]['name'] if default_output >= 0 else 'Nenhum'}")
except Exception as e:
    print(f"Erro ao acessar dispositivos de som: {e}")
