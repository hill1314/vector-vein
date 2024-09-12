# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 12:43:52
# @Last Modified by:   Bi Ying
# @Last Modified time: 2024-06-15 01:45:12
import json
import uuid
from pathlib import Path
from datetime import date, datetime

from playhouse.shortcuts import model_to_dict
from peewee_migrate import Router
from peewee import (
    Model,
    TextField,
    SqliteDatabase,
)

from utilities.config import config


# 创建一个连接到SQLite数据库的实例, # 如果文件不存在，它会被创建
database = SqliteDatabase(Path(config.data_path) / "my_database.db")


# 在 SQLite 中将 JSON 数据存储为文本的自定义字段
class JSONField(TextField):
    """Custom field to store JSON data as text in SQLite"""

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)
        return None

    def python_value(self, value):
        if value is not None:
            return json.loads(value)
        return None


# 定义一个模型，该模型对应数据库中的一个表
class BaseModel(Model):
    class Meta:
        database = database


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return int(obj.timestamp() * 1000)
    elif isinstance(obj, uuid.UUID):
        return obj.hex
    raise TypeError(f"Type {type(obj)} not serializable")


def get_model_fields(model, field_names):
    return [getattr(model, field_name) for field_name in field_names if hasattr(model, field_name)]


def model_serializer(obj, many: bool = False, manytomany: bool = False, fields: list | None = None):
    if fields:
        if many and obj:
            model_class = obj[0].__class__
        else:
            model_class = obj.__class__
        fields = get_model_fields(model_class, fields)

    if many:
        results = []
        for o in obj:
            dict_obj = model_to_dict(o, manytomany=manytomany, recurse=False, only=fields)
            serialized_obj = json.dumps(dict_obj, default=json_serializer)
            results.append(json.loads(serialized_obj))
        return results
    else:
        dict_obj = model_to_dict(obj, manytomany=manytomany, recurse=False, only=fields)
        serialized_obj = json.dumps(dict_obj, default=json_serializer)
        return json.loads(serialized_obj)


# 迁移
def run_migrations(fake: bool = False):
    router = Router(database, migrate_dir="./migrations")
    router.run(fake=fake)


def create_migrations(name: str = "auto"):
    router = Router(database, migrate_dir="./migrations")
    router.create(name, auto=True)
