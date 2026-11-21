# Copyright 2026 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import io
import stat
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def setup_module():
    path = Path(__file__).resolve().parents[1] / "setup.py"
    spec = importlib.util.spec_from_file_location("kcl_setup", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def downloader(setup_module, tmp_path):
    pom = tmp_path / "pom.xml"
    pom.write_text('''<project xmlns="http://maven.apache.org/POM/4.0.0">
        <properties/>
        <dependencies><dependency>
            <groupId>example</groupId><artifactId>test</artifactId><version>1</version>
        </dependency></dependencies>
    </project>''')
    jars = tmp_path / "jars"
    jars.mkdir()
    return setup_module.MavenJarDownloader(Mock(), str(jars), str(pom))


class InterruptedResponse(io.BytesIO):
    def __init__(self, prefix, error):
        super().__init__(prefix)
        self.error = error

    def read(self, size=-1):
        chunk = super().read(size)
        if chunk:
            return chunk
        raise self.error


@pytest.mark.parametrize("prefix", [b"", b"PK\x03\x04partial"])
@pytest.mark.parametrize("error", [OSError("interrupted"), IncompleteRead(b"partial")])
def test_failed_download_is_not_cached(setup_module, downloader, monkeypatch, prefix, error):
    response = InterruptedResponse(prefix, error)
    monkeypatch.setattr(setup_module, "urlopen", lambda url: response)

    downloader.download_files()

    assert len(downloader.missing_jars()) == 1
    assert list(Path(downloader.destdir).iterdir()) == []
    assert response.closed


def test_interrupted_download_is_retried(setup_module, downloader, monkeypatch):
    interrupted = InterruptedResponse(b"PK\x03\x04partial", OSError("interrupted"))
    complete = io.BytesIO(b"complete jar contents")
    urlopen = Mock(side_effect=[interrupted, complete])
    monkeypatch.setattr(setup_module, "urlopen", urlopen)

    downloader.download_files()
    downloader.download_files()

    assert urlopen.call_count == 2
    assert Path(downloader.destdir, "test-1.jar").read_bytes() == b"complete jar contents"
    assert downloader.missing_jars() == []
    assert interrupted.closed and complete.closed


def test_failed_download_is_reported(setup_module, downloader, monkeypatch):
    response = InterruptedResponse(b"partial", OSError("interrupted"))
    monkeypatch.setattr(setup_module, "urlopen", lambda url: response)

    with pytest.raises(RuntimeError, match="test-1.jar"):
        downloader.download_and_check()

    downloader.on_completion.assert_called_once_with()


def test_failed_download_preserves_existing_file(setup_module, downloader, monkeypatch):
    destination = Path(downloader.destdir, "test-1.jar")
    destination.write_bytes(b"existing jar contents")
    response = InterruptedResponse(b"partial", OSError("interrupted"))
    monkeypatch.setattr(setup_module, "urlopen", lambda url: response)

    downloader.download_file("https://example.invalid/test.jar", str(destination))

    assert destination.read_bytes() == b"existing jar contents"
    assert list(Path(downloader.destdir).iterdir()) == [destination]


def test_download_open_failure(setup_module, downloader, monkeypatch):
    monkeypatch.setattr(setup_module, "urlopen", Mock(side_effect=OSError("unavailable")))

    downloader.download_files()

    assert len(downloader.missing_jars()) == 1
    assert list(Path(downloader.destdir).iterdir()) == []


def test_existing_download_is_skipped(setup_module, downloader, monkeypatch):
    destination = Path(downloader.destdir, "test-1.jar")
    destination.write_bytes(b"existing jar contents")
    urlopen = Mock(side_effect=AssertionError("existing jars must not be downloaded"))
    monkeypatch.setattr(setup_module, "urlopen", urlopen)

    downloader.download_files()

    urlopen.assert_not_called()
    assert destination.read_bytes() == b"existing jar contents"
    assert downloader.missing_jars() == []


def test_successful_download(setup_module, downloader, monkeypatch):
    response = io.BytesIO(b"complete jar contents")
    monkeypatch.setattr(setup_module, "urlopen", lambda url: response)
    reference = Path(downloader.destdir, "reference")
    reference.write_bytes(b"")

    downloader.download_and_check()

    destination = Path(downloader.destdir, "test-1.jar")
    assert destination.read_bytes() == b"complete jar contents"
    assert stat.S_IMODE(destination.stat().st_mode) == stat.S_IMODE(reference.stat().st_mode)
    assert set(Path(downloader.destdir).iterdir()) == {destination, reference}
    assert response.closed
    downloader.on_completion.assert_called_once_with()


def test_relative_download_destination(setup_module, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = io.BytesIO(b"complete jar contents")
    monkeypatch.setattr(setup_module, "urlopen", lambda url: response)
    downloader = object.__new__(setup_module.MavenJarDownloader)

    downloader.download_file("https://example.invalid/test.jar", "test.jar")

    assert Path("test.jar").read_bytes() == b"complete jar contents"
    assert list(tmp_path.iterdir()) == [tmp_path / "test.jar"]
