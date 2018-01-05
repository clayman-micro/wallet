from aiohttp import web

from wallet.entities import Owner
from wallet.gateways.owners import PassportGateway


class OwnerAdapter(object):
    def __init__(self, gateway: PassportGateway) -> None:
        self.gateway = gateway

    async def identify(self, access_token: str) -> Owner:
        if not access_token:
            raise web.HTTPUnauthorized(text='Access denied')

        owner = await self.gateway.identify(access_token)

        return owner
