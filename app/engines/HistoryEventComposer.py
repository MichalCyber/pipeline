import subprocess
from pathlib import Path
import random
from gtts import gTTS 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HistoryEventComposer:
    """Extended for history events recreation + voice over"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", mode: str = "drama"):
        self.ffmpeg = ffmpeg_path
        self.mode = mode  # "drama" or "history"
        
        # Mode-specific configs
        if mode == "drama":
            self.emotions = ["longing", "regret", "passion", "betrayal"]
            self.story_styles = ["romantic encounter", "dramatic revelation", "emotional farewell"]
            self.filters_extra = "hue=s=0.8"  # Soft desaturation for drama
        else:  # history
            self.emotions = ["triumph", "tragedy", "discovery", "conflict"]
            self.story_styles = ["epic battle moment", "historical turning point", "ancient discovery"]
            self.filters_extra = "vignette=PI/4,noise=alls=20:allf=t"  # Vintage grain + vignette
        
        self.music_dir = Path("D:/Music/RoyaltyFree")  # Dir s MP3 (dramatic orchestral)
    
    def create_short(
        self,
        image_path: Path,
        caption: str,
        output_path: Path,
        duration: int = 15,
        add_voice: bool = True
    ):
        """
        Creates viral short:
        - Dramatic zoom + effects
        - Caption overlay
        - Random background music
        - Optional AI voice over
        """
        # Random emotion/story for variety
        emotion = random.choice(self.emotions)
        story = random.choice(self.story_styles)
        
        # Caption with storytelling
        full_caption = f"{story.capitalize()}: {caption[:60]}... ({emotion})"
        
        # Base filters
        filters = [
            # Scale to vertical
            "scale=1920:-1,crop=1080:1920:(iw-1080)/2:(ih-1920)/2",
            # Slow zoom
            "zoompan=z='min(1+0.0015*on,1.15)':d=375:s=1080x1920:fps=30",
            # Mode-specific
            self.filters_extra,
            # Text overlay
            f"drawtext=text='{full_caption}':fontsize=48:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-200:shadowx=2:shadowy=2"
        ]
        
        cmd = [
            self.ffmpeg, "-loop", "1", "-i", str(image_path),
            "-vf", ",".join(filters),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-pix_fmt", "yuv420p"
        ]
        
        # Add music
        music = random.choice(list(self.music_dir.glob("*.mp3"))) if self.music_dir.exists() else None
        if music:
            cmd.extend(["-i", str(music), "-shortest", "-c:a", "aac", "-b:a", "128k"])
        
        # Add voice over
        if add_voice:
            voice_path = output_path.with_suffix('.mp3')
            self._generate_voice_over(full_caption, voice_path)
            cmd.extend(["-i", str(voice_path), "-shortest"])
        
        cmd.extend(["-y", str(output_path)])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _generate_voice_over(self, text: str, output: Path):
        """AI TTS voice over (gTTS - free, or replace with Coqui for better quality)"""
        tts = gTTS(text, lang='en', slow=False)  # 'zh-cn' for Chinese
        tts.save(str(output))
    
    def watch_fooocus(self, fooocus_dir: Path, output_dir: Path):
        """Watch Fooocus output and auto-process new images"""
        class Handler(FileSystemEventHandler):
            def on_created(event):
                if event.is_directory or not event.src_path.endswith(('.png', '.jpg')):
                    return
                image = Path(event.src_path)
                caption = image.stem  # Or extract from metadata
                self.create_short(image, caption, output_dir / f"{image.stem}.mp4")
        
        observer = Observer()
        observer.schedule(Handler(), str(fooocus_dir), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

# Example usage
if __name__ == "__main__":
    composer = HistoryEventComposer(mode="history")
    composer.create_short(
        Path("D:/Fooocus/outputs/input.png"),
        "Fall of Rome: Emperor's last stand",
        Path("D:/Output/history_short.mp4")
    )
    
    # Watcher
    # composer.watch_fooocus(Path("D:/Fooocus/outputs"), Path("D:/Output"))