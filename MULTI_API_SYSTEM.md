# 🤖 Sistema Multi-API - Documentação

## 📋 Visão Geral

O sistema suporta múltiplas APIs de IA com fallback automático. Se uma API falhar, o sistema tenta automaticamente a próxima.

---

## 🔄 Arquitetura

```
Comando de Voz
      │
      v
┌─────────────────────────┐
│ Procura Ação Local      │
│ (rápido)                │
└─────────────────────────┘
      │ Não encontrado
      v
┌─────────────────────────┐
│ Tenta Gemini API        │ ← Priority 1
└─────────────────────────┘
      │ Falha/erro
      v
┌─────────────────────────┐
│ Tenta OpenAI API        │ ← Priority 2
└─────────────────────────┘
      │ Falha/erro
      v
┌─────────────────────────┐
│ Comando não reconhecido │
└─────────────────────────┘
      │ Sucesso
      v
┌─────────────────────────────┐
│ Valida segurança            │
│ Executa e salva              │
└─────────────────────────────┘
```

---

## 🔧 Configuração Multi-API

### Arquivo `.env`

```env
# API Gemini (Priority: 1)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# API OpenAI (Priority: 2)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

# Ordem de preferência (separadas por vírgula)
AI_PROVIDERS_ORDER=gemini,openai
```

### Função `get_ai_api_key(provider)`

```python
# Obter chave específica
gemini_key = get_ai_api_key("gemini")
openai_key = get_ai_api_key("openai")

# Obter primeira chave disponível
any_key = get_ai_api_key()
```

---

## 🤖 APIs Suportadas

### 1. **Gemini (Google)**
- **Status**: ✅ Implementado
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent`
- **Função**: `query_gemini_api(text, api_key)`
- **Idioma**: Português (PT)

### 2. **OpenAI (ChatGPT)**
- **Status**: ✅ Implementado
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Função**: `query_openai_api(text, api_key)`
- **Modelo**: `gpt-3.5-turbo`
- **Idioma**: English (por padrão, adaptável)

---

## 📋 Prompts de Cada API

### Gemini
- Responde em **Português**
- Formato: JSON com campos `type`, `value`, `name`
- Temperatura: 0.1 (preciso)
- Max tokens: 500

### OpenAI
- Responde em **English**
- Formato: JSON com campos `type`, `value`, `name`
- Temperatura: 0.1 (preciso)
- Max tokens: 500

---

## 🔄 Fallback Automático

Se a API Gemini não responder:
1. ✅ Sistema tenta automaticamente OpenAI
2. ✅ Se OpenAI também falhar, retorna `None`
3. ✅ Processo é transparente para o usuário
4. ✅ Logs mostram qual API foi utilizada

### Exemplo de Log

```
🔧 Consultando GEMINI API para: "abrir youtube"
⚠️ Erro ao chamar Gemini API: [erro]
🔧 Consultando OPENAI API para: "abrir youtube"
✓ Resposta recebida de OPENAI
```

---

## 🛡️ Segurança

✅ **Validação de Ações**
- `is_safe_ai_action()` valida todas as ações propostas
- Apenas URLs `https://...` são permitidas
- Aplicações estão em whitelist
- Comandos shell precisam de prefixos conhecidos

✅ **Proteção de API Keys**
- Chaves armazenadas em `.env` (não no código)
- Fallback para `config.json` como último recurso
- Variáveis de ambiente têm prioridade

---

## 💾 Persistência

### Como Funciona

1. Usuário dá comando de voz desconhecido: "abrir spotify"
2. Sistema consulta API (Gemini/OpenAI)
3. API retorna: `{"type": "app", "value": "spotify.exe", "name": "Spotify"}`
4. Ação é validada e executada
5. **Ação é salva em `config.json`**
6. Próxima vez que disser "abrir spotify", será reconhecido localmente

### Arquivo Config

```json
{
  "actions": [
    {
      "id": "auto_speech_abc123",
      "name": "Abrir Spotify",
      "trigger": "speech",
      "trigger_value": "abrir spotify",
      "steps": [{"type": "app", "value": "spotify.exe"}]
    }
  ]
}
```

---

## 📊 Estatísticas de API

| API | Provider | Latência | Custo | Idioma |
|-----|----------|----------|-------|--------|
| Gemini | Google | ~1-2s | Gratuito* | PT/EN |
| OpenAI | OpenAI | ~1-3s | Pago | EN |

*Gemini tem limite de requisições gratuitas

---

## 🔍 Debugging

### Ver qual API será usada

```python
from dotenv import load_dotenv
import os

load_dotenv(".env")
providers = os.getenv("AI_PROVIDERS_ORDER", "gemini,openai").split(",")
providers = [p.strip().lower() for p in providers if p.strip()]
print(f"Providers: {providers}")
```

### Testar uma API específica

```bash
python test_multi_api.py
```

### Logs do Sistema

O sistema escreve logs detalhados:
- `[🔧] Consultando X API para: "..."`
- `[✓] Resposta recebida de X`
- `[⚠️] Erro ao chamar X API: ...`

---

## ⚙️ Configurações Avançadas

### Mudar Ordem de Providers

Em `.env`:
```env
# Tentar OpenAI primeiro, depois Gemini
AI_PROVIDERS_ORDER=openai,gemini
```

### Usar Apenas Uma API

```env
# Só usar Gemini
AI_PROVIDERS_ORDER=gemini

# Só usar OpenAI
AI_PROVIDERS_ORDER=openai
```

### Salvar API Key Automaticamente

```python
from main import save_ai_api_key
save_ai_api_key("sk-nova-chave-aqui")
```

---

## 🚀 Exemplo de Uso Completo

### 1. **Configuração Inicial (.env)**
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
AI_PROVIDERS_ORDER=gemini,openai
```

### 2. **Executar Sistema**
```bash
python main.py
```

### 3. **Testar Voz**
- Diga: "Abrir Spotify"
- Sistema: ✓ Encontrado localmente (se foi salvo antes)
- ou
- Sistema: 🔧 Consultando API (se for novo)
- Sistema: ✓ Ação salva para próxima vez

---

## 🐛 Troubleshooting

### Erro: "API key not found"
- Verifique se `.env` existe e tem `GEMINI_API_KEY=...`
- Verifique se a variável de ambiente está configurada: `$env:GEMINI_API_KEY`

### Erro: "Invalid response format"
- A API retornou um formato inesperado
- Verifique os logs para mais detalhes
- Tente novamente (pode ser falha temporária)

### Comando não foi reconhecido
- Sistema tentou todas as APIs
- Nenhuma conseguiu gerar uma ação válida
- Tente ser mais específico no comando

---

## 📞 Suporte

Para problemas com:
- **Gemini API**: https://ai.google.dev/support
- **OpenAI API**: https://help.openai.com

