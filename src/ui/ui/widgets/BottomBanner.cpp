#include "BottomBanner.h"
#include <QPainter>
#include <QHBoxLayout>

BottomBanner::BottomBanner(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(30);
    setupData();
}

void BottomBanner::setupData()
{
    m_gainers = {
        "ICBP +1.82%",
        "ADRO +2.01%",
        "BBCA +1.66%",
        "BREN +1.80%",
        "MDKA +3.44%"
    };

    m_losers = {
        "GOTO -2.30%",
        "UNVR -1.73%",
        "BBRI -1.03%",
        "EXCL -0.71%",
        "BBNI -0.57%"
    };
}

void BottomBanner::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#09111F"));

    // Gainers
    painter.setPen(QColor("#1AF37B"));
    painter.setFont(QFont("monospace", 9, QFont::Bold));

    int x = 10;
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), "GAINERS: ");
    x += painter.fontMetrics().horizontalAdvance("GAINERS: ");

    painter.setPen(QColor("#1AF37B"));
    for (const auto &g : m_gainers) {
        painter.drawText(x, y + painter.fontMetrics().ascent(), g);
        x += painter.fontMetrics().horizontalAdvance(g) + 20;
    }

    // Losers
    painter.setPen(QColor("#7E8AA3"));
    painter.drawText(x, y + painter.fontMetrics().ascent(), "  |  ");
    x += painter.fontMetrics().horizontalAdvance("  |  ");

    painter.setPen(QColor("#FF5C72"));
    painter.drawText(x, y + painter.fontMetrics().ascent(), "LOSERS: ");
    x += painter.fontMetrics().horizontalAdvance("LOSERS: ");

    for (const auto &l : m_losers) {
        painter.drawText(x, y + painter.fontMetrics().ascent(), l);
        x += painter.fontMetrics().horizontalAdvance(l) + 20;
    }

    // Top border
    painter.setPen(QPen(QColor("#1D2B40"), 1));
    painter.drawLine(0, 0, width(), 0);
}
