#include <QApplication>
#include <QCommandLineParser>
#include "app/MainWindow.h"
#include "ui/theme/ThemeManager.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("Niskala");
    app.setApplicationVersion("2.0.0");
    app.setOrganizationName("Niskala");

    QCommandLineParser parser;
    parser.setApplicationDescription("Professional Indonesian Stock Market Terminal");
    parser.addHelpOption();
    parser.addVersionOption();
    parser.process(app);

    ThemeManager::instance().loadTheme();

    MainWindow window;
    window.showMaximized();

    return app.exec();
}
