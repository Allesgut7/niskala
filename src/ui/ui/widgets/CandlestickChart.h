#pragma once

#include <QWidget>
#include <QTimer>

class FinancialChart;

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

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();
    void generateSampleData();

    FinancialChart *m_chart = nullptr;
    QString m_currentSymbol = "BBCA";
    QString m_timeframe = "1D";
    QTimer *m_refreshTimer = nullptr;
};
