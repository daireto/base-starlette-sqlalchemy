import asyncio
import random
from datetime import datetime, timezone

from dummy_text_generator import (
    TOPICS,
    generate_comment,
    generate_email_from_username,
    generate_paragraph,
    generate_sentence,
    generate_username_from_fullname,
)
from faker import Faker

from core.auth.enums import Roles
from core.logger import logger
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
from utils.func import random_datetime, strip_accents

LANG = 'es'
FAKER_LANG = 'es_CO'

USERS_NUMBER = 100
POSTS_NUMBER = 100
COMMENTS_PER_POST_NUMBER = 5
REACTIONS_PER_POST_NUMBER = 50
REACTIONS_PER_COMMENT_NUMBER = 10


conn = Settings.create_db_connection()
faker = Faker(FAKER_LANG)


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
    admin = await User.find(username=username).first()
    if admin:
        logger.info('Admin already exists')
        return admin

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
    return admin


async def seed_users(admin: User) -> list[User]:
    def get_users(gender: Gender):
        users = []
        usernames = []
        for _ in range(int(USERS_NUMBER / 2)):
            while True:
                if gender == Gender.MALE:
                    first_name = faker.first_name_male()
                    last_name = faker.last_name_male()
                else:
                    first_name = faker.first_name_female()
                    last_name = faker.last_name_female()

                username = generate_username_from_fullname(
                    f'{first_name} {last_name}'
                )
                username = strip_accents(username)
                if username not in usernames:
                    usernames.append(username)
                    break

            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=generate_email_from_username(username),
                role=Roles.USER,
                gender=gender,
                birthday=random_datetime(min_year=1980, max_year=2004),
                created_by_id=admin.uid,
                updated_by_id=admin.uid,
            )
            user.set_password(username)
            users.append(user)

        return users

    logger.debug('Seeding users...')
    users = get_users(Gender.MALE) + get_users(Gender.FEMALE)
    await User.insert_all(users)
    logger.info('Users seeded')
    return users


async def seed_posts(users: list[User]) -> list[tuple[Post, str]]:
    logger.debug('Seeding posts...')
    posts = []
    posts_and_topics: list[tuple[Post, str]] = []
    for _ in range(POSTS_NUMBER):
        topic = random.choice(TOPICS[LANG])
        tags = [topic] + [faker.word() for _ in range(random.randint(1, 3))]
        post = Post(
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
    logger.debug('Seeding comments...')
    comments = []
    for post, topic in posts_and_topics:
        for _ in range(COMMENTS_PER_POST_NUMBER):
            comment = Comment(
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
    logger.debug('Seeding post reactions...')
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
    logger.debug('Seeding comment reactions...')
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
    logger.debug('Seeding database...')
    admin = await create_admin()
    users = await seed_users(admin)
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
