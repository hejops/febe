import os
import subprocess


def subp_cmd(cmd: str) -> str:
    return subprocess.check_output(cmd.split()).decode("utf-8").strip()


def is_paused() -> bool:
    try:
        return subp_cmd("playerctl status") == "Paused"
    except subprocess.CalledProcessError:
        return True


def get_metadata(field: str) -> str | None:
    try:
        return subp_cmd(f"playerctl metadata {field}")
    except subprocess.CalledProcessError:
        return None


def next() -> None:
    os.system("playerctl next")


def play_pause() -> None:
    os.system("playerctl play-pause")


def stop() -> None:
    os.system("playerctl stop")
