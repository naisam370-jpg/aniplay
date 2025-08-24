#pragma once
#include <QMainWindow>
#include "mpvwidget.h"

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

private:
    MpvWidget *player;
};
