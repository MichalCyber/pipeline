import json
import subprocess
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

FOOOCUS_PATH = Path("D:\Fooocus\Fooocus_win64_2-5-0\Fooocus")  # uprav podľa umiestnenia
JOBS_DIR = Path("outputs/jobs")

class FooocusRunner:
    def run_job(self, job_file: Path):
        logger.info(f"Running Fooocus job: {job_file.name}")

        with open(job_file, "r", encoding="utf-8") as f:
            job = json.load(f)

        cmd = [
            "python",
            "entry_with_update.py",
            "--prompt", job["prompt"],
            "--negative_prompt", job["negative_prompt"],
            "--image_number", str(job["num_images"]),
            "--resolution", job["resolution"]
        ]

        if job.get("seed"):
            cmd += ["--seed", str(job["seed"])]

        subprocess.Popen(
            cmd,
            cwd=FOOOCUS_PATH
        )

        logger.info(" Fooocus generation started")
