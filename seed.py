import asyncio
import random
from datetime import datetime, timezone
from uuid import uuid4

from dummy_text_generator import (
    NAMES,
    SURNAMES,
    TOPICS,
    generate_comment,
    generate_email_from_username,
    generate_paragraph,
    generate_sentence,
    generate_username_from_fullname,
)

from core.auth.enums import Roles
from core.settings import Settings
from models.db import (
    BaseModel,
    Comment,
    CommentReaction,
    Gender,
    Post,
    PostReaction,
    Reactions,
    User,
)
from utils.func import get_colored_logger, random_datetime, strip_accents

LANG = 'es'
USERS_NUMBER = 100
POSTS_NUMBER = 100
COMMENTS_PER_POST_NUMBER = 5
REACTIONS_PER_POST_NUMBER = 50
REACTIONS_PER_COMMENT_NUMBER = 10


logger = get_colored_logger()

conn = Settings.create_db_connection()


async def connect():
    logger.info('Connecting to database and initializing models...')
    await conn.init_db(BaseModel)
    logger.info('Database connected and models initialized')


async def disconnect():
    logger.info('Disconnecting from database...')
    await conn.close(BaseModel)
    logger.info('Database disconnected')


async def create_admin():
    username = 'daireto15'
    if await User.find(username=username).first():
        logger.info('Admin already exists')
        return

    logger.info('Creating admin...')
    admin = User(
        first_name='Dairo',
        last_name='Mosquera',
        username=username,
        email='daireto15@yopmail.com',
        role=Roles.ADMIN,
        gender=Gender.MALE,
        birthday=datetime(2002, 12, 4),
    )
    admin.set_password(username)
    await admin.save()
    logger.info('Admin created')


async def seed_users() -> list[User]:
    logger.info('Seeding users...')
    users = []
    usernames = []
    for _ in range(USERS_NUMBER):
        first_name = random.choice(NAMES[LANG])
        last_name = random.choice(SURNAMES[LANG])
        while True:
            username = generate_username_from_fullname(
                f'{first_name} {last_name}'
            )
            username = strip_accents(username)
            if username not in usernames:
                usernames.append(username)
                break
        email = generate_email_from_username(username)
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        birthday = random_datetime(min_year=1980, max_year=2004)
        user = User(
            uid=uuid4(),
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=Roles.USER,
            gender=gender,
            birthday=birthday,
        )
        user.set_password(username)
        users.append(user)

    await User.insert_all(users)
    logger.info('Users seeded')
    return users


async def seed_posts(users: list[User]) -> list[tuple[Post, str]]:
    logger.info('Seeding posts...')
    posts = []
    posts_and_topics: list[tuple[Post, str]] = []
    for _ in range(POSTS_NUMBER):
        topic = random.choice(TOPICS[LANG])
        tags = [topic] + random.sample(TOPICS[LANG], random.randint(1, 3))
        post = Post(
            uid=uuid4(),
            title=generate_sentence(
                lang=LANG,
                topic=topic,
                add_hashtag=random.choice([True, False]),
            ),
            body=generate_paragraph(lang=LANG, topic=topic),
            tags=tags,
            publisher_id=random.choice(users).uid,
            published_at=random_datetime(
                min_year=2023, max_year=2024, tz=timezone.utc
            ),
        )
        posts.append(post)
        posts_and_topics.append((post, topic))

    await Post.insert_all(posts)
    logger.info('Posts seeded')
    return posts_and_topics


async def seed_comments(
    users: list[User], posts_and_topics: list[tuple[Post, str]]
) -> list[Comment]:
    logger.info('Seeding comments...')
    comments = []
    for post, topic in posts_and_topics:
        for _ in range(COMMENTS_PER_POST_NUMBER):
            comment = Comment(
                uid=uuid4(),
                body=generate_comment(lang=LANG, topic=topic),
                user_id=random.choice(users).uid,
                post_id=post.uid,
                created_at=post.published_at,
                updated_at=post.published_at,
            )
            comments.append(comment)

    await Comment.insert_all(comments)
    logger.info('Comments seeded')
    return comments


async def seed_post_reactions(
    users: list[User], posts_and_topics: list[tuple[Post, str]]
):
    logger.info('Seeding post reactions...')
    post_reactions = []
    for post, _ in posts_and_topics:
        for _ in range(REACTIONS_PER_POST_NUMBER):
            reaction_type = random.choice(list(Reactions))
            user_id = random.choice(users).uid
            post_reaction = PostReaction(
                reaction_type=reaction_type,
                user_id=user_id,
                post_id=post.uid,
                created_at=post.published_at,
                updated_at=post.published_at,
            )
            post_reactions.append(post_reaction)

    await PostReaction.insert_all(post_reactions)
    logger.info('Post reactions seeded')


async def seed_comment_reactions(users: list[User], comments: list[Comment]):
    logger.info('Seeding comment reactions...')
    comment_reactions = []
    for comment in comments:
        for _ in range(REACTIONS_PER_COMMENT_NUMBER):
            reaction_type = random.choice(list(Reactions))
            user_id = random.choice(users).uid
            comment_reaction = CommentReaction(
                reaction_type=reaction_type,
                user_id=user_id,
                comment_id=comment.uid,
                created_at=comment.created_at,
                updated_at=comment.created_at,
            )
            comment_reactions.append(comment_reaction)

    await CommentReaction.insert_all(comment_reactions)
    logger.info('Comment reactions seeded')


async def seed():
    logger.info('Seeding database...')
    await create_admin()
    users = await seed_users()
    posts_and_topics = await seed_posts(users)
    comments = await seed_comments(users, posts_and_topics)
    await seed_post_reactions(users, posts_and_topics)
    await seed_comment_reactions(users, comments)
    logger.info('Database seeded')


async def main():
    try:
        await connect()
        await seed()
        await disconnect()
    except Exception as e:
        logger.critical(e)


if __name__ == '__main__':
    asyncio.run(main())
