import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


async def orm_add_user(*, session: AsyncSession, user: dict):
    obj = User(
        tg_id=user['id'],
        full_name=f"{user['first_name']}{user['last_name'] if user['last_name'] else ''}({user['username']})",
        data=json.dumps(user)
    )
    try:
        session.add(obj)
        await session.commit()
    except Exception as error:
        print(error)


async def orm_get_users(*, session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()
