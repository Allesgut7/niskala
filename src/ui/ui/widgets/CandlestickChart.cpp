#include "CandlestickChart.h"
#include "FinancialChart.h"
#include <QVBoxLayout>

CandlestickChart::CandlestickChart(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    generateSampleData();

    m_refreshTimer = new QTimer(this);
    connect(m_refreshTimer, &QTimer::timeout, this, &CandlestickChart::generateSampleData);
    m_refreshTimer->start(10000);
}

void CandlestickChart::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);

    m_chart = new FinancialChart();
    layout->addWidget(m_chart);
}

void CandlestickChart::generateSampleData()
{
    QVector<OHLCData> data;
    double basePrice = 9000.0;

    for (int i = 0; i < 50; ++i) {
        OHLCData candle;
        candle.open = basePrice + (rand() % 300 - 150);
        candle.close = candle.open + (rand() % 200 - 100);
        candle.high = qMax(candle.open, candle.close) + (rand() % 100);
        candle.low = qMin(candle.open, candle.close) - (rand() % 100);
        candle.volume = 1000000 + rand() % 5000000;
        candle.timestamp = i;
        data.append(candle);

        basePrice = candle.close;
    }

    m_chart->loadData(data);
}

void CandlestickChart::loadSymbol(const QString &symbol)
{
    m_currentSymbol = symbol;
    generateSampleData();
}

void CandlestickChart::setTimeframe(const QString &tf)
{
    m_timeframe = tf;
    m_chart->setTimeframe(tf);
    generateSampleData();
}

void CandlestickChart::setMA5Visible(bool visible)
{
    m_chart->setMA5Visible(visible);
}

void CandlestickChart::setMA20Visible(bool visible)
{
    m_chart->setMA20Visible(visible);
}

void CandlestickChart::setVolumeVisible(bool visible)
{
    m_chart->setVolumeVisible(visible);
}

void CandlestickChart::addRealTimeCandle(const OHLCData &candle)
{
    m_chart->addCandle(candle);
}
