from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import jinja2

import image_manipulation.showth as showth


def _fake_stat(tmp_file: Path, mtime: float = 1700000000.0, size: int = 2048) -> os.stat_result:
    """Helper to create fake stat info."""

    class _Stat:
        st_mtime = mtime
        st_size = size

    # Simulate `os.stat()` output partially
    return _Stat()  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# make_thumbnail
# ---------------------------------------------------------------------------


@patch("subprocess.run")
def test_make_thumbnail_invokes_convert(mock_run: MagicMock) -> None:
    showth.make_thumbnail("img.jpg", "out.jpg", 160, 120)
    mock_run.assert_called_once_with(["convert", "img.jpg", "-strip", "-resize", "160x120", "out.jpg"], check=False)


# ---------------------------------------------------------------------------
# get_image_info
# ---------------------------------------------------------------------------


@patch("os.stat")
@patch("time.strftime", return_value="Nov 11 2025")
def test_get_image_info_returns_expected(mock_strftime: MagicMock, mock_stat: MagicMock, tmp_path: Path) -> None:
    img_path = tmp_path / "photo.jpg"
    img_path.write_bytes(b"fake")

    mock_stat.return_value = _fake_stat(img_path)
    info = showth.get_image_info(str(img_path), 160, 120)

    assert info["tname"].startswith(showth.THUMB_DIR)
    assert info["size"].endswith("kB")
    assert info["date"] == "Nov 11 2025"
    assert info["width"] == 160
    assert info["height"] == 120
    assert isinstance(info["ddate"], float)


# ---------------------------------------------------------------------------
# render_page
# ---------------------------------------------------------------------------


def test_render_page_creates_expected_file(tmp_path: Path) -> None:
    tmpl = jinja2.Template("<html>{{ thispage }} of {{ data|length }}</html>")
    data = [{"name": "x.jpg"}]

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        showth.render_page(data, i=1, total=2, tmpl=tmpl, linktoparent=False)
        output_file = tmp_path / "index.html"
        assert output_file.exists()
        html = output_file.read_text()
        assert "1 of 1" in html or "1 of 2" in html
    finally:
        os.chdir(cwd)


# ---------------------------------------------------------------------------
# create_html
# ---------------------------------------------------------------------------


@patch("jinja2.Environment.get_template")
@patch("image_manipulation.showth.render_page")
def test_create_html_paginates_and_renders(
    mock_render: MagicMock, mock_get_template: MagicMock, tmp_path: Path
) -> None:
    tmpl = jinja2.Template("dummy")
    mock_get_template.return_value = tmpl

    data = []
    for i in range(25):
        data.append(
            {
                "name": f"img{i}.jpg",
                "tname": f"th/img{i}.th.jpg",
                "ddate": 1700000000.0 + i,
                "size": "1kB",
                "date": "Nov 11 2025",
                "width": 160,
                "height": 120,
            }
        )

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        showth.create_html(data, linktoparent=False)
    finally:
        os.chdir(cwd)

    # Expect 3 pages (12, 12, 1)
    assert mock_render.call_count == 3


# ---------------------------------------------------------------------------
# make_thumbnails
# ---------------------------------------------------------------------------


@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
@patch("image_manipulation.showth.make_thumbnail")
def test_make_thumbnails_parallel(mock_make: MagicMock, mock_exists: MagicMock, mock_makedirs: MagicMock) -> None:
    imgs = [
        {"name": "a.jpg", "tname": "th/a.th.jpg"},
        {"name": "b.jpg", "tname": "th/b.th.jpg"},
    ]
    showth.make_thumbnails(imgs)
    mock_make.assert_any_call("a.jpg", "th/a.th.jpg", showth.THUMB_WIDTH, showth.THUMB_HEIGHT)
    mock_make.assert_any_call("b.jpg", "th/b.th.jpg", showth.THUMB_WIDTH, showth.THUMB_HEIGHT)


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


@patch("image_manipulation.showth.create_html")
@patch("image_manipulation.showth.make_thumbnails")
@patch("image_manipulation.showth.get_image_info")
@patch("os.listdir")
def test_main_happy_path(
    mock_listdir: MagicMock,
    mock_get: MagicMock,
    mock_thumbs: MagicMock,
    mock_html: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_listdir.return_value = ["a.jpg", "b.JPG", "c.th.jpg"]
    mock_get.side_effect = lambda f, *_: {"name": f, "tname": f"th/{f}.th.jpg"}
    monkeypatch.chdir(tmp_path)

    showth.main()
    mock_thumbs.assert_called_once()
    mock_html.assert_called_once()


@patch("builtins.print")
@patch("os.listdir", return_value=[])
def test_main_no_images(mock_listdir: MagicMock, mock_print: MagicMock) -> None:
    showth.main()
    mock_print.assert_any_call("No JPG files found.")


def test_full_render_integration(tmp_path: Path) -> None:
    """Integration test: verifies HTML output is correctly generated from real Jinja2 template."""

    # --- prepare fake data ---
    data = [
        {
            "name": f"img{i}.jpg",
            "tname": f"th/img{i}.th.jpg",
            "ddate": 1700000000.0 + i,
            "size": "1kB",
            "date": "Nov 11 2025",
            "width": 160,
            "height": 120,
        }
        for i in range(15)
    ]  # 15 → will produce two pages

    tmpl_html = """
    <h1>Gallery page {{ thispage }}/{{ next if next else total }}</h1>
    {% for img in data %}
            <img src="{{ img.tname }}" alt="{{ img.name }}">
            <span>{{ img.size }}</span>
    {% endfor %}
    {% if prevlink %}
        <a href="index{{ prev }}.html">Prev</a>
    {% endif %}
    {% if next %}
        <a href="index{{ next }}.html">Next</a>
    {% endif %}
    {% if linktoparent %}
        <a href="../index.html">Up</a>
    {% endif %}
    """
    tmpl_file = tmp_path / "tmpl.html"
    tmpl_file.write_text(tmpl_html, encoding="utf-8")

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        showth.create_html(data, linktoparent=True)
        html_files = sorted(tmp_path.glob("index*.html"))
    finally:
        os.chdir(cwd)

    # --- assertions ---
    assert len(html_files) == 2  # pagination (12 per page)
    first_html = html_files[0].read_text()
    second_html = html_files[1].read_text()

    # The first page should contain 'Next' link and 'Up' link
    assert '<a href="index2.html">Next</a>' in first_html
    assert '<a href="../index.html">Up</a>' in first_html

    # The second page should contain 'Prev' link
    assert "Prev" in second_html
    # Each image reference should appear at least once -- and they're sorted backwards, alphabetically
    assert "th/img9.th.jpg" in first_html
    assert "th/img10.th.jpg" in second_html
