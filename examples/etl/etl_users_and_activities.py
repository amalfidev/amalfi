from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Self
from uuid import uuid4

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from amalfi.stream import astream

fake = Faker()
fake.seed_instance(42)


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    country: str
    activities: list[Activity] = Field(default_factory=list)

    @classmethod
    def random(cls) -> Self:
        return cls(
            id=str(uuid4()),
            name=fake.name(),
            email=fake.email(),
            country=fake.country_code(),
        )


class Activity(BaseModel):
    id: str
    user_id: str
    type: str
    date: datetime

    @classmethod
    def random(cls, user_id: str) -> Self:
        return cls(
            id=str(uuid4()),
            user_id=user_id,
            type=fake.random_element(elements=("login", "logout", "click")),
            date=fake.date_time_between(start_date="-1y", end_date="now"),
        )


async def fetch_users():
    total_users = fake.random_int(min=100, max=1000)
    for user in (User.random() for _ in range(total_users)):
        await asyncio.sleep(0.000001)
        yield user.model_dump()


async def fetch_user_activities(user_id: str):
    total_activities = fake.random_int(min=10, max=100)
    for activity in (Activity.random(user_id) for _ in range(total_activities)):
        await asyncio.sleep(0.000001)
        yield activity.model_dump()


async def augment_user_with_activities(user: User):
    return (
        (await astream(fetch_user_activities(user.id)).to_pipe())
        .then(Activity.model_validate)
        .then(lambda a: {"activities": a})
        .then(lambda a: User.model_validate(user.model_dump() | a))
        .run()
    )


async def main():
    user_stream = (
        astream(fetch_users())
        .map(User.model_validate)
        .filter(lambda u: u.country in ["IT", "FR", "ES", "DE", "US"])
        .map(augment_user_with_activities)
        .tap(lambda u: print(f"{u.email} ({len(u.activities)} activities)"))
    )

    users = await user_stream.collect()
    print(f"Fetched {len(users)} users")


if __name__ == "__main__":
    asyncio.run(main())
