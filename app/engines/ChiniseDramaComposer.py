import subprocess


class ChineseDramaComposer:
    """Specialized for Chinese drama viral shorts"""
    
    def create_drama_short(
        self,
        image_path: r"D:\Fooocus\Fooocus_win64_2-5-0\Fooocus\outputs",
        caption: str,
        output_path: r"D:\Fooocus"
    ):
        """
        Creates viral-style short:
        - Slow dramatic zoom
        - Caption overlay (white text, black outline)
        - Emotional music
        - 12-15 seconds
        """
        
        # Clean caption (max 60 chars)
        caption = caption[:60]
        
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", str(image_path),
            "-vf", (
                # 1. Scale + crop to 9:16 (vertical)
                "scale=1920:-1,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,"
                # 2. Slow zoom (1.0 → 1.2 over 12s)
                "zoompan=z='min(1+0.0017*on,1.2)':d=300:s=1080x1920:fps=25,"
                # 3. Add cinematic bars
                "pad=1080:1920:0:0:black,"
                # 4. Text caption
                f"drawtext=text='{caption}':"
                "fontfile=/Windows/Fonts/arial.ttf:"
                "fontsize=48:fontcolor=white:"
                "borderw=4:bordercolor=black:"
                "x=(w-text_w)/2:y=h-200:"
                "shadowx=2:shadowy=2"
            ),
            "-t", "12",
            # Audio
            "-af", "volume=0.7,afade=in:st=0:d=1,afade=out:st=11:d=1",
            "-shortest",
            # Output
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y", str(output_path)
        ]
        
        subprocess.run(cmd, check=True)