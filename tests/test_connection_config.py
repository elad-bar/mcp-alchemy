import pytest

from mcp_alchemy.connection_config import (
    merge_config,
    normalize_header_key,
    resolve_db_url,
)


def test_db_url_only_backward_compatible():
    merged = merge_config(
        {"DB_URL": "postgresql://u:p@localhost/mydb"},
        {},
    )
    assert resolve_db_url(merged) == "postgresql://u:p@localhost/mydb"


def test_parts_from_headers_only():
    merged = merge_config(
        {},
        {
            "DB_DRIVER": "postgresql+psycopg2",
            "DB_HOST": "db.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "tenant_a",
            "DB_USER": "alice",
            "DB_PASSWORD": "secret",
        },
    )
    url = resolve_db_url(merged)
    assert "postgresql+psycopg2://" in url
    assert "alice" in url
    assert "db.example.com" in url
    assert "tenant_a" in url


def test_env_defaults_header_overrides():
    merged = merge_config(
        {
            "DB_DRIVER": "postgresql",
            "DB_HOST": "shared.host",
            "DB_PORT": "5432",
            "DB_NAME": "default_db",
            "DB_USER": "default_user",
            "DB_PASSWORD": "default_pass",
        },
        {
            "DB_NAME": "tenant_b",
            "DB_USER": "bob",
            "DB_PASSWORD": "bob_pass",
        },
    )
    url = resolve_db_url(merged)
    assert "shared.host" in url
    assert "tenant_b" in url
    assert "bob" in url
    assert "default_db" not in url


def test_empty_header_does_not_override_env():
    merged = merge_config(
        {"DB_HOST": "from.env"},
        {"DB_HOST": "   "},
    )
    assert merged["DB_HOST"] == "from.env"


def test_missing_parts_lists_keys():
    merged = merge_config({"DB_HOST": "h"}, {})
    with pytest.raises(ValueError, match="DB_DRIVER"):
        resolve_db_url(merged)


def test_db_url_wins_over_parts():
    merged = merge_config(
        {
            "DB_URL": "sqlite:////tmp/x.db",
            "DB_DRIVER": "postgresql",
            "DB_HOST": "ignored",
        },
        {},
    )
    assert resolve_db_url(merged) == "sqlite:////tmp/x.db"


def test_password_special_characters():
    merged = merge_config(
        {
            "DB_DRIVER": "postgresql",
            "DB_HOST": "localhost",
            "DB_NAME": "db",
            "DB_USER": "u",
            "DB_PASSWORD": "p@ss:w/ord?",
        },
        {},
    )
    url = resolve_db_url(merged)
    assert "p%40ss" in url or "p@ss" in url


def test_distinct_configs_distinct_urls():
    base = {
        "DB_DRIVER": "postgresql",
        "DB_HOST": "localhost",
        "DB_NAME": "db",
        "DB_USER": "u",
        "DB_PASSWORD": "p",
    }
    url_a = resolve_db_url(merge_config(base, {"DB_NAME": "a"}))
    url_b = resolve_db_url(merge_config(base, {"DB_NAME": "b"}))
    assert url_a != url_b


def test_normalize_header_key_case_insensitive():
    assert normalize_header_key("X-DB-Host") == "DB_HOST"
    assert normalize_header_key("x-db-url") == "DB_URL"
