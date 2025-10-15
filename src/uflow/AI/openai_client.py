import json
import os
import urllib.request
import urllib.parse
import re
import time
import threading
from typing import Optional, Dict, Any
from .config import config_manager
from .service import (
    AIServiceInterface,
    AIServiceError,
    ConfigurationError,
    ValidationError,
    NetworkError,
    APIError,
)


class OpenAIClient(AIServiceInterface):
    """安全的OpenAI客户端，支持输入验证和错误处理"""

    # 常量定义
    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"
    MAX_PROMPT_LENGTH = 4000
    MAX_RESPONSE_LENGTH = 8000
    REQUEST_TIMEOUT = 30

    def __init__(self):
        """初始化OpenAI客户端"""
        self._config = config_manager.get_config()
        self._validate_config()
        self._last_request_time = 0
        self._rate_limit_lock = threading.Lock()

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            self._validate_config()
            return True
        except (ConfigurationError, ValidationError):
            return False

    def _validate_config(self) -> None:
        """验证配置"""
        if not self._config.api_key:
            raise ConfigurationError("API密钥未配置")
        if not isinstance(self._config.api_key, str):
            raise ConfigurationError("API密钥必须是字符串")
        if len(self._config.api_key) < 20:
            raise ConfigurationError("API密钥格式无效，长度不足")
        if len(self._config.api_key) > 200:
            raise ConfigurationError("API密钥格式无效，长度过长")
        # 检查API密钥格式（通常以sk-开头）
        if not self._config.api_key.startswith(("sk-", "pk-")):
            raise ConfigurationError("API密钥格式无效，应以sk-或pk-开头")

        # 验证URL
        parsed = urllib.parse.urlparse(self._config.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ConfigurationError("基础URL格式无效")
        if parsed.scheme not in ["http", "https"]:
            raise ConfigurationError("基础URL必须使用HTTP或HTTPS协议")

        # 验证模型名称
        if re.search(r'[<>"\']', self._config.model):
            raise ConfigurationError("模型名称包含非法字符")

    def _validate_prompt(self, prompt: str) -> str:
        """验证用户输入"""
        if not prompt:
            raise ValidationError("提示词不能为空")
        if not isinstance(prompt, str):
            raise ValidationError("提示词必须是字符串")
        if len(prompt) > self._config.max_prompt_length:
            raise ValidationError(
                f"提示词过长，最大长度: {self._config.max_prompt_length}"
            )
        if len(prompt) < 3:
            raise ValidationError("提示词过短，至少需要3个字符")

        # 检查是否包含恶意代码
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"data:text/html",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"compile\s*\(",
            r"open\s*\(",
            r"file\s*\(",
            r"input\s*\(",
            r"raw_input\s*\(",
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                raise ValidationError("提示词包含潜在危险内容")

        # 检查是否包含过多特殊字符
        special_char_count = len(re.findall(r"[^\w\s\u4e00-\u9fff]", prompt))
        if special_char_count > len(prompt) * 0.3:
            raise ValidationError("提示词包含过多特殊字符")

        return prompt.strip()

    def _validate_generated_code(self, code: str) -> None:
        """验证生成的代码安全性"""
        if not code:
            raise ValidationError("生成的代码为空")

        # 检查危险函数调用
        dangerous_functions = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"compile\s*\(",
            r"open\s*\(",
            r"file\s*\(",
            r"input\s*\(",
            r"raw_input\s*\(",
            r"os\.system\s*\(",
            r"subprocess\s*\(",
            r"urllib\s*\(",
            r"requests\s*\(",
            r"socket\s*\(",
            r"shutil\s*\(",
        ]

        for pattern in dangerous_functions:
            if re.search(pattern, code, re.IGNORECASE):
                raise ValidationError(f"生成的代码包含危险函数: {pattern}")

        # 检查是否包含执行流相关代码（违反纯函数原则）
        exec_patterns = [
            r"ExecPin",
            r"outExec",
            r"inExec",
            r"\.call\s*\(",
        ]

        for pattern in exec_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise ValidationError(f"生成的代码包含执行流相关代码: {pattern}")

        # 检查代码长度
        if len(code) > 10000:
            raise ValidationError("生成的代码过长")

        # 检查是否包含必要的函数
        if "def prepareNode" not in code:
            raise ValidationError("生成的代码缺少prepareNode函数")
        if "def compute" not in code:
            raise ValidationError("生成的代码缺少compute函数")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config.api_key}",
        }

    def generate_code(self, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """直接生成Python节点代码"""
        # 验证输入
        validated_prompt = self._validate_prompt(user_prompt)

        last_error = None
        for attempt in range(max_retries):
            try:
                return self._make_api_request(validated_prompt)
            except (NetworkError, APIError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    import time

                    time.sleep(2**attempt)  # 指数退避
                    continue
                else:
                    raise e
            except Exception as e:
                raise e

        if last_error:
            raise last_error
        return None

    def _make_api_request(self, validated_prompt: str) -> str:
        """执行API请求"""
        # 请求限流：每秒最多1个请求
        with self._rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < 1.0:
                time.sleep(1.0 - time_since_last)
            self._last_request_time = time.time()

        url = f"{self._config.base_url}/v1/chat/completions"
        body = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是 uflow 纯函数节点生成器。只生成纯函数节点，不包含执行流。"
                        "代码格式："
                        "from uflow.Core.Common import *\n"
                        "def prepareNode(node):\n"
                        "    # 创建输入引脚\n"
                        '    node.createInputPin(pinName="input_name", dataType="StringPin", callback=None)\n'
                        "    # 创建输出引脚\n"
                        '    node.createOutputPin(pinName="output_name", dataType="StringPin")\n'
                        "def compute(node):\n"
                        "    # 读取输入\n"
                        '    input_name = node.getData("input_name")\n'
                        "    # 处理逻辑\n"
                        "    result = input_name[:5]\n"
                        "    # 设置输出\n"
                        '    node.setData("output_name", result)\n'
                        "重要：\n"
                        "1. 不要创建 ExecPin 类型的引脚\n"
                        '2. 不要调用 node["outExec"].call()\n'
                        "3. 只进行数据计算和转换，不执行副作用操作\n"
                        "4. 只输出代码，不要包含任何说明文字或注释"
                    ),
                },
                {"role": "user", "content": validated_prompt},
            ],
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_response_length,
        }

        try:
            req = urllib.request.Request(
                url, data=json.dumps(body).encode("utf-8"), headers=self._headers()
            )
            with urllib.request.urlopen(
                req, timeout=self._config.request_timeout
            ) as resp:
                if resp.status != 200:
                    raise APIError(f"API请求失败: HTTP {resp.status}")

                response_data = resp.read().decode("utf-8")
                data = json.loads(response_data)

                # 检查API响应结构
                if "choices" not in data or not data["choices"]:
                    raise APIError("API响应格式错误: 缺少choices字段")

                choice = data["choices"][0]
                if "message" not in choice or "content" not in choice["message"]:
                    raise APIError("API响应格式错误: 缺少message.content字段")

                text = choice["message"]["content"].strip()
                if not text:
                    raise APIError("API返回空内容")

                # 去掉可能的围栏
                if text.startswith("```"):
                    text = text.strip("`\n")
                    if text.startswith("python\n"):
                        text = text[7:]
                    elif text.startswith("py\n"):
                        text = text[3:]
                    elif text.startswith("json\n"):
                        text = text[5:]
                    elif text.startswith("JSON\n"):
                        text = text[5:]

                # 验证生成的代码安全性
                self._validate_generated_code(text)

                return text

        except urllib.error.HTTPError as e:
            error_msg = f"HTTP错误 {e.code}: {e.reason}"
            try:
                error_body = e.read().decode("utf-8")
                error_data = json.loads(error_body)
                if "error" in error_data and "message" in error_data["error"]:
                    error_msg += f" - {error_data['error']['message']}"
            except:
                pass
            raise APIError(error_msg)

        except urllib.error.URLError as e:
            raise NetworkError(f"网络连接错误: {e.reason}")

        except json.JSONDecodeError as e:
            raise APIError(f"API响应JSON解析失败: {e}")

        except (ConfigurationError, ValidationError) as e:
            raise e

        except Exception as e:
            raise AIServiceError(f"生成DSL时发生未知错误: {e}")
