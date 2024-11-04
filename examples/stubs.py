from __future__ import annotations

from datetime import datetime
from typing import Iterable, Self
from uuid import uuid4

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

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

    def add_activities(self, activities: Iterable[Activity]) -> Self:
        self.activities.extend(activities)
        return self


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
