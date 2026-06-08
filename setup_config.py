"""
Setup de Configuração - Ei Light
Instala e valida o ambiente
"""

import os
import sys
import subprocess
import json
from config_manager import ConfigManager


def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")


def print_error(text: str):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")


def print_info(text: str):
    """Imprime mensagem de informação"""
    print(f"ℹ️  {text}")


def check_python():
    """Verifica versão do Python"""
    print_header("Verificando Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ necessário. Você tem: {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def check_venv():
    """Verifica se está em ambiente virtual"""
    print_header("Verificando Ambiente Virtual")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print_info("Não está em um venv ativo")
        print_info("Recomendado usar: venv\\Scripts\\activate")
        return False
    
    print_success("Ambiente virtual ativo")
    return True


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print_header("Verificando Dependências")
    
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'sounddevice': 'sounddevice',
        'numpy': 'numpy',
        'SpeechRecognition': 'speech_recognition',
        'pyaudio': 'pyaudio',
        'jinja2': 'jinja2',
        'websockets': 'websockets'
    }
    
    missing = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_success(f"{package} instalado")
        except ImportError:
            print_error(f"{package} não encontrado")
            missing.append(package)
    
    if missing:
        print_info(f"\nPacotes em falta: {', '.join(missing)}")
        return False
    
    return True


def install_dependencies():
    """Instala dependências do requirements.txt"""
    print_header("Instalando Dependências")
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print_error(f"requirements.txt não encontrado em {requirements_file}")
        return False
    
    try:
        print_info("Instalando pacotes...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print_success("Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao instalar: {e}")
        return False


def setup_config():
    """Setup do arquivo de configuração"""
    print_header("Configurando Arquivo de Configuração")
    
    try:
        # Carrega ou cria config
        config = ConfigManager.load_config()
        print_success("Arquivo de configuração preparado")
        
        # Valida
        if ConfigManager.validate_config():
            print_success("Configuração validada")
        else:
            print_error("Configuração inválida - resetando para padrão")
            ConfigManager.reset_to_default()
        
        return True
    except Exception as e:
        print_error(f"Erro ao configurar: {e}")
        return False


def check_microphone():
    """Verifica se há microfone disponível"""
    print_header("Verificando Microfone")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        
        if not input_devices:
            print_error("Nenhum microfone detectado")
            return False
        
        print_success(f"{len(input_devices)} microfone(s) detectado(s):")
        for i in input_devices:
            print(f"  [{i}] {devices[i]['name']}")
        
        return True
    except Exception as e:
        print_error(f"Erro ao verificar microfone: {e}")
        return False


def create_directories():
    """Cria diretórios necessários"""
    print_header("Preparando Diretórios")
    
    directories = ['audios', 'backups', 'logs']
    
    for directory in directories:
        dir_path = os.path.join(os.path.dirname(__file__), directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print_success(f"Diretório criado: {directory}/")
        else:
            print_info(f"Diretório já existe: {directory}/")
    
    return True


def display_summary(results: dict):
    """Exibe resumo do setup"""
    print_header("Resumo da Instalação")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check, result in results.items():
        status = "✅" if result else "⚠️ "
        print(f"{status} {check}")
    
    print(f"\nTotal: {passed}/{total} ✓")
    
    if passed == total:
        print_success("Setup completo! Pronto para usar.")
        print_info("Execute: python main.py")
    else:
        print_error("Alguns passos não foram completados.")


def main():
    """Executa setup completo"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         Ei Light — Setup de Configuração                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Verificações
    results['Python 3.8+'] = check_python()
    results['Ambiente Virtual'] = check_venv()
    
    # Se não tem dependências, tenta instalar
    if not check_dependencies():
        print_info("\nTentando instalar dependências...")
        if install_dependencies():
            results['Dependências'] = True
        else:
            results['Dependências'] = False
    else:
        results['Dependências'] = True
    
    # Setup
    results['Configuração'] = setup_config()
    results['Diretórios'] = create_directories()
    results['Microfone'] = check_microphone()
    
    # Resumo
    display_summary(results)
    
    # Retorna status geral
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
