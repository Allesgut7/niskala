#include "FearGreedGauge.h"
#include <QPainterPath>
#include <cmath>

FearGreedGauge::FearGreedGauge(const QString &label, QWidget *parent)
    : QWidget(parent), m_label(label)
{
    setMinimumSize(120, 100);
    setMaximumHeight(120);
}

void FearGreedGauge::setScore(int score)
{
    m_score = qBound(0, score, 100);
    update();
    emit scoreChanged(m_score);
}

void FearGreedGauge::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    QRect rect(10, 5, width() - 20, height() - 30);
    drawGauge(painter, rect);

    // Label
    painter.setPen(QColor("#e0e0e0"));
    painter.setFont(QFont("monospace", 10, QFont::Bold));
    painter.drawText(rect(0, height() - 25, width(), 20), Qt::AlignCenter, m_label);
}

void FearGreedGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 10;
    int radius = qMin(rect.width() / 2, rect.height()) - 5;

    // Background arc (gray)
    QPen bgPen(QColor("#0f3460"), 8, Qt::SolidLine, Qt::RoundCap);
    painter.setPen(bgPen);
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Colored segments
    QList<QPair<int, QColor>> segments = {
        {25, QColor("#ff4757")},    // Extreme Fear - Red
        {20, QColor("#ffc107")},    // Fear - Yellow
        {10, QColor("#e0e0e0")},    // Neutral - Gray
        {20, QColor("#00bcd4")},    // Greed - Cyan
        {25, QColor("#00d989")}     // Extreme Greed - Green
    };

    int startAngle = 0;
    for (const auto &seg : segments) {
        QPen segPen(seg.second, 8, Qt::SolidLine, Qt::RoundCap);
        painter.setPen(segPen);
        painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                        startAngle * 16, seg.first * 16);
        startAngle += seg.first;
    }

    // Needle
    double angle = 180.0 - (m_score / 100.0 * 180.0);
    double rad = angle * M_PI / 180.0;
    int needleLen = radius - 15;

    QPoint needleEnd(
        centerX + static_cast<int>(needleLen * cos(rad)),
        centerY - static_cast<int>(needleLen * sin(rad))
    );

    painter.setPen(QPen(QColor("#e0e0e0"), 2));
    painter.drawLine(centerX, centerY, needleEnd);

    // Center dot
    painter.setBrush(QColor("#e94560"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 4, centerY - 4, 8, 8);

    // Score text
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 16, QFont::Bold));
    painter.drawText(rect(0, centerY - 45, rect.width(), 25), Qt::AlignCenter,
                     QString::number(m_score));

    // Status text
    painter.setPen(QColor("#888888"));
    painter.setFont(QFont("monospace", 8));
    painter.drawText(rect(0, centerY - 25, rect.width(), 15), Qt::AlignCenter,
                     getScoreLabel(m_score));
}

QColor FearGreedGauge::getScoreColor(int score) const
{
    if (score <= 25) return QColor("#ff4757");
    if (score <= 45) return QColor("#ffc107");
    if (score >= 75) return QColor("#00d989");
    if (score >= 55) return QColor("#00bcd4");
    return QColor("#e0e0e0");
}

QString FearGreedGauge::getScoreLabel(int score) const
{
    if (score <= 20) return "EXTREME FEAR";
    if (score <= 40) return "FEAR";
    if (score <= 60) return "NEUTRAL";
    if (score <= 80) return "GREED";
    return "EXTREME GREED";
}
