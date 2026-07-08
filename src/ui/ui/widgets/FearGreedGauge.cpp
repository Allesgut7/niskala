#include "FearGreedGauge.h"
#include <QPainterPath>
#include <cmath>

FearGreedGauge::FearGreedGauge(const QString &label, QWidget *parent)
    : QWidget(parent), m_label(label)
{
    setMinimumSize(100, 80);
    setMaximumHeight(90);
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

    int centerX = width() / 2;
    int gaugeY = 22;
    int radius = qMin(width() / 2 - 10, 30);

    // Mini semicircle gauge (Stitch style)
    // Background arc
    painter.setPen(QPen(QColor("#3B4A3D"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, gaugeY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Colored segments
    QList<QPair<int, QColor>> segments = {
        {25, QColor("#FFB3AE")},    // Extreme Fear
        {20, QColor("#CEE8FF")},    // Fear
        {10, QColor("#859585")},    // Neutral
        {20, QColor("#CEE8FF")},    // Greed
        {25, QColor("#75FF9E")}     // Extreme Greed
    };

    int startAngle = 0;
    for (const auto &seg : segments) {
        QPen segPen(seg.second, 6, Qt::SolidLine, Qt::RoundCap);
        painter.setPen(segPen);
        painter.drawArc(centerX - radius, gaugeY - radius, radius * 2, radius * 2,
                        startAngle * 16, seg.first * 16);
        startAngle += seg.first;
    }

    // Center dot
    painter.setBrush(QColor("#1D2023"));
    painter.setPen(QPen(QColor("#75FF9E"), 1));
    painter.drawEllipse(centerX - 3, gaugeY - 3, 6, 6);

    // Score
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("JetBrains Mono", 14, QFont::Bold));
    painter.drawText(QRect(centerX - 25, gaugeY + 10, 50, 20), Qt::AlignCenter,
                     QString::number(m_score));

    // Label
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 8));
    QRect labelRect(0, height() - 16, width(), 14);
    painter.drawText(labelRect, Qt::AlignCenter, m_label);
}

QColor FearGreedGauge::getScoreColor(int score) const
{
    if (score <= 25) return QColor("#FFB3AE");
    if (score <= 45) return QColor("#CEE8FF");
    if (score >= 75) return QColor("#75FF9E");
    if (score >= 55) return QColor("#CEE8FF");
    return QColor("#859585");
}

QString FearGreedGauge::getScoreLabel(int score) const
{
    if (score <= 20) return "Extreme Fear";
    if (score <= 40) return "Fear";
    if (score <= 60) return "Neutral";
    if (score <= 80) return "Greed";
    return "Extreme Greed";
}
