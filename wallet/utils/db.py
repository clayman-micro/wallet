

class Connection(object):

    def __init__(self, engine):
        self.conn = None
        self.engine = engine

    async def __aenter__(self):
        self.conn = await self.engine.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        try:
            self.engine.release(self.conn)
        finally:
            self.conn = None
            self.engine = None

