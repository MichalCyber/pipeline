import time
from pathlib import Path

WATCH_DIR = Path("outputs/images")
PROCESSED = set()

def route_file(file: Path):
    print(f" Routing {file.name}")

    if file.suffix.lower() in [".jpg", ".png"]:
        print(" → IG / FB candidate")
    elif file.suffix.lower() in [".mp4", ".mov"]:
        print(" → YouTube / Shorts candidate")

def watch():
    WATCH_DIR.mkdir(parents=True, exist_ok=True)

    print(f" Watching {WATCH_DIR.resolve()}")

    while True:
        for file in WATCH_DIR.iterdir():
            if file.is_file() and file not in PROCESSED:
                route_file(file)
                PROCESSED.add(file)

        time.sleep(2)

if __name__ == "__main__":
    watch()
