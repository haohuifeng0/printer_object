# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, Float, Date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
# 创建实体类的基类
from sqlalchemy.orm import Session

from libs.db import engine

Base = declarative_base(engine)


class BaseMode(Base):
    """实体类-包装基类"""
    db = Session()

    __abstract__ = True  # 抽象类，不会转成表
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键id

    def save(self):
        """新增"""
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def delete(self):
        """删除"""
        session = Session()
        session.delete(self)
        session.commit()
        session.close()

    def update(self):
        """更新"""
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    def delete_all(self, model):
        session = Session()
        session.query(model).filter(model.id > 0).delete(synchronize_session=False)
        session.commit()
        session.close()


class SendData(BaseMode):
    __tablename__ = "t_send_data"  # 数据库表名
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键id
    db_code = Column(String(64), unique=True)
    ems_code = Column(String(64))
    recipient_name = Column(String(64))
    recipient_phone = Column(String(64))
    recipient_addr = Column(String(255))
    comment = Column(String(255))
    weight = Column(Float)
    good = Column(String(64))
    flag = Column(Integer, default=0)


if __name__ == '__main__':
    # 删除表，创建表
    # Base.metadata.drop_all()
    Base.metadata.create_all()
    # try:
    #     SendData(db_code='12313213',
    #              ems_code='asafsfasfasf',
    #              recipient_name='haohuifeng',
    #              recipient_phone='13212313',
    #              recipient_addr='FJKHJKJHSADFKJHKADSHFK',
    #              # sender_name='1321213213',
    #              # sender_phone='2123132131',
    #              # sender_addr='kjashkdkajshdhuwq',
    #              weight=1.2,
    #              good='xxsl').save()
    # except IntegrityError:
    #     print('not unique')

    # SendData().delete_all(SendData)

