from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from src.core.config import settings

TABLE_ARGS = {"schema": settings.SCHEMA_NAME}


class UserBase(SQLModel):
    """Establishes the fundamental fields common to all user-related models,
    such as email, is_active, is_superuser, and full_name."""

    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Inherits from UserBase and is used specifically for creating new users.
    It adds a password field that is required only during the user creation process."""

    password: str = Field(min_length=8, max_length=72)


class User(UserBase, table=True):
    """This is the primary database table model for a user.
    It includes all fields from UserBase plus the database-specific fields: id (the primary key) and hashed_password.
    It also defines the one-to-many relationship, indicating that a user can own multiple items."""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    distraction_block_start: str = Field(default="10:30", max_length=5)
    distraction_block_end: str = Field(default="20:00", max_length=5)
    items: list["Item"] = Relationship(back_populates="owner")
    weekly_schedule_entries: list["WeeklyScheduleEntry"] = Relationship(
        back_populates="owner"
    )
    blocked_sites: list["BlockedSite"] = Relationship(back_populates="owner")

    __table_args__ = TABLE_ARGS


class BlockedSite(SQLModel, table=True):
    """Blocked hostnames for the browser distraction blocker (one row per user + url)."""

    __tablename__ = "blocked_site"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key=f"{settings.SCHEMA_NAME}.user.id", index=True)
    url: str = Field(max_length=2048)
    owner: Optional["User"] = Relationship(back_populates="blocked_sites")

    __table_args__ = (
        UniqueConstraint("owner_id", "url", name="uq_blocked_site_owner_url"),
        TABLE_ARGS,
    )


class UserRead(UserBase):
    """Designed for API responses when retrieving user data.
    It includes the user's id but omits sensitive information like the hashed_password to prevent it from being exposed."""

    id: int

class WeeklyScheduleEntry(SQLModel, table=True):
    """A single time-block row on the weekly importance × weekday grid."""

    __tablename__ = "weekly_schedule_entry"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    due_day: str
    importance: int = Field(default=0)
    category: str = Field(default="general")
    sort_order: int = Field(default=0)
    time_spent_minutes: float = Field(default=0.0)
    is_completed: bool = Field(default=False)

    owner_id: Optional[int] = Field(
        default=None,
        foreign_key=f"{settings.SCHEMA_NAME}.user.id",
    )

    owner: Optional["User"] = Relationship(back_populates="weekly_schedule_entries")

    __table_args__ = TABLE_ARGS


class WeeklyScheduleEntryUpdate(SQLModel):
    """Partial update for a weekly schedule row."""

    name: Optional[str] = None
    due_day: Optional[str] = None
    importance: Optional[int] = None
    category: Optional[str] = None
    sort_order: Optional[int] = None
    time_spent_minutes: Optional[float] = None
    is_completed: Optional[bool] = None

class BlockedSite(SQLModel, table=True):
    """Blocked hostnames for the browser distraction blocker."""

    __tablename__ = "blocked_site"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(
        foreign_key=f"{settings.SCHEMA_NAME}.user.id",
        index=True,
    )
    url: str = Field(max_length=2048)

    owner: Optional["User"] = Relationship(back_populates="blocked_sites")

    __table_args__ = (
        UniqueConstraint("owner_id", "url", name="uq_blocked_site_owner_url"),
        TABLE_ARGS,
    )

class ItemBase(SQLModel):
    """The base model for items, containing the core fields: title and description."""

    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Inherits from ItemBase and is used for validating the data when a new item is created."""

    pass


class ItemUpdate(SQLModel):
    """Used for updating an existing item. Its fields are optional,
    allowing for partial updates where only the changed fields need to be provided."""

    title: Optional[str] = None
    description: Optional[str] = None


class Item(ItemBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    owner_id: Optional[int] = Field(
        default=None,
        foreign_key=f"{settings.SCHEMA_NAME}.user.id"
    )

    owner: Optional["User"] = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"foreign_keys": "Item.owner_id"}
    )

    __table_args__ = TABLE_ARGS


class ItemRead(ItemBase):
    """The model for returning item data in API responses, including the item's id and the owner_id."""

    id: int
    owner_id: int
    category: str = "general"
    time_spent_minutes: float = 0.0
    is_completed: bool = False

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner: str

    __table_args__ = TABLE_ARGS


class WeeklyScheduleEntry(SQLModel, table=True):
    """A single time-block row on the weekly importance × weekday grid."""

    __tablename__ = "weekly_schedule_entry"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    due_day: str
    importance: int = Field(default=0)
    category: str = Field(default="general")
    sort_order: int = Field(default=0)
    time_spent_minutes: float = Field(default=0.0)
    is_completed: bool = Field(default=False)
    owner_id: Optional[int] = Field(
        default=None, foreign_key=f"{settings.SCHEMA_NAME}.user.id"
    )
    owner: Optional["User"] = Relationship(back_populates="weekly_schedule_entries")

    __table_args__ = TABLE_ARGS


class WeeklyScheduleEntryUpdate(SQLModel):
    """Partial update for a weekly schedule row (task board / tracker)."""

    name: Optional[str] = None
    due_day: Optional[str] = None
    importance: Optional[int] = None
    category: Optional[str] = None
    sort_order: Optional[int] = None
    time_spent_minutes: Optional[float] = None
    is_completed: Optional[bool] = None