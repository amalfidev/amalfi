from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Self
from uuid import uuid4

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from amalfi.ops.map import map_
from amalfi.stream import astream

fake = Faker(locale="it_IT")
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


async def read_users_from_json_file():
    """Simulates a slow IO operation."""
    total_users = fake.random_int(min=5000, max=10000)
    await asyncio.sleep(0.000001)
    for user in (User.random() for _ in range(total_users)):
        yield user.model_dump()


async def fetch_user_activities_from_database(user_id: str):
    """Simulates a slow IO operation."""
    total_activities = fake.random_int(min=10, max=20)
    await asyncio.sleep(0.000001)
    for activity in (Activity.random(user_id) for _ in range(total_activities)):
        yield activity.model_dump()


async def augment_user_with_activities(user: User):
    return await astream(fetch_user_activities_from_database(user.id)).pipe(
        lambda p: p.then(map_(Activity.model_validate))
        .then(lambda a: {"activities": a})
        .then(lambda a: User.model_validate(user.model_dump() | a))
    )


async def write_users_to_json_file(users: list[User]):
    """Simulates a slow IO operation."""
    await asyncio.sleep(0.000001)
    print(f"Writing {len(users)} users to file")


async def main():
    user_stream = (
        astream(read_users_from_json_file())
        .map(User.model_validate)
        .filter(lambda u: u.country in ["IT"])
        .map(augment_user_with_activities)
        .tap(lambda u: print(f"{u.name} ({len(u.activities)} activities)"))
    )

    users = await user_stream.collect()
    print(f"Fetched {len(users)} users")

    ## Output:
    # > Maura Garzoni-Cannizzaro (19 activities)
    # > Priscilla Leoncavallo (16 activities)
    # > Ludovica Fracci (17 activities)
    # ...
    # > Fetched 28 users


if __name__ == "__main__":
    asyncio.run(main())
