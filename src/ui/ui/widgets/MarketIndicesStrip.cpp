#include "MarketIndicesStrip.h"
#include <QHBoxLayout>
#include <QMap>

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

    // Index names - start with empty data, will be updated by API
    QStringList indexNames = {"IHSG", "NIKKEI 225", "HANG SENG", "KOSPI", "S&P 500", "NASDAQ", "USD/IDR"};

    for (const auto &name : indexNames) {
        auto *card = new MarketIndexCard(name, 0, 0, 0);
        card->setObjectName(name);
        m_cards.append(card);
        layout->addWidget(card);
    }

    setStyleSheet("MarketIndicesStrip { background-color: #1D2023; }");
}

void MarketIndicesStrip::updateData(const QString &name, double value, double change, double changePct)
{
    // Map Yahoo Finance symbols ke display names
    QMap<QString, QString> symbolMap = {
        {"^JKSE", "IHSG"},
        {"^N225", "NIKKEI 225"},
        {"^HSI", "HANG SENG"},
        {"^KS11", "KOSPI"},
        {"^GSPC", "S&P 500"},
        {"^IXIC", "NASDAQ"},
        {"USDIDR=X", "USD/IDR"}
    };
    
    QString displayName = symbolMap.value(name, name);
    
    for (auto *card : m_cards) {
        if (card->objectName() == displayName) {
            card->updateData(value, change, changePct);
            break;
        }
    }
}
