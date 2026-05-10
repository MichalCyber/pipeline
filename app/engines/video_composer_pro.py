import subprocess
from pathlib import Path
import random

class VideoComposerPro:
    """
    Professional video effects for viral Chinese drama shorts
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path
    
    def dramatic_zoom(
        self,
        image: Path,
        output: Path,
        caption: str = "",
        duration: int = 12,
        music: Path | None = None
    ):
        """Slow zoom + text overlay (MOST VIRAL)"""
        
        filters = [
            # Vertical format
            "scale=1920:-1,crop=1080:1920:(iw-1080)/2:(ih-1920)/2",
            # Zoom effect
            "zoompan=z='min(1+0.0017*on,1.2)':d=300:s=1080x1920:fps=25"
        ]
        
        # Add text if provided
        if caption:
            filters.append(
                f"drawtext=text='{caption}':"
                "fontsize=48:fontcolor=white:borderw=4:bordercolor=black:"
                "x=(w-text_w)/2:y=h-200"
            )
        
        cmd = [
            self.ffmpeg, "-loop", "1", "-i", str(image),
            "-vf", ",".join(filters),
            "-t", str(duration)
        ]
        
        if music:
            cmd.extend(["-i", str(music), "-shortest", "-c:a", "aac"])
        
        cmd.extend(["-c:v", "libx264", "-preset", "medium", "-y", str(output)])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output
    
    def split_reveal(self, left: Path, right: Path, output: Path):
        """Before/after split screen"""
        
        cmd = [
            self.ffmpeg,
            "-loop", "1", "-t", "12", "-i", str(left),
            "-loop", "1", "-t", "12", "-i", str(right),
            "-filter_complex", (
                "[0:v]scale=1080:1920,fade=out:st=5:d=1[v0];"
                "[1:v]scale=1080:1920,fade=in:st=5:d=1[v1];"
                "[v0][v1]overlay"
            ),
            "-c:v", "libx264", "-y", str(output)
        ]
        
        subprocess.run(cmd, check=True)
        return output
    
    def slideshow(
        self,
        images: list[Path],
        output: Path,
        transition: str = "fade",
        duration_per: int = 4
    ):
        """Multi-image slideshow with transitions"""
        
        # Available transitions:
        # fade, wipeleft, wiperight, slideup, slidedown, 
        # circleopen, circleclose, dissolve
        
        filters = []
        for i, img in enumerate(images):
            filters.append(
                f"[{i}:v]scale=1080:1920,setsar=1,fps=25,"
                f"trim=duration={duration_per}[v{i}]"
            )
        
        # Build transition chain
        prev = "v0"
        for i in range(1, len(images)):
            offset = (i * duration_per) - 1
            xfade = f"[{prev}][v{i}]xfade=transition={transition}:duration=1:offset={offset}[vf{i}]"
            filters.append(xfade)
            prev = f"vf{i}"
        
        cmd = [
            self.ffmpeg,
            *[item for img in images for item in ["-loop", "1", "-i", str(img)]],
            "-filter_complex", ";".join(filters),
            "-map", f"[{prev}]",
            "-t", str(len(images) * duration_per),
            "-c:v", "libx264",
            "-y", str(output)
        ]
        
        subprocess.run(cmd, check=True)
        return output