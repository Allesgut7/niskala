#include "FinancialChart.h"
#include <QPainterPath>
#include <cmath>

FinancialChart::FinancialChart(QWidget *parent)
    : QWidget(parent)
{
    setMouseTracking(true);
    setMinimumSize(400, 300);
    setStyleSheet("background-color: #1D2023;");
}

void FinancialChart::loadData(const QVector<OHLCData> &data)
{
    m_data = data;

    // Calculate price range
    m_priceMin = 1e9;
    m_priceMax = -1e9;
    m_volumeMax = 0;

    for (const auto &candle : data) {
        m_priceMin = qMin(m_priceMin, candle.low);
        m_priceMax = qMax(m_priceMax, candle.high);
        m_volumeMax = qMax(m_volumeMax, candle.volume);
    }

    m_priceMin -= (m_priceMax - m_priceMin) * 0.05;
    m_priceMax += (m_priceMax - m_priceMin) * 0.05;

    update();
}

void FinancialChart::setMA5Visible(bool visible) { m_ma5Visible = visible; update(); }
void FinancialChart::setMA20Visible(bool visible) { m_ma20Visible = visible; update(); }
void FinancialChart::setVolumeVisible(bool visible) { m_volumeVisible = visible; update(); }
void FinancialChart::setTimeframe(const QString &tf) { m_timeframe = tf; }

void FinancialChart::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#1D2023"));

    if (m_data.isEmpty()) return;

    // Chart area (with margins)
    int marginL = 60, marginR = 20, marginT = 20, marginB = m_volumeVisible ? 80 : 30;
    QRect chartRect(marginL, marginT, width() - marginL - marginR, height() - marginT - marginB);

    drawGrid(painter, chartRect);
    drawCandlesticks(painter, chartRect);
    if (m_volumeVisible) drawVolume(painter, chartRect);
    if (m_ma5Visible || m_ma20Visible) drawMALines(painter, chartRect);
    drawAxes(painter, chartRect);
    if (m_crosshairActive) drawCrosshair(painter, chartRect);
}

void FinancialChart::drawGrid(QPainter &painter, const QRect &chartRect)
{
    painter.setPen(QPen(QColor("#3B4A3D"), 1, Qt::DotLine));

    // Horizontal lines (price levels)
    int numLines = 6;
    for (int i = 0; i <= numLines; ++i) {
        int y = chartRect.top() + (chartRect.height() * i / numLines);
        painter.drawLine(chartRect.left(), y, chartRect.right(), y);
    }

    // Vertical lines (time)
    int numVertical = qMin(10, m_data.size());
    for (int i = 0; i <= numVertical; ++i) {
        int x = chartRect.left() + (chartRect.width() * i / numVertical);
        painter.drawLine(x, chartRect.top(), x, chartRect.bottom());
    }
}

void FinancialChart::drawCandlesticks(QPainter &painter, const QRect &chartRect)
{
    if (m_data.isEmpty()) return;

    int numCandles = m_data.size();
    double candleWidth = qMax(1.0, (chartRect.width() / numCandles) * 0.7);
    double bodyWidth = candleWidth * 0.6;

    for (int i = 0; i < numCandles; ++i) {
        const auto &candle = m_data[i];

        // Calculate positions
        double x = chartRect.left() + (i + 0.5) * (chartRect.width() / numCandles);
        double openY = chartRect.top() + (1.0 - (candle.open - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();
        double closeY = chartRect.top() + (1.0 - (candle.close - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();
        double highY = chartRect.top() + (1.0 - (candle.high - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();
        double lowY = chartRect.top() + (1.0 - (candle.low - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();

        bool isGreen = candle.close >= candle.open;
        QColor color = isGreen ? QColor("#75FF9E") : QColor("#FFB3AE");

        // Wick
        painter.setPen(QPen(color, 1));
        painter.drawLine(QPointF(x, highY), QPointF(x, lowY));

        // Body
        double bodyTop = qMin(openY, closeY);
        double bodyHeight = qAbs(closeY - openY);
        if (bodyHeight < 1) bodyHeight = 1;

        if (isGreen) {
            painter.setBrush(color);
            painter.setPen(Qt::NoPen);
        } else {
            painter.setBrush(color);
            painter.setPen(Qt::NoPen);
        }

        painter.drawRect(QRectF(x - bodyWidth/2, bodyTop, bodyWidth, bodyHeight));
    }
}

void FinancialChart::drawVolume(QPainter &painter, const QRect &chartRect)
{
    if (m_data.isEmpty() || m_volumeMax == 0) return;

    int numCandles = m_data.size();
    double candleWidth = qMax(1.0, (chartRect.width() / numCandles) * 0.7);
    int volumeHeight = 40;
    int volumeTop = chartRect.bottom() + 10;

    for (int i = 0; i < numCandles; ++i) {
        const auto &candle = m_data[i];

        double x = chartRect.left() + (i + 0.5) * (chartRect.width() / numCandles);
        int barHeight = static_cast<int>((candle.volume / m_volumeMax) * volumeHeight);

        bool isGreen = candle.close >= candle.open;
        QColor color = isGreen ? QColor(117, 255, 158, 100) : QColor(255, 179, 174, 100);

        painter.setBrush(color);
        painter.setPen(Qt::NoPen);
        painter.drawRect(QRectF(x - candleWidth/2, volumeTop + volumeHeight - barHeight,
                                candleWidth, barHeight));
    }
}

void FinancialChart::drawMALines(QPainter &painter, const QRect &chartRect)
{
    if (m_data.size() < 5) return;

    int numCandles = m_data.size();

    // MA5
    if (m_ma5Visible && m_data.size() >= 5) {
        painter.setPen(QPen(QColor("#CEE8FF"), 1));
        QPainterPath ma5Path;
        bool first = true;

        for (int i = 4; i < numCandles; ++i) {
            double sum = 0;
            for (int j = i - 4; j <= i; ++j) {
                sum += m_data[j].close;
            }
            double ma5 = sum / 5.0;
            double x = chartRect.left() + (i + 0.5) * (chartRect.width() / numCandles);
            double y = chartRect.top() + (1.0 - (ma5 - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();

            if (first) {
                ma5Path.moveTo(x, y);
                first = false;
            } else {
                ma5Path.lineTo(x, y);
            }
        }
        painter.drawPath(ma5Path);
    }

    // MA20
    if (m_ma20Visible && m_data.size() >= 20) {
        painter.setPen(QPen(QColor("#859585"), 1, Qt::DashLine));
        QPainterPath ma20Path;
        bool first = true;

        for (int i = 19; i < numCandles; ++i) {
            double sum = 0;
            for (int j = i - 19; j <= i; ++j) {
                sum += m_data[j].close;
            }
            double ma20 = sum / 20.0;
            double x = chartRect.left() + (i + 0.5) * (chartRect.width() / numCandles);
            double y = chartRect.top() + (1.0 - (ma20 - m_priceMin) / (m_priceMax - m_priceMin)) * chartRect.height();

            if (first) {
                ma20Path.moveTo(x, y);
                first = false;
            } else {
                ma20Path.lineTo(x, y);
            }
        }
        painter.drawPath(ma20Path);
    }
}

void FinancialChart::drawAxes(QPainter &painter, const QRect &chartRect)
{
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 9));

    // Price axis (right)
    int numLabels = 6;
    for (int i = 0; i <= numLabels; ++i) {
        double price = m_priceMin + (m_priceMax - m_priceMin) * i / numLabels;
        int y = chartRect.top() + (chartRect.height() * (numLabels - i) / numLabels);
        painter.drawText(chartRect.right() + 5, y + 4, QString::number(price, 'f', 0));
    }

    // Time axis (bottom)
    if (!m_data.isEmpty()) {
        int numTicks = qMin(5, m_data.size());
        for (int i = 0; i < numTicks; ++i) {
            int idx = i * (m_data.size() - 1) / (numTicks - 1);
            int x = chartRect.left() + (idx + 0.5) * (chartRect.width() / m_data.size());
            painter.drawText(x - 15, chartRect.bottom() + 15, QString::number(idx));
        }
    }

    // Timeframe label
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("JetBrains Mono", 10, QFont::Bold));
    painter.drawText(chartRect.left(), chartRect.top() - 5, m_timeframe);
}

void FinancialChart::drawCrosshair(QPainter &painter, const QRect &chartRect)
{
    if (!chartRect.contains(m_mousePos)) return;

    painter.setPen(QPen(QColor("#859585"), 1, Qt::DashLine));

    // Vertical line
    painter.drawLine(m_mousePos.x(), chartRect.top(), m_mousePos.x(), chartRect.bottom());

    // Horizontal line
    painter.drawLine(chartRect.left(), m_mousePos.y(), chartRect.right(), m_mousePos.y());

    // Price label
    double price = m_priceMax - (m_mousePos.y() - chartRect.top()) * (m_priceMax - m_priceMin) / chartRect.height();
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("JetBrains Mono", 9));
    painter.drawText(chartRect.right() + 5, m_mousePos.y() + 4, QString::number(price, 'f', 0));
}

void FinancialChart::drawTooltip(QPainter &painter, const QRect &chartRect)
{
    if (m_hoveredCandle < 0 || m_hoveredCandle >= m_data.size()) return;

    const auto &candle = m_data[m_hoveredCandle];

    QString text = QString("O: %1 H: %2 L: %3 C: %4")
        .arg(candle.open, 0, 'f', 2)
        .arg(candle.high, 0, 'f', 2)
        .arg(candle.low, 0, 'f', 2)
        .arg(candle.close, 0, 'f', 2);

    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("JetBrains Mono", 9));
    painter.drawText(chartRect.left() + 10, chartRect.top() + 15, text);
}

void FinancialChart::mouseMoveEvent(QMouseEvent *event)
{
    m_mousePos = event->pos();
    m_crosshairActive = true;

    // Calculate hovered candle
    int marginL = 60;
    int numCandles = m_data.size();
    if (numCandles > 0) {
        double candleWidth = (width() - marginL - 20) / numCandles;
        int idx = static_cast<int>((m_mousePos.x() - marginL) / candleWidth);
        m_hoveredCandle = (idx >= 0 && idx < numCandles) ? idx : -1;
    }

    update();
}

void FinancialChart::mousePressEvent(QMouseEvent *event)
{
    if (m_hoveredCandle >= 0) {
        emit candleClicked(m_hoveredCandle);
    }
}

void FinancialChart::wheelEvent(QWheelEvent *event)
{
    double delta = event->angleDelta().y() / 120.0;
    m_scaleX *= (1.0 + delta * 0.1);
    m_scaleX = qBound(0.5, m_scaleX, 5.0);
    update();
}
