# 📦 Sistema de Backup - Ei Light

## Descrição

O sistema de backup permite guardar, restaurar e gerir cópias de segurança das suas ações de automação. Cada backup preserva a configuração completa das ações, gatilhos e passos.

---

## 🎯 Como Usar

### 1. Criar um Backup

No painel **"Ações de Automação"**, clique no botão **"Backup"** para criar uma cópia instantânea das suas ações atuais.

- Um backup é automaticamente nomeado com data e hora: `config_backup_YYYYMMDD_HHMMSS.json`
- Uma mensagem de confirmação aparecerá no Terminal de Logs
- Os backups são guardados na pasta `backups/` do projeto

### 2. Restaurar um Backup

Clique no botão **"Restaurar"** para abrir a lista de backups disponíveis.

- Cada backup mostra a **data/hora** e o **tamanho** do ficheiro
- Clique no ícone de **rotação** para restaurar um backup específico
- **Importante:** Ao restaurar, a configuração atual é automaticamente guardada como backup
- A restauração é imediata e as mudanças refletem-se em tempo real

### 3. Segurança e Precauções

⚠️ **Recomendações:**

- Crie um backup **antes de fazer mudanças importantes**
- Os backups anteriores ficam guardados (máximo 10 backups por padrão)
- Não elimine manualmente ficheiros na pasta `backups/` (pode quebrar referências)

---

## 📁 Estrutura de Ficheiros

```
Ei Light/
├── config.json              (configuração atual)
├── backups/                 (pasta de backups)
│   ├── config_backup_20260608_100530.json
│   ├── config_backup_20260608_101200.json
│   └── config_backup_20260608_102045.json
├── main.py                  (backend)
├── requirements.txt         (dependências)
└── ...outros ficheiros...
```

---

## 🔧 API Endpoints

### Criar Backup

**POST** `/api/backup/create`

Resposta bem-sucedida:
```json
{
    "status": "success",
    "backup": "config_backup_20260608_143022.json"
}
```

### Listar Backups

**GET** `/api/backup/list`

Resposta:
```json
{
    "backups": [
        {
            "name": "config_backup_20260608_143022.json",
            "date": "08/06/2026 14:30:22",
            "size": "2048 bytes"
        },
        ...
    ]
}
```

### Restaurar Backup

**POST** `/api/backup/restore/{backup_name}`

Exemplo:
```
/api/backup/restore/config_backup_20260608_143022.json
```

Resposta bem-sucedida:
```json
{
    "status": "success",
    "detail": "Backup config_backup_20260608_143022.json restaurado com sucesso"
}
```

---

## 📊 Conteúdo de um Backup

Um ficheiro de backup é uma cópia JSON completa que inclui:

```json
{
  "settings": {
    "mic_index": null,
    "clap_threshold": 0.3,
    "clap_delay": 0.8,
    "clap_count_required": 2,
    "speech_language": "pt-PT",
    "speech_phrases": ["abrir gu", "abrir spotify"],
    "autostart": true
  },
  "actions": [
    {
      "id": "action_default_1",
      "name": "Ativar Ei Light",
      "trigger": "speech",
      "trigger_value": "ei light",
      "steps": [
        {
          "type": "audio",
          "value": "ei light ativado.mp3"
        }
      ]
    },
    ...
  ]
}
```

---

## ⚡ Fluxo de Backup Automático

Quando restaura um backup, o sistema:

1. **Cria um backup automático** da configuração atual
2. **Carrega o ficheiro** do backup selecionado
3. **Atualiza a configuração** em memória e em disco
4. **Envia notificação** via WebSocket para atualizar o interface
5. **Registra o evento** no Terminal de Logs

---

## 🛡️ Limitações e Considerações

- **Sem sincronização**: Os backups são armazenados apenas localmente
- **Sem compressão**: Os ficheiros não são comprimidos (maior tamanho)
- **Sem criptografia**: Os ficheiros JSON são texto plano (proteja a pasta!)
- **Sem histórico automático**: Crie backups manualmente quando necessário

---

## 🔍 Troubleshooting

### "Backup não encontrado"

- Verifique se a pasta `backups/` existe
- Certifique-se que o nome do ficheiro está correto (case-sensitive)

### "Erro ao restaurar"

- Confirme que o ficheiro JSON não foi corrompido
- Tente restaurar um backup mais antigo
- Verifique as permissões de ficheiro

### Backups desaparecem

- Os backups são armazenados na pasta `backups/` relativa ao projeto
- Não execute o projeto de localizações diferentes (altera o diretório de trabalho)

---

## 📝 Boas Práticas

✅ **Faça:**

- Criar um backup antes de modificar ações importantes
- Usar nomes descritivos nas suas ações (facilita a identificação)
- Testar as ações antes de as guardar
- Manter backups regularmente

❌ **Não Faça:**

- Editar manualmente ficheiros JSON na pasta `backups/`
- Eliminar backups sem verificar o conteúdo
- Usar caracteres especiais nos nomes das ações
- Ignorar mensagens de erro durante restauração

---

## 📞 Suporte

Para problemas com o sistema de backup:

1. Verifique o **Terminal de Logs** para mensagens de erro
2. Consulte o terminal do servidor para detalhes técnicos
3. Tente restaurar um backup anterior
4. Reinicie o servidor se houver problemas de sincronização

---

**Última atualização:** 08 de Junho de 2026
