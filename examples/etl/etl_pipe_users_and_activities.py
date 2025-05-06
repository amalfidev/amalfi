from __future__ import annotations

import asyncio

from amalfi.ops import filter_, map_, tap, tap_each
from amalfi.pipeline import pipe
from examples.stubs import Activity, User, fake


def read_users_from_json_file():
    """Simulates a slow IO operation."""
    total_users = fake.random_int(min=5000, max=10000)
    return [User.random().model_dump() for _ in range(total_users)]


def read_activities_from_json_file(user_id: str):
    """Simulates a slow IO operation."""
    total_activities = fake.random_int(min=5, max=10)
    return [Activity.random(user_id).model_dump() for _ in range(total_activities)]


def log_user(user: User):
    print(f"{user.name} ({len(user.activities)} activities)")


async def main():
    users_pipeline = (
        pipe(read_users_from_json_file())
        .then(tap(lambda _: print("Running ETL pipeline...")))
        .then(map_(User.model_validate))
        .then(filter_(lambda u: u.country == "IT"))
        .then(
            map_(
                lambda user: user.add_activities(
                    pipe(read_activities_from_json_file(user.id))
                    .then(map_(Activity.model_validate))
                    .run()
                )
            )
        )
        .then(tap_each(log_user))
        .then(list)
        .then(len)
        .then(print)
    )
    users_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
