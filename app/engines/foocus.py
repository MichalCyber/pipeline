import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

JOBS_DIR = Path("outputs/jobs")
IMAGES_DIR = Path("outputs/images")

class FooocusEngine:

    def __init__(self):
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    def create_job(
        self,
        run_id: str,
        prompt: str,
        negative_prompt = (
            "text, watermark, logo, subtitles, extra fingers, extra limbs, "
            "deformed face, bad anatomy, low quality"
        ),
        num_images: int = 2,
        resolution: str = "1024x1024",
        seed: int | None = None
    ) -> Path:

        job = {
            "run_id": run_id,
            "engine": "foocus",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_images": num_images,
            "resolution": resolution,
            "seed": seed,
            "created_at": datetime.utcnow().isoformat()
        }

        job_path = JOBS_DIR / f"job_{run_id}.json"

        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job, f, indent=2)

        logger.info(f" Fooocus job created: {job_path}")
        return job_path
