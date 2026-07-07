#pragma once

#include <QWidget>
#include <QComboBox>
#include <QCheckBox>
#include <QSpinBox>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QSettings>

class SettingsScreen : public QWidget
{
    Q_OBJECT

public:
    explicit SettingsScreen(QWidget *parent = nullptr);

    void loadSettings();
    void saveSettings();

signals:
    void themeChanged(const QString &theme);
    void settingsSaved();

private slots:
    void onThemeChanged(int index);
    void onApplyClicked();
    void onResetClicked();

private:
    void setupUI();
    void setupGeneralSection();
    void setupDataSection();
    void setupDisplaySection();
    void setupKeyboardShortcuts();

    QComboBox *m_themeCombo = nullptr;
    QComboBox *m_languageCombo = nullptr;
    QComboBox *m_dataSourceCombo = nullptr;
    QSpinBox *m_refreshInterval = nullptr;
    QSpinBox *m_cacheTTL = nullptr;
    QCheckBox *m_showGridLines = nullptr;
    QCheckBox *m_showVolume = nullptr;
    QCheckBox *m_smoothScrolling = nullptr;
    QPushButton *m_applyBtn = nullptr;
    QPushButton *m_resetBtn = nullptr;
    QSettings *m_settings = nullptr;
};
