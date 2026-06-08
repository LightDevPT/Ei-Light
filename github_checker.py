"""
GitHub Readiness Checker - Ei Light
Verifica se o projeto está pronto para ser publicado no GitHub
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


class GitHubChecker:
    """Verifica se projeto está seguro para publicar no GitHub"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
    
    def print_header(self, text: str):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_section(self, text: str):
        print(f"\n📋 {text}")
        print("-" * 60)
    
    def check_gitignore(self) -> bool:
        """Verifica se .gitignore está bem configurado"""
        self.print_section("Verificando .gitignore")
        
        gitignore_path = self.root / ".gitignore"
        if not gitignore_path.exists():
            self.errors.append("❌ .gitignore não encontrado")
            return False
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        critical_ignores = ['config.json', 'venv/', '.env', '__pycache__']
        
        for ignore_pattern in critical_ignores:
            if ignore_pattern in content:
                self.passed.append(f"✅ .gitignore contém '{ignore_pattern}'")
            else:
                self.warnings.append(f"⚠️  .gitignore não contém '{ignore_pattern}'")
        
        return len([x for x in critical_ignores if x in content]) == len(critical_ignores)
    
    def check_config_files(self) -> bool:
        """Verifica arquivos de configuração"""
        self.print_section("Verificando Arquivos de Configuração")
        
        all_good = True
        
        # config.default.json deve existir
        default_config = self.root / "config.default.json"
        if default_config.exists():
            self.passed.append("✅ config.default.json encontrado")
            
            # Verifica se não tem dados pessoais
            with open(default_config, 'r') as f:
                content = f.read().lower()
            
            personal_strings = ['euafo', 'C:\\Users\\', 'appdata', 'spotify:', 'opera.exe']
            found_personal = [s for s in personal_strings if s.lower() in content]
            
            if found_personal:
                self.errors.append(f"❌ config.default.json contém dados pessoais: {found_personal}")
                all_good = False
            else:
                self.passed.append("✅ config.default.json limpo de dados pessoais")
        else:
            self.errors.append("❌ config.default.json não encontrado")
            all_good = False
        
        # config.json não deve ser versionado
        config = self.root / "config.json"
        if config.exists():
            # Tenta verificar se está em git
            try:
                result = subprocess.run(
                    ['git', 'ls-files', 'config.json'],
                    cwd=str(self.root),
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    self.errors.append("❌ config.json está versionado (deve estar em .gitignore)")
                    all_good = False
                else:
                    self.passed.append("✅ config.json não está versionado")
            except:
                self.warnings.append("⚠️  Não consegui verificar versionamento (git não disponível)")
        
        return all_good
    
    def check_sensitive_data(self) -> bool:
        """Verifica se não há dados sensíveis nos arquivos"""
        self.print_section("Verificando Dados Sensíveis")
        
        python_files = list(self.root.glob("*.py"))
        html_files = list(self.root.glob("templates/*.html"))
        json_files = list(self.root.glob("*.json"))
        
        sensitive_patterns = [
            ('password', 'Senha/Password hardcoded'),
            ('api_key', 'API Key hardcoded'),
            ('secret', 'Secret hardcoded'),
            ('C:\\Users\\', 'Path absoluto pessoal'),
            ('token =', 'Token hardcoded'),
            ('euafo', 'Username pessoal'),
        ]
        
        found_sensitive = False
        all_files = python_files + html_files + json_files
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, description in sensitive_patterns:
                        if pattern.lower() in content.lower():
                            # Verificar se não é apenas um comentário ou exemplo
                            if not any(x in content for x in ['example', '#', '//']) or \
                               (f'{pattern} =' in content and '{' not in content):
                                self.errors.append(f"❌ {file_path.name}: Possível {description}")
                                found_sensitive = True
            except:
                pass
        
        if not found_sensitive:
            self.passed.append("✅ Nenhum dado sensível detectado")
        
        return not found_sensitive
    
    def check_required_files(self) -> bool:
        """Verifica se todos os arquivos necessários existem"""
        self.print_section("Verificando Arquivos Necessários")
        
        required_files = {
            'README.md': 'Documentação principal',
            'SECURITY.md': 'Política de segurança',
            'CONTRIBUTING.md': 'Guia de contribuição',
            'LICENSE': 'Licença',
            'requirements.txt': 'Dependências',
            'main.py': 'Código principal',
            'config_manager.py': 'Gerenciador de config',
            'setup_config.py': 'Script de setup',
            '.gitignore': 'Git ignore',
            '.gitattributes': 'Git attributes',
        }
        
        all_exist = True
        for filename, description in required_files.items():
            if (self.root / filename).exists():
                self.passed.append(f"✅ {filename} ({description})")
            else:
                self.errors.append(f"❌ {filename} NÃO encontrado ({description})")
                all_exist = False
        
        return all_exist
    
    def check_code_quality(self) -> bool:
        """Verifica qualidade básica do código"""
        self.print_section("Verificando Qualidade do Código")
        
        python_files = list(self.root.glob("*.py"))
        all_good = True
        
        for py_file in python_files:
            # Verificar encoding
            with open(py_file, 'rb') as f:
                content = f.read()
                if b'# -*- coding:' not in content and b'# coding:' not in content:
                    self.warnings.append(f"⚠️  {py_file.name}: Sem declaração de encoding")
            
            # Verificar se é válido Python
            try:
                compile(open(py_file, 'r', encoding='utf-8').read(), str(py_file), 'exec')
                self.passed.append(f"✅ {py_file.name}: Sintaxe válida")
            except SyntaxError as e:
                self.errors.append(f"❌ {py_file.name}: Erro de sintaxe - {e}")
                all_good = False
        
        return all_good
    
    def check_git_status(self) -> bool:
        """Verifica status do repositório git"""
        self.print_section("Verificando Git Status")
        
        try:
            # Verifica se é um repo git
            result = subprocess.run(
                ['git', 'status'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warnings.append("⚠️  Não é um repositório Git")
                return False
            
            # Verifica se há commits
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.passed.append("✅ Repositório Git inicializado")
            else:
                self.warnings.append("⚠️  Nenhum commit realizado ainda")
            
            # Verifica status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.warnings.append(f"⚠️  {len(result.stdout.split(chr(10)))} arquivos não commitados")
            else:
                self.passed.append("✅ Repositório limpo")
            
            return True
        except FileNotFoundError:
            self.warnings.append("⚠️  Git não está instalado")
            return False
    
    def run_all_checks(self) -> bool:
        """Executa todos os checks"""
        self.print_header("🔍 GitHub Readiness Checker - Ei Light")
        
        print("Verificando se seu projeto está pronto para GitHub...\n")
        
        results = []
        results.append(("Arquivos Necessários", self.check_required_files()))
        results.append((".gitignore", self.check_gitignore()))
        results.append(("Arquivos de Config", self.check_config_files()))
        results.append(("Dados Sensíveis", self.check_sensitive_data()))
        results.append(("Qualidade de Código", self.check_code_quality()))
        results.append(("Status Git", self.check_git_status()))
        
        # Resumo
        self.print_header("📊 Relatório Final")
        
        if self.passed:
            print("✅ PASSOU:")
            for msg in self.passed:
                print(f"  {msg}")
        
        if self.warnings:
            print("\n⚠️  AVISOS:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\n❌ ERROS:")
            for msg in self.errors:
                print(f"  {msg}")
        
        # Status geral
        print(f"\n{'='*60}")
        total = len(self.passed) + len(self.warnings) + len(self.errors)
        passed = len(self.passed)
        
        if not self.errors:
            print(f"✨ PRONTO PARA GITHUB! ({passed}/{total} verificações)")
            print("\nPróximos passos:")
            print("  1. git add .")
            print("  2. git commit -m 'Initial commit'")
            print("  3. git push -u origin main")
            return True
        else:
            print(f"⚠️  PROBLEMAS ENCONTRADOS ({len(self.errors)} críticos)")
            print("\nCorreja os erros acima antes de fazer push!")
            return False
    
    def export_report(self, filename: str = "github_check_report.txt"):
        """Exporta relatório para arquivo"""
        with open(self.root / filename, 'w', encoding='utf-8') as f:
            f.write("GitHub Readiness Report - Ei Light\n")
            f.write(f"{'='*60}\n\n")
            
            f.write("✅ PASSOU:\n")
            for msg in self.passed:
                f.write(f"  {msg}\n")
            
            f.write(f"\n⚠️  AVISOS:\n")
            for msg in self.warnings:
                f.write(f"  {msg}\n")
            
            f.write(f"\n❌ ERROS:\n")
            for msg in self.errors:
                f.write(f"  {msg}\n")


if __name__ == "__main__":
    checker = GitHubChecker()
    success = checker.run_all_checks()
    
    # Exportar relatório
    checker.export_report()
    print(f"\n📄 Relatório salvo em: github_check_report.txt")
    
    sys.exit(0 if success else 1)
