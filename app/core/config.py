from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import HttpUrl
from pydantic import PostgresDsn
from pydantic import SecretStr
from pydantic import computed_field
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from app.constants.auth import JWTAlgorithm
from app.constants.db import DBDriver
from app.constants.env_type import EnvironmentType
from app.constants.messages.config import ConfigErrorMessage

if TYPE_CHECKING:
    from typing import Self

BASE_DIR: Path = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    projects: str = "/projects"
    documents: str = "/documents"


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
    endpoint_url: HttpUrl | None = None
    access_key: str | None = None
    secret_key: str | None = None
    bucket_name: str
    region: str

    presigned_url_expire_seconds: int = 5 * 60


class AuthConfig(BaseModel):
    secret: SecretStr
    algorithm: JWTAlgorithm = JWTAlgorithm.HS256
    lifetime_seconds: int = 60 * 60


class FastAPIMailConfig(BaseModel):
    mail_server: str
    mail_port: int
    mail_from: EmailStr
    mail_starttls: bool
    mail_ssl_tls: bool
    use_credentials: bool
    validate_certs: bool

    mail_username: str | None = None
    mail_password: SecretStr | None = None

    mail_from_name: str | None = None
    mail_debug: int = 0
    suppress_send: int = 0
    timeout: int = 60
    local_hostname: str | None = None
    cert_bundle: str | None = None


class SESMailConfig(BaseModel):
    region: str
    sender: str


class EmailConfig(BaseModel):
    app_domain: str

    fastapi: FastAPIMailConfig | None = None
    ses: SESMailConfig | None = None


class TemplatesConfig(BaseModel):
    path: Path = BASE_DIR / "templates"


class Settings(BaseSettings):
    env: EnvironmentType = EnvironmentType.LOCAL
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    test_db: TestDBConfig = TestDBConfig()
    test_api: TestAPIConfig = TestAPIConfig()
    templates: TemplatesConfig = TemplatesConfig()
    db: DatabaseConfig
    s3: S3Config
    auth: AuthConfig
    email: EmailConfig

    model_config = SettingsConfigDict(
        env_file=("app/.env.template", "app/.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_s3_credentials_for_env(self) -> Self:
        env_depends_on_minio = self.env in {EnvironmentType.LOCAL, EnvironmentType.TEST}
        missing_minio_credentials = not all(
            [self.s3.access_key, self.s3.secret_key, self.s3.endpoint_url]
        )

        if env_depends_on_minio and missing_minio_credentials:
            raise ValueError(ConfigErrorMessage.LOCAL_S3_MISSING_CREDENTIALS)
        return self

    @model_validator(mode="after")
    def validate_email_credentials_for_env(self) -> Self:
        env_depends_on_fastapi_mail = self.env in {
            EnvironmentType.LOCAL,
            EnvironmentType.TEST,
        }
        fastapi_mail = self.email.fastapi

        if env_depends_on_fastapi_mail and fastapi_mail is None:
            raise ValueError(ConfigErrorMessage.MISSING_LOCAL_EMAIL_CONFIG)

        env_depends_on_ses = self.env == EnvironmentType.PROD
        ses = self.email.ses

        if env_depends_on_ses and ses is None:
            raise ValueError(ConfigErrorMessage.MISSING_PROD_EMAIL_CONFIG)

        return self


settings = Settings()
