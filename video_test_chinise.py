from app.engines.video_composer_pro import VideoComposerPro
from pathlib import Path

composer = VideoComposerPro()

# Test 1: Dramatic zoom
composer.dramatic_zoom(
    image=Path("your_fooocus_image.png"),
    output=Path("test_zoom.mp4"),
    caption="After divorce, she became a billionaire CEO",
    duration=12
)

# Test 2: Before/After
composer.split_reveal(
    left=Path("before.png"),
    right=Path("after.png"),
    output=Path("test_reveal.mp4")
)