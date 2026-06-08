# 📋 Estrutura do Projeto - Ei Light

## Descrição Geral

Ei Light é uma aplicação de automação por voz e palmas desenvolvida em Python com FastAPI, servindo uma interface web moderna. O projeto foi estruturado para facilitar o desenvolvimento, manutenção e distribuição segura pelo GitHub.

## 🗂️ Estrutura de Diretórios

```
ei-light/
│
├── main.py                  # Aplicação principal (FastAPI + WebSocket)
├── config_manager.py        # Gerenciador de configurações com proteção
├── setup_config.py          # Script de setup e validação
│
├── requirements.txt         # Dependências Python
├── config.default.json      # Configuração padrão (protegida, versionada)
├── config.json             # Configuração do usuário (gitignore, NÃO versionada)
│
├── install.bat             # Instalador para Windows
├── start.bat               # Atalho para iniciar a aplicação
│
├── templates/
│   └── index.html          # Interface web
│
├── static/
│   ├── css/
│   │   └── style.css       # Estilos da aplicação
│   ├── images/             # Logos e ícones
│   └── js/
│       └── app.js          # Lógica frontend (WebSocket)
│
├── audios/                 # Áudios customizados (gitignore para local)
│   └── .gitkeep
├── backups/                # Backups de configuração (gitignore)
│   └── .gitkeep
├── logs/                   # Logs de execução (gitignore)
│   └── .gitkeep
│
├── docs/
│   ├── README.md           # Documentação principal
│   ├── SECURITY.md         # Política de segurança
│   ├── CONTRIBUTING.md     # Guia de contribuição
│   └── PROJECT.md          # Este arquivo
│
├── .gitignore              # O que não versionar
├── .gitattributes          # Configuração de line endings
└── LICENSE                 # Licença MIT
```

## 🔑 Conceitos Chave

### Proteção de Configuração

O projeto usa um sistema de proteção de configurações em duas camadas:

1. **config.default.json** (Versionado)
   - Contém valores protegidos: nome, versão, descrição
   - Define schema padrão
   - Não contém dados pessoais
   - Serve como referência para novos usuários

2. **config.json** (Não versionado - gitignore)
   - Configuração específica de cada instalação
   - Contém dados do usuário e personalizações
   - Gerada automaticamente se não existir
   - Reseta valores protegidos se forem modificados

### Arquitetura da Aplicação

```
Frontend (HTML/CSS/JS)
    ↓ WebSocket
Backend (FastAPI)
    ↓
Config Manager (Proteção)
    ↓
Sistema (Audio, Apps, URLs)
```

## 🔒 Proteção Implementada

### Elementos Imutáveis
- Identificação da app (nome, versão)
- Endpoints base
- Estrutura de configuração

### Validação
- Hash de integridade em `app.*`
- Validação automática na inicialização
- Reset automático se detectada alteração

### Versionamento
- config.default.json: versionado (sempre sincronizado)
- config.json: ignorado (específico de cada máquina)

## 🚀 Fluxo de Inicialização

```
1. User executa install.bat
        ↓
2. Cria venv e instala dependências
        ↓
3. Executa setup_config.py
        ↓
4. Valida e cria config.json
        ↓
5. User executa start.bat
        ↓
6. main.py inicia FastAPI
        ↓
7. Abre http://localhost:8000 no navegador
```

## 📦 Dependências

Listadas em `requirements.txt`:

```
fastapi          - Framework web
uvicorn          - ASGI server
sounddevice      - Captura de áudio
numpy            - Processamento numérico
SpeechRecognition - Reconhecimento de voz
pyaudio          - Interface de áudio
jinja2           - Templates
websockets       - Comunicação real-time
```

## 🎯 Fluxos de Uso Principal

### Fluxo 1: Detecção de Palmas
```
1. Usuário ativa "Listening"
2. Script monitora áudio continuamente
3. Detecta padrão de palmas
4. Executa ação associada
5. Retorna feedback
```

### Fluxo 2: Reconhecimento de Voz
```
1. Usuário fala comando
2. Speech Recognition captura
3. Traduz para texto (português)
4. Procura em speech_phrases
5. Executa ação correspondente
```

### Fluxo 3: Ações Customizadas
```
1. Usuário define ação em UI
2. Config salva com proteção
3. Ao acionar trigger:
   - Executa steps em sequência
   - Suporta: URL, APP, COMMAND
   - Retorna resultado em log
```

## 🛠️ Desenvolvimento

### Setup Local

```bash
# Clone
git clone https://github.com/yourusername/ei-light.git
cd ei-light

# Ambiente
python -m venv venv
venv\Scripts\activate

# Instalar
pip install -r requirements.txt

# Executar
python main.py
```

### Modificar Configuração Padrão

Para adicionar novos campos padrão:

1. Edite `config.default.json`
2. Atualize `config_manager.py` se necessário
3. Teste com `setup_config.py`

### Adicionar Nova Action Type

Em `main.py`:

```python
# Em execute_action()
elif step['type'] == 'new_type':
    # Implementar lógica
    pass
```

### Testes

Execute antes de PR:

```bash
# Validar config
python -c "from config_manager import ConfigManager; ConfigManager.validate_config()"

# Testar setup
python setup_config.py

# Verificar linting
python -m py_compile main.py config_manager.py setup_config.py
```

## 🔄 Ciclo de Release

1. **Desenvolvimento** → Branch feature
2. **Teste Local** → Validações passam
3. **PR** → Code review
4. **Merge** → Main branch
5. **Release** → Tag versão
6. **Distribuição** → GitHub Releases

## 📊 Métricas de Qualidade

- ✅ Python 3.8+ compatível
- ✅ Sem dependências externas perigosas
- ✅ Proteção de dados funcionando
- ✅ Setup automatizado
- ✅ Sem hardcoded credentials
- ✅ GDPR compliant

## 🐛 Common Issues & Soluções

### Issue: config.json corrompido
**Solução:** `python setup_config.py` → Reset automático

### Issue: Microfone não detecta
**Solução:** Verificar em Windows Settings → Sound

### Issue: Porta 8000 já em uso
**Solução:** Editar `main.py` linha uvicorn.run() → mudar porta

## 📝 Checklist para Contribudores

- [ ] Código segue PEP 8
- [ ] Sem modificação de elementos protegidos
- [ ] Config.default.json não modificado (sem motivo)
- [ ] Testes executados localmente
- [ ] Documentação atualizada
- [ ] PR descreve mudanças claras

---

**Última atualização**: 2024
**Versão do Projeto**: 2.0
