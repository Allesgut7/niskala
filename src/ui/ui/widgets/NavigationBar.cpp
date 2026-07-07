#include "NavigationBar.h"
#include <QHBoxLayout>
#include <QSpacerItem>

NavigationBar::NavigationBar(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(55);
    setupUI();
}

void NavigationBar::setupUI()
{
    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(16, 8, 16, 0);
    layout->setSpacing(4);

    // Logo (stylized N)
    auto *logoLabel = new QLabel("N");
    logoLabel->setStyleSheet(
        "QLabel { color: #10b981; font-size: 22px; font-weight: bold; "
        "border: 2px solid #10b981; border-radius: 6px; padding: 4px 8px; }");
    layout->addWidget(logoLabel);

    // Brand
    auto *brandWidget = new QWidget();
    auto *brandLayout = new QVBoxLayout(brandWidget);
    brandLayout->setContentsMargins(8, 0, 0, 0);
    brandLayout->setSpacing(0);

    auto *brandLabel = new QLabel("NISKALA");
    brandLabel->setStyleSheet("color: #e5e7eb; font-size: 16px; font-weight: bold; letter-spacing: 2px;");
    brandLayout->addWidget(brandLabel);

    auto *tagline = new QLabel("REVEALING THE UNSEEN");
    tagline->setStyleSheet("color: #6b7280; font-size: 7px; letter-spacing: 1px;");
    brandLayout->addWidget(tagline);

    layout->addWidget(brandWidget);

    layout->addSpacing(30);

    // Tabs
    QStringList tabs = {"Dashboard", "Market", "News", "Screener", "Kalender Market", "Portofolio", "Settings"};

    for (int i = 0; i < tabs.size(); ++i) {
        auto *btn = new QPushButton(tabs[i]);
        btn->setObjectName("navTab");
        btn->setCheckable(true);
        btn->setChecked(i == 0);
        connect(btn, &QPushButton::clicked, this, &NavigationBar::onTabClicked);
        m_tabs.append(btn);
        layout->addWidget(btn);
    }

    updateTabStyles();

    layout->addStretch();

    // Right icons
    auto *searchBtn = new QLabel("🔍");
    searchBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 10px;");
    layout->addWidget(searchBtn);

    auto *notifBtn = new QLabel("🔔");
    notifBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 10px;");
    layout->addWidget(notifBtn);

    auto *settingsBtn = new QLabel("⚙");
    settingsBtn->setStyleSheet("color: #9ca3af; font-size: 16px; padding: 0 10px;");
    layout->addWidget(settingsBtn);

    auto *userBtn = new QLabel("N");
    userBtn->setStyleSheet(
        "QLabel { color: #10b981; font-size: 12px; font-weight: bold; "
        "border: 2px solid #10b981; border-radius: 14px; padding: 4px 6px; }");
    layout->addWidget(userBtn);

    setStyleSheet("NavigationBar { background-color: #0a0e17; border-bottom: 1px solid #1f2937; }");
}

void NavigationBar::updateTabStyles()
{
    for (int i = 0; i < m_tabs.size(); ++i) {
        if (i == m_activeTab) {
            m_tabs[i]->setStyleSheet(
                "QPushButton { background-color: #111827; color: #10b981; border: none; "
                "border-bottom: 2px solid #10b981; padding: 8px 16px; font-size: 13px; font-weight: bold; }");
        } else {
            m_tabs[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #9ca3af; border: none; "
                "border-bottom: 2px solid transparent; padding: 8px 16px; font-size: 13px; }"
                "QPushButton:hover { color: #e5e7eb; }");
        }
    }
}

void NavigationBar::onTabClicked()
{
    auto *btn = qobject_cast<QPushButton*>(sender());
    if (!btn) return;

    int index = m_tabs.indexOf(btn);
    if (index >= 0) {
        m_activeTab = index;
        updateTabStyles();
        emit tabClicked(index);
    }
}
