#include <mpv/client.h>
#include <mpv/render_gl.h>
#include <GLFW/glfw3.h>
#include <iostream>

static void on_mpv_update(void *ctx) {
    mpv_handle *mpv = (mpv_handle *)ctx;
    while (true) {
        mpv_event *event = mpv_wait_event(mpv, 0);
        if (event->event_id == MPV_EVENT_NONE) {
            break;
        }
        // Handle events if needed
    }
}

int main(int argc, char **argv) {
    if (!glfwInit()) {
        std::cerr << "Failed to init GLFW" << std::endl;
        return -1;
    }

    GLFWwindow *window = glfwCreateWindow(1280, 720, "Aniplay", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create window" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // Init mpv
    mpv_handle *mpv = mpv_create();
    if (!mpv) {
        std::cerr << "failed creating mpv" << std::endl;
        return -1;
    }

    mpv_set_option_string(mpv, "vo", "gpu");
    mpv_initialize(mpv);

    // Proper function loader wrapper
    mpv_opengl_init_params gl_init_params;
    gl_init_params.get_proc_address = [](void *, const char *name) -> void * {
        return reinterpret_cast<void *>(glfwGetProcAddress(name));
    };
    gl_init_params.get_proc_address_ctx = nullptr;

    mpv_render_param params[] = {
        {MPV_RENDER_PARAM_API_TYPE, (void *)MPV_RENDER_API_TYPE_OPENGL},
        {MPV_RENDER_PARAM_OPENGL_INIT_PARAMS, &gl_init_params},
        {MPV_RENDER_PARAM_FLIP_Y, (void *)1},  // 👈 Fix upside-down video
        {MPV_RENDER_PARAM_INVALID, nullptr}};

    mpv_render_context *mpv_gl = nullptr;
    if (mpv_render_context_create(&mpv_gl, mpv, params) < 0) {
        std::cerr << "failed to initialize mpv GL context" << std::endl;
        return -1;
    }

    mpv_render_context_set_update_callback(mpv_gl, on_mpv_update, mpv);

    // Load a file (replace with your own path)
    const char *cmd[] = {"loadfile", "test.mp4", nullptr};
    mpv_command(mpv, cmd);

    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT);

        int win_w, win_h;
        glfwGetFramebufferSize(window, &win_w, &win_h);

        // Create FBO struct as a real variable
        mpv_opengl_fbo fbo = {0, win_w, win_h};

        mpv_render_param r_params[] = {
            {MPV_RENDER_PARAM_OPENGL_FBO, &fbo},
            {MPV_RENDER_PARAM_INVALID, nullptr}};

        mpv_render_context_render(mpv_gl, r_params);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    mpv_render_context_free(mpv_gl);
    mpv_terminate_destroy(mpv);
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
