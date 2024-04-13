import os
import shlex
from random import choice
from random import sample
from urllib.parse import unquote

import streamlit as st

from febe import library
from febe import mpris

LIBRARY_ROOT = os.environ.get("MU")
assert LIBRARY_ROOT

st.session_state["is_paused"] = mpris.is_paused()

for k in ["np_artist", "np_album"]:
    st.session_state[k] = mpris.get_metadata(k.removeprefix("np_"))


def playback_controls():
    if not (st.session_state.np_artist and st.session_state.np_album):
        return

    st.header("Now playing")
    col1, col2 = st.columns([1, 1])

    label = "Play" if mpris.is_paused() else "Pause"

    def toggle_cb():
        mpris.play_pause()
        st.session_state["is_paused"] = not st.session_state["is_paused"]

    def vol_up():
        os.system("vol +5")

    def vol_down():
        os.system("vol -5")

    # st.write(st.session_state.np_artist, st.session_state.np_album)
    with col1:
        st.text(" - ".join([st.session_state.np_artist, st.session_state.np_album]))
        if genre := mpris.get_metadata("xesam:genre"):
            st.text(genre)
        try:
            st.text(mpris.get_metadata("xesam:contentCreated").split("-")[0])
        except AttributeError:
            pass

        # TODO: discogs, lastfm, ytm, sp

        buttons = {
            label: toggle_cb,
            # "Stop": mpris.stop,
            "Next": mpris.next,
            "`-`": vol_down,
            "`+`": vol_up,
        }

        for col, (label, cb) in zip(st.columns(len(buttons)), buttons.items()):
            with col:
                st.button(label, on_click=cb)

    with col2:
        show_album_art()


def play_album(album: str):
    assert os.path.isdir(album)

    mpv_args = "--mute=no --no-audio-display --pause=no --start=0%"

    def cb():
        os.system("pkill mpv")
        os.system(f"mpv {mpv_args} {shlex.quote(album)} &")
        os.system("sleep 1")
        st.session_state.np_artist = mpris.get_metadata("artist")
        st.session_state.np_album = mpris.get_metadata("album")

    st.button(
        "Play",
        on_click=cb,
        key=album,
        help="Current playback will be stopped!",
    )


def show_album_art():
    path = mpris.get_metadata("xesam:url")
    if not path:
        return
    art = os.path.dirname(unquote(path).removeprefix("file://")) + "/folder.jpg"
    if os.path.isfile(art):
        st.image(art)


def get_random_albums():
    # scanning all artists is a pretty bad idea; better to just scan 5 and select 1 album each (or just use the queue)
    albs = []
    for art in sample(list(library.get_artists()), 5):
        albs.append(choice(list(os.scandir(art))))
    return [x.path for x in albs]


playback_controls()

tab1, tab2, tab3 = st.tabs(["Manual", "Queued", "Random"])
with tab1:
    st.selectbox(
        label="Artist",
        # options=library.get_artists(),  # cannot pickle
        options=sorted(x.path for x in library.get_artists()),
        key="artist",
        format_func=lambda x: x.split("/")[-1],
    )

    st.radio(
        "Album",
        options=sorted(
            [x.path for x in library.get_albums(st.session_state.artist)],
            key=lambda x: x.split()[-1],
        ),
        key="album",
        format_func=lambda x: x.split("/")[-1],
    )

    play_album(st.session_state.album)

with tab2:
    with open(f"{os.environ.get('HOME')}/.config/mpv/queue") as f:
        albs = [l.strip() for l in f.readlines()]
        # st.write(albs)

    queued = st.selectbox(
        "Select queued album",
        options=sample(albs, 5),
    )
    assert queued
    play_album(os.path.join(LIBRARY_ROOT, queued))

with tab3:
    rand = st.selectbox(
        "Select random album",
        options=get_random_albums(),
        format_func=lambda x: x.removeprefix(LIBRARY_ROOT + "/"),
    )
    assert rand
    play_album(rand)
