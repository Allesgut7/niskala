#include "BreakingNewsTicker.h"
#include <QPainter>
#include <QDateTime>

BreakingNewsTicker::BreakingNewsTicker(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(36);

    m_headlines = {
        "BBRI Buyback approved",
        "BI Pertahankan Suku Bunga di 6.25%",
        "Foreign Net Buy IDR 1.24T (All Market)",
        "The Fed Minutes Tonight",
        "Oil Menguat 1.8%",
        "Nvidia +2.6% After Hours",
        "IHSG Ditutup Menguat 1.23%",
        "Rupiah Stabil di 16.140"
    };

    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &BreakingNewsTicker::scroll);
    m_timer->start(60);
}

void BreakingNewsTicker::scroll()
{
    m_scrollOffset++;
    if (m_scrollOffset > 500) m_scrollOffset = 0;
    update();
}

void BreakingNewsTicker::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#0a0e17"));

    // BREAKING badge
    painter.setBrush(QColor("#dc2626"));
    painter.setPen(Qt::NoPen);
    QRect badgeRect(8, 6, 80, 24);
    painter.drawRoundedRect(badgeRect, 4, 4);
    painter.setPen(QColor("#ffffff"));
    painter.setFont(QFont("monospace", 10, QFont::Bold));
    painter.drawText(badgeRect, Qt::AlignCenter, "BREAKING");

    // Scrolling headlines
    QString ticker;
    for (const auto &h : m_headlines) {
        ticker += h + "   •   ";
    }
    ticker += ticker;

    painter.setPen(QColor("#e5e7eb"));
    painter.setFont(QFont("monospace", 10));

    int x = 100 - m_scrollOffset;
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), ticker);

    // Time
    QString time = QTime::currentTime().toString("HH:mm") + " WIB";
    painter.setPen(QColor("#9ca3af"));
    QRect timeRect(width() - 120, 0, 110, height());
    painter.drawText(timeRect, Qt::AlignRight | Qt::AlignVCenter, time);

    // Bottom border
    painter.setPen(QPen(QColor("#1f2937"), 1));
    painter.drawLine(0, height() - 1, width(), height() - 1);
}
