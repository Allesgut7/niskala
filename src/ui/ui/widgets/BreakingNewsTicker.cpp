#include "BreakingNewsTicker.h"
#include <QPainter>
#include <QDateTime>

BreakingNewsTicker::BreakingNewsTicker(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(36);

    m_headlines = {
        "Loading news..."
    };

    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &BreakingNewsTicker::scroll);
    m_timer->start(60);
}

void BreakingNewsTicker::updateHeadlines(const QStringList &headlines)
{
    if (!headlines.isEmpty()) {
        m_headlines = headlines;
        m_scrollOffset = 0;
        update();
    }
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
    painter.fillRect(rect(), QColor("#111417"));

    // BREAKING badge with bracket
    painter.setPen(QColor("#FFB3AE"));
    painter.setFont(QFont("Inter", 9, QFont::Bold));
    QRect badgeRect(8, 8, 90, 20);
    painter.drawText(badgeRect, Qt::AlignVCenter, "[ BREAKING ]");

    // Scrolling headlines
    QString ticker;
    for (const auto &h : m_headlines) {
        ticker += h + "   •   ";
    }
    ticker += ticker;

    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("Inter", 10));

    int x = 110 - m_scrollOffset;
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), ticker);

    // Time
    QString time = QTime::currentTime().toString("HH:mm") + " WIB";
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 9));
    QRect timeRect(width() - 120, 0, 110, height());
    painter.drawText(timeRect, Qt::AlignRight | Qt::AlignVCenter, time);

    // Bottom border
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.drawLine(0, height() - 1, width(), height() - 1);
}
