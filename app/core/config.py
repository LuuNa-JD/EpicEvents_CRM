from decouple import config


class Settings:
    DATABASE_URL = config("DATABASE_URL")
    DEBUG = config("DEBUG", cast=bool, default=False)
    SECRET_KEY = config("SECRET_KEY", default="changeme")


settings = Settings()
