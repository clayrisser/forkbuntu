from __future__ import annotations

import os
from pathlib import Path

import pytest

from forkbuntu.config import ConfigError, load_conf
from tests.conftest import write_config


class TestLoadConf:
    def test_missing_config_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigError, match="config not found"):
            load_conf(str(tmp_path))

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        (tmp_path / "config.yml").write_text("{invalid")
        with pytest.raises(ConfigError, match="invalid config"):
            load_conf(str(tmp_path))

    def test_non_mapping_yaml_raises(self, tmp_path: Path) -> None:
        (tmp_path / "config.yml").write_text("- a\n- b")
        with pytest.raises(ConfigError, match="expected a mapping"):
            load_conf(str(tmp_path))

    def test_defaults(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src")
        conf = load_conf(str(src))
        assert conf.apt.restricted is True
        assert conf.apt.universe is True
        assert conf.keyring is False
        assert conf.autoinstall == {}
        assert conf.packages == []
        assert conf.filesystem.compress is False

    def test_config_overrides_defaults(self, tmp_path: Path) -> None:
        src = write_config(
            tmp_path / "src",
            {"apt": {"restricted": False}, "keyring": True},
        )
        conf = load_conf(str(src))
        assert conf.apt.restricted is False
        assert conf.apt.universe is True
        assert conf.keyring is True

    def test_version_coerced_to_string(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src", {"version": 24.04})
        conf = load_conf(str(src))
        assert conf.version == "24.04"

    def test_paths_resolve_against_source_dir(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src", {"paths": {"iso": "base.iso"}})
        conf = load_conf(str(src))
        assert conf.paths.iso == str(src / "base.iso")
        assert conf.paths.cwt == str(src / ".tmp")
        assert conf.paths.mount == str(src / ".tmp" / "iso")

    def test_output_resolves_against_invocation_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        src = write_config(tmp_path / "src")
        invocation = tmp_path / "elsewhere"
        invocation.mkdir()
        monkeypatch.chdir(invocation)
        conf = load_conf(str(src))
        assert conf.paths.output == str(invocation / "forkbuntu.iso")

    def test_explicit_output_wins(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        src = write_config(tmp_path / "src", {"paths": {"output": "ignored.iso"}})
        monkeypatch.chdir(tmp_path)
        conf = load_conf(str(src), output="custom.iso")
        assert conf.paths.output == str(tmp_path / "custom.iso")

    def test_debug_flag_wins_over_config(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src")
        assert load_conf(str(src), debug=True).debug is True
        assert load_conf(str(src)).debug is False

    def test_tmp_dir_created(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src")
        conf = load_conf(str(src))
        assert os.path.isdir(conf.paths.tmp)

    def test_src_defaults_to_package_dir(self, tmp_path: Path) -> None:
        src = write_config(tmp_path / "src")
        conf = load_conf(str(src))
        assert os.path.exists(os.path.join(conf.paths.src, "preseed.seed"))
