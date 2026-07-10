#include "CandlestickChart.h"
#include "FinancialChart.h"
#include <QVBoxLayout>

CandlestickChart::CandlestickChart(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
}

void CandlestickChart::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);

    m_chart = new FinancialChart();
    layout->addWidget(m_chart);
}

void CandlestickChart::loadSymbol(const QString &symbol)
{
    m_currentSymbol = symbol;
}

void CandlestickChart::setTimeframe(const QString &tf)
{
    m_timeframe = tf;
    m_chart->setTimeframe(tf);
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

void CandlestickChart::loadOHLCVData(const QVector<OHLCData> &data)
{
    m_chart->loadData(data);
}
