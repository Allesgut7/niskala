#pragma once

#include <QObject>
#include <QApplication>
#include <QString>

class ThemeManager : public QObject
{
    Q_OBJECT

public:
    static ThemeManager &instance();

    void loadTheme();
    void applyTheme(QApplication *app);
    void setTheme(const QString &themeName);

    QString currentTheme() const { return m_currentTheme; }
    bool isDark() const { return m_currentTheme == "dark"; }

    // Color palette
    static constexpr const char *BG_PRIMARY = "#1a1a2e";
    static constexpr const char *BG_SURFACE = "#16213e";
    static constexpr const char *BG_ELEVATED = "#1f3056";
    static constexpr const char *ACCENT_BLUE = "#0f3460";
    static constexpr const char *ACCENT_RED = "#e94560";
    static constexpr const char *TEXT_PRIMARY = "#e0e0e0";
    static constexpr const char *TEXT_SECONDARY = "#888888";
    static constexpr const char *COLOR_GREEN = "#00d989";
    static constexpr const char *COLOR_RED = "#ff4757";
    static constexpr const char *COLOR_YELLOW = "#ffc107";
    static constexpr const char *COLOR_CYAN = "#00bcd4";

signals:
    void themeChanged();

private:
    ThemeManager() = default;
    QString m_currentTheme = "dark";
    QString m_stylesheet;
};
