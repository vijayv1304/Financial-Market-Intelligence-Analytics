
# --------------------------------------------------
# Financial Market Intelligence & Currency Risk Analytics
# Master Daily Market Refresh Pipeline
# --------------------------------------------------

import sys
import subprocess
from pathlib import Path
from datetime import datetime

from pipeline_logger import get_logger


# --------------------------------------------------
# 1. Initialize paths and logger
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "Python" / "Scripts"

logger = get_logger("Daily_Market_Refresh")

logger.info("Master daily market refresh started")
logger.info("Execution time: %s", datetime.now())


# --------------------------------------------------
# 2. Define incremental pipelines
# --------------------------------------------------

pipelines = [
    ("FX Incremental Refresh", "fx_incremental_refresh.py"),
    ("Stock Incremental Refresh", "stock_incremental_refresh.py")
]


# --------------------------------------------------
# 3. Execute pipelines sequentially
# --------------------------------------------------

for pipeline_name, script_name in pipelines:

    script_path = SCRIPTS_DIR / script_name

    if not script_path.is_file():
        raise FileNotFoundError(
            f"Pipeline script not found: {script_path}"
        )

    logger.info("Starting: %s", pipeline_name)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=False
    )

    if result.returncode != 0:
        logger.error(
            "%s FAILED | Exit Code: %s",
            pipeline_name,
            result.returncode
        )
        raise SystemExit(result.returncode)

    logger.info("%s completed successfully", pipeline_name)


# --------------------------------------------------
# 4. Final execution status
# --------------------------------------------------

logger.info("All market refresh pipelines completed successfully")
logger.info("Master daily market refresh finished")
