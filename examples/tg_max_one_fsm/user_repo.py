import uuid
from dataclasses import dataclass
from enum import Enum

import aiosqlite

from .ids import DbId, MaxId, SharedId, TgId


class ExternalType(Enum):
    TG = "TG"
    MAX = "MAX"


@dataclass
class DbUser:
    id: DbId
    external_id: TgId | MaxId
    external_type: ExternalType
    shared_id: SharedId


class UserRepo:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def create_table(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    external_id BIGINT,
                    external_type TEXT,
                    shared_id TEXT,
                    UNIQUE(external_id, external_type)
                )
                """,
            )
            await db.commit()

    async def get_or_create_user(
        self,
        external_id: TgId | MaxId,
        external_type: ExternalType,
    ) -> DbUser:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                (
                    "SELECT id, shared_id FROM users "
                    "WHERE external_id = ? AND external_type = ?"
                ),
                (external_id, external_type.value),
            )
            row = await cursor.fetchone()
            if row:
                db_id, shared_id = row
                return DbUser(
                    id=DbId(db_id),
                    external_id=external_id,
                    external_type=external_type,
                    shared_id=SharedId(int(shared_id)),
                )

            shared_id = str(uuid.uuid4().int)
            cursor = await db.execute(
                (
                    "INSERT OR IGNORE INTO users "
                    "(external_id, external_type, shared_id) "
                    "VALUES (?, ?, ?)"
                ),
                (external_id, external_type.value, shared_id),
            )
            await db.commit()

            if cursor.lastrowid == 0 or cursor.rowcount == 0:
                # Concurrent insert happened, re-fetch
                cursor = await db.execute(
                    (
                        "SELECT id, shared_id FROM users "
                        "WHERE external_id = ? AND external_type = ?"
                    ),
                    (external_id, external_type.value),
                )
                row = await cursor.fetchone()
                db_id, shared_id = row
                return DbUser(
                    id=DbId(db_id),
                    external_id=external_id,
                    external_type=external_type,
                    shared_id=SharedId(int(shared_id)),
                )

            db_id = cursor.lastrowid
            return DbUser(
                id=DbId(db_id),
                external_id=external_id,
                external_type=external_type,
                shared_id=SharedId(int(shared_id)),
            )

    async def link_accounts(
        self,
        current_user: DbUser,
        shared_id_to_link: SharedId,
    ) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET shared_id = ? WHERE shared_id = ?",
                (str(shared_id_to_link), str(current_user.shared_id)),
            )
            await db.commit()

    async def get_user_by_shared_id(self, shared_id: SharedId) -> list[DbUser]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                (
                    "SELECT id, external_id, external_type, shared_id FROM users "
                    "WHERE shared_id = ?"
                ),
                (str(shared_id),),
            )
            rows = await cursor.fetchall()
            return [
                DbUser(
                    id=DbId(row[0]),
                    external_id=row[1],
                    external_type=ExternalType(row[2]),
                    shared_id=SharedId(int(row[3])),
                )
                for row in rows
            ]
