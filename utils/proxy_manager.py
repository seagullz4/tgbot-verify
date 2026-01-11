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
    """
    # 匹配 socks5://user:pass@host:port 格式
    pattern = r'(socks5://)[^:]+:[^@]+(@.+)'
    masked = re.sub(pattern, r'\1***:***\2', proxy_url)
    return masked


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
                self.proxies = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            
            if self.proxies:
                logger.info(f"成功加载 {len(self.proxies)} 个代理")
            else:
                logger.warning(f"代理文件为空: {self.proxy_file_path}")
        except FileNotFoundError:
            logger.error(f"代理文件未找到: {self.proxy_file_path}")
            self.proxies = []
        except PermissionError:
            logger.error(f"无权限读取代理文件: {self.proxy_file_path}")
            self.proxies = []
        except UnicodeDecodeError:
            logger.error(f"代理文件编码错误，请确保使用 UTF-8 编码: {self.proxy_file_path}")
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
