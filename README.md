# Ei Light — Painel de Automação por Voz e Palmas

Automatize suas aplicações com reconhecimento de voz e detecção de palmas. Controle seu ambiente de desenvolvimento de forma intuitiva.

## 🌟 Características

- **Reconhecimento de Palmas**: Detecte sequências de palmas personalizadas
- **Reconhecimento de Voz**: Acione ações por comandos de voz em português
- **Automação Flexível**: Configure ações personalizadas para abrir apps, URLs ou executar comandos
- **Interface Web**: Painel de controlo elegante e responsivo
- **Inicialização Automática**: Inicie a aplicação com Windows

## 📋 Requisitos

- Python 3.8+
- Microfone conectado
- Windows 10/11

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/yourusername/ei-light.git
cd ei-light
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Inicie a aplicação

**Opção 1: Usando o arquivo batch**
```bash
start.bat
```

**Opção 2: Direto com Python**
```bash
python main.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8000`

## 🎯 Primeira Utilização

1. **Selecione o Microfone**: No painel, escolha o microfone correto
2. **Configure as Palmas**: Ajuste limiar e quantidade de palmas necessárias
3. **Configure a Voz**: Ative o reconhecimento de voz e adicione frases
4. **Adicione Ações**: Crie ações personalizadas (abrir apps, URLs, comandos)

## 📝 Configuração

A configuração principal fica em `config.json`. Para resetar à configuração padrão:

```bash
python setup_config.py
```

### Estrutura do config.json

```json
{
  "app": {
    "name": "Ei Light",
    "version": "2.0",
    "protected": true
  },
  "settings": {
    "mic_index": null,
    "clap_threshold": 0.3,
    "clap_delay": 0.8,
    "clap_count_required": 2,
    "speech_language": "pt-PT",
    "autostart": false
  },
  "actions": []
}
```

## 🎛️ Tipos de Ações Disponíveis

### URL
Abre um link no navegador padrão
```json
{
  "type": "url",
  "value": "https://github.com"
}
```

### APP
Abre uma aplicação instalada
```json
{
  "type": "app",
  "value": "C:\\Users\\YourUser\\AppData\\Local\\Programs\\YourApp\\app.exe"
}
```

### COMMAND
Executa um comando PowerShell
```json
{
  "type": "command",
  "value": "powershell -Command \"Get-ChildItem\""
}
```

## 🔒 Segurança

- **Configurações Protegidas**: Elementos core como nome e versão do app não podem ser modificados
- **config.json Ignorado**: Suas configurações pessoais não são sincronizadas ao GitHub
- **Sem Dados Sensíveis**: O repositório não contém paths absolutos ou credenciais

## 📱 Painel de Controlo

O painel oferece:

- 📊 Visualizador de áudio em tempo real
- 🎙️ Seletor de microfone
- 🔧 Ajustes para palmas e voz
- ⚡ Gerenciador de ações
- 💾 Sistema de backup de configurações
- 🔌 Status de conexão WebSocket

## 🐛 Troubleshooting

### Microfone não detectado
1. Verifique se o microfone está conectado
2. Teste o microfone em Configurações do Windows
3. Reinicie a aplicação

### Reconhecimento de voz impreciso
1. Ajuste o idioma em Configurações
2. Fale claramente
3. Aumente o microfone em volume

### Porta 8000 já em uso
A aplicação usa a porta 8000 por padrão. Se já estiver em uso:
```bash
# Edite main.py e mude: uvicorn.run(app, host="127.0.0.1", port=8001)
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## ✨ Créditos

Desenvolvido com ❤️ para automação inteligente

---

**Suporte**: Para questões, abra uma [issue](https://github.com/yourusername/ei-light/issues)
