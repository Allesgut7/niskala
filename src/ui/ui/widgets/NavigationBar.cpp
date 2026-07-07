#include "NavigationBar.h"
#include <QHBoxLayout>
#include <QSpacerItem>

NavigationBar::NavigationBar(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(50);
    setupUI();
}

void NavigationBar::setupUI()
{
    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(16, 8, 16, 8);
    layout->setSpacing(4);

    // Logo
    auto *logoLabel = new QLabel("N");
    logoLabel->setStyleSheet(
        "QLabel { color: #10b981; font-size: 20px; font-weight: bold; "
        "border: 2px solid #10b981; border-radius: 4px; padding: 2px 6px; }");
    layout->addWidget(logoLabel);

    auto *brandLabel = new QLabel("NISKALA");
    brandLabel->setStyleSheet("color: #e5e7eb; font-size: 14px; font-weight: bold; margin-left: 8px;");
    layout->addWidget(brandLabel);

    layout->addSpacing(20);

    // Tabs
    QStringList tabs = {"Dashboard", "Market", "News", "Screener", "Kalender Market", "Portofolio", "Settings"};

    for (int i = 0; i < tabs.size(); ++i) {
        auto *btn = new QPushButton(tabs[i]);
        btn->setObjectName("navTab");
        btn->setCheckable(true);
        btn->setChecked(i == 0);
        btn->setStyleSheet(
            "QPushButton { background-color: transparent; color: #9ca3af; border: none; "
            "padding: 8px 16px; font-size: 13px; }"
            "QPushButton:hover { color: #e5e7eb; }"
            "QPushButton:checked { background-color: #1f2937; color: #10b981; border-radius: 4px; }");
        connect(btn, &QPushButton::clicked, this, &NavigationBar::onTabClicked);
        m_tabs.append(btn);
        layout->addWidget(btn);
    }

    layout->addStretch();

    // Right icons
    auto *searchBtn = new QLabel("🔍");
    searchBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 8px;");
    layout->addWidget(searchBtn);

    auto *notifBtn = new QLabel("🔔");
    notifBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 8px;");
    layout->addWidget(notifBtn);

    auto *settingsBtn = new QLabel("⚙");
    settingsBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 8px;");
    layout->addWidget(settingsBtn);

    auto *userBtn = new QLabel("N");
    userBtn->setStyleSheet(
        "QLabel { color: #10b981; font-size: 12px; font-weight: bold; "
        "border: 2px solid #10b981; border-radius: 12px; padding: 4px; }");
    layout->addWidget(userBtn);

    setStyleSheet("NavigationBar { background-color: #0a0e17; border-bottom: 1px solid #1f2937; }");
}

void NavigationBar::onTabClicked()
{
    auto *btn = qobject_cast<QPushButton*>(sender());
    if (!btn) return;

    int index = m_tabs.indexOf(btn);
    if (index >= 0) {
        m_activeTab = index;
        for (int i = 0; i < m_tabs.size(); ++i) {
            m_tabs[i]->setChecked(i == index);
        }
        emit tabClicked(index);
    }
}
