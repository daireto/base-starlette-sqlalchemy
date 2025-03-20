"""Admin model views."""

from collections.abc import Sequence
from html import escape

from jinja2 import Template
from sqlalchemy import Row, desc, func, literal_column, select, text
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView
from starlette_admin.fields import (
    EmailField,
    EnumField,
    IntegerField,
    PasswordField,
    TagsField,
    TextAreaField,
)

from core.bases.base_admin_view import BaseAdminView
from models.db import (
    Comment,
    CommentReaction,
    Post,
    PostReaction,
    Reactions,
    User,
)


class UserView(BaseAdminView, model=User):
    icon = 'fa fa-users'

    fields = [
        User.username,
        EmailField('email', required=True),
        PasswordField('password', required=True),
        User.first_name,
        User.last_name,
        User.role,
        User.gender,
        User.birthday,
        IntegerField('age', exclude_from_create=True, exclude_from_edit=True),
        User.is_active,
        User.created_at,
        User.updated_at,
    ]

    sortable_fields = [
        User.username,
        User.email,
        User.first_name,
        User.last_name,
    ]
    fields_default_sort = [User.username]
    exclude_fields_from_list = [User.birthday]
    exclude_timestamp_fields_from_list = True

    async def select2_selection(self, obj: User, _: Request) -> str:
        username = escape(obj.username)
        full_name = escape(obj.full_name)
        template_str = '<span>{{ username }} ({{ full_name }})</span>'
        return Template(template_str, autoescape=True).render(
            username=username, full_name=full_name
        )


class PostView(BaseAdminView, model=Post):
    icon = 'fa fa-blog'

    fields = [
        Post.title,
        TextAreaField('body', required=True, exclude_from_list=True),
        TagsField(
            'tags', display_template='tags.j2', render_function_key='tags'
        ),
        Post.publisher,
        Post.published_at,
    ]

    sortable_fields = [Post.title, Post.publisher, Post.published_at]
    sortable_field_mapping = {'publisher': User.username}
    fields_default_sort = [Post.published_at]

    def can_edit(self, _: Request) -> bool:
        return False


class CommentView(BaseAdminView, model=Comment):
    icon = 'fa fa-comments'

    fields = [
        Comment.user,
        Comment.post,
        TextAreaField('body', required=True),
        Comment.created_at,
    ]

    sortable_fields = [Comment.user, Comment.created_at]
    sortable_field_mapping = {'user': User.username}
    fields_default_sort = [Comment.created_at]

    def can_edit(self, _: Request) -> bool:
        return False


class PostReactionView(BaseAdminView, model=PostReaction):
    icon = 'fa fa-thumbs-up'

    fields = [
        EnumField(
            'reaction_type',
            enum=Reactions,
            form_template='reaction_field.j2',
            display_template='reaction.j2',
            render_function_key='reaction',
        ),
        PostReaction.user,
        PostReaction.post,
        PostReaction.created_at,
    ]

    sortable_fields = [
        PostReaction.user,
        PostReaction.reaction_type,
        PostReaction.created_at,
    ]
    sortable_field_mapping = {'user': User.username}
    fields_default_sort = [PostReaction.created_at]

    def can_edit(self, _: Request) -> bool:
        return False


class CommentReactionView(BaseAdminView, model=CommentReaction):
    icon = 'fa fa-thumbs-down'

    fields = [
        EnumField(
            'reaction_type',
            enum=Reactions,
            display_template='reaction.j2',
            render_function_key='reaction',
        ),
        CommentReaction.user,
        CommentReaction.comment,
        CommentReaction.created_at,
    ]

    sortable_fields = [
        CommentReaction.user,
        CommentReaction.reaction_type,
        CommentReaction.created_at,
    ]
    sortable_field_mapping = {'user': User.username}
    fields_default_sort = [CommentReaction.created_at]

    def can_edit(self, _: Request) -> bool:
        return False


class IndexView(CustomView):
    """Admin index view."""

    async def __fetch_top_publishers(
        self, session: AsyncSession
    ) -> Sequence[User]:
        """Fetches top 10 publishers.

        Parameters
        ----------
        session : AsyncSession
            SQLAlchemy session.

        Returns
        -------
        Sequence[User]
            List of top 10 publishers.
        """
        stmt = (
            select(User, func.count(Post.uid).label('cnt'))
            .limit(10)
            .join(Post)
            .group_by(User.uid)
            .order_by(desc('cnt'))
        )
        publishers_and_post_count = (
            (await session.execute(stmt)).tuples().all()
        )

        publishers = []
        for user, post_count in publishers_and_post_count:
            setattr(user, 'post_count', post_count)
            publishers.append(user)

        return publishers

    async def __fetch_latest_posts(
        self, session: AsyncSession
    ) -> Sequence[tuple[Post, list[tuple[Reactions, int]]]]:
        """Fetches 10 latest posts with reactions.

        Parameters
        ----------
        session : AsyncSession
            SQLAlchemy session.

        Returns
        -------
        Sequence[Post]
            List of 10 latest posts with reactions.
        """
        posts_with_reactions = []
        posts = (
            await Post.limit(10)
            .order_by('-published_at')
            .join(Post.publisher)
            .all()
        )
        for post in posts:
            stmt = (
                select(
                    PostReaction.reaction_type,
                    func.count(PostReaction.reaction_type).label('cnt'),
                )
                .join(Post)
                .filter(Post.uid == post.uid)
                .group_by(PostReaction.reaction_type)
                .order_by(desc('cnt'))
            )
            reactions_counter = (await session.execute(stmt)).tuples().all()
            posts_with_reactions.append((post, reactions_counter))

        return posts_with_reactions

    async def __fetch_recent_activity(
        self, session: AsyncSession
    ) -> Sequence[Row]:
        """Fetches recent activity (latest posts and comments).

        Parameters
        ----------
        session : AsyncSession
            SQLAlchemy session.

        Returns
        -------
        Sequence[Row]
            List of recent activity (latest posts and comments).
        """
        recent_posts_stmt = select(
            Post.title,
            Post.published_at.label('date'),
            literal_column('"ha publicado un post"').label('activity'),
            User.uid,
            User.username,
        ).join(User, Post.publisher_id == User.uid)

        recent_comments_stmt = select(
            Comment.body,
            Comment.created_at.label('date'),
            literal_column('"ha comentado en un post"').label('activity'),
            User.uid,
            User.username,
        ).join(User, Comment.user_id == User.uid)

        stmt = recent_posts_stmt.union(recent_comments_stmt)
        stmt = stmt.order_by(text('date desc')).limit(8)
        recent_activity = (await session.execute(stmt)).all()

        return recent_activity

    async def render(
        self, request: Request, templates: Jinja2Templates
    ) -> Response:
        session: AsyncSession = request.state.session

        # Top 10 publishers
        publishers = await self.__fetch_top_publishers(session)

        # 10 latest posts
        latest_posts = await self.__fetch_latest_posts(session)

        # Recent activity
        recent_activity = await self.__fetch_recent_activity(session)

        return templates.TemplateResponse(
            'home.j2',
            {
                'request': request,
                'posts': latest_posts,
                'publishers': publishers,
                'recent_activity': recent_activity,
            },
        )
