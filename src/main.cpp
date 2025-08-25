#include <QApplication>
#include "mpvwidget.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    MpvWidget player;
    player.resize(800, 600);
    player.show();

    return app.exec();
}
