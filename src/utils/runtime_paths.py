"""
런타임 경로 유틸리티
- 소스 실행/패키지 실행(예: PyInstaller) 환경 모두 지원
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    프로젝트 루트 추정.

    우선순위:
    1) HEIGHT_AI_BASE_DIR 환경 변수
    2) 패키지 실행 시 실행 파일 디렉터리
    3) 소스 실행 시 src/utils/.. 기준 루트
    """
    env_root = os.environ.get("HEIGHT_AI_BASE_DIR")
    if env_root:
        return Path(env_root).expanduser().resolve()

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    # src/utils/runtime_paths.py -> 프로젝트 루트
    return Path(__file__).resolve().parents[2]


def get_model_dir() -> Path:
    """
    모델 디렉터리 경로.

    우선순위:
    1) HEIGHT_AI_MODEL_DIR 환경 변수
    2) <project_root>/models/saved_models
    """
    env_model_dir = os.environ.get("HEIGHT_AI_MODEL_DIR")
    if env_model_dir:
        return Path(env_model_dir).expanduser().resolve()

    return get_project_root() / "models" / "saved_models"

