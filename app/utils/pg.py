from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Optional, List, Any, Tuple
from dataclasses import dataclass
from pydantic import BaseModel
import logging
from psycopg.types.json import Jsonb
# from datetime import datetime

logger = logging.getLogger(__name__)

pool : ConnectionPool | None = None

@dataclass
class QueryCondition:
    limit: int | None = None
    offset:  int | None  = None
    order_by: str | None = None
    cols: List[str] | None = None
    where:  str | None = None
    params: Tuple[Any, ...] = None

    def __post_init__(self):
        if self.cols is None:
            self.cols = ["*"]
        if self.params is None:
            self.params = ()

def init_pool(url:str):
    global pool
    pool = ConnectionPool(url)


# Low level functions
def query(sql:str, params:tuple):
    logger.info(f"query: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
        
def query_dict(sql:str, params:tuple):
    logger.info(f"query_dict: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def query_one(sql:str, params:tuple):
    logger.info(f"query_one: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
        
def query_one_dict(sql:str, params:tuple):
    logger.info(f"query_one_dict: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchone()
        
def execute_none(sql:str, params:tuple):
    logger.info(f"execute_none: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return {"success": True}

def execute(sql:str, params:tuple):
    logger.info(f"execute: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchall()

def execute_dict(sql:str, params:tuple|None=None):
    logger.info(f"execute_dict: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchall()
        
def execute_one(sql:str, params:tuple):
    logger.info(f"execute_one: {sql} {params}")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchone()

def execute_one_dict(sql: str, params: tuple = ()):
    logger.info(f"execute_one_dict: {sql} \n {params}")
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchone()

# High level functions
def create(table:str, data: BaseModel):
    data_dict = data.model_dump(exclude_unset=True)
    sql = f"INSERT INTO {table} ({', '.join(data_dict.keys())}) VALUES ({', '.join([f"%s" for v in data_dict.values()])}) RETURNING id"
    data_values = tuple(Jsonb(value) if isinstance(value, dict) else value for value in data_dict.values())
    return execute_one_dict(sql, data_values)

def update(table:str, id:int, data:BaseModel, columns:list[str]=["*"]):
    data_dict = data.model_dump(exclude_unset=True)
    sql = f"UPDATE {table} SET {', '.join([f"{k}=%s" for k in data_dict.keys()])} WHERE id=%s RETURNING {', '.join(columns)}"
    data_values = tuple(Jsonb(value) if isinstance(value, dict) else value for value in data_dict.values())
    return execute_one_dict(sql, data_values + (id,))

def delete(table:str, id:int): 
    sql = f"DELETE FROM {table} WHERE id=%s"
    return execute_none(sql, (id,))

def delete_where(table:str, conditions: QueryCondition): 
    sql = f"DELETE FROM {table}"
    if conditions.where:
        sql += f" WHERE {conditions.where}"
    return execute_none(sql, conditions.params)
        
def detail(table: str, id: int, columns: tuple[str, ...] = ("*",)):
    sql = f"SELECT {', '.join(columns)} FROM {table} WHERE id=%s"
    return query_one_dict(sql, (id,))

def list_all(table:str, columns:list[str]=["*"]):
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    return query_dict(sql)
    
# def datetime_to_iso(obj):
#     if isinstance(obj, datetime):
#         return obj.isoformat()
#     return obj

def list(table: str, conditions: QueryCondition):
    sql = f"SELECT {', '.join(conditions.cols)} FROM {table}"
    if conditions.where:
        sql += f" WHERE {conditions.where}"
    if conditions.order_by:
        sql += f" ORDER BY {conditions.order_by}"
    if conditions.limit is not None:
        sql += f" LIMIT {conditions.limit}"
    if conditions.offset is not None:
        sql += f" OFFSET {conditions.offset}"
    return query_dict(sql, conditions.params)
            # return [{k: datetime_to_iso(v) for k, v in row.items()} for row in rows]

def count(table: str, conditions: QueryCondition):
    sql = f"SELECT COUNT(*) FROM {table}"
    if conditions.where:
        sql += f" WHERE {conditions.where}"
    return query_one(sql, conditions.params)[0]

def get_by_id(table: str, id: int, columns: tuple[str, ...] = ("*",)):
    return detail(table, id, columns)


