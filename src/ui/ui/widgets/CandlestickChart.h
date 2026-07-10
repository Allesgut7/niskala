#pragma once

#include <QWidget>
#include <QTimer>
#include "FinancialChart.h"

class CandlestickChart : public QWidget
{
    Q_OBJECT

public:
    explicit CandlestickChart(QWidget *parent = nullptr);

    void loadSymbol(const QString &symbol);
    void setTimeframe(const QString &tf);
    void setMA5Visible(bool visible);
    void setMA20Visible(bool visible);
    void setVolumeVisible(bool visible);
    void addRealTimeCandle(const OHLCData &candle);
    void loadOHLCVData(const QVector<OHLCData> &data);

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();

    FinancialChart *m_chart = nullptr;
    QString m_currentSymbol = "BBCA";
    QString m_timeframe = "1D";
};
