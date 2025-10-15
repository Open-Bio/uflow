"""AI配置管理模块"""
from dataclasses import dataclass
from typing import Optional
from uflow.ConfigManager import ConfigManager


@dataclass
class AIConfig:
    """AI配置数据类"""
    api_key: str
    base_url: str
    model: str
    max_prompt_length: int = 4000
    max_response_length: int = 8000
    request_timeout: int = 30
    temperature: float = 0.1


class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self):
        self._config = None
        
    def get_config(self) -> AIConfig:
        """获取AI配置"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> AIConfig:
        """从配置文件加载配置"""
        settings = ConfigManager().getSettings("PREFS")
        settings.beginGroup("AI")
        
        api_key = settings.value("OpenAI/api_key", "")
        if not api_key:
            import os
            api_key = os.environ.get("DEEPSEEK_API_KEY", "")
            
        base_url = settings.value("OpenAI/base_url", "https://api.deepseek.com")
        model = settings.value("OpenAI/model", "deepseek-chat")
        
        # 高级配置
        max_prompt_length = settings.value("max_prompt_length", 4000)
        max_response_length = settings.value("max_response_length", 8000)
        request_timeout = settings.value("request_timeout", 30)
        temperature = settings.value("temperature", 0.1)
        
        settings.endGroup()
        
        return AIConfig(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_prompt_length=int(max_prompt_length),
            max_response_length=int(max_response_length),
            request_timeout=int(request_timeout),
            temperature=float(temperature)
        )
    
    def save_config(self, config: AIConfig) -> None:
        """保存配置到文件"""
        settings = ConfigManager().getSettings("PREFS")
        settings.beginGroup("AI")
        
        settings.setValue("OpenAI/api_key", config.api_key)
        settings.setValue("OpenAI/base_url", config.base_url)
        settings.setValue("OpenAI/model", config.model)
        settings.setValue("max_prompt_length", config.max_prompt_length)
        settings.setValue("max_response_length", config.max_response_length)
        settings.setValue("request_timeout", config.request_timeout)
        settings.setValue("temperature", config.temperature)
        
        settings.endGroup()
        self._config = config
    
    def reload_config(self) -> AIConfig:
        """重新加载配置"""
        self._config = None
        return self.get_config()


# 全局配置管理器实例
config_manager = AIConfigManager()
