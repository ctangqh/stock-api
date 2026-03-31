"""
比较操作符模块
提供通用的比较操作符枚举
"""
from enum import Enum


class Operator(Enum):
    """比较操作符枚举"""
    GREATER_THAN = ">"
    GREATER_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_OR_EQUAL = "<="
    EQUAL = "=="


def compare_values(value1: float, operator: Operator, value2: float) -> bool:
    """
    执行数值比较
    
    :param value1: 第一个值
    :param operator: 比较操作符
    :param value2: 第二个值
    :return: 比较结果
    """
    if operator == Operator.GREATER_THAN:
        return value1 > value2
    elif operator == Operator.GREATER_OR_EQUAL:
        return value1 >= value2
    elif operator == Operator.LESS_THAN:
        return value1 < value2
    elif operator == Operator.LESS_OR_EQUAL:
        return value1 <= value2
    elif operator == Operator.EQUAL:
        return abs(value1 - value2) < 0.001  # 浮点数比较允许小误差
    return False
