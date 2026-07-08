#pragma once

#include <QWidget>
#include <QChartView>
#include <QCandlestickSeries>
#include <QLineSeries>
#include <QChart>
#include <QValueAxis>
#include <QTimer>

class CandlestickChart : public QWidget
{
    Q_OBJECT

public:
    explicit CandlestickChart(QWidget *parent = nullptr);

    void loadSymbol(const QString &symbol);
    void setTimeframe(const QString &tf);
    void setMA5Visible(bool visible);
    void setMA20Visible(bool visible);

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();
    void setupChart();
    void generateSampleData();
    void updateChart();

    QChart *m_chart = nullptr;
    QChartView *m_chartView = nullptr;
    QCandlestickSeries *m_candleSeries = nullptr;
    QLineSeries *m_ma5Series = nullptr;
    QLineSeries *m_ma20Series = nullptr;
    QValueAxis *m_axisX = nullptr;
    QValueAxis *m_axisY = nullptr;

    QString m_currentSymbol = "BBCA";
    QString m_timeframe = "1D";
    QTimer *m_refreshTimer = nullptr;
};
