import logging
from datetime import datetime
from pathlib import Path


def setup_logging() -> str:
    """Returns the run prefix (e.g. logs/run_20260305_152412) for use in output filenames."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fmt = logging.Formatter("%(asctime)s %(message)s")

    run_handler = logging.FileHandler(logs_dir / f"run_{timestamp}.log")
    run_handler.setLevel(logging.INFO)
    run_handler.setFormatter(fmt)

    detail_handler = logging.FileHandler(logs_dir / f"run_{timestamp}_detail.log")
    detail_handler.setLevel(logging.DEBUG)
    detail_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(run_handler)
    root.addHandler(detail_handler)

    # Terminal stays at INFO
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler):
            h.setLevel(logging.INFO)

    return str(logs_dir / f"run_{timestamp}")


def section(title: str) -> None:
    logging.getLogger(__name__).info("\n%s\n  %s\n%s", "=" * 60, title, "=" * 60)
