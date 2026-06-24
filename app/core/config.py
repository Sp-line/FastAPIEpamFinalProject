from pydantic import BaseModel
from pydantic import HttpUrl
from pydantic import PostgresDsn
from pydantic import SecretStr
from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from app.constants.auth import JWTAlgorithm
from app.constants.db import DBDriver


class RunConfig(BaseModel):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    projects: str = "/projects"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class TestDBConfig(BaseModel):
    image: str = "postgres:15-alpine"
    driver: DBDriver = DBDriver.ASYNCPG


class TestAPIConfig(BaseModel):
    base_url: HttpUrl = HttpUrl("http://test")


class DatabaseConfig(BaseModel):
    host: str
    port: int = 5432
    name: str
    user: str
    password: SecretStr

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @computed_field
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        )


class S3Config(BaseModel):
    bucket_name: str
    region: str


class AuthConfig(BaseModel):
    secret: SecretStr
    algorithm: JWTAlgorithm = JWTAlgorithm.HS256
    lifetime_seconds: int = 60 * 60


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    test_db: TestDBConfig = TestDBConfig()
    test_api: TestAPIConfig = TestAPIConfig()
    db: DatabaseConfig
    s3: S3Config
    auth: AuthConfig

    model_config = SettingsConfigDict(
        env_file=("app/.env.template", "app/.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )


settings = Settings()
