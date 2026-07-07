#pragma once

#include <QWidget>
#include <QHBoxLayout>
#include "MarketIndexCard.h"

class MarketIndicesStrip : public QWidget
{
    Q_OBJECT

public:
    explicit MarketIndicesStrip(QWidget *parent = nullptr);

private:
    void setupUI();

    QList<MarketIndexCard*> m_cards;
};
