# Contribuindo para Ei Light

Obrigado por considerar contribuir para o Ei Light! Qualquer ajuda é bem-vinda.

## 🐛 Reportar Bugs

Antes de criar um bug report, verifique a lista de issues - o seu problema pode já ter sido reportado.

Se você encontrou um bug:
- Use um título descritivo
- Descreva os passos exatos para reproduzir
- Forneça exemplos específicos
- Descreva o comportamento observado
- Descreva o que você esperava ver
- Inclua screenshots se possível

## ✨ Sugerir Features

Para sugerir features:
- Use um título descritivo
- Descreva a funcionalidade em detalhes
- Liste alguns exemplos de use cases
- Explique por que seria útil

## 🔧 Desenvolvendo

### Setup Local

1. Fork o repositório
2. Clone sua fork
3. Crie um venv: `python -m venv venv`
4. Ative: `venv\Scripts\activate`
5. Instale: `pip install -r requirements.txt`
6. Execute: `python main.py`

### Estrutura do Projeto

```
ei-light/
├── main.py                 # Aplicação principal (FastAPI)
├── config_manager.py       # Gerenciador de configurações
├── setup_config.py         # Setup inicial
├── config.default.json     # Configuração padrão (protegida)
├── config.json            # Configuração do usuário (não versionada)
├── templates/
│   └── index.html         # Interface Web
├── static/
│   ├── css/               # Estilos
│   └── js/                # Scripts frontend
└── audios/                # Áudios customizados
```

### Padrões de Código

- Use Python 3.8+
- Siga PEP 8
- Documente funções públicas
- Use type hints
- Teste localmente antes de fazer PR

### Fazendo Commit

- Commits em português ou inglês
- Mensagens descritivas
- Um commit lógico por mudança

### Pull Requests

1. Atualize a documentação se necessário
2. Inclua screenshots para mudanças UI
3. Mantenha PRs focadas e simples
4. Descreva o problema que resolve

## 📝 Guidelines

### Não Modifique:
- Arquivos do core (`main.py` - estrutura base)
- Elementos protegidos (nome, versão)
- `config.default.json` (sem motivo forte)

### Mantenha:
- Compatibilidade com Python 3.8+
- Segurança (sem hardcode de secrets)
- Compatibilidade com Windows 10/11
- Proteção de configurações

## 🎯 Áreas de Contribuição

### Código
- Bug fixes
- Novas actions
- Melhorias de performance
- Suporte para novos idiomas de voz

### Documentação
- Melhorias no README
- Guias de uso
- Tradução de documentação
- Exemplos de ações

### Testes
- Testes unitários
- Testes de integração
- Relatórios de bugs

## ❓ Dúvidas?

- Abra uma discussion no repositório
- Leia o SECURITY.md para política de segurança

---

**Obrigado por contribuir! 🎉**
