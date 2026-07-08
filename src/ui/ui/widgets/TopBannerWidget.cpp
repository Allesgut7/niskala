#include "TopBannerWidget.h"
#include <QPainter>
#include <QHBoxLayout>

TopBannerWidget::TopBannerWidget(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(35);
    setMinimumWidth(400);

    m_indices = {
        "IHSG 7,123.45 +0.50%",
        "S&P500 5,432.10 +1.20%",
        "Nikkei 38,450.00 -0.30%",
        "STI 3,245.67 +0.80%",
        "HSI 18,234.50 -1.10%"
    };

    m_commodities = {
        "Gold 2,050.30 +0.20%",
        "Crude 78.50 -0.80%",
        "Copper 4.25 +1.50%"
    };

    m_forex = {
        "USD/IDR 15,600 +0.30%",
        "EUR/IDR 17,050 -0.15%",
        "SGD/IDR 11,700 +0.10%"
    };

    m_scrollTimer = new QTimer(this);
    connect(m_scrollTimer, &QTimer::timeout, this, &TopBannerWidget::scrollTicker);
    m_scrollTimer->start(100);
}

void TopBannerWidget::scrollTicker()
{
    m_scrollOffset++;
    if (m_scrollOffset > 200) m_scrollOffset = 0;
    update();
}

void TopBannerWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#09111F"));

    // Build ticker string
    QStringList all;
    all << m_indices << m_commodities << m_forex;
    QString ticker = all.join("   |   ");
    ticker = ticker + "   |   " + ticker; // Duplicate for scrolling

    // Draw scrolling text
    painter.setPen(QColor("#F7FAFC"));
    painter.setFont(QFont("monospace", 10));

    int textWidth = painter.fontMetrics().horizontalAdvance(ticker);
    int x = -m_scrollOffset;
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), ticker);

    // If scrolled past half, reset
    if (x + textWidth / 2 < 0) {
        m_scrollOffset = 0;
    }

    // Border bottom
    painter.setPen(QPen(QColor("#1D2B40"), 2));
    painter.drawLine(0, height() - 2, width(), height() - 2);
}

void TopBannerWidget::setIndices(const QStringList &indices)
{
    m_indices = indices;
}

void TopBannerWidget::setCommodities(const QStringList &commodities)
{
    m_commodities = commodities;
}

void TopBannerWidget::setForex(const QStringList &forex)
{
    m_forex = forex;
}
