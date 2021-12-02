from dataclasses import dataclass
from datetime import date
from typing import Callable, Generator

import pendulum  # type: ignore
import pytest  # type: ignore
from aiohttp import web
from aiohttp_storage.tests import storage  # type: ignore
from config import EnvValueProvider, load  # type: ignore
from cryptography.hazmat.primitives import serialization  # type: ignore
from cryptography.hazmat.primitives.asymmetric import rsa  # type: ignore
from passport.domain import TokenType, User  # type: ignore
from passport.services.tokens import TokenGenerator

from wallet.app import init
from wallet.config import AppConfig, VaultConfig, VaultProvider


@pytest.fixture(scope="function")
def user(faker) -> User:
    """Fake user."""
    return User(key=1, email=faker.free_email())


@dataclass
class Keypair:
    public: bytes
    private: bytes


@pytest.fixture(scope="session")
def keypair() -> Keypair:
    """Generate RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    return Keypair(
        private=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        public=private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH
        ),
    )


@pytest.fixture(scope="session")
def get_token_for(keypair: Keypair) -> Callable[[User], str]:
    """Fixture to generate access tokens for users."""
    generator = TokenGenerator(private_key=keypair.private.decode("utf-8"))

    def generate(user: User, token_type: TokenType = TokenType.access, ttl: int = 600) -> str:
        return generator.generate(user, token_type=token_type, expire=ttl)

    return generate


@pytest.fixture(scope="session")
def config(keypair: Keypair) -> AppConfig:
    """Generate application config."""
    vault_config = VaultConfig()
    load(vault_config, providers=[EnvValueProvider()])

    config = AppConfig(
        defaults={
            "debug": True,
            "passport": {"host": "http://localhost", "public_key": keypair.public.decode("utf-8")},
        }
    )
    load(config, providers=[VaultProvider(config=vault_config, mount_point="credentials"), EnvValueProvider()])

    return config


@pytest.fixture(scope="function")
def app(config) -> Generator[web.Application, None, None]:
    """Prepare test application."""
    app = init("wallet", config)

    with storage(config=app["config"].db, root=app["storage_root"]):
        yield app


@pytest.fixture(scope="function")
async def client(app, aiohttp_client):
    """Test client."""
    client = await aiohttp_client(app)

    return client


@pytest.fixture(scope="session")
def today() -> date:
    """Current date."""
    return pendulum.today()


@pytest.fixture(scope="session")
def month(today: pendulum.date) -> date:
    """Current month."""
    return today.start_of("month").date()
