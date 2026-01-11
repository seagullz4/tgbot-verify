"""代理管理器 - 从文件中读取和管理 SOCKS5 代理"""
import logging
import random
import os
import re
from typing import Optional, List
from threading import Lock

logger = logging.getLogger(__name__)


def mask_proxy_credentials(proxy_url: str) -> str:
    """遮蔽代理 URL 中的凭据信息
    
    Args:
        proxy_url: 代理 URL
        
    Returns:
        str: 遮蔽凭据后的 URL
        
    Note:
        此函数假设用户名和密码中不包含 @ 字符（这是标准做法）
        如果确实需要在凭据中使用特殊字符，应使用 URL 编码
    """
    # 匹配 socks5://credentials@host:port 格式
    # 注意：假设凭据中不包含 @ 字符（标准 URL 做法）
    pattern = r'(socks5://)[^@]+@(.+)'
    masked = re.sub(pattern, r'\1***:***@\2', proxy_url)
    return masked


def validate_proxy_url(proxy_url: str) -> bool:
    """验证代理 URL 格式是否正确
    
    Args:
        proxy_url: 代理 URL
        
    Returns:
        bool: URL 格式是否有效
    """
    # 基本格式验证: socks5://[user:pass@]host:port
    pattern = r'^socks5://([^:]+:[^@]+@)?[^:]+:\d+$'
    return bool(re.match(pattern, proxy_url))


class ProxyManager:
    """SOCKS5 代理管理器"""

    def __init__(self, proxy_file_path: str = ""):
        """初始化代理管理器
        
        Args:
            proxy_file_path: 代理文件路径，每行一个代理，格式: socks5://user:pass@host:port 或 socks5://host:port
        """
        self.proxy_file_path = proxy_file_path
        self.proxies: List[str] = []
        self.lock = Lock()
        self._load_proxies()

    def _load_proxies(self):
        """从文件加载代理列表"""
        if not self.proxy_file_path:
            logger.info("未配置代理文件路径，将不使用代理")
            return

        if not os.path.exists(self.proxy_file_path):
            logger.warning(f"代理文件不存在: {self.proxy_file_path}")
            return

        try:
            with open(self.proxy_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 过滤空行和注释，并验证格式
                valid_proxies = []
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if validate_proxy_url(line):
                        valid_proxies.append(line)
                    else:
                        logger.warning(f"代理文件第 {line_num} 行格式无效，已跳过: {line}")
                
                self.proxies = valid_proxies
            
            if self.proxies:
                logger.info(f"成功加载 {len(self.proxies)} 个代理")
            else:
                logger.warning(f"代理文件为空或无有效代理: {self.proxy_file_path}")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f"加载代理文件失败: {e}")
            self.proxies = []
        except Exception as e:
            logger.error(f"加载代理文件时发生未知错误: {e}")
            self.proxies = []

    def get_proxy(self) -> Optional[str]:
        """获取一个随机代理
        
        Returns:
            str: 代理URL，如果没有可用代理则返回 None
        """
        with self.lock:
            if not self.proxies:
                return None
            return random.choice(self.proxies)

    def reload_proxies(self):
        """重新加载代理列表"""
        with self.lock:
            self._load_proxies()

    def has_proxies(self) -> bool:
        """检查是否有可用代理"""
        return len(self.proxies) > 0


# 全局代理管理器实例
_proxy_manager: Optional[ProxyManager] = None


def init_proxy_manager(proxy_file_path: str = ""):
    """初始化全局代理管理器
    
    Args:
        proxy_file_path: 代理文件路径
    """
    global _proxy_manager
    _proxy_manager = ProxyManager(proxy_file_path)


def get_proxy_manager() -> ProxyManager:
    """获取全局代理管理器实例
    
    Returns:
        ProxyManager: 代理管理器实例
    """
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager
