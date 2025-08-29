// src/aniplay.cpp
#include <mpv/client.h>
#include <mpv/render_gl.h>
#include <iostream>
#include <string>

static mpv_handle *mpv = nullptr;

extern "C" {

// Initialize MPV
bool aniplay_init() {
    mpv = mpv_create();
    if (!mpv) return false;

    if (mpv_initialize(mpv) < 0) {
        return false;
    }
    return true;
}

// Load a video file
bool aniplay_load(const char *filename) {
    if (!mpv) return false;

    const char *cmd[] = {"loadfile", filename, nullptr};
    if (mpv_command(mpv, cmd) < 0) {
        return false;
    }
    return true;
}

// Stop and destroy
void aniplay_shutdown() {
    if (mpv) {
        mpv_terminate_destroy(mpv);
        mpv = nullptr;
    }
}

}
