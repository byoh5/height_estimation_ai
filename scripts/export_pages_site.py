"""
GitHub Pages 배포용 정적 페이지 생성 스크립트.

`app/templates/index.html`의 Jinja 변수 일부를 실제 문자열로 치환해
`docs/index.html`로 내보낸다.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from version import __app_name__  # noqa: E402


def main():
    source_path = PROJECT_ROOT / "app" / "templates" / "index.html"
    output_dir = PROJECT_ROOT / "docs"
    output_path = output_dir / "index.html"
    nojekyll_path = output_dir / ".nojekyll"

    html = source_path.read_text(encoding="utf-8")

    replacements = {
        "{{ app_name }}": __app_name__,
    }

    for key, value in replacements.items():
        html = html.replace(key, value)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    nojekyll_path.write_text("", encoding="utf-8")

    print(f"✅ Pages 파일 생성 완료: {output_path}")


if __name__ == "__main__":
    main()

