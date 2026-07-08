#pragma once

#include <QWidget>
#include <QVector>
#include <QPainter>
#include <QMouseEvent>
#include <QTimer>

struct OHLCData {
    double open;
    double high;
    double low;
    double close;
    double volume;
    int timestamp;
};

class FinancialChart : public QWidget
{
    Q_OBJECT

public:
    explicit FinancialChart(QWidget *parent = nullptr);

    void loadData(const QVector<OHLCData> &data);
    void addCandle(const OHLCData &candle);
    void setMA5Visible(bool visible);
    void setMA20Visible(bool visible);
    void setVolumeVisible(bool visible);
    void setTimeframe(const QString &tf);

signals:
    void crosshairMoved(double x, double y);
    void candleClicked(int index);

protected:
    void paintEvent(QPaintEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void wheelEvent(QWheelEvent *event) override;

private:
    void drawGrid(QPainter &painter, const QRect &chartRect);
    void drawCandlesticks(QPainter &painter, const QRect &chartRect);
    void drawVolume(QPainter &painter, const QRect &chartRect);
    void drawMALines(QPainter &painter, const QRect &chartRect);
    void drawCrosshair(QPainter &painter, const QRect &chartRect);
    void drawAxes(QPainter &painter, const QRect &chartRect);
    void drawTooltip(QPainter &painter, const QRect &chartRect);

    QVector<OHLCData> m_data;
    bool m_ma5Visible = true;
    bool m_ma20Visible = true;
    bool m_volumeVisible = true;
    QString m_timeframe = "1D";

    double m_priceMin = 0;
    double m_priceMax = 0;
    double m_volumeMax = 0;

    QPoint m_mousePos;
    bool m_crosshairActive = false;
    int m_hoveredCandle = -1;

    double m_offsetX = 0;
    double m_scaleX = 1.0;
};
