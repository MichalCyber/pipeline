# test_video.py
from app.engines.video_generator import VideoComposer
from pathlib import Path

composer = VideoComposer()

# Najdi posledný vygenerovaný obrázok
images = list(Path("D:\Fooocus\Fooocus_win64_2-5-0\Fooocus\outputs").glob("*.png"))
latest = max(images, key=lambda p: p.stat().st_mtime)

# Vytvor video
video = composer.create_short(
    image_path=latest,
    output_path=Path("test_output.mp4"),
    duration=10,
    add_zoom=True
)

print(f"Video: {video}")