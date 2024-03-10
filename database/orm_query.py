import json
import logging
import os
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError
from database.models import User, Phrase, UserPhrase

logging.basicConfig(filename=os.path.abspath('logs/db_errors.log'), format="%(asctime)s %(levelname)s %(message)s")


async def orm_add_user(*, session: AsyncSession, user: dict):
    try:
        obj = User(
            tg_id=user['id'],
            full_name=f"{user['first_name']}{user['last_name'] if user['last_name'] else ''}({user['username']})",
            data=json.dumps(user)
        )
        session.add(obj)
        await session.commit()
        return True
    except Exception as error:
        if error.orig.__cause__.__class__ != UniqueViolationError:
            logging.error(error)


async def orm_get_users(*, session: AsyncSession):
    try:
        query = select(User)
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as error:
        logging.error(error)


async def orm_get_user_by_tg_id(*, session: AsyncSession, tg_id: int):
    try:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        return result.scalar()
    except Exception as error:
        print(error)


async def orm_get_phrase(*, session: AsyncSession, phrase: str) -> Optional[Phrase]:
    try:
        phrase = phrase.lower()
        query_phrase = select(Phrase).where(Phrase.phrase == phrase.strip())
        result = await session.execute(query_phrase)
        return result.scalar()
    except Exception as error:
        logging.error(error)


async def orm_add_phrase(*, session: AsyncSession, phrase: str) -> Optional[Phrase]:
    try:
        phrase = phrase.lower().strip()
        obj = Phrase(
            phrase=phrase
        )
        session.add(obj)
        await session.commit()
        return obj
    except Exception as error:
        logging.error(error)


async def _orm_add_user_phrase(*, session: AsyncSession, phrase_id: int, user_id: int):
    try:
        obj = UserPhrase(
            user_id=user_id,
            phrase_id=phrase_id
        )
        session.add(obj)
        await session.commit()
    except Exception as error:
        logging.error(error)


async def orm_add_user_phrase(*, session: AsyncSession, phrase: str, user_id: int):
    try:
        user_obj = await orm_get_user_by_tg_id(session=session, tg_id=user_id)
        if user_obj is None:
            return

        phrase_obj = await orm_get_phrase(session=session, phrase=phrase)

        if phrase_obj is None:
            phrase_obj = await orm_add_phrase(session=session, phrase=phrase)

        if phrase_obj is None or phrase_obj.id <= 0:
            return
        await _orm_add_user_phrase(session=session, phrase_id=phrase_obj.id, user_id=user_obj.id)
    except Exception as error:
        logging.error(error)
