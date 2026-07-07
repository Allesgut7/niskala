#include "CandlestickChart.h"
#include <QtCharts/QBarCategoryAxis>
#include <QtCharts/QValueAxis>
#include <QtCharts/QCandlestickSet>
#include <QtCharts/QAreaSeries>
#include <QVBoxLayout>
#include <QDateTime>
#include <cmath>

using namespace QtCharts;

CandlestickChart::CandlestickChart(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    generateSampleData();

    m_refreshTimer = new QTimer(this);
    connect(m_refreshTimer, &QTimer::timeout, this, &CandlestickChart::updateChart);
    m_refreshTimer->start(5000);
}

void CandlestickChart::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);

    setupChart();

    m_chartView = new QChartView(m_chart);
    m_chartView->setRenderHint(QPainter::Antialiasing);
    m_chartView->setStyleSheet("background-color: #1a1a2e;");
    layout->addWidget(m_chartView);
}

void CandlestickChart::setupChart()
{
    m_chart = new QChart();
    m_chart->setBackgroundBrush(QBrush(QColor("#1a1a2e")));
    m_chart->setTitleBrush(QBrush(QColor("#e0e0e0")));
    m_chart->setTitleFont(QFont("monospace", 12, QFont::Bold));
    m_chart->setTitle("BBCA - Daily Chart");
    m_chart->setAnimationOptions(QChart::SeriesAnimations);
    m_chart->legend()->setVisible(false);

    m_candleSeries = new QCandlestickSeries();
    m_candleSeries->setName("Price");
    m_candleSeries->setIncreasingColor(QColor("#00d989"));
    m_candleSeries->setDecreasingColor(QColor("#ff4757"));
    m_candleSeries->setBodyOutlineVisible(false);

    m_ma5Series = new QLineSeries();
    m_ma5Series->setName("MA5");
    m_ma5Series->setPen(QPen(QColor("#ffc107"), 1, Qt::SolidLine));

    m_ma20Series = new QLineSeries();
    m_ma20Series->setName("MA20");
    m_ma20Series->setPen(QPen(QColor("#00bcd4"), 1, Qt::DashLine));

    m_axisX = new QValueAxis();
    m_axisX->setLabelsVisible(false);
    m_axisX->setGridLinePen(QPen(QColor("#0f3460"), 1, Qt::DotLine));

    m_axisY = new QValueAxis();
    m_axisY->setLabelsColor(QColor("#888888"));
    m_axisY->setGridLinePen(QPen(QColor("#0f3460"), 1, Qt::DotLine));

    m_chart->addSeries(m_candleSeries);
    m_chart->addSeries(m_ma5Series);
    m_chart->addSeries(m_ma20Series);
    m_chart->addAxis(m_axisX, Qt::AlignBottom);
    m_chart->addAxis(m_axisY, Qt::AlignRight);
    m_candleSeries->attachAxis(m_axisX);
    m_candleSeries->attachAxis(m_axisY);
    m_ma5Series->attachAxis(m_axisX);
    m_ma5Series->attachAxis(m_axisY);
    m_ma20Series->attachAxis(m_axisX);
    m_ma20Series->attachAxis(m_axisY);
}

void CandlestickChart::generateSampleData()
{
    m_candleSeries->clear();
    m_ma5Series->clear();
    m_ma20Series->clear();

    double basePrice = 9000.0;
    QList<double> closes;

    for (int i = 0; i < 30; ++i) {
        double open = basePrice + (rand() % 300 - 150);
        double close = open + (rand() % 200 - 100);
        double high = qMax(open, close) + (rand() % 100);
        double low = qMin(open, close) - (rand() % 100);

        QCandlestickSet *set = new QCandlestickSet(i);
        set->setOpen(open);
        set->setHigh(high);
        set->setLow(low);
        set->setClose(close);
        m_candleSeries->append(set);

        closes.append(close);
        m_ma5Series->append(i, close);

        m_axisX->setRange(0, 29);
    }

    // MA20
    for (int i = 19; i < 30; ++i) {
        double sum = 0;
        for (int j = i - 19; j <= i; ++j) {
            sum += closes[j];
        }
        m_ma20Series->append(i, sum / 20.0);
    }

    double minPrice = 8500;
    double maxPrice = 9800;
    m_axisY->setRange(minPrice, maxPrice);
}

void CandlestickChart::loadSymbol(const QString &symbol)
{
    m_currentSymbol = symbol;
    m_chart->setTitle(symbol + " - " + m_timeframe + " Chart");
    generateSampleData();
}

void CandlestickChart::setTimeframe(const QString &tf)
{
    m_timeframe = tf;
    m_chart->setTitle(m_currentSymbol + " - " + tf + " Chart");
    generateSampleData();
}

void CandlestickChart::updateChart()
{
    if (m_candleSeries->count() == 0) return;

    auto *last = m_candleSeries->at(m_candleSeries->count() - 1);
    double open = last->open();
    double change = (rand() % 50 - 25);
    last->setClose(last->close() + change);
    last->setHigh(qMax(last->high(), last->close()));
    last->setLow(qMin(last->low(), last->close()));
}
