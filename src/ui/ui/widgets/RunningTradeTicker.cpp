#include "RunningTradeTicker.h"
#include <QPainter>

RunningTradeTicker::RunningTradeTicker(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(28);

    m_trades = {
        "BBCA 9200 150000",
        "BBRI 4800 200000",
        "BMRI 6150 80000",
        "TLKM 2850 120000",
        "GOTO 85 500000",
        "ADRO 1520 90000",
        "UNVR 4250 50000",
        "ICBP 11200 30000",
        "ASII 5400 70000",
        "PGAS 1890 110000",
    };

    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &RunningTradeTicker::scroll);
    m_timer->start(80);
}

void RunningTradeTicker::scroll()
{
    m_scrollOffset++;
    if (m_scrollOffset > 300) m_scrollOffset = 0;
    update();
}

void RunningTradeTicker::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#16213e"));

    // Build ticker
    QString ticker;
    for (const auto &t : m_trades) {
        ticker += t + "   ●   ";
    }
    ticker += ticker; // Duplicate for scrolling

    // Draw text
    painter.setPen(QColor("#ffc107"));
    painter.setFont(QFont("monospace", 10, QFont::Bold));

    int textWidth = painter.fontMetrics().horizontalAdvance(ticker);
    int x = -m_scrollOffset;
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), ticker);

    // Border
    painter.setPen(QPen(QColor("#0f3460"), 1));
    painter.drawLine(0, height() - 1, width(), height() - 1);
}
