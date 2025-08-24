#include "mainwindow.h"
#include <QVBoxLayout>
#include <QFileDialog>
#include <QMenuBar>
#include <QAction>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent) 
{
    QWidget *central = new QWidget(this);
    QVBoxLayout *layout = new QVBoxLayout(central);

    player = new MpvWidget(this);
    layout->addWidget(player);

    setCentralWidget(central);

    QMenu *fileMenu = menuBar()->addMenu("&File");

    QAction *openFile = new QAction("Open Video", this);
    fileMenu->addAction(openFile);

    connect(openFile, &QAction::triggered, this, [this]() {
        QString file = QFileDialog::getOpenFileName(this, "Open Video");
        if (!file.isEmpty()) {
            player->playFile(file);
        }
    });

    QAction *quit = new QAction("Quit", this);
    fileMenu->addAction(quit);
    connect(quit, &QAction::triggered, this, &QWidget::close);
}
