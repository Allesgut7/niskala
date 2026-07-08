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

    // Background colors (Stitch Obsidian Terminal)
    static constexpr const char *BG_PRIMARY = "#060B16";
    static constexpr const char *BG_SECONDARY = "#111417";
    static constexpr const char *BG_SURFACE = "#1D2023";
    static constexpr const char *SURFACE_LOW = "#191C1F";
    static constexpr const char *SURFACE_HOVER = "#272A2E";
    static constexpr const char *SURFACE_ACTIVE = "#323538";

    // Border
    static constexpr const char *BORDER = "#3B4A3D";

    // Brand / Accent
    static constexpr const char *BRAND_CYAN = "#CEE8FF";
    static constexpr const char *BRAND_GREEN = "#75FF9E";
    static constexpr const char *ACCENT_RED = "#FFB4AB";

    // Text
    static constexpr const char *TEXT_PRIMARY = "#E1E2E7";
    static constexpr const char *TEXT_SECONDARY = "#BACBB9";
    static constexpr const char *TEXT_MUTED = "#859585";

    // Market colors
    static constexpr const char *BULL = "#75FF9E";
    static constexpr const char *BEAR = "#FFB3AE";
    static constexpr const char *WARNING = "#CEE8FF";
    static constexpr const char *ERROR = "#FFB4AB";
    static constexpr const char *INFO = "#8DCDFF";

signals:
    void themeChanged();

private:
    ThemeManager() = default;
    QString m_currentTheme = "dark";
    QString m_stylesheet;
};
