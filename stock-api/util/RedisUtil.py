import redis
import json
import logging
from typing import Any, Optional, Union, List, Dict, Callable
from datetime import timedelta
from conf.Config import REDIS_CONFIG

# 配置日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisUtil:
    """
    Redis 操作工具类
    功能：连接管理、字符串操作、哈希操作、列表操作、集合操作、有序集合操作、键操作
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Redis 连接
        
        参数:
        config -- Redis 配置字典，如果为 None 则使用默认配置
        """
        # 使用传入的配置或默认配置
        redis_config = config or REDIS_CONFIG
        
        self.host = redis_config.get('host', 'localhost')
        self.port = redis_config.get('port', 6379)
        self.db = redis_config.get('db', 0)
        self.password = redis_config.get('password')
        self.decode_responses = redis_config.get('decode_responses', True)
        self.socket_timeout = redis_config.get('socket_timeout', 5)
        self.socket_connect_timeout = redis_config.get('socket_connect_timeout', 5)
        
        try:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # 测试连接
            self._client.ping()
            logger.info(f"Redis 连接成功: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            raise

    def close(self):
        """关闭 Redis 连接"""
        try:
            if self._pool:
                self._pool.disconnect()
                logger.info("Redis 连接已关闭")
        except Exception as e:
            logger.error(f"关闭 Redis 连接失败: {e}")

    def __enter__(self):
        """支持 with 语句的进入操作"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句的退出操作"""
        self.close()
        if exc_type is not None:
            logger.error(f"发生异常: {exc_type}, {exc_val}")
        return False  # 不抑制异常

    # ==================== 字符串操作 ====================

    def set(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None) -> bool:
        """
        设置键值对
        
        参数:
        key -- 键
        value -- 值
        ex -- 过期时间（秒）
        px -- 过期时间（毫秒）
        
        返回:
        是否设置成功
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            result = self._client.set(key, value, ex=ex, px=px)
            return result
        except Exception as e:
            logger.error(f"设置键值对失败: {key}, 错误: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """
        获取键值
        
        参数:
        key -- 键
        
        返回:
        值，如果键不存在则返回 None
        """
        try:
            value = self._client.get(key)
            if value is None:
                return None
            
            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"获取键值失败: {key}, 错误: {e}")
            raise
    
    def delete(self, key: str) -> int:
        """
        删除键值
        
        参数:
        key -- 键
        
        返回:
        值，如果键不存在则返回 None
        """
        try:
            value = self._client.delete(key)
            if value is None:
                return 0
        except Exception as e:
            logger.error(f"获取键值失败: {key}, 错误: {e}")
            raise

    def get_or_fetch(self, key: str, fetch_func: Callable[[], Any], 
                    expire_days: int = 1, use_cache: bool = True) -> Any:
        """
        获取键值，如果不存在则通过回调函数获取并存储到 Redis 中
        
        参数:
        key -- 键
        fetch_func -- 获取数据的回调函数
        expire_days -- 过期天数，默认为1天
        use_cache -- 是否使用缓存，默认为True
        
        返回:
        值
        """
        try:
            # 如果使用缓存，尝试从 Redis 获取数据
            if use_cache:
                value = self.get(key)
                
                if value is not None:
                    logger.info(f"从 Redis 获取数据: {key}")
                    return value
            else:
                self.delete(key)
                logger.info(f"清理缓存获取数据: {key}")
            
            # 数据不存在或不使用缓存，调用回调函数获取数据
            logger.info(f"从回调函数获取数据: {key}")
            value = fetch_func()
            
            if value is not None:
                # 将数据存储到 Redis 中，设置过期时间
                expire_seconds = int(timedelta(days=expire_days).total_seconds())
                self.set(key, value, ex=expire_seconds)
                logger.info(f"数据已存储到 Redis: {key}，过期时间: {expire_days}天")
            
            return value
        except Exception as e:
            logger.error(f"获取或存储数据失败: {key}, 错误: {e}")
            raise

    # ... 其余方法保持不变 ...


# 使用示例
if __name__ == "__main__":
    # 定义获取数据的回调函数
    def fetch_stock_data():
        """模拟从远程 API 获取股票数据"""
        logger.info("从远程 API 获取股票数据")
        # 这里应该是实际的 API 调用
        return {
            "code": "000001",
            "name": "平安银行",
            "price": 12.34,
            "change": 0.56
        }
    
    # 使用默认配置
    with RedisUtil() as redis:
        # 第一次调用，数据不存在于 Redis，会调用回调函数
        data = redis.get_or_fetch("stock:000001", fetch_stock_data)
        print(f"第一次获取数据: {data}")
        
        # 第二次调用，数据已存在于 Redis，直接返回
        data = redis.get_or_fetch("stock:000001", fetch_stock_data)
        print(f"第二次获取数据: {data}")
        
        # 不使用缓存，每次都从回调函数获取数据
        data = redis.get_or_fetch("stock:000001", fetch_stock_data, use_cache=False)
        print(f"不使用缓存获取数据: {data}")
        
        # 查看过期时间
        ttl = redis.ttl("stock:000001")
        print(f"数据过期时间: {ttl}秒")

