#pragma once

#include <QWidget>
#include <QPainter>
#include <QPainterPath>

class MarketBreadthWidget : public QWidget
{
    Q_OBJECT

public:
    explicit MarketBreadthWidget(QWidget *parent = nullptr);

    void updateData(int naik, int turun, int stagnan);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void setupData();

    int m_naik = 272;
    int m_turun = 158;
    int m_stagnan = 46;
    int m_total = 476;
};
