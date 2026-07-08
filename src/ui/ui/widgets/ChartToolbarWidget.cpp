#include "ChartToolbarWidget.h"
#include <QHBoxLayout>
#include <QLabel>

ChartToolbarWidget::ChartToolbarWidget(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(40);
    setupUI();
}

void ChartToolbarWidget::setupUI()
{
    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(8, 4, 8, 4);
    layout->setSpacing(4);

    // Symbol name
    auto *symbolLabel = new QLabel("IHSG INDEX");
    symbolLabel->setStyleSheet("color: #75FF9E; font-family: 'Inter'; font-size: 12px; font-weight: bold;");
    layout->addWidget(symbolLabel);

    layout->addSpacing(12);

    // Timeframe buttons
    QStringList timeframes = {"1m", "5m", "15m", "1h", "D", "W", "M"};
    for (int i = 0; i < timeframes.size(); ++i) {
        auto *btn = new QPushButton(timeframes[i]);
        btn->setFixedSize(28, 24);
        btn->setCheckable(true);
        btn->setChecked(i == m_activeTf);
        connect(btn, &QPushButton::clicked, this, &ChartToolbarWidget::onTimeframeClicked);
        m_tfButtons.append(btn);
        layout->addWidget(btn);
    }

    updateTimeframeStyles();

    layout->addSpacing(8);

    // Separator
    auto *sep = new QFrame();
    sep->setFrameShape(QFrame::VLine);
    sep->setStyleSheet("color: #3B4A3D;");
    sep->setFixedHeight(20);
    layout->addWidget(sep);

    layout->addSpacing(8);

    // Chart type icons (text placeholders)
    QStringList icons = {"📈", "📊", "📉"};
    for (const auto &icon : icons) {
        auto *iconBtn = new QPushButton(icon);
        iconBtn->setFixedSize(28, 24);
        iconBtn->setStyleSheet(
            "QPushButton { background: transparent; border: none; font-size: 14px; }"
            "QPushButton:hover { background-color: #272A2E; border-radius: 6px; }");
        layout->addWidget(iconBtn);
    }

    layout->addStretch();

    // Current price
    auto *priceLabel = new QLabel("7,164.57");
    priceLabel->setStyleSheet("color: #75FF9E; font-family: 'JetBrains Mono'; font-size: 12px; font-weight: bold;");
    layout->addWidget(priceLabel);

    layout->addSpacing(8);

    // Settings icon
    auto *settingsBtn = new QPushButton("⚙");
    settingsBtn->setFixedSize(24, 24);
    settingsBtn->setStyleSheet(
        "QPushButton { background: transparent; border: none; color: #859585; font-size: 14px; }"
        "QPushButton:hover { color: #CEE8FF; }");
    layout->addWidget(settingsBtn);

    // Fullscreen icon
    auto *fsBtn = new QPushButton("⛶");
    fsBtn->setFixedSize(24, 24);
    fsBtn->setStyleSheet(
        "QPushButton { background: transparent; border: none; color: #859585; font-size: 14px; }"
        "QPushButton:hover { color: #CEE8FF; }");
    layout->addWidget(fsBtn);

    setStyleSheet("ChartToolbarWidget { background-color: #272A2E; border-bottom: 1px solid #3B4A3D; }");
}

void ChartToolbarWidget::onTimeframeClicked()
{
    auto *btn = qobject_cast<QPushButton*>(sender());
    if (!btn) return;

    int index = m_tfButtons.indexOf(btn);
    if (index >= 0) {
        m_activeTf = index;
        updateTimeframeStyles();
        QStringList tfs = {"1m", "5m", "15m", "1h", "D", "W", "M"};
        emit timeframeChanged(tfs[index]);
    }
}

void ChartToolbarWidget::updateTimeframeStyles()
{
    for (int i = 0; i < m_tfButtons.size(); ++i) {
        if (i == m_activeTf) {
            m_tfButtons[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #75FF9E; border: none; "
                "font-weight: bold; font-size: 11px; }");
        } else {
            m_tfButtons[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #859585; border: none; "
                "font-size: 11px; }"
                "QPushButton:hover { color: #E1E2E7; }");
        }
    }
}
