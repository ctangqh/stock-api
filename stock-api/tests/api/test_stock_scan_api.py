import pytest
from unittest import mock
from datetime import date
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_scan_records():
    """测试用的选股扫描记录"""
    return [
        {
            'id': 1,
            'scan_date': date(2024, 1, 3),
            'ts_code': '000001',
            'ts_name': '平安银行',
            'strategy_name': 'test_strategy',
            'scan_time': '2024-01-03 09:30:00'
        },
        {
            'id': 2,
            'scan_date': date(2024, 1, 3),
            'ts_code': '000002',
            'ts_name': '万科A',
            'strategy_name': 'test_strategy',
            'scan_time': '2024-01-03 09:31:00'
        }
    ]


@pytest.mark.unit
class TestStockScanAPI:
    """测试选股扫描 API"""

    def test_get_scan_results_success(self, client, test_scan_records):
        """测试成功获取选股扫描结果"""
        with mock.patch('api.stock_scan.StockBestChooseORM') as mock_orm:
            # 配置 mock
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.__enter__.return_value = mock_orm_instance
            mock_orm_instance.get_by_scan_date.return_value = test_scan_records
            
            # 发送请求
            response = client.get("/api/stock/scan-results", params={"date": "2024-01-03", "limit": 10})
            
            # 断言
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]['ts_code'] == '000001'
            assert data[1]['ts_code'] == '000002'
            mock_orm_instance.get_by_scan_date.assert_called_once()

    def test_get_scan_results_invalid_date(self, client):
        """测试日期格式不正确"""
        response = client.get("/api/stock/scan-results", params={"date": "invalid-date"})
        
        assert response.status_code == 400
        assert "日期格式不正确" in response.json()['detail']

    def test_get_scan_results_limit_exceeded(self, client):
        """测试 limit 超过最大值 (FastAPI 自动验证)"""
        response = client.get("/api/stock/scan-results", params={"limit": 2000})
        
        # FastAPI 的 Query 参数验证会返回 422
        assert response.status_code == 422

    def test_get_scan_results_internal_error(self, client):
        """测试服务器内部错误"""
        with mock.patch('api.stock_scan.StockBestChooseORM') as mock_orm:
            # 配置 mock: 抛出异常
            mock_orm_instance = mock_orm.return_value
            mock_orm_instance.__enter__.side_effect = Exception("数据库连接失败")
            
            # 发送请求
            response = client.get("/api/stock/scan-results")
            
            # 断言
            assert response.status_code == 500
            assert "服务器内部错误" in response.json()['detail']


if __name__ == "__main__":
    pytest.main([__file__])
