#pragma once

#include <QWidget>
#include <QPainter>
#include <QPainterPath>

class MarketIndexCard : public QWidget
{
    Q_OBJECT

public:
    explicit MarketIndexCard(const QString &name, double value, double change,
                             double changePct, QWidget *parent = nullptr);

    void updateData(double value, double change, double changePct);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_name;
    double m_value;
    double m_change;
    double m_changePct;
};
