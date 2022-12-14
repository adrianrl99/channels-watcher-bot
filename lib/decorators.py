from pyrogram.types import Message
from prisma.models import User, Channel

import lib.database as db
import lib.app as app
from lib.i18n import t
from lib.logger import log


def only_admin(fn):
    async def wrapper(user: User | None, message: Message, t):
        if user and user.admin:
            await fn(user=user, message=message, t=t)
        else:
            await message.reply(t("not_admin"))

    return wrapper


def only_invited(fn):
    async def wrapper(user: User | None, message: Message, t):
        if user and (user.admin or not user.id):
            await fn(user=user, message=message, t=t)
        else:
            await message.reply(t("not_allowed"))

    return wrapper


def only_allowed(fn):
    async def wrapper(user: User | None, message: Message, t):
        if user:
            await fn(user=user, message=message, t=t)
        else:
            await message.reply(t("not_allowed"))

    return wrapper


def bot_inject(fn):
    async def wrapper(_, message: Message):
        code = message.from_user.language_code
        user = await db.find_user_invited(
            message.from_user.username
        ) or await db.find_user_accepted(message.from_user.id)

        if user:
            if (
                message.from_user.username != user.username
                or message.from_user.language_code != user.lang
            ):
                user = await db.update_user(user.uuid, message.from_user)

        if app.admin is None and user is None:
            app.admin = user = await db.create_admin(message.from_user)

        if user and user.id is None and user.username == message.from_user.username:
            user = await db.update_user_id(user.uuid, message.from_user.id)

        await fn(user=user, message=message, t=t(code))

    return wrapper


def log_try_access(fn):
    async def wrapper(_, message: Message):
        user = message.from_user
        command = message.command[0]
        log.info(
            f"User try to access to command {command} [id={user.id}, username={user.username}]"
        )
        await fn(_, message)

    return wrapper


def log_access(fn):
    async def wrapper(user: User, message: Message, t):
        command = message.command[0]
        log.info(
            f"User access to command {command} [uuid={user.uuid}, id={user.id}, username={user.username}]"
        )
        await fn(user=user, message=message, t=t)

    return wrapper


def userbot_inject(fn):
    async def wrapper(_, message: Message):
        channel = await db.find_channel_with_users(message.chat.id)
        await fn(channel=channel, message=message)

    return wrapper


def only_joined(fn):
    async def wrapper(channel: Channel | None, message: Message):
        if channel:
            await fn(channel=channel, message=message)

    return wrapper
