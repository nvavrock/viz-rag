#!/usr/bin/env python3
"""Build JSONL chunks for viz-rag embedding. Usage: python ingest/build_corpus.py"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
OUT = ROOT / "chunks" / "corpus.jsonl"


def split_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"\n(?=## )", text)
    out: list[tuple[str, str]] = []
    for part in parts:
        lines = part.splitlines()
        if lines and lines[0].startswith("## "):
            out.append((lines[0][3:].strip(), "\n".join(lines[1:]).strip()))
        else:
            out.append(("", part.strip()))
    return out


def strip_yaml_rmd(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---\n", 3)
        if end != -1:
            return text[end + 5 :]
    return text


def strip_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", html).strip()


def write_chunk(
    fh,
    source: str,
    path: str,
    section: str,
    text: str,
    meta: dict,
    counter: list[int],
) -> None:
    text = text.strip()
    if not text:
        return
    counter[0] += 1
    row = {
        "id": str(counter[0]),
        "source": source,
        "path": path,
        "section": section,
        "text": text,
        **meta,
    }
    fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def ingest_rmd(fh, path: Path, source: str, meta: dict, counter: list[int]) -> None:
    text = strip_yaml_rmd(path.read_text(encoding="utf-8", errors="replace"))
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    for heading, body in split_sections(text):
        section = heading or path.name
        write_chunk(fh, source, rel, section, body, meta, counter)


def ingest_md(fh, path: Path, source: str, meta: dict, counter: list[int]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    for heading, body in split_sections(text):
        section = heading or path.name
        write_chunk(fh, source, rel, section, body, meta, counter)


def ingest_html_caveat(fh, path: Path, source: str, meta: dict, counter: list[int]) -> None:
    html = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = m.group(1).strip() if m else path.name
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    write_chunk(fh, source, rel, title, strip_html(html), meta, counter)


def ingest_r_file(fh, path: Path, source: str, meta: dict, counter: list[int]) -> None:
    try:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        rel = str(path).replace("\\", "/")
    write_chunk(fh, source, rel, path.name, path.read_text(encoding="utf-8", errors="replace"), meta, counter)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    counter = [0]

    with OUT.open("w", encoding="utf-8") as fh:
        dtv = SOURCES / "data_to_viz"
        if dtv.is_dir():
            story = dtv / "story"
            for rmd in sorted(story.glob("*.Rmd")):
                ingest_rmd(
                    fh,
                    rmd,
                    "data_to_viz",
                    {"language": "r", "role": "chart_selection", "package": "ggplot2"},
                    counter,
                )
            readme = dtv / "Example_dataset" / "Readme.md"
            if readme.is_file():
                ingest_md(
                    fh,
                    readme,
                    "data_to_viz",
                    {"language": "r", "role": "data_shape", "package": "ggplot2"},
                    counter,
                )
            caveat = dtv / "caveat"
            if caveat.is_dir():
                for html in sorted(caveat.glob("*.html")):
                    ingest_html_caveat(
                        fh, html, "data_to_viz", {"language": "en", "role": "caveat"}, counter
                    )
        else:
            print("Missing sources/data_to_viz — run scripts/fetch_sources.sh")

        ggp = SOURCES / "ggplot2" / "vignettes"
        if ggp.is_dir():
            for vignette in sorted(ggp.glob("*.qmd")) + sorted(ggp.glob("*.Rmd")):
                ingest_rmd(
                    fh,
                    vignette,
                    "ggplot2",
                    {"language": "r", "role": "implementation", "package": "ggplot2"},
                    counter,
                )
        else:
            print("Missing sources/ggplot2 — run scripts/fetch_sources.sh")

        for sub, role in (
            ("corpus/style", "style"),
            ("corpus/notes", "theory"),
            ("corpus/lessons", "lesson"),
        ):
            d = ROOT / sub
            if d.is_dir():
                for md in sorted(d.glob("*.md")):
                    ingest_md(
                        fh,
                        md,
                        "local",
                        {"language": "en", "role": role, "package": "ggplot2"},
                        counter,
                    )

        tt_lessons = ROOT.parent / "tidytuesday" / "VIZ_LESSONS.md"
        if tt_lessons.is_file():
            ingest_md(
                fh,
                tt_lessons,
                "tidytuesday",
                {"language": "en", "role": "lesson", "package": "ggplot2"},
                counter,
            )

        tt_r = ROOT.parent / "tidytuesday" / "2026_06_16_uk_baby_names" / "R"
        if tt_r.is_dir():
            for rfile in sorted(tt_r.glob("*.R")):
                if rfile.name == "paths.R":
                    continue
                ingest_r_file(
                    fh,
                    rfile,
                    "tidytuesday",
                    {"language": "r", "role": "recipe", "package": "ggplot2"},
                    counter,
                )

    print(f"Wrote {counter[0]} chunks to {OUT}")


if __name__ == "__main__":
    main()
