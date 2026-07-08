#include "FearGreedGauge.h"
#include <QPainterPath>
#include <cmath>

FearGreedGauge::FearGreedGauge(const QString &label, QWidget *parent)
    : QWidget(parent), m_label(label)
{
    setMinimumSize(120, 120);
    setMaximumHeight(120);
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

    // Label (title) - top
    painter.setPen(QColor("#25D9FF"));
    painter.setFont(QFont("monospace", 9, QFont::Bold));
    QRect labelRect(0, 2, width(), 14);
    painter.drawText(labelRect, Qt::AlignCenter, m_label);

    // Gauge - below title with margin
    QRect gaugeRect(10, 18, width() - 20, height() - 50);
    drawGauge(painter, gaugeRect);

    // Delta text - bottom
    if (m_delta != 0) {
        QColor deltaColor = m_delta > 0 ? QColor("#1AF37B") : QColor("#FF5C72");
        painter.setPen(deltaColor);
        painter.setFont(QFont("monospace", 8));
        QString deltaStr = (m_delta > 0 ? "+" : "") + QString::number(m_delta) + " dari kemarin";
        QRect deltaRect(0, height() - 14, width(), 14);
        painter.drawText(deltaRect, Qt::AlignCenter, deltaStr);
    }
}

void FearGreedGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 5;
    int radius = qMin(rect.width() / 2, rect.height() - 10) - 5;

    // Background arc
    painter.setPen(QPen(QColor("#1D2B40"), 10, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Colored segments (cyan/teal theme from screenshot)
    QList<QPair<int, QColor>> segments = {
        {25, QColor("#FF5C72")},    // Extreme Fear - Red
        {20, QColor("#E6874C")},    // Fear - Yellow
        {10, QColor("#7E8AA3")},    // Neutral - Gray
        {20, QColor("#25D9FF")},    // Greed - Cyan
        {25, QColor("#1AF37B")}     // Extreme Greed - Green
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

    painter.setPen(QPen(QColor("#F7FAFC"), 2));
    painter.drawLine(needleStart, needleEnd);

    // Center dot
    painter.setBrush(QColor("#F7FAFC"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 4, centerY - 4, 8, 8);

    // Score text - inside gauge
    QRect scoreRect(centerX - 30, centerY - 45, 60, 25);
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 18, QFont::Bold));
    painter.drawText(scoreRect, Qt::AlignCenter, QString::number(m_score));

    // Status text - below score
    QRect statusRect(centerX - 30, centerY - 25, 60, 15);
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(statusRect, Qt::AlignCenter, getScoreLabel(m_score));
}

QColor FearGreedGauge::getScoreColor(int score) const
{
    if (score <= 25) return QColor("#FF5C72");
    if (score <= 45) return QColor("#E6874C");
    if (score >= 75) return QColor("#1AF37B");
    if (score >= 55) return QColor("#25D9FF");
    return QColor("#7E8AA3");
}

QString FearGreedGauge::getScoreLabel(int score) const
{
    if (score <= 20) return "Extreme Fear";
    if (score <= 40) return "Fear";
    if (score <= 60) return "Neutral";
    if (score <= 80) return "Greed";
    return "Extreme Greed";
}
