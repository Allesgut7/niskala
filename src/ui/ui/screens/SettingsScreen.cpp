#include "SettingsScreen.h"
#include "../theme/ThemeManager.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QGridLayout>
#include <QFormLayout>
#include <QMessageBox>

SettingsScreen::SettingsScreen(QWidget *parent)
    : QWidget(parent)
{
    m_settings = new QSettings("Niskala", "Niskala", this);
    setupUI();
    loadSettings();
}

void SettingsScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(6);

    auto *title = new QLabel("SETTINGS");
    title->setStyleSheet("color: #D84B63; font-size: 16px; font-weight: bold;");
    mainLayout->addWidget(title);

    setupGeneralSection();
    setupDataSection();
    setupDisplaySection();
    setupKeyboardShortcuts();

    mainLayout->addStretch();

    auto *btnLayout = new QHBoxLayout();
    m_applyBtn = new QPushButton("Apply");
    m_applyBtn->setStyleSheet(
        "QPushButton { background-color: #09111F; color: #F7FAFC; padding: 8px 24px; font-weight: bold; }"
        "QPushButton:hover { background-color: #D84B63; }");
    connect(m_applyBtn, &QPushButton::clicked, this, &SettingsScreen::onApplyClicked);

    m_resetBtn = new QPushButton("Reset to Default");
    m_resetBtn->setStyleSheet(
        "QPushButton { background-color: transparent; color: #7E8AA3; padding: 8px 16px; border: 1px solid #09111F; }"
        "QPushButton:hover { border-color: #D84B63; color: #F7FAFC; }");
    connect(m_resetBtn, &QPushButton::clicked, this, &SettingsScreen::onResetClicked);

    btnLayout->addStretch();
    btnLayout->addWidget(m_resetBtn);
    btnLayout->addWidget(m_applyBtn);
    mainLayout->addLayout(btnLayout);
}

void SettingsScreen::setupGeneralSection()
{
    auto *group = new QGroupBox("GENERAL");
    group->setStyleSheet("QGroupBox { color: #25D9FF; }");
    auto *layout = new QFormLayout(group);

    m_themeCombo = new QComboBox();
    m_themeCombo->addItems({"Dark", "Light", "Monokai", "Nord"});
    m_themeCombo->setCurrentIndex(0);
    connect(m_themeCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &SettingsScreen::onThemeChanged);
    layout->addRow("Theme:", m_themeCombo);

    m_languageCombo = new QComboBox();
    m_languageCombo->addItems({"English", "Indonesia", "Melayu", "Thai"});
    m_languageCombo->setCurrentIndex(1);
    layout->addRow("Language:", m_languageCombo);

    this->layout()->addWidget(group);
}

void SettingsScreen::setupDataSection()
{
    auto *group = new QGroupBox("DATA");
    group->setStyleSheet("QGroupBox { color: #25D9FF; }");
    auto *layout = new QFormLayout(group);

    m_dataSourceCombo = new QComboBox();
    m_dataSourceCombo->addItems({"Yahoo Finance", "AkShare", "IDX BEI"});
    layout->addRow("Primary Source:", m_dataSourceCombo);

    m_refreshInterval = new QSpinBox();
    m_refreshInterval->setRange(5, 300);
    m_refreshInterval->setValue(30);
    m_refreshInterval->setSuffix(" sec");
    layout->addRow("Refresh Interval:", m_refreshInterval);

    m_cacheTTL = new QSpinBox();
    m_cacheTTL->setRange(60, 3600);
    m_cacheTTL->setValue(300);
    m_cacheTTL->setSuffix(" sec");
    layout->addRow("Cache TTL:", m_cacheTTL);

    this->layout()->addWidget(group);
}

void SettingsScreen::setupDisplaySection()
{
    auto *group = new QGroupBox("DISPLAY");
    group->setStyleSheet("QGroupBox { color: #E6874C; }");
    auto *layout = new QGridLayout(group);

    m_showGridLines = new QCheckBox("Show Grid Lines");
    m_showGridLines->setChecked(true);
    layout->addWidget(m_showGridLines, 0, 0);

    m_showVolume = new QCheckBox("Show Volume in Charts");
    m_showVolume->setChecked(true);
    layout->addWidget(m_showVolume, 0, 1);

    m_smoothScrolling = new QCheckBox("Smooth Scrolling");
    m_smoothScrolling->setChecked(false);
    layout->addWidget(m_smoothScrolling, 1, 0);

    this->layout()->addWidget(group);
}

void SettingsScreen::setupKeyboardShortcuts()
{
    auto *group = new QGroupBox("KEYBOARD SHORTCUTS");
    group->setStyleSheet("QGroupBox { color: #D84B63; }");
    auto *layout = new QVBoxLayout(group);

    QStringList shortcuts = {
        "F1  - Dashboard",
        "F2  - Chart",
        "F3  - Screener",
        "F4  - Portfolio",
        "F5  - Refresh Data",
        "F6  - News",
        "F7  - Settings",
        "Esc - Exit"
    };

    for (const auto &s : shortcuts) {
        auto *label = new QLabel(s);
        label->setStyleSheet("color: #F7FAFC; font-family: monospace;");
        layout->addWidget(label);
    }

    this->layout()->addWidget(group);
}

void SettingsScreen::loadSettings()
{
    m_themeCombo->setCurrentIndex(m_settings->value("theme", 0).toInt());
    m_languageCombo->setCurrentIndex(m_settings->value("language", 1).toInt());
    m_dataSourceCombo->setCurrentIndex(m_settings->value("dataSource", 0).toInt());
    m_refreshInterval->setValue(m_settings->value("refreshInterval", 30).toInt());
    m_cacheTTL->setValue(m_settings->value("cacheTTL", 300).toInt());
    m_showGridLines->setChecked(m_settings->value("showGridLines", true).toBool());
    m_showVolume->setChecked(m_settings->value("showVolume", true).toBool());
    m_smoothScrolling->setChecked(m_settings->value("smoothScrolling", false).toBool());
}

void SettingsScreen::saveSettings()
{
    m_settings->setValue("theme", m_themeCombo->currentIndex());
    m_settings->setValue("language", m_languageCombo->currentIndex());
    m_settings->setValue("dataSource", m_dataSourceCombo->currentIndex());
    m_settings->setValue("refreshInterval", m_refreshInterval->value());
    m_settings->setValue("cacheTTL", m_cacheTTL->value());
    m_settings->setValue("showGridLines", m_showGridLines->isChecked());
    m_settings->setValue("showVolume", m_showVolume->isChecked());
    m_settings->setValue("smoothScrolling", m_smoothScrolling->isChecked());
    m_settings->sync();
}

void SettingsScreen::onThemeChanged(int index)
{
    Q_UNUSED(index);
}

void SettingsScreen::onApplyClicked()
{
    saveSettings();
    emit settingsSaved();
    QMessageBox::information(this, "Settings", "Settings applied successfully!");
}

void SettingsScreen::onResetClicked()
{
    m_themeCombo->setCurrentIndex(0);
    m_languageCombo->setCurrentIndex(1);
    m_dataSourceCombo->setCurrentIndex(0);
    m_refreshInterval->setValue(30);
    m_cacheTTL->setValue(300);
    m_showGridLines->setChecked(true);
    m_showVolume->setChecked(true);
    m_smoothScrolling->setChecked(false);
}
