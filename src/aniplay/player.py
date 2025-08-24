from __future__ import annotations
import mpv

class Player:
    def __init__(self, embed_wid: int | None = None):
        if embed_wid is None:
            self._mpv = mpv.MPV()
        else:
            self._mpv = mpv.MPV(wid=str(int(embed_wid)))
        self._mpv["input-default-bindings"] = True
        self._mpv["osc"] = True
        self._mpv["hwdec"] = "auto-safe"

    def play(self, path: str) -> None:
        self._mpv.play(path)
        try:
            self._mpv.fullscreen = True
        except Exception:
            pass

    def stop(self) -> None:
        try:
            self._mpv.stop()
        except Exception:
            pass

    def quit(self) -> None:
        try:
            self._mpv.terminate()
        except Exception:
            pass