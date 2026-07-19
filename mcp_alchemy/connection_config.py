from sqlalchemy.engine import URL

PARAM_DB_URL = "DB_URL"
PARAM_DB_DRIVER = "DB_DRIVER"
PARAM_DB_HOST = "DB_HOST"
PARAM_DB_PORT = "DB_PORT"
PARAM_DB_NAME = "DB_NAME"
PARAM_DB_USER = "DB_USER"
PARAM_DB_PASSWORD = "DB_PASSWORD"
PARAM_DB_ENGINE_OPTIONS = "DB_ENGINE_OPTIONS"
PARAM_EXECUTE_QUERY_MAX_CHARS = "EXECUTE_QUERY_MAX_CHARS"

CONNECTION_PART_KEYS = [
    PARAM_DB_DRIVER,
    PARAM_DB_HOST,
    PARAM_DB_PORT,
    PARAM_DB_NAME,
    PARAM_DB_USER,
    PARAM_DB_PASSWORD,
]

PARTS_MODE_REQUIRED_KEYS = [
    PARAM_DB_DRIVER,
    PARAM_DB_HOST,
    PARAM_DB_NAME,
    PARAM_DB_USER,
    PARAM_DB_PASSWORD,
]

SUPPORTED_ENV_VARS = [
    PARAM_DB_URL,
    *CONNECTION_PART_KEYS,
    PARAM_DB_ENGINE_OPTIONS,
    PARAM_EXECUTE_QUERY_MAX_CHARS,
]

SUPPORTED_HEADERS = {
    f"x-{env_var.replace('_', '-').lower()}": env_var
    for env_var in SUPPORTED_ENV_VARS
}


def normalize_header_key(key: str) -> str:
    lower = key.lower()
    if lower.startswith("x-") and lower in SUPPORTED_HEADERS:
        return SUPPORTED_HEADERS[lower]
    return key.upper()


def _non_empty(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def merge_config(
    env: dict[str, str],
    headers: dict[str, str],
) -> dict[str, str | None]:
    merged: dict[str, str | None] = {}
    for key in SUPPORTED_ENV_VARS:
        header_val = _non_empty(headers.get(key))
        env_val = _non_empty(env.get(key))
        merged[key] = header_val if header_val is not None else env_val
    return merged


def resolve_db_url(merged: dict[str, str | None]) -> str:
    db_url = _non_empty(merged.get(PARAM_DB_URL))
    if db_url is not None:
        return db_url

    missing = [key for key in PARTS_MODE_REQUIRED_KEYS if _non_empty(merged.get(key)) is None]
    if missing:
        raise ValueError(
            f"Database connection incomplete; set DB_URL or provide: {', '.join(missing)}"
        )

    port_raw = _non_empty(merged.get(PARAM_DB_PORT))
    port = int(port_raw) if port_raw is not None else None

    url = URL.create(
        drivername=merged[PARAM_DB_DRIVER],
        username=merged[PARAM_DB_USER],
        password=merged[PARAM_DB_PASSWORD],
        host=merged[PARAM_DB_HOST],
        port=port,
        database=merged[PARAM_DB_NAME],
    )
    return url.render_as_string(hide_password=False)
