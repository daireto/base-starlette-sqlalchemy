"""Database models."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from jinja2 import Template
from passlib.hash import pbkdf2_sha256
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from starlette.requests import Request

from core.auth.enums import Roles
from core.bases.base_model import BaseModel
from utils.enums import StrEnum, auto
from utils.func import get_robohash_url


class Reactions(StrEnum):
    LIKE = auto()
    DISLIKE = auto()
    LOVE = auto()
    LAUGH = auto()
    SAD = auto()
    HUSHED = auto()
    ANGRY = auto()


class Gender(StrEnum):
    MALE = auto()
    FEMALE = auto()
    OTHER = auto()


class User(BaseModel):
    __tablename__ = 'users'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(
        String(15), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(40), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    role: Mapped[Roles] = mapped_column(
        Enum(Roles), nullable=False, default=Roles.USER
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender), nullable=False, default=Gender.OTHER
    )
    birthday: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('users.uid')
    )
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('users.uid')
    )

    created_by: Mapped[Optional['User']] = relationship(
        foreign_keys=[created_by_id], remote_side=[uid], lazy='noload'
    )
    updated_by: Mapped[Optional['User']] = relationship(
        foreign_keys=[updated_by_id], remote_side=[uid], lazy='noload'
    )
    posts: Mapped[list['Post']] = relationship(
        back_populates='publisher', lazy='noload'
    )
    comments: Mapped[list['Comment']] = relationship(
        back_populates='user', lazy='noload'
    )
    post_reactions: Mapped[list['PostReaction']] = relationship(
        back_populates='user', lazy='noload'
    )
    comment_reactions: Mapped[list['CommentReaction']] = relationship(
        back_populates='user', lazy='noload'
    )

    def verify_password(self, password: str) -> bool:
        """Verifies the user's password."""
        return pbkdf2_sha256.verify(password, self.password)

    def set_password(self, password: str) -> None:
        """Sets the user's password."""
        self.password = pbkdf2_sha256.hash(password)

    @hybrid_property
    def full_name(self) -> str:
        """Returns the user's full name."""
        return f'{self.first_name} {self.last_name}'

    @hybrid_property
    def age(self) -> int:
        """Returns the user's age."""
        today = date.today()
        return (
            today.year
            - self.birthday.year
            - (
                (today.month, today.day)
                < (self.birthday.month, self.birthday.day)
            )
        )

    @hybrid_property
    def is_adult(self) -> bool:
        """Checks if the user is an adult."""
        return self.age >= 18

    @hybrid_property
    def is_admin(self) -> bool:
        """Checks if the user is an admin."""
        return self.role == Roles.ADMIN

    @hybrid_property
    def is_user(self) -> bool:
        """Checks if the user is a user."""
        return self.role == Roles.USER

    @hybrid_method
    def has_role(self, role: Roles) -> bool:
        """Checks if the user has a role.

        Parameters
        ----------
        role : Roles
            Role to compare to the user's role.
        """
        return self.role == role

    @hybrid_method
    def older_than(self, other: 'User') -> bool:
        """Checks if the user is older than another user.

        Parameters
        ----------
        other : User
            User to compare to the current user.
        """
        return self.age > other.age

    @hybrid_method
    def younger_than(self, other: 'User') -> bool:
        """Checks if the user is younger than another user.

        Parameters
        ----------
        other : User
            User to compare to the current user.
        """
        return self.age < other.age

    @property
    def avatar_url(self) -> str:
        """Returns the user's avatar URL."""
        return get_robohash_url(self.username)

    @property
    def initials(self) -> str:
        """Returns the user's initials."""
        return f'{self.first_name[0].upper()}{self.last_name[0].upper()}'

    @classmethod
    async def authenticate(cls, username: str, password: str) -> bool:
        """Authenticates a user.

        Parameters
        ----------
        username : str
            Username.
        password : str
            Password.

        Returns
        -------
        bool
            True if the user is authenticated, False otherwise.
        """
        user = await cls.find(username=username, role=Roles.ADMIN).first()
        if user is None:
            return False

        if not user.verify_password(password):
            return False

        return True

    async def __admin_repr__(self, _: Request):
        return f'{self.username} ({self.full_name})'

    async def __admin_select2_repr__(self, _: Request) -> str:
        template_str = (
            '<div class="d-flex align-items-center">'
            '<span class="me-2 avatar avatar-xs" style="background-image: url({{ url }});--tblr-avatar-size: 1.5rem;"></span>'
            '{{ obj.username }} ({{ obj.full_name }})'
            '<div>'
        )
        return Template(template_str, autoescape=True).render(
            obj=self, url=self.avatar_url
        )


class Post(BaseModel):
    __tablename__ = 'posts'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=[])
    publisher_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='CASCADE')
    )
    published_at: Mapped[datetime] = mapped_column(
        'published_at',
        TIMESTAMP(timezone=False),
        default=func.now(),
        nullable=False,
    )

    publisher: Mapped['User'] = relationship(
        back_populates='posts', lazy='noload'
    )
    comments: Mapped[list['Comment']] = relationship(
        back_populates='post', lazy='noload'
    )
    reactions: Mapped[list['PostReaction']] = relationship(
        back_populates='post', lazy='noload'
    )

    @property
    def short_title(self) -> str:
        """Returns the post's short title."""
        return self.title if len(self.title) < 50 else self.title[:47] + '...'

    async def __admin_repr__(self, _: Request):
        return self.title

    async def __admin_select2_repr__(self, _: Request) -> str:
        template_str = (
            '<span>'
            '<strong>Title: </strong>{{ obj.short_title }},'
            '&nbsp;'
            '<strong>Published by: </strong>{{ obj.publisher.full_name }}'
            '</span>'
        )
        return Template(template_str, autoescape=True).render(obj=self)


class Comment(BaseModel):
    __tablename__ = 'comments'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    body: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='CASCADE')
    )
    post_id: Mapped[UUID] = mapped_column(
        ForeignKey('posts.uid', ondelete='CASCADE')
    )

    user: Mapped['User'] = relationship(
        back_populates='comments', lazy='noload'
    )
    post: Mapped['Post'] = relationship(
        back_populates='comments', lazy='noload'
    )
    reactions: Mapped[list['CommentReaction']] = relationship(
        back_populates='comment', lazy='noload'
    )

    @property
    def short_body(self) -> str:
        """Returns the comment's short body."""
        return self.body if len(self.body) < 50 else self.body[:47] + '...'

    async def __admin_repr__(self, _: Request):
        return self.body

    async def __admin_select2_repr__(self, _: Request) -> str:
        template_str = (
            '<span>'
            '<strong>Body: </strong>{{ obj.short_body }},'
            '&nbsp;'
            '<strong>Commented by: </strong>{{ obj.user.full_name }}'
            '</span>'
        )
        return Template(template_str, autoescape=True).render(obj=self)


class PostReaction(BaseModel):
    __tablename__ = 'post_reactions'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reaction_type: Mapped[Reactions] = mapped_column(
        Enum(Reactions), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='CASCADE')
    )
    post_id: Mapped[UUID] = mapped_column(
        ForeignKey('posts.uid', ondelete='CASCADE')
    )

    user: Mapped['User'] = relationship(
        back_populates='post_reactions', lazy='noload'
    )
    post: Mapped['Post'] = relationship(
        back_populates='reactions', lazy='noload'
    )


class CommentReaction(BaseModel):
    __tablename__ = 'comment_reactions'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reaction_type: Mapped[Reactions] = mapped_column(
        Enum(Reactions), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='CASCADE')
    )
    comment_id: Mapped[UUID] = mapped_column(
        ForeignKey('comments.uid', ondelete='CASCADE')
    )

    user: Mapped['User'] = relationship(
        back_populates='comment_reactions', lazy='noload'
    )
    comment: Mapped['Comment'] = relationship(
        back_populates='reactions', lazy='noload'
    )
