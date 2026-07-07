#include "MarketIndicesStrip.h"
#include <QHBoxLayout>

MarketIndicesStrip::MarketIndicesStrip(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(90);
    setupUI();
}

void MarketIndicesStrip::setupUI()
{
    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(8, 4, 8, 4);
    layout->setSpacing(6);

    struct IndexData { QString name; double value; double change; double pct; };
    QList<IndexData> indices = {
        {"IHSG", 7164.57, 87.23, 1.23},
        {"NIKKEI 225", 39805.66, -134.27, -0.34},
        {"HANG SENG", 18502.45, 190.63, 1.04},
        {"KOSPI", 2688.97, 21.37, 0.80},
        {"S&P 500", 5461.48, 14.79, 0.27},
        {"NASDAQ", 17721.59, 95.18, 0.54},
        {"USD/IDR", 16140, -15, -0.09}
    };

    for (const auto &idx : indices) {
        auto *card = new MarketIndexCard(idx.name, idx.value, idx.change, idx.pct);
        m_cards.append(card);
        layout->addWidget(card);
    }

    setStyleSheet("MarketIndicesStrip { background-color: #0a0e17; }");
}
