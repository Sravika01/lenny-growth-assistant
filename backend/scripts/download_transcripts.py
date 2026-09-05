from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "transcripts"

REPOSITORY_URL = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"


def download_transcripts():
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)

    if DATA_DIR.exists() and any(DATA_DIR.iterdir()):
        print("Transcripts already exist.")
        return

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            REPOSITORY_URL,
            str(DATA_DIR),
        ],
        check=True,
    )

    print(f"Transcripts downloaded to: {DATA_DIR}")


if __name__ == "__main__":
    download_transcripts()