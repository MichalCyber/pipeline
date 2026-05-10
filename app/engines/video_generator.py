import subprocess
from pathlib import Path
import random

class VideoComposer:
    """
    Create short-form videos from static images
    Uses FFmpeg for Ken Burns effect, transitions, music
    """
    
    def __init__(self):
        self.ffmpeg = "ffmpeg"  # alebo plná cesta ak nie je v PATH
    
    def create_short(
        self,
        image_path: Path,
        output_path: Path,
        duration: int = 10,
        music_path: Path | None = None,
        add_zoom: bool = True
    ) -> Path:
        """
        Create short video from single image
        
        Args:
            image_path: Input AI image
            output_path: Where to save video
            duration: Video length in seconds (default 10)
            music_path: Optional background music
            add_zoom: Enable Ken Burns zoom effect
        
        Returns:
            Path to created video
        """
        
        # Ken Burns parameters (random for variety)
        if add_zoom:
            zoom_start = 1.0
            zoom_end = random.uniform(1.15, 1.3)  # Subtle zoom
            pan_x = random.choice(["0", "iw*0.1", "-iw*0.1"])
            pan_y = random.choice(["0", "ih*0.1", "-ih*0.1"])
            
            # Zoom + pan filter
            video_filter = (
                f"scale=1920:1080:force_original_aspect_ratio=increase,"
                f"crop=1920:1080,"
                f"zoompan=z='min(zoom+0.0015,{zoom_end})':x='{pan_x}':y='{pan_y}':"
                f"d={duration * 25}:s=1920x1080:fps=25"
            )
        else:
            # Static with fade
            video_filter = (
                f"scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
                f"fade=in:0:25,fade=out:{duration*25-25}:25"
            )
        
        # Base command
        cmd = [
            self.ffmpeg,
            "-loop", "1",
            "-i", str(image_path),
            "-vf", video_filter,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"
        ]
        
        # Add music if provided
        if music_path and music_path.exists():
            cmd.extend([
                "-i", str(music_path),
                "-shortest",
                "-c:a", "aac",
                "-b:a", "128k"
            ])
        else:
            # Silent video
            cmd.extend(["-an"])
        
        cmd.extend([
            "-y",  # Overwrite
            str(output_path)
        ])
        
        print(f"Creating video: {output_path.name}")
        subprocess.run(cmd, check=True, capture_output=True)
        
        return output_path
    
    def create_slideshow(
        self,
        image_paths: list[Path],
        output_path: Path,
        duration_per_image: int = 5,
        transition_duration: float = 1.0,
        music_path: Path | None = None
    ) -> Path:
        """
        Create slideshow video from multiple images
        
        Args:
            image_paths: List of input images
            output_path: Where to save video
            duration_per_image: Seconds per image
            transition_duration: Crossfade duration
            music_path: Optional background music
        """
        
        # Create concat file for FFmpeg
        concat_file = output_path.parent / "concat_list.txt"
        
        with open(concat_file, "w") as f:
            for img in image_paths:
                f.write(f"file '{img.absolute()}'\n")
                f.write(f"duration {duration_per_image}\n")
        
        # FFmpeg slideshow command
        cmd = [
            self.ffmpeg,
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-vf", (
                f"scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
                f"fade=in:0:25,fade=out:st={len(image_paths)*duration_per_image-1}:d=1"
            ),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p"
        ]
        
        if music_path and music_path.exists():
            cmd.extend([
                "-i", str(music_path),
                "-shortest",
                "-c:a", "aac"
            ])
        
        cmd.extend(["-y", str(output_path)])
        
        subprocess.run(cmd, check=True, capture_output=True)
        concat_file.unlink()  # Cleanup
        
        return output_path