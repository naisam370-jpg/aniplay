#pragma once
#include <QWidget>
#include <mpv/client.h>
#include <mpv/render_gl.h>

class QOpenGLWidget;

class MpvWidget : public QWidget {
    Q_OBJECT

public:
    explicit MpvWidget(QWidget *parent = nullptr);
    ~MpvWidget();

    void playFile(const QString &file);

protected:
    void initializeGL();
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    mpv_handle *mpv;
    mpv_render_context *mpv_gl;
};
