"""
로컬 예측 엔진 실행기

정적 웹(GitHub Pages 등)에서 localhost API를 호출할 수 있도록 Flask API 서버를 실행한다.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
        # PyInstaller onedir 배포 시 데이터 파일은 _internal 하위에 배치된다.
        base_dir = Path(sys.executable).resolve().parent
        bundle_dir = Path(getattr(sys, "_MEIPASS", base_dir / "_internal")).resolve()
        model_dir = bundle_dir / "models" / "saved_models"
        if not model_dir.exists():
            # 일부 환경에서는 _MEIPASS가 비어 있어 실행 파일 기준 경로를 사용해야 한다.
            fallback_model_dir = base_dir / "models" / "saved_models"
            if fallback_model_dir.exists():
                bundle_dir = base_dir
                model_dir = fallback_model_dir

        os.environ.setdefault("HEIGHT_AI_BASE_DIR", str(bundle_dir))
        os.environ.setdefault("HEIGHT_AI_MODEL_DIR", str(model_dir))

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
