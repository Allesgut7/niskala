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
    m_timer->start(40);
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
    update();
}

void BreakingNewsTicker::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#111417"));

    // BREAKING badge
    painter.setPen(QColor("#FFB3AE"));
    painter.setFont(QFont("Inter", 9, QFont::Bold));
    QRect badgeRect(8, 8, 90, 20);
    painter.drawText(badgeRect, Qt::AlignVCenter, "[ BREAKING ]");

    // Clip area setelah badge (text menghilang di belakang badge)
    painter.setClipRect(QRect(110, 0, width() - 110, height()));

    // Scrolling headlines (seamless loop)
    QString ticker;
    for (const auto &h : m_headlines) {
        ticker += h + "   •   ";
    }
    QString fullTicker = ticker + ticker;

    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("Inter", 10));

    int textWidth = painter.fontMetrics().horizontalAdvance(fullTicker);
    int x = 110 - (m_scrollOffset % textWidth);
    int y = (height() - painter.fontMetrics().height()) / 2;

    painter.drawText(x, y + painter.fontMetrics().ascent(), fullTicker);

    // Reset clip
    painter.setClipping(false);

    // Time
    QString time = QTime::currentTime().toString("HH:mm") + " WIB";
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 9));
    QRect timeRect(width() - 120, 0, 110, height());
    painter.drawText(timeRect, Qt::AlignRight | Qt::AlignVCenter, time);
}
