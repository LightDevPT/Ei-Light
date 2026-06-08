@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

TITLE Ei Light — Instalador

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Ei Light — Setup de Instalação                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não foi encontrado no PATH!
    echo.
    echo Instale Python 3.8+ de: https://www.python.org/downloads/
    echo Certifique-se de assinalar "Add Python to PATH" durante instalação
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM PASSO 1: Ambiente Virtual
echo 📦 [PASSO 1/3] Criando ambiente virtual...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
) else (
    echo ✅ Ambiente virtual já existe
)

REM PASSO 2: Instalar dependências
echo.
echo 📥 [PASSO 2/3] Instalando dependências...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)
echo ✅ Dependências instaladas

REM PASSO 3: Setup Config
echo.
echo ⚙️  [PASSO 3/3] Configurando aplicação...
python setup_config.py

if errorlevel 1 (
    echo ⚠️  Aviso: Algumas configurações podem não ter sido completadas
)

REM Sucesso
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✨ Instalação Completa!                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Para iniciar: execute start.bat
echo.
pause
exit /b 0
