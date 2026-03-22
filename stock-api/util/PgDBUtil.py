import psycopg2
from psycopg2 import pool, extras
import logging
import json

# 配置日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PgDBUtil:
    """
    PostgreSQL 数据库工具类
    功能：连接池管理、增删改查、批量操作、事务管理、JSONB 数据操作
    """

    def __init__(self, min_conn=1, max_conn=10, **kwargs):
        """初始化数据库连接池"""
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 5432)
        self.database = kwargs.get('database')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        
        if not all([self.database, self.user, self.password]):
            raise ValueError("必须提供 database, user 和 password 参数")

        try:
            self._pool = pool.ThreadedConnectionPool(
                min_conn, max_conn,
                host=self.host, port=self.port,
                database=self.database, user=self.user, password=self.password
            )
            logger.info("PostgreSQL 连接池初始化成功")
        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            raise

    def get_connection(self):
        """从连接池中获取一个连接"""
        try:
            return self._pool.getconn()
        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise

    def release_connection(self, conn):
        """将连接释放回连接池"""
        if conn:
            try:
                self._pool.putconn(conn)
            except Exception as e:
                logger.error(f"释放连接失败: {e}")

    def close_all(self):
        """关闭连接池，释放所有资源"""
        try:
            if self._pool:
                self._pool.closeall()
                logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭连接池失败: {e}")

    def execute_query(self, sql, params=None, fetch_one=False):
        """执行查询 SQL (SELECT)，返回字典列表"""
        conn = None
        cursor = None
        result = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(sql, params)
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"SQL 查询执行出错: {sql}, 参数: {params}, 错误: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        """执行更新 SQL (INSERT, UPDATE, DELETE)，返回受影响行数"""
        conn = None
        cursor = None
        rows_affected = 0
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"SQL 更新执行出错: {sql}, 参数: {params}, 错误: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def execute_batch(self, sql, params_list):
        """
        批量执行 SQL (INSERT, UPDATE, DELETE)，使用 executemany 一次性提交
        适用于大量数据的批量操作
        :param sql: SQL 语句模板
        :param params_list: 参数列表，每个元素是一条记录的参数元组
        :return: 受影响的行数列表
        """
        conn = None
        cursor = None
        results = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            results = cursor.executemany(sql, params_list)
            conn.commit()
            return results
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"批量 SQL 执行出错: {sql}, 错误: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    # ==================== JSON/JSONB 操作方法 ====================

    def insert_json(self, table_name, json_column, data_dict):
        """插入一条包含 JSONB 数据的记录"""
        sql = f"INSERT INTO {table_name} ({json_column}) VALUES (%s)"
        return self.execute_update(sql, (extras.Json(data_dict),))

    def update_json(self, table_name, json_column, data_dict, where_condition, where_params=None):
        """更新表中的 JSONB 列"""
        sql = f"UPDATE {table_name} SET {json_column} = %s WHERE {where_condition}"
        params = [extras.Json(data_dict)]
        if where_params:
            params.extend(where_params)
        return self.execute_update(sql, tuple(params))

    def query_json_contains(self, table_name, json_column, key, value):
        """查询 JSONB 中包含特定 键:值 的记录 (@> 操作符)"""
        query_val = json.dumps({key: value})
        sql = f"SELECT * FROM {table_name} WHERE {json_column} @> %s::jsonb"
        return self.execute_query(sql, (query_val,))

    def query_json_key_exists(self, table_name, json_column, key):
        """查询 JSONB 中存在特定 Key 的记录 (? 操作符)"""
        sql = f"SELECT * FROM {table_name} WHERE {json_column} ? %s"
        return self.execute_query(sql, (key,))

    def update_json_value(self, table_name, json_column, key, new_value, where_condition, where_params=None):
        """更新 JSONB 列中的某个特定 Key 的值 (jsonb_set 函数)"""
        sql = f"UPDATE {table_name} SET {json_column} = jsonb_set({json_column}, %s, %s) WHERE {where_condition}"
        params = [f'{{{key}}}', json.dumps(new_value)]
        if where_params:
            params.extend(where_params)
        return self.execute_update(sql, tuple(params))

    def get_json_value(self, table_name, json_column, key, where_condition=None, where_params=None, fetch_one=False):
        """获取 JSONB 列中某个 Key 的值 (->> 操作符)"""
        sql = f"SELECT {json_column}->>%s AS value FROM {table_name}"
        params = [key]
        if where_condition:
            sql += f" WHERE {where_condition}"
            if where_params:
                params.extend(where_params)
        return self.execute_query(sql, tuple(params), fetch_one=fetch_one)

    def add_json_field(self, table_name, json_column, key, value, where_condition, where_params=None):
        """
        向 JSONB 对象中添加一个新字段 (如果字段已存在则覆盖)
        使用 PostgreSQL 的 || (合并) 操作符
        :param table_name: 表名
        :param json_column: JSONB 列名
        :param key: 要添加的字段名
        :param value: 字段值 (Python 对象，会自动转为 JSON)
        :param where_condition: WHERE 条件字符串 (例如 "id = %s")
        :param where_params: WHERE 条件参数元组
        :return: 受影响的行数
        """
        # 逻辑: json_column = json_column || '{"key": value}'::jsonb
        # 注意: || 操作符会合并两个 JSONB 对象，右边的键会覆盖左边的同名键
        
        # 构造要添加的 JSON 对象字符串
        new_field_json = json.dumps({key: value})
        
        sql = f"UPDATE {table_name} SET {json_column} = {json_column} || %s::jsonb WHERE {where_condition}"
        
        params = [new_field_json]
        if where_params:
            params.extend(where_params)
            
        return self.execute_update(sql, tuple(params))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()
        if exc_type is not None:
            logger.error(f"发生异常: {exc_type}, {exc_val}")
        return False  # 不抑制异常


# ==========================================
# 使用示例 (演示添加字段)
# ==========================================
if __name__ == "__main__":
    db_config_instance = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'test_db',
        'user': 'postgres',
        'password': '123456'
    }

    with PgDBUtil(**db_config_instance) as db:
        
        # 0. 准备环境：创建表并插入初始数据
        db.execute_update("DROP TABLE IF EXISTS products")
        create_table_sql = """
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            attributes JSONB
        );
        """
        db.execute_update(create_table_sql)
        
        # 初始数据：只有 color 和 size
        initial_attrs = {"color": "red", "size": "M"}
        db.execute_update("INSERT INTO products (name, attributes) VALUES (%s, %s)", 
                          ("T-Shirt", extras.Json(initial_attrs)))
        print("0. 初始数据插入完成")

        # 1. 查看当前数据
        current_data = db.execute_query("SELECT * FROM products WHERE id = 1", fetch_one=True)
        print(f"1. 当前数据: {current_data['attributes']}")

        # 2. 使用 add_json_field 添加 'price' 字段
        # 对应 SQL: UPDATE products SET attributes = attributes || '{"price": 99.9}'::jsonb WHERE id = 1
        rows = db.add_json_field("products", "attributes", "price", 99.9, "id = %s", (1,))
        print(f"2. 添加 price 字段，影响行数: {rows}")

        # 3. 查看添加后的数据
        updated_data = db.execute_query("SELECT * FROM products WHERE id = 1", fetch_one=True)
        print(f"3. 添加后的数据: {updated_data['attributes']}")

        # 4. 演示覆盖已存在的字段 (将 color 改为 blue)
        # || 操作符的特性：右边的键值会覆盖左边的同名键
        rows = db.add_json_field("products", "attributes", "color", "blue", "id = %s", (1,))
        print(f"4. 修改 color 字段，影响行数: {rows}")

        # 5. 查看覆盖后的数据
        final_data = db.execute_query("SELECT * FROM products WHERE id = 1", fetch_one=True)
        print(f"5. 最终数据: {final_data['attributes']}")
        
        # 6. 演示添加复杂对象 (例如 metadata)
        metadata = {"created_by": "admin", "tags": ["sale", "summer"]}
        db.add_json_field("products", "attributes", "metadata", metadata, "id = %s", (1,))
        print(f"6. 添加复杂对象 metadata 后的数据: {db.execute_query('SELECT attributes FROM products WHERE id=1', fetch_one=True)['attributes']}")
