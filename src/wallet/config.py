from pathlib import Path
from typing import Optional

import config  # type: ignore
import hvac
from aiohttp_micro import AppConfig as BaseConfig  # type: ignore
from config.abc import Field
from passport.client import PassportConfig


class StorageConfig(config.PostgresConfig):
    host = config.StrField(default="localhost", env="POSTGRES_HOST")
    port = config.IntField(default=5432, env="POSTGRES_PORT")
    user = config.StrField(default="postgres", vault_path="micro/wallet/postgres:user", env="POSTGRES_USER")
    password = config.StrField(default="postgres", vault_path="micro/wallet/postgres:password", env="POSTGRES_PASSWORD")
    database = config.StrField(default="postgres", env="POSTGRES_DATABASE")
    min_pool_size = config.IntField(default=1, env="POSTGRES_MIN_POOL_SIZE")
    max_pool_size = config.IntField(default=2, env="POSTGRES_MAX_POOL_SIZE")

    @property
    def uri(self) -> str:
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=self.user, password=self.password, host=self.host, port=self.port, database=self.database,
        )


class AppConfig(BaseConfig):
    db = config.NestedField[StorageConfig](StorageConfig)
    passport = config.NestedField[PassportConfig](PassportConfig)
    sentry_dsn = config.StrField(vault_path="micro/wallet/sentry:dsn", env="SENTRY_DSN")


class VaultConfig(config.Config):
    host = config.StrField(env="VAULT_HOST")
    auth_method = config.StrField(default="approle", env="VAULT_AUTH_METHOD")
    service_name = config.StrField(default=None, env="VAULT_SERVICE_NAME")
    role_id = config.StrField(default=None, env="VAULT_ROLE_ID")
    secret_id = config.StrField(default=None, env="VAULT_SECRET_ID")


class VaultProvider(config.ValueProvider):
    def __init__(self, config: VaultConfig, mount_point: str) -> None:
        self.client = hvac.Client(url=config.host)
        self.mount_point = mount_point

        if config.auth_method == "approle":
            self.client.auth.approle.login(role_id=config.role_id, secret_id=config.secret_id)
        elif config.auth_method == "kubernetes":
            path = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
            with path.open("r") as fp:
                token = fp.read()

            self.client.auth.kubernetes.login(role=config.service_name, jwt=token)

    def load(self, field: Field) -> Optional[str]:
        value = None

        if field.vault_path:
            path, key = field.vault_path, None
            if ":" in field.vault_path:
                path, key = field.vault_path.split(":")

            secret_response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.mount_point)

            if key:
                value = secret_response["data"]["data"][key]

        return value
