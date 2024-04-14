from datetime import timedelta
from typing import AsyncIterator

from app.settings import settings
from rethinkdb.asyncio_net.net_asyncio import Connection

from rethinkdb import RethinkDB
from rethinkdb import query as r

__all__ = ["get_database", "Connection", "_get_database_sync", "_get_database_async"]

rethinkdb = RethinkDB()
rethinkdb_async = RethinkDB()
rethinkdb_async.set_loop_type("asyncio")


def _get_database_sync():
    """Internal function to get a database session. Use get_database() instead."""
    return rethinkdb.connect(
        db=settings.rethinkdb_database,
        host=settings.rethinkdb_host,
        port=settings.rethinkdb_port,
    )


async def _get_database_async():
    """Internal function to get a database session. Use get_database() instead."""
    return await rethinkdb_async.connect(
        db=settings.rethinkdb_database,
        host=settings.rethinkdb_host,
        port=settings.rethinkdb_port,
    )


async def get_database() -> AsyncIterator[Connection]:
    """Get a database session to be used with FastAPI's Depends()"""
    async with await _get_database_async() as conn:
        yield conn

