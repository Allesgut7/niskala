#pragma once

#include <QWidget>
#include <QtCharts/QChartView>
#include <QtCharts/QCandlestickSeries>
#include <QtCharts/QLineSeries>
#include <QtCharts/QBarSeries>
#include <QtCharts/QChart>
#include <QtCharts/QValueAxis>
#include <QtCharts/QBarCategoryAxis>
#include <QTimer>

class CandlestickChart : public QWidget
{
    Q_OBJECT

public:
    explicit CandlestickChart(QWidget *parent = nullptr);

    void loadSymbol(const QString &symbol);
    void setTimeframe(const QString &tf);

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();
    void setupChart();
    void generateSampleData();
    void updateChart();
    void addMovingAverage(QLineSeries *series, int period);

    QtCharts::QChart *m_chart = nullptr;
    QtCharts::QChartView *m_chartView = nullptr;
    QtCharts::QCandlestickSeries *m_candleSeries = nullptr;
    QtCharts::QLineSeries *m_ma5Series = nullptr;
    QtCharts::QLineSeries *m_ma20Series = nullptr;
    QtCharts::QValueAxis *m_axisX = nullptr;
    QtCharts::QValueAxis *m_axisY = nullptr;

    QString m_currentSymbol = "BBCA";
    QString m_timeframe = "1D";
    QTimer *m_refreshTimer = nullptr;
};
