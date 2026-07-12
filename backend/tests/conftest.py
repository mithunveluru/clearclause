import pytest_asyncio

from app.core.redis import redis_client
from app.db.session import engine


@pytest_asyncio.fixture(autouse=True)
async def isolate_loop_bound_clients():
    """Give every test fresh connections to the shared engine/redis singletons.

    Both bind their sockets to the event loop that first opens them, and each test
    gets a new loop. Without this, the second test to touch either one inherits
    connections tied to a closed loop — and because those tests guard themselves
    with a try/except reachability check, they would *skip silently* rather than
    fail. A test that opts itself out is worse than no test.

    Both calls abandon the stale connections rather than closing them; closing
    would reach back into the dead loop.
    """
    await engine.dispose(close=False)
    redis_client.connection_pool.reset()
    yield
