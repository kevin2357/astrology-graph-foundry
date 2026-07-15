from astro_analysis_sdk.common.logging_config import configure_logging


def test_configure_logging_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    used = configure_logging(default_log_file=str(tmp_path / "test.log"))
    assert used is None or used.exists()
