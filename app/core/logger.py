import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ログの基本設定
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "app", level: int = logging.INFO) -> logging.Logger:
    """アプリ全体で共通利用するロガーを生成"""
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # すでに設定済みなら再設定しない

    logger.setLevel(level)

    # --- コンソール出力 ---
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(stream_handler)

    # --- ファイル出力（循環ログ: 最大10MB×5世代）---
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)

    # 外部ライブラリの過剰なログを抑制
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger


# --- グローバルロガー（例: app.logger で呼べる）---
logger = get_logger()
