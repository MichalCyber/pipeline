import logging
from datetime import datetime
from app.pipeline.analyzer import ViralAnalyzer
from app.pipeline.prompt_builder import PromptBuilder
from app.pipeline.quality_gate import QualityGate
from app.pipeline.storage import StorageManager
from app.pipeline.collector import YouTubeShortsCollector
from app.collectors.ytdlp_collector import YtDlpCollector
import os

logger = logging.getLogger(__name__)

class ViralImagePipeline:
    def __init__(self):
        self.run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if os.getenv("USE_YTDLP", "false").lower() == "true":
            self.collector = YtDlpCollector()
            logger.info("Collector: yt-dlp")
        else:
            self.collector = YouTubeShortsCollector(
                os.getenv("YOUTUBE_API_KEY")
            )
            logger.info("Collector: YouTube API")

        self.analyzer = ViralAnalyzer()
        self.prompt_builder = PromptBuilder()
        self.quality_gate = QualityGate()
        self.storage = StorageManager()

    def run(self, query, num_images):
        self.storage.create_job_dir(self.run_id)
        self.storage.save_job_json(self.run_id, "meta", {
            "run_id": self.run_id,
            "query": query,
            "requested_images": num_images
        })
        posts = self.collector.search_shorts(query, 50)
        self.storage.save_job_json(self.run_id, "posts", posts)
        viral = self.analyzer.analyze(posts, top_k=20)
        self.storage.save_job_json(self.run_id, "viral", viral)

        results = []

        for post in viral:
            if len(results) >= num_images:
                break

            prompt = self.prompt_builder.build(post)

            # mock inference loop
            for attempt in range(3):
                import random
                clip_score = random.uniform(0.2, 0.4)
                passed, reasons = self.quality_gate.check(None, clip_score)

                self.storage.save_image(
                    self.run_id,
                    post["video_id"],
                    post["caption"],
                    prompt,
                    post["score"],
                    clip_score,
                    passed,
                    attempt + 1
                )

                if passed:
                    results.append({
                        "prompt": prompt,
                        "score": post["score"],
                        "video_id": post["video_id"]
                    })
                    break

        stats = self.quality_gate.get_stats()
        self.storage.save_job_json(self.run_id, "prompts", results)
        self.storage.save_job_json(self.run_id, "stats", stats)
        self.storage.save_job_json(self.run_id, "status", {"state": "done"})
        self.storage.save_run(
            self.run_id, query, num_images, len(results),
            stats["pass_rate"], stats["avg_clip_score"]
        )
        return results, stats
