"""Runtime settings for the RankUno GBP Intelligence Engine.

Secrets are read from ``.env`` (never hard-coded here). Thresholds and the
Learning Care Group sister-brand roster are plain configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings (see ``.env``)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
        extra="ignore",
    )

    # Bright Data Scraping Browser credentials. Empty by default so that a
    # missing .env fails loudly at the adapter boundary, not silently here.
    BRIGHT_DATA_AUTH: str = ""
    BRIGHT_DATA_WS_URL: str = ""

    # Google Business Profile API (official, client locations only).
    # OAuth desktop-app client secrets downloaded from Google Cloud Console and
    # the refresh-token store written by `python scripts/gbp_auth.py login`.
    GBP_CLIENT_SECRETS_FILE: str = "client_secret.json"
    GBP_TOKEN_FILE: str = ".gbp_token.json"

    # A service/category is a "gap" when at least this share of TRUE
    # competitors offer/claim it and the client GBP does not.
    GAP_THRESHOLD_PCT: int = 50

    # Star rating below which the Local Reputation Alert is CRITICAL.
    REPUTATION_CRITICAL_BELOW: float = 4.0

    # 11 Learning Care Group brands. Any discovered entity matching one of
    # these (by name or domain) is a sister brand, never a competitor.
    LCG_SISTER_BRANDS: list[str] = [
        "Childtime",
        "La Petite Academy",
        "Tutor Time",
        "The Children's Courtyard",
        "Everbrook Academy",
        "Montessori Unlimited",
        "Creative Kids Learning Centers",
        "Pathways Learning Academy",
        "Young School",
        "Apple Tree Children's Centers",
        "U-GRO Learning Centres",
    ]

    # Extra lower-case tokens that identify a sister brand in a business
    # name or website URL (short forms and known domains).
    LCG_SISTER_ALIASES: list[str] = [
        "creative kids",
        "pathways learning",
        "apple tree",
        "u-gro",
        "childtime.com",
        "lapetite.com",
        "tutortime.com",
        "childrenscourtyard.com",
        "everbrookacademy.com",
        "montessoriunlimited.com",
    ]


settings = Settings()
