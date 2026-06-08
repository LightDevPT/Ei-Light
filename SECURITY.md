# 🔒 Política de Segurança - Ei Light

## Elementos Protegidos

Os seguintes elementos **não podem ser modificados** pelos usuários e são protegidos no código:

### 1. **Identidade da Aplicação**
- Nome: "Ei Light"
- Versão
- Descrição da aplicação
- Ícone e logo

### 2. **Configurações de Core**
- Estrutura base de configuração
- Versão do protocolo
- Endpoints da API

### 3. **Integridade do Código**
- Arquivos Python
- Templates HTML
- Folhas de estilo CSS
- Scripts JavaScript (app.js)

## O que Pode Ser Modificado

Os usuários podem **livremente personalizar**:

- ✅ Sensibilidade de detecção de palmas
- ✅ Delay entre palmas
- ✅ Idioma de reconhecimento de voz
- ✅ Frases de comando de voz
- ✅ Ações personalizadas (apps, URLs, comandos)
- ✅ Seleção de microfone
- ✅ Inicialização automática

## Arquivo de Configuração (config.json)

### Estrutura

```
config.json (Não versionado - gitignore)
├── app (PROTEGIDO - não pode ser modificado)
│   ├── name
│   ├── version
│   └── protected: true
├── settings (MODIFICÁVEL)
│   ├── mic_index
│   ├── clap_threshold
│   └── ...
└── actions (MODIFICÁVEL)
    ├── id
    ├── name
    └── steps
```

### Proteção Implementada

1. **Validação na Inicialização**
   - Se `config.json` não existir, é criado a partir de `config.default.json`
   - Se houver alterações em `app.*`, são resetadas automaticamente

2. **Checksum de Integridade**
   - Elementos protegidos possuem hash verificado
   - Qualquer modificação é detectada e corrigida

3. **.gitignore**
   - `config.json` não é versionado
   - Cada instalação tem sua própria configuração

## Instalação Segura

### Primeira Instalação

1. Clone do GitHub
2. Execute: `python setup_config.py`
3. Este script:
   - Verifica integridade
   - Cria `config.json` se necessário
   - Valida dependências
   - Prepara ambiente

### Atualização

1. `git pull` (não afeta `config.json` local)
2. Execute: `python main.py`
3. A aplicação detecta alterações e se auto-repara

## Autenticação e Autorização

- 🔓 **Sem Autenticação**: Painel está protegido por localhost
- 🔐 **Localhost Only**: WebSocket e API apenas em `localhost:8000`
- 🚫 **Não é publicável remotamente**: Use VPN ou SSH para acesso remoto

## Dados Pessoais

### Não Recolhidos
- Credentials
- Dados de uso
- Histórico de ações executadas
- Informações do sistema

### Armazenamento Local
- Configurações em `config.json` (local machine)
- Backups em `backups/` (local machine)
- Logs em `logs/` (local machine)

## Conformidade

- ✅ Sem telemetria
- ✅ Sem analytics
- ✅ Sem rastreamento
- ✅ Totalmente offline (exceto URLs abertas)
- ✅ GDPR compliant

## Reporte de Segurança

Se encontrar uma vulnerabilidade:

1. **NÃO** reporte publicamente
2. Envie um email privado para: `security@yourdomain.com`
3. Descreva a vulnerabilidade
4. Aguarde resposta em 48 horas

## Checklist de Segurança

- [ ] `config.json` não versionado
- [ ] Elementos protegidos imutáveis em produção
- [ ] Sem hardcoding de secrets
- [ ] Validação de entrada em todas as ações
- [ ] HTTPS para URLs externas (quando aplicável)
- [ ] Logs sem informação sensível

## Atualizações de Segurança

Será mantida uma política de:
- Patches de segurança em 24-48 horas
- Comunicação proativa de vulnerabilidades
- Versionamento semântico

---

**Última Atualização**: 2024
**Versão de Política**: 1.0
