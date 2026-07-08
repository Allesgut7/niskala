#include "NavigationBar.h"
#include <QHBoxLayout>
#include <QLineEdit>
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

    // Logo
    auto *logoLabel = new QLabel();
    logoLabel->setPixmap(QPixmap(":/images/Logo-fix.png").scaled(40, 40, Qt::KeepAspectRatio, Qt::SmoothTransformation));
    layout->addWidget(logoLabel);

    layout->addSpacing(8);

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

    // Search input
    auto *searchInput = new QLineEdit();
    searchInput->setPlaceholderText("Search Assets...");
    searchInput->setFixedSize(200, 30);
    searchInput->setStyleSheet(
        "QLineEdit { background-color: #191C1F; color: #E1E2E7; border: 1px solid #3B4A3D; "
        "border-radius: 6px; padding: 4px 8px; font-family: 'Inter'; font-size: 12px; }"
        "QLineEdit:focus { border-color: #CEE8FF; }"
        "QLineEdit::placeholder { color: #859585; }");
    layout->addWidget(searchInput);

    layout->addSpacing(8);

    // Notification icon
    auto *notifBtn = new QLabel("🔔");
    notifBtn->setStyleSheet("color: #859585; font-size: 16px; padding: 0 8px;");
    layout->addWidget(notifBtn);

    // User icon
    auto *userBtn = new QLabel("👤");
    userBtn->setStyleSheet("color: #859585; font-size: 16px; padding: 0 8px;");
    layout->addWidget(userBtn);

    setStyleSheet("NavigationBar { background-color: #1D2023; border-bottom: 1px solid #3B4A3D; }");
}

void NavigationBar::updateTabStyles()
{
    for (int i = 0; i < m_tabs.size(); ++i) {
        if (i == m_activeTab) {
            m_tabs[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #75FF9E; border: none; "
                "border-bottom: 2px solid #75FF9E; padding: 8px 12px; font-size: 12px; font-weight: bold; }");
        } else {
            m_tabs[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #BACBB9; border: none; "
                "border-bottom: 2px solid transparent; padding: 8px 12px; font-size: 12px; }"
                "QPushButton:hover { color: #E1E2E7; }");
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
