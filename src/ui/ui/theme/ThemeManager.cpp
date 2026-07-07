#include "ThemeManager.h"
#include <QFile>
#include <QTextStream>

ThemeManager &ThemeManager::instance()
{
    static ThemeManager manager;
    return manager;
}

void ThemeManager::loadTheme()
{
    QFile file(":/themes/dark_theme.qss");
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream stream(&file);
        m_stylesheet = stream.readAll();
        file.close();
    }
}

void ThemeManager::applyTheme(QApplication *app)
{
    if (app && !m_stylesheet.isEmpty()) {
        app->setStyleSheet(m_stylesheet);
    }
}

void ThemeManager::setTheme(const QString &themeName)
{
    if (m_currentTheme != themeName) {
        m_currentTheme = themeName;
        loadTheme();
        emit themeChanged();
    }
}
