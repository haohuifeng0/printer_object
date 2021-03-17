#!coding: utf-8
from sqlalchemy import create_engine
import os


# 项目的路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sqlite的路径
# db_path = "sqlite:///" + os.path.join(base_dir, "db.sqlite")
db_path = "sqlite://"

# 创建核心对象engine
engine = create_engine(
    db_path,  # 数据库的路径
    encoding="utf-8",  # 编码格式
    echo=True,  # 将sql语句显示到控制台
)
# if __name__ == '__main__':
#     print(base_dir)
#     print(db_path)

