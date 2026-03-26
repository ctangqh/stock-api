#!/usr/bin/env python3
"""定时任务调度器"""

import logging
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from conf.Config import SCHEDULER_CONFIG
from job.stock_scan import screen_stocks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_stock_scan():
    """执行选股任务"""
    logger.info("=" * 70)
    logger.info("定时任务：开始执行选股任务")
    logger.info("=" * 70)
    try:
        screen_stocks()
        logger.info("选股任务执行完成")
    except Exception as e:
        logger.exception(f"选股任务执行异常: {e}")
    logger.info("=" * 70)


def parse_cron_expression(cron_expr):
    """解析 cron 表达式"""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"无效的 cron 表达式: {cron_expr}, 需要5个部分")
    return {
        'minute': parts[0],
        'hour': parts[1],
        'day': parts[2],
        'month': parts[3],
        'day_of_week': parts[4]
    }


def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("股票定时任务调度器启动")
    logger.info("=" * 70)

    scheduler = BlockingScheduler()

    # 配置选股任务
    stock_scan_config = SCHEDULER_CONFIG.get('stock_scan', {})
    enabled = stock_scan_config.get('enabled', True)
    cron_expr = stock_scan_config.get('cron', '30 20 * * *')

    if enabled:
        try:
            cron_kwargs = parse_cron_expression(cron_expr)
            logger.info(f"注册选股任务: cron={cron_expr}")
            scheduler.add_job(
                run_stock_scan,
                trigger=CronTrigger(**cron_kwargs),
                id='stock_scan',
                name='选股任务',
                replace_existing=True
            )
            logger.info("选股任务注册成功")
        except Exception as e:
            logger.exception(f"注册选股任务失败: {e}")
    else:
        logger.info("选股任务已禁用")

    logger.info("\n调度器已启动，按 Ctrl+C 停止")
    logger.info("=" * 70)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器已停止")


if __name__ == '__main__':
    main()
