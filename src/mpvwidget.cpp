#include "mpvwidget.h"
#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QDebug>

static void on_mpv_redraw(void *ctx) {
    QWidget *widget = static_cast<QWidget *>(ctx);
    widget->update(); // schedule a repaint
}

MpvWidget::MpvWidget(QWidget *parent)
    : QWidget(parent), mpv(nullptr), mpv_gl(nullptr) 
{
    setAttribute(Qt::WA_OpaquePaintEvent);
    setAttribute(Qt::WA_NoSystemBackground);

    mpv = mpv_create();
    if (!mpv) {
        qFatal("failed to create mpv context");
    }

    // Use GPU rendering
    mpv_set_option_string(mpv, "vo", "gpu");
    mpv_initialize(mpv);

    mpv_opengl_init_params gl_init_params{nullptr, nullptr, nullptr};
    mpv_render_param params[] = {
        {MPV_RENDER_PARAM_API_TYPE, (void *)MPV_RENDER_API_TYPE_OPENGL},
        {MPV_RENDER_PARAM_OPENGL_INIT_PARAMS, &gl_init_params},
        {MPV_RENDER_PARAM_INVALID, nullptr}
    };

    if (mpv_render_context_create(&mpv_gl, mpv, params) < 0) {
        qFatal("failed to initialize mpv GL context");
    }

    mpv_render_context_set_update_callback(mpv_gl, on_mpv_redraw, this);
}

MpvWidget::~MpvWidget() {
    if (mpv_gl)
        mpv_render_context_free(mpv_gl);
    if (mpv)
        mpv_destroy(mpv);
}

void MpvWidget::playFile(const QString &file) {
    const QByteArray ba = file.toUtf8();
    const char *args[] = {"loadfile", ba.data(), nullptr};
    mpv_command(mpv, args);
}

void MpvWidget::paintEvent(QPaintEvent *) {
    if (!mpv_gl) return;

    mpv_opengl_fbo fbo = {
        .fbo = 0,
        .w = width(),
        .h = height(),
        .internal_format = 0
    };

    mpv_render_param params[] = {
        {MPV_RENDER_PARAM_OPENGL_FBO, &fbo},
        {MPV_RENDER_PARAM_INVALID, nullptr}
    };

    mpv_render_context_render(mpv_gl, params);
}

void MpvWidget::resizeEvent(QResizeEvent *) {
    update();
}
