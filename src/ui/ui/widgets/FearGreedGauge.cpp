#include "FearGreedGauge.h"
#include <QPainterPath>
#include <cmath>

FearGreedGauge::FearGreedGauge(const QString &label, QWidget *parent)
    : QWidget(parent), m_label(label)
{
    setMinimumSize(120, 110);
    setMaximumHeight(110);
}

void FearGreedGauge::setScore(int score)
{
    m_score = qBound(0, score, 100);
    update();
    emit scoreChanged(m_score);
}

void FearGreedGauge::setDelta(int delta)
{
    m_delta = delta;
    update();
}

void FearGreedGauge::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    QRect gaugeRect(10, 5, width() - 20, height() - 40);
    drawGauge(painter, gaugeRect);

    // Label (header)
    painter.setPen(QColor("#3b82f6"));
    painter.setFont(QFont("monospace", 9, QFont::Bold));
    QRect labelRect(0, 0, width(), 15);
    painter.drawText(labelRect, Qt::AlignCenter, m_label);

    // Delta text
    if (m_delta != 0) {
        QColor deltaColor = m_delta > 0 ? QColor("#10b981") : QColor("#ef4444");
        painter.setPen(deltaColor);
        painter.setFont(QFont("monospace", 8));
        QString deltaStr = (m_delta > 0 ? "+" : "") + QString::number(m_delta) + " dari kemarin";
        QRect deltaRect(0, height() - 15, width(), 15);
        painter.drawText(deltaRect, Qt::AlignCenter, deltaStr);
    }
}

void FearGreedGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 5;
    int radius = qMin(rect.width() / 2, rect.height() - 5) - 5;

    // Background arc
    painter.setPen(QPen(QColor("#1f2937"), 10, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Colored segments (cyan/teal theme from screenshot)
    QList<QPair<int, QColor>> segments = {
        {25, QColor("#ef4444")},    // Extreme Fear - Red
        {20, QColor("#f59e0b")},    // Fear - Yellow
        {10, QColor("#6b7280")},    // Neutral - Gray
        {20, QColor("#06b6d4")},    // Greed - Cyan
        {25, QColor("#10b981")}     // Extreme Greed - Green
    };

    int startAngle = 0;
    for (const auto &seg : segments) {
        QPen segPen(seg.second, 10, Qt::SolidLine, Qt::RoundCap);
        painter.setPen(segPen);
        painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                        startAngle * 16, seg.first * 16);
        startAngle += seg.first;
    }

    // Needle
    double angle = 180.0 - (m_score / 100.0 * 180.0);
    double rad = angle * M_PI / 180.0;
    int needleLen = radius - 15;

    QPoint needleStart(centerX, centerY);
    QPoint needleEnd(
        centerX + static_cast<int>(needleLen * cos(rad)),
        centerY - static_cast<int>(needleLen * sin(rad))
    );

    painter.setPen(QPen(QColor("#e5e7eb"), 2));
    painter.drawLine(needleStart, needleEnd);

    // Center dot
    painter.setBrush(QColor("#e5e7eb"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 4, centerY - 4, 8, 8);

    // Score text
    QRect scoreRect(centerX - 30, centerY - 45, 60, 25);
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 18, QFont::Bold));
    painter.drawText(scoreRect, Qt::AlignCenter, QString::number(m_score));

    // Status text
    QRect statusRect(centerX - 30, centerY - 25, 60, 15);
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(statusRect, Qt::AlignCenter, getScoreLabel(m_score));
}

QColor FearGreedGauge::getScoreColor(int score) const
{
    if (score <= 25) return QColor("#ef4444");
    if (score <= 45) return QColor("#f59e0b");
    if (score >= 75) return QColor("#10b981");
    if (score >= 55) return QColor("#06b6d4");
    return QColor("#6b7280");
}

QString FearGreedGauge::getScoreLabel(int score) const
{
    if (score <= 20) return "Extreme Fear";
    if (score <= 40) return "Fear";
    if (score <= 60) return "Neutral";
    if (score <= 80) return "Greed";
    return "Extreme Greed";
}
