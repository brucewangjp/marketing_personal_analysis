"""Credentials come from the environment, never from the repository."""

from pathlib import Path

from app import config


def test_env_file_is_read(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('FRED_API_KEY="from-file"\n# a comment\n\nREQUEST_TIMEOUT=5\n')
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)
    monkeypatch.setattr(config, "ENV_FILE", env)

    settings = config.load()
    assert settings.fred_api_key == "from-file"
    assert settings.request_timeout == 5.0


def test_real_environment_wins_over_the_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("FRED_API_KEY=from-file\n")
    monkeypatch.setenv("FRED_API_KEY", "from-environment")
    monkeypatch.setattr(config, "ENV_FILE", env)

    assert config.load().fred_api_key == "from-environment"


def test_missing_env_file_is_fine(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / "absent")
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    assert config.load().has_fred_key is False


def test_blank_key_counts_as_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / "absent")
    monkeypatch.setenv("FRED_API_KEY", "")
    assert config.load().has_fred_key is False


def test_env_file_is_gitignored():
    ignored = Path(".gitignore").read_text()
    assert ".env" in ignored
    assert not Path(".env").exists() or ".env" in ignored


def test_example_env_carries_no_values():
    for line in Path(".env.example").read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            assert not value.strip() or key.strip() in {
                "TRENDS_IMPORT_DIR",
                "EVIDENCE_DB",
                "REQUEST_TIMEOUT",
            }, f"{key} has a value in .env.example"
