"""
Configuration Manager - Protege elementos críticos da aplicação
Garante que nome, versão e settings protegidas não podem ser alteradas
"""

import json
import os
import hashlib
import shutil
from typing import Dict, Any, Optional


class ConfigManager:
    """Gerencia configurações com proteção de elementos críticos"""
    
    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG_FILE = "config.default.json"
    
    # Elementos que NÃO podem ser modificados
    PROTECTED_KEYS = ["app"]
    
    @staticmethod
    def get_config_path() -> str:
        """Retorna caminho do arquivo config.json"""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ConfigManager.CONFIG_FILE)
    
    @staticmethod
    def get_default_config_path() -> str:
        """Retorna caminho do arquivo config.default.json"""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ConfigManager.DEFAULT_CONFIG_FILE)
    
    @staticmethod
    def load_default_config() -> Dict[str, Any]:
        """Carrega configuração padrão protegida"""
        try:
            with open(ConfigManager.get_default_config_path(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.default.json não encontrado!")
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """
        Carrega configuração do usuário com validação de segurança.
        Se o arquivo não existir, cria a partir do padrão.
        """
        config_path = ConfigManager.get_config_path()
        
        # Se não existe, cria a partir do padrão
        if not os.path.exists(config_path):
            default_config = ConfigManager.load_default_config()
            ConfigManager.save_config(default_config)
            print(f"✅ Config criada: {config_path}")
            return default_config
        
        # Carrega e valida
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Valida integridade
            default_config = ConfigManager.load_default_config()
            user_config = ConfigManager._ensure_protected_elements(user_config, default_config)
            
            return user_config
            
        except json.JSONDecodeError:
            print(f"⚠️  Erro ao ler config.json, usando padrão")
            return ConfigManager.load_default_config()
    
    @staticmethod
    def _ensure_protected_elements(user_config: Dict, default_config: Dict) -> Dict:
        """
        Garante que elementos protegidos não foram alterados.
        Se foram, restaura os valores padrão.
        """
        for protected_key in ConfigManager.PROTECTED_KEYS:
            if protected_key in default_config:
                # Restaura valores protegidos se foram alterados
                user_config[protected_key] = default_config[protected_key]
                print(f"🔒 Elemento protegido '{protected_key}' verificado")
        
        return user_config
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> bool:
        """
        Salva configuração com proteção de elementos críticos.
        Não permite modificações em campos protegidos.
        """
        try:
            # Valida antes de salvar
            default_config = ConfigManager.load_default_config()
            
            # Força elementos protegidos
            for protected_key in ConfigManager.PROTECTED_KEYS:
                if protected_key in default_config:
                    config[protected_key] = default_config[protected_key]
            
            config_path = ConfigManager.get_config_path()
            
            # Backup antes de salvar
            if os.path.exists(config_path):
                backup_path = f"{config_path}.bak"
                shutil.copy2(config_path, backup_path)
            
            # Salva com formatação legível
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Config salva: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar config: {e}")
            return False
    
    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        """Obtém uma configuração específica"""
        config = ConfigManager.load_config()
        return config.get("settings", {}).get(key, default)
    
    @staticmethod
    def set_setting(key: str, value: Any) -> bool:
        """Define uma configuração específica (só se não protegida)"""
        if key in ConfigManager.PROTECTED_KEYS:
            print(f"🔒 Não é permitido modificar '{key}'")
            return False
        
        config = ConfigManager.load_config()
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"][key] = value
        return ConfigManager.save_config(config)
    
    @staticmethod
    def get_actions() -> list:
        """Retorna lista de ações configuradas"""
        config = ConfigManager.load_config()
        return config.get("actions", [])
    
    @staticmethod
    def add_action(action: Dict[str, Any]) -> bool:
        """Adiciona uma nova ação"""
        config = ConfigManager.load_config()
        if "actions" not in config:
            config["actions"] = []
        
        config["actions"].append(action)
        return ConfigManager.save_config(config)
    
    @staticmethod
    def update_action(action_id: str, action_data: Dict[str, Any]) -> bool:
        """Atualiza uma ação existente"""
        config = ConfigManager.load_config()
        actions = config.get("actions", [])
        
        for i, action in enumerate(actions):
            if action.get("id") == action_id:
                actions[i].update(action_data)
                config["actions"] = actions
                return ConfigManager.save_config(config)
        
        print(f"❌ Ação '{action_id}' não encontrada")
        return False
    
    @staticmethod
    def delete_action(action_id: str) -> bool:
        """Remove uma ação"""
        config = ConfigManager.load_config()
        actions = config.get("actions", [])
        
        config["actions"] = [a for a in actions if a.get("id") != action_id]
        return ConfigManager.save_config(config)
    
    @staticmethod
    def get_app_info() -> Dict[str, Any]:
        """Retorna informações da aplicação (protegidas)"""
        config = ConfigManager.load_config()
        return config.get("app", {})
    
    @staticmethod
    def reset_to_default() -> bool:
        """
        Reset completo às configurações padrão.
        Mantém elementos protegidos, reseta user settings.
        """
        try:
            default_config = ConfigManager.load_default_config()
            config_path = ConfigManager.get_config_path()
            
            # Backup da config anterior
            if os.path.exists(config_path):
                backup_path = f"{config_path}.before-reset"
                shutil.copy2(config_path, backup_path)
                print(f"💾 Backup criado: {backup_path}")
            
            ConfigManager.save_config(default_config)
            print("✅ Config resetada para padrão")
            return True
        except Exception as e:
            print(f"❌ Erro ao fazer reset: {e}")
            return False
    
    @staticmethod
    def validate_config() -> bool:
        """Valida integridade do config.json"""
        try:
            config = ConfigManager.load_config()
            
            # Verifica estrutura básica
            assert isinstance(config, dict), "Config deve ser um dicionário"
            assert "app" in config, "Config deve conter 'app'"
            assert "settings" in config, "Config deve conter 'settings'"
            assert "actions" in config, "Config deve conter 'actions'"
            
            # Verifica app info
            app_info = config.get("app", {})
            assert app_info.get("protected") == True, "App deve ser marcado como protegido"
            
            print("✅ Config validada com sucesso")
            return True
            
        except AssertionError as e:
            print(f"❌ Config inválida: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False


if __name__ == "__main__":
    # Teste
    print("🧪 Testando ConfigManager...")
    
    # Carrega config
    config = ConfigManager.load_config()
    print(f"App: {config['app']}")
    
    # Tenta modificar elemento protegido (deve falhar)
    print("\n📝 Tentando modificar elemento protegido...")
    ConfigManager.set_setting("version", "1.0")  # Deve ficar como 2.0
    
    # Modifica settings (deve funcionar)
    print("\n✏️  Modificando settings...")
    ConfigManager.set_setting("autostart", True)
    
    # Valida
    print("\n🔍 Validando...")
    ConfigManager.validate_config()
    
    print("\n✨ Teste completo!")
