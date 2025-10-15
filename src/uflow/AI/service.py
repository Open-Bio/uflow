"""AI服务接口"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .config import AIConfig


class AIServiceInterface(ABC):
    """AI服务接口"""
    
    @abstractmethod
    def generate_code(self, prompt: str) -> Optional[str]:
        """直接生成Python节点代码"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        pass


class AIServiceError(Exception):
    """AI服务异常基类"""
    pass


class ConfigurationError(AIServiceError):
    """配置错误"""
    pass


class ValidationError(AIServiceError):
    """验证错误"""
    pass


class NetworkError(AIServiceError):
    """网络错误"""
    pass


class APIError(AIServiceError):
    """API错误"""
    pass
