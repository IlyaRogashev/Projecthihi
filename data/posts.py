import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')