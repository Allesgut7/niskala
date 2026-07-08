#pragma once

#include <QWidget>
#include <QHBoxLayout>
#include "MarketIndexCard.h"

class MarketIndicesStrip : public QWidget
{
    Q_OBJECT

public:
    explicit MarketIndicesStrip(QWidget *parent = nullptr);

    void updateData(const QString &name, double value, double change, double changePct);

private:
    void setupUI();

    QList<MarketIndexCard*> m_cards;
};
