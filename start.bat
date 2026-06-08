@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

TITLE Ei Light — Painel de Controlo

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Ei Light — Iniciando Painel de Controlo            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verifica venv
if not exist venv (
    echo ❌ Ambiente virtual não encontrado!
    echo.
    echo Execute primeiro: install.bat
    echo.
    pause
    exit /b 1
)

REM Ativa venv
call venv\Scripts\activate.bat

REM Executa
echo 🚀 Iniciando Ei Light na porta 8000...
echo 📱 O painel abrirá em: http://localhost:8000
echo.
echo ℹ️  Pressione Ctrl+C para parar o servidor
echo.

python main.py

REM Tratamento de erro
if %errorlevel% neq 0 (
    echo.
    echo ❌ Aplicação encerrou com erro: %errorlevel%
)

echo.
pause
