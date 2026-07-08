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

    // Background colors
    static constexpr const char *BG_PRIMARY = "#060B16";
    static constexpr const char *BG_SECONDARY = "#09111F";
    static constexpr const char *BG_SURFACE = "#101827";
    static constexpr const char *SURFACE_HOVER = "#162235";
    static constexpr const char *SURFACE_ACTIVE = "#1B2940";

    // Border
    static constexpr const char *BORDER = "#1D2B40";

    // Brand / Accent
    static constexpr const char *BRAND_CYAN = "#25D9FF";
    static constexpr const char *BRAND_GREEN = "#1AF37B";
    static constexpr const char *ACCENT_RED = "#D84B63";

    // Text
    static constexpr const char *TEXT_PRIMARY = "#F7FAFC";
    static constexpr const char *TEXT_SECONDARY = "#B7C2D6";
    static constexpr const char *TEXT_MUTED = "#7E8AA3";

    // Market colors
    static constexpr const char *BULL = "#1AF37B";
    static constexpr const char *BEAR = "#FF5C72";
    static constexpr const char *WARNING = "#E6874C";
    static constexpr const char *ERROR = "#D84B63";
    static constexpr const char *INFO = "#25D9FF";

signals:
    void themeChanged();

private:
    ThemeManager() = default;
    QString m_currentTheme = "dark";
    QString m_stylesheet;
};
