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

    QRect gaugeRect(10, 5, width() - 20, height() - 30);
    drawGauge(painter, gaugeRect);

    painter.setPen(QColor("#e0e0e0"));
    painter.setFont(QFont("monospace", 10, QFont::Bold));
    QRect labelRect(0, height() - 25, width(), 20);
    painter.drawText(labelRect, Qt::AlignCenter, m_label);
}

void FearGreedGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 10;
    int radius = qMin(rect.width() / 2, rect.height()) - 5;

    QPen bgPen(QColor("#0f3460"), 8, Qt::SolidLine, Qt::RoundCap);
    painter.setPen(bgPen);
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    QList<QPair<int, QColor>> segments = {
        {25, QColor("#ff4757")},
        {20, QColor("#ffc107")},
        {10, QColor("#e0e0e0")},
        {20, QColor("#00bcd4")},
        {25, QColor("#00d989")}
    };

    int startAngle = 0;
    for (const auto &seg : segments) {
        QPen segPen(seg.second, 8, Qt::SolidLine, Qt::RoundCap);
        painter.setPen(segPen);
        painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                        startAngle * 16, seg.first * 16);
        startAngle += seg.first;
    }

    double angle = 180.0 - (m_score / 100.0 * 180.0);
    double rad = angle * M_PI / 180.0;
    int needleLen = radius - 15;

    QPoint needleStart(centerX, centerY);
    QPoint needleEnd(
        centerX + static_cast<int>(needleLen * cos(rad)),
        centerY - static_cast<int>(needleLen * sin(rad))
    );

    painter.setPen(QPen(QColor("#e0e0e0"), 2));
    painter.drawLine(needleStart, needleEnd);

    painter.setBrush(QColor("#e94560"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 4, centerY - 4, 8, 8);

    QRect scoreRect(centerX - 30, centerY - 45, 60, 25);
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("monospace", 16, QFont::Bold));
    painter.drawText(scoreRect, Qt::AlignCenter, QString::number(m_score));

    QRect statusRect(centerX - 30, centerY - 25, 60, 15);
    painter.setPen(QColor("#888888"));
    painter.setFont(QFont("monospace", 8));
    painter.drawText(statusRect, Qt::AlignCenter, getScoreLabel(m_score));
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
