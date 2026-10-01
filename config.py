import os
from dotenv import load_dotenv

# Load .env file from the project directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)


class Config:

    # ==============================
    # MYSQL DATABASE CONFIGURATION
    # ==============================

    MYSQL_HOST = os.getenv(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_PORT = int(os.getenv(
        "MYSQL_PORT",
        3306
    ))

    MYSQL_USER = os.getenv(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.getenv(
        "MYSQL_PASSWORD",
        ""
    )

    MYSQL_DB = os.getenv(
        "MYSQL_DB",
        "smartprep"
    )

    # ==============================
    # AIVEN MYSQL SSL CONFIGURATION
    # ==============================

    MYSQL_SSL_CA = os.getenv(
        "MYSQL_SSL_CA",
        ""
    )

    # ==============================
    # EMAIL CONFIGURATION
    # ==============================

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(os.getenv(
        "MAIL_PORT",
        587
    ))

    MAIL_USE_TLS = os.getenv(
        "MAIL_USE_TLS",
        "True"
    ).lower() in ("true", "1", "yes")

    MAIL_USE_SSL = os.getenv(
        "MAIL_USE_SSL",
        "False"
    ).lower() in ("true", "1", "yes")

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        ""
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        ""
    )

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        os.getenv(
            "MAIL_USERNAME",
            "SmartPrep <noreply@smartprep.com>"
        )
    )

    # ==============================
    # APPLICATION URL
    # ==============================

    APP_BASE_URL = os.getenv(
        "APP_BASE_URL",
        "http://127.0.0.1:5000"
    )