import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, UserMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"), nullable=True)
    mate = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("users.id"), nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
