# ✅ Checklist: Preparar para GitHub

Antes de fazer push do seu projeto para GitHub, siga este checklist de segurança.

## 🔍 Verificações Críticas

### Configuração Segura

- [ ] **config.json não versionado**: Verificar `.gitignore` contém `config.json`
- [ ] **config.default.json limpo**: Sem paths absolutos, sem usernames
- [ ] **Sem .env files**: `.env` e `*.env` estão em `.gitignore`
- [ ] **Sem venv versionado**: Pasta `venv/` está em `.gitignore`
- [ ] **Sem credenciais**: Não há senhas, tokens ou API keys em nenhum arquivo

### Código

- [ ] **PEP 8 compliant**: Formatação de código consistente
- [ ] **Type hints**: Funções principais têm type hints
- [ ] **Docstrings**: Funções públicas têm documentação
- [ ] **Sem TODOs**: Todos os TODO comments resolvidos ou documentados
- [ ] **Sem debug code**: Sem `print()` desnecessários ou `pdb`

### Documentação

- [ ] **README.md completo**: Instruções claras para setup
- [ ] **SECURITY.md revisto**: Política de segurança atualizada
- [ ] **CONTRIBUTING.md presente**: Guidelines para contribuidores
- [ ] **LICENSE**: MIT License presente e válida
- [ ] **PROJECT.md**: Estrutura do projeto documentada

### Arquivos Necessários

- [ ] `.gitignore` (bem preenchido)
- [ ] `.gitattributes` (line endings configurados)
- [ ] `requirements.txt` (dependências listadas)
- [ ] `config.default.json` (sem dados pessoais)
- [ ] `setup_config.py` (setup script presente)
- [ ] `config_manager.py` (proteção de config)

## 🚀 Preparação Final

### 1. Limpar Repositório Local

```bash
# Remova arquivos pessoais do histórico (se necessário)
git rm --cached config.json
git rm --cached venv/ -r
git commit -m "Remove sensitive files"

# Ou de forma segura:
git clean -fd  # Remove untracked files
```

### 2. Validar Gitignore

```bash
# Verifique o que será enviado
git status

# Nada de pessoal deve aparecer em "Changes to be committed"
```

### 3. Testar em Máquina Limpa (Opcional)

```bash
# Clone em outro diretório para simular novo usuário
git clone ./seu-repo ./teste
cd teste
.\install.bat
.\start.bat
```

### 4. Criar .gitignore Robusto

```
# Executar este comando para remover cached files
git rm -r --cached .
git add .
git commit -m "Update .gitignore"
```

## 📋 Arquivos que NÃO devem ser versionados

```
❌ config.json               (Configuração do usuário)
❌ .env, .env.local          (Variáveis de ambiente)
❌ venv/                     (Ambiente virtual)
❌ __pycache__/              (Cache Python)
❌ *.pyc                     (Compiled Python)
❌ .vscode/, .idea/          (IDE config)
❌ logs/                     (Logs locais)
❌ backups/                  (Backups pessoais)
```

## ✨ Arquivos que DEVEM ser versionados

```
✅ config.default.json       (Padrão seguro)
✅ requirements.txt          (Dependências)
✅ main.py                   (Código principal)
✅ config_manager.py         (Proteção)
✅ setup_config.py           (Setup script)
✅ install.bat, start.bat    (Atalhos)
✅ templates/, static/       (Frontend)
✅ README.md                 (Documentação)
✅ SECURITY.md               (Segurança)
✅ LICENSE                   (Licença)
✅ .gitignore                (Ignore patterns)
```

## 🔐 Verificações de Segurança

### Não deve conter:

```python
# ❌ Hardcoded credentials
api_key = "sk-1234567890"

# ❌ Caminhos absolutos pessoais
path = "C:\\Users\\EuAfo\\..."

# ❌ Usernames no código
username = "EuAfo"

# ❌ Senhas em texto
password = "minha_senha"

# ❌ URLs privadas
url = "https://meu-servidor-privado.com"
```

### Deve conter:

```python
# ✅ Variáveis de ambiente
api_key = os.getenv("API_KEY")

# ✅ Paths relativos
config_path = os.path.join(os.path.dirname(__file__), "config.json")

# ✅ Configuração segura
app_name = "Ei Light"  # Define em config.default.json

# ✅ Localhost por padrão
BASE_URL = "http://localhost:8000"
```

## 📝 Commit Message

Recomendado para o primeiro push:

```bash
git commit -m "Initial commit: Ei Light automation platform

- FastAPI + WebSocket server
- Voice and clap recognition system
- Secure config management
- Windows batch installers
- MIT Licensed"
```

## 🏷️ Release Tags

```bash
# Criar primeira release
git tag -a v2.0 -m "Ei Light v2.0 - Initial GitHub Release"
git push origin v2.0
```

## 📊 Verificação Final

Execute estes comandos antes de fazer push:

```bash
# 1. Verificar status
git status

# 2. Verificar logs (deve estar limpo de dados pessoais)
git log --oneline | head -5

# 3. Verificar .gitignore
cat .gitignore | grep -E "config\.json|venv|\.env"

# 4. Validar Python
python setup_config.py

# 5. Listar arquivos a enviar
git ls-files
```

## ✅ Checklist Final - Antes do Push

```
Git Status:
  [ ] git status está limpo (ou apenas com novos arquivos)
  [ ] Nenhum arquivo pessoal listado

Documentação:
  [ ] README.md escrito e testado
  [ ] SECURITY.md revisto
  [ ] Todos os links funcionam

Configuração:
  [ ] config.json em .gitignore
  [ ] config.default.json sem dados pessoais
  [ ] requirements.txt atualizado

Código:
  [ ] main.py sem prints de debug
  [ ] config_manager.py sem TO-DO
  [ ] Sem paths hardcoded

Segurança:
  [ ] Nenhuma senha em arquivos
  [ ] Nenhum API key exposto
  [ ] Nenhum username pessoal

Permissões:
  [ ] .bat files com permissão de execução
  [ ] Python scripts com encoding utf-8

Pronto?
  [ ] ✨ TUDO VERIFICADO - PODE FAZER PUSH!
```

## 🚀 Fazer Push para GitHub

```bash
# 1. Criar repositório no GitHub

# 2. Adicionar remote
git remote add origin https://github.com/yourusername/ei-light.git

# 3. Fazer push da primeira vez
git branch -M main
git push -u origin main

# 4. Fazer push de tags
git push origin --tags

# 5. Verificar no GitHub
# Abrir: https://github.com/yourusername/ei-light
```

## 📞 Suporte

Se tiver dúvidas durante este processo:

1. Revise [SECURITY.md](SECURITY.md) para políticas
2. Leia [PROJECT.md](PROJECT.md) para estrutura
3. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines

---

**Checklist Versão**: 1.0
**Data**: 2024
**Status**: ✅ Pronto para usar
