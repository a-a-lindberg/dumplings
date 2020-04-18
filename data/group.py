import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'group'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    followers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    info = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    admin_list = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    posts_list = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    followers_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    posts = relationship("Post", backref="group")
