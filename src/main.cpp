#include <mpv/client.h>
#include <mpv/render_gl.h>
#include <SDL2/SDL.h>
#include <GL/gl.h>
#include <iostream>
#include <stdexcept>

int main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        std::cerr << "Failed to init SDL: " << SDL_GetError() << "\n";
        return -1;
    }

    // Create SDL window with OpenGL context
    SDL_Window *window = SDL_CreateWindow(
        "AniPlay (SDL2 + mpv)",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        1280, 720,
        SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE
    );

    if (!window) {
        std::cerr << "Failed to create SDL window: " << SDL_GetError() << "\n";
        return -1;
    }

    SDL_GLContext gl_ctx = SDL_GL_CreateContext(window);
    if (!gl_ctx) {
        std::cerr << "Failed to create OpenGL context: " << SDL_GetError() << "\n";
        return -1;
    }

    // Init mpv
    mpv_handle *mpv = mpv_create();
    if (!mpv) {
        std::cerr << "Failed creating mpv instance\n";
        return -1;
    }

    if (mpv_initialize(mpv) < 0) {
        std::cerr << "mpv failed to initialize\n";
        return -1;
    }

    // Create render context
    mpv_opengl_init_params gl_init_params = {nullptr, nullptr, nullptr};
    mpv_render_param params[] = {
        {MPV_RENDER_PARAM_API_TYPE, const_cast<char*>(MPV_RENDER_API_TYPE_OPENGL)},
        {MPV_RENDER_PARAM_OPENGL_INIT_PARAMS, &gl_init_params},
        {MPV_RENDER_PARAM_INVALID, nullptr}
    };

    mpv_render_context *mpv_gl = nullptr;
    if (mpv_render_context_create(&mpv_gl, mpv, params) < 0) {
        std::cerr << "Failed to create mpv render context\n";
        return -1;
    }

    // Load a test video
    const char *cmd[] = {"loadfile", argc > 1 ? argv[1] : "video.mp4", nullptr};
    mpv_command(mpv, cmd);

    bool running = true;
    while (running) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) running = false;
        }

        glClear(GL_COLOR_BUFFER_BIT);

        mpv_render_param rp[] = {
            {MPV_RENDER_PARAM_OPENGL_FBO, (void*)(uintptr_t)0},
            {MPV_RENDER_PARAM_INVALID, nullptr}
        };

        mpv_render_context_render(mpv_gl, rp);

        SDL_GL_SwapWindow(window);
    }

    mpv_render_context_free(mpv_gl);
    mpv_terminate_destroy(mpv);
    SDL_GL_DeleteContext(gl_ctx);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
