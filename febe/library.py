import os


def get_artists():  # -> list[str]:
    return os.scandir(os.environ.get("MU"))


def get_albums(artist: str):  # -> list[str]:
    return os.scandir(
        os.path.join(
            os.environ.get("MU"),
            artist,
        )
    )
