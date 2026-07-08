#pragma once

#include <QWidget>
#include <QPainter>

class AIMarketRegimeWidget : public QWidget
{
    Q_OBJECT

public:
    explicit AIMarketRegimeWidget(QWidget *parent = nullptr);

    void updateData(const QString &regime, int confidence, const QString &analysis);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_regime = "MODERATE BULL";
    int m_confidence = 82;
    QString m_analysis = "Momentum indicates sustained accumulation in Blue Chip stocks. RSI divergence suggests a potential cooling period near 7,200.";
};
