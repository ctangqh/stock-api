import os
import logging
from datetime import datetime

def setup_logging():
    """配置日志输出到根目录的 logs 文件夹"""
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建 logs 目录
    log_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志文件名（按日期）
    log_file = os.path.join(log_dir, f'pgdb_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置日志处理器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
