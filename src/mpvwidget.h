#ifndef MPVWIDGET_H
#define MPVWIDGET_H

#include <QOpenGLWidget>
#include <QOpenGLContext>
#include <mpv/client.h>
#include <mpv/render_gl.h>

class MpvWidget : public QOpenGLWidget
{
    Q_OBJECT   // 👈 This is REQUIRED for signals/slots, vtable
public:
    explicit MpvWidget(QWidget *parent = nullptr);
    ~MpvWidget();

protected:
    void paintGL() override;

private:
    mpv_handle *mpv;
    mpv_render_context *mpv_gl;
};

#endif // MPVWIDGET_H
