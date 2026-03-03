"""
로컬 예측 엔진 실행기

정적 웹(GitHub Pages 등)에서 localhost API를 호출할 수 있도록 Flask API 서버를 실행한다.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="키 예측 로컬 엔진 실행기")
    parser.add_argument("--host", default=os.environ.get("HEIGHT_AI_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("HEIGHT_AI_PORT", "58761")),
    )
    parser.add_argument(
        "--allow-origin",
        action="append",
        default=[],
        help="허용할 Origin. 여러 번 지정 가능 (예: --allow-origin https://obyeong-yun.github.io)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if getattr(sys, "frozen", False):
        # PyInstaller 배포 실행 시, 실행 파일 위치를 기준 경로로 사용
        base_dir = Path(sys.executable).resolve().parent
        os.environ.setdefault("HEIGHT_AI_BASE_DIR", str(base_dir))
        os.environ.setdefault("HEIGHT_AI_MODEL_DIR", str(base_dir / "models" / "saved_models"))

    if args.allow_origin:
        os.environ["HEIGHT_AI_ALLOWED_ORIGINS"] = ",".join(args.allow_origin)

    os.environ["HEIGHT_AI_HOST"] = args.host
    os.environ["HEIGHT_AI_PORT"] = str(args.port)

    from app.app import app, init_predictors  # pylint: disable=import-outside-toplevel

    print("=" * 60)
    print("Height Prediction Local Engine")
    print("=" * 60)
    print(f"API Endpoint: http://{args.host}:{args.port}")
    if args.allow_origin:
        print(f"Allowed Origins: {', '.join(args.allow_origin)}")
    print("")

    init_predictors()
    app.run(debug=False, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

