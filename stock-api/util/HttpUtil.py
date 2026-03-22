import requests
import json
from typing import Dict, Optional, Union, Any
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class HttpUtil:
    """
    HTTP 请求工具类
    支持 GET 和 POST 请求，并在请求头中支持公共设置 cookie 信息
    """
    
    def __init__(self, base_url: str = "", default_headers: Optional[Dict[str, str]] = None, 
                 default_cookies: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        初始化 HTTP 工具类
        
        参数:
        base_url -- 基础 URL
        default_headers -- 默认请求头
        default_cookies -- 默认 cookies
        timeout -- 请求超时时间（秒）
        """
        logger.info(f"初始化 HttpUtil，base_url: {base_url}")
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.default_headers = default_headers or {}
        self.default_cookies = default_cookies or {}
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认请求头
        for key, value in self.default_headers.items():
            self.session.headers[key] = value
        
        # 设置默认 cookies
        for key, value in self.default_cookies.items():
            self.session.cookies.set(key, value)

    @staticmethod
    def get_request_url_info(url: str) -> tuple:
        """
        将包含查询参数的 URL 转换为基础 URL 和参数字典
        
        参数:
        url -- 包含查询参数的 URL
        
        返回:
        元组 (base_url, context, query_params)
        """
        from urllib.parse import urlparse, parse_qs
        
        # 解析 URL
        parsed_url = urlparse(url)
        
        # 获取基础 URL
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        context = f"{parsed_url.path}"
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        
        # 将参数值从列表转换为单个值
        params = {}
        for key, value in query_params.items():
            # 如果参数只有一个值，则直接使用该值
            if len(value) == 1:
                params[key] = value[0]
            # 如果参数有多个值，则保留为列表
            else:
                params[key] = value
        
        return base_url, context, params

    @staticmethod
    def url2param(url: str) -> tuple:
        """
        将包含查询参数的 URL 转换为基础 URL 和参数字典
        
        参数:
        url -- 包含查询参数的 URL
        
        返回:
        元组 (base_url, query_params)
        """
        from urllib.parse import urlparse, parse_qs
        
        # 解析 URL
        parsed_url = urlparse(url)
        
        # 获取基础 URL
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        
        # 将参数值从列表转换为单个值
        params = {}
        for key, value in query_params.items():
            # 如果参数只有一个值，则直接使用该值
            if len(value) == 1:
                params[key] = value[0]
            # 如果参数有多个值，则保留为列表
            else:
                params[key] = value
        
        return base_url, params

    @staticmethod
    def url_context(url):
        """
        从 URL 中提取上下文请求路径
        
        参数:
        url -- 完整的 URL
        
        返回:
        包含上下文信息的字典，包括基础 URL、路径和查询参数
        """
        # 解析 URL
        parsed_url = urlparse(url)
        
        # 提取基础信息
        context = {
            'scheme': parsed_url.scheme,  # 协议 (http/https)
            'netloc': parsed_url.netloc,  # 网络位置 (域名:端口)
            'path': parsed_url.path,      # 路径
            'params': parsed_url.params,   # 参数
            'query': parsed_url.query,    # 查询字符串
            'fragment': parsed_url.fragment  # 片段
        }
        
        # 构建基础 URL
        base_url = f"{context['scheme']}://{context['netloc']}"
        context['base_url'] = base_url
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        context['query_params'] = query_params
        
        # 将参数值从列表转换为单个值
        params = {}
        for key, value in query_params.items():
            # 如果参数只有一个值，则直接使用该值
            if len(value) == 1:
                params[key] = value[0]
            # 如果参数有多个值，则保留为列表
            else:
                params[key] = value
        
        context['params'] = params
        
        return context

    @staticmethod
    def cookie_translate(cookie_str: str) -> Dict[str, str]:
        """
        将 cookie 字符串转换为字典类型
        
        参数:
        cookie_str -- cookie 字符串，格式为 "key1=value1; key2=value2; ..."
        
        返回:
        cookie 字典 {key: value}
        """
        from urllib.parse import unquote
        
        # 初始化结果字典
        cookie_dict = {}
        
        # 分割 cookie 字符串
        cookie_pairs = cookie_str.split(';')
        
        # 处理每个键值对
        for pair in cookie_pairs:
            # 去除首尾空格
            pair = pair.strip()
            
            # 跳过空字符串
            if not pair:
                continue
            
            # 分割键值对
            if '=' in pair:
                key, value = pair.split('=', 1)
                # URL 解码值
                cookie_dict[key.strip()] = unquote(value.strip())
            else:
                # 处理没有值的 cookie
                cookie_dict[pair] = ''
        
        return cookie_dict


    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None) -> requests.Response:
        """
        发送 GET 请求
        
        参数:
        url -- 请求 URL
        params -- 查询参数
        headers -- 请求头
        cookies -- cookies
        timeout -- 请求超时时间（秒）
        
        返回:
        requests.Response 对象
        """
        # 合并 URL
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        logger.info(f"发送 GET 请求，URL: {full_url}, params: {params}")
        
        # 合并请求头
        request_headers = {**self.default_headers, **(headers or {})}
        
        # 合并 cookies
        request_cookies = {**self.default_cookies, **(cookies or {})}
        
        # 设置超时时间
        request_timeout = timeout if timeout is not None else self.timeout

        # 发送请求
        response = self.session.get(
            full_url,
            params=params,
            headers=request_headers,
            cookies=request_cookies,
            timeout=request_timeout
        )
        logger.info(f"GET 请求完成，状态码: {response.status_code}")
        
        return response
    
    def post(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None, 
             json_data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None) -> requests.Response:
        """
        发送 POST 请求
        
        参数:
        url -- 请求 URL
        data -- 请求体数据（表单数据）
        json_data -- JSON 格式的请求体数据
        headers -- 请求头
        cookies -- cookies
        timeout -- 请求超时时间（秒）
        
        返回:
        requests.Response 对象
        """
        # 合并 URL
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        logger.info(f"发送 POST 请求，URL: {full_url}")
        
        # 合并请求头
        request_headers = {**self.default_headers, **(headers or {})}
        
        # 合并 cookies
        request_cookies = {**self.default_cookies, **(cookies or {})}
        
        # 设置超时时间
        request_timeout = timeout if timeout is not None else self.timeout
        
        # 发送请求
        response = self.session.post(
            full_url,
            data=data,
            json=json_data,
            headers=request_headers,
            cookies=request_cookies,
            timeout=request_timeout
        )
        logger.info(f"POST 请求完成，状态码: {response.status_code}")
        
        return response
    
    def put(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None, 
            json_data: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None) -> requests.Response:
        """
        发送 PUT 请求
        
        参数:
        url -- 请求 URL
        data -- 请求体数据（表单数据）
        json_data -- JSON 格式的请求体数据
        headers -- 请求头
        cookies -- cookies
        timeout -- 请求超时时间（秒）
        
        返回:
        requests.Response 对象
        """
        # 合并 URL
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        
        # 合并请求头
        request_headers = {**self.default_headers, **(headers or {})}
        
        # 合并 cookies
        request_cookies = {**self.default_cookies, **(cookies or {})}
        
        # 设置超时时间
        request_timeout = timeout if timeout is not None else self.timeout
        
        # 发送请求
        response = self.session.put(
            full_url,
            data=data,
            json=json_data,
            headers=request_headers,
            cookies=request_cookies,
            timeout=request_timeout
        )
        
        return response
    
    def delete(self, url: str, params: Optional[Dict[str, Any]] = None, 
               headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
               timeout: Optional[int] = None) -> requests.Response:
        """
        发送 DELETE 请求
        
        参数:
        url -- 请求 URL
        params -- 查询参数
        headers -- 请求头
        cookies -- cookies
        timeout -- 请求超时时间（秒）
        
        返回:
        requests.Response 对象
        """
        # 合并 URL
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        
        # 合并请求头
        request_headers = {**self.default_headers, **(headers or {})}
        
        # 合并 cookies
        request_cookies = {**self.default_cookies, **(cookies or {})}
        
        # 设置超时时间
        request_timeout = timeout if timeout is not None else self.timeout
        
        # 发送请求
        response = self.session.delete(
            full_url,
            params=params,
            headers=request_headers,
            cookies=request_cookies,
            timeout=request_timeout
        )
        
        return response
    
    
    def close(self):
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()



# 使用示例
if __name__ == "__main__":
    # 创建 HTTP 工具实例，设置默认请求头和 cookies
    http_util = HttpUtil(
        base_url="https://api.example.com",
        default_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        default_cookies={
            "session_id": "abc123",
            "user_token": "xyz789"
        },
        timeout=30
    )
    
    # 示例 URL
    url = "https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230919858424235644_1770456637056&fid=f72&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13"

    # 使用 url2param 方法解析 URL
    base_url, params = HttpUtil.url2param(url)

    # 使用 with 语句自动关闭会话
    with http_util:
        # 发送 GET 请求
        response = http_util.get("/users", params={"page": 1, "limit": 10})
        print(f"GET 请求状态码: {response.status_code}")
        print(f"GET 请求响应: {response.json()}")
        
        # 发送 POST 请求
        response = http_util.post(
            "/users",
            json_data={
                "name": "张三",
                "email": "zhangsan@example.com"
            }
        )
        print(f"POST 请求状态码: {response.status_code}")
        print(f"POST 请求响应: {response.json()}")
        
        # 发送 PUT 请求
        response = http_util.put(
            "/users/1",
            json_data={
                "name": "李四",
                "email": "lisi@example.com"
            }
        )
        print(f"PUT 请求状态码: {response.status_code}")
        print(f"PUT 请求响应: {response.json()}")
        
        # 发送 DELETE 请求
        response = http_util.delete("/users/1")
        print(f"DELETE 请求状态码: {response.status_code}")
        print(f"DELETE 请求响应: {response.json()}")
        
        # 使用自定义请求头和 cookies
        custom_headers = {
            "X-Custom-Header": "custom_value"
        }
        custom_cookies = {
            "custom_cookie": "custom_value"
        }
        response = http_util.get(
            "/custom",
            headers=custom_headers,
            cookies=custom_cookies
        )
        print(f"自定义请求 GET 请求状态码: {response.status_code}")
        print(f"自定义请求 GET 请求响应: {response.json()}")

