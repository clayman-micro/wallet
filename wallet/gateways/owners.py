import ujson
from aiohttp import ClientSession

from wallet.entities import Owner


class BrokenResponse(Exception):
    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text


class BadResponse(Exception):
    def __init__(self, status: int) -> None:
        self._status = status

    @property
    def status(self) -> int:
        return self._status


class BadToken(Exception):
    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text


class PassportGateway(object):
    def __init__(self, passport_dsn: str) -> None:
        self.passport_dsn = passport_dsn

    async def identify(self, token: str) -> Owner:
        headers = {'X-ACCESS-TOKEN': token}
        url = f'{self.passport_dsn}/api/identify'

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                status = resp.status
                text = await resp.text()

        if status == 200:
            try:
                payload = ujson.loads(text)
            except KeyError:
                raise BrokenResponse(text=text)
            except ValueError:
                raise BrokenResponse(text=text)
        elif status == 401:
            raise BadToken(text=text)
        else:
            raise BadResponse(status=status)

        return Owner(payload['owner']['email'], pk=payload['owner']['id'])
