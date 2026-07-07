#include "SentimentGauge.h"
#include <cmath>

SentimentGauge::SentimentGauge(QWidget *parent)
    : QWidget(parent)
{
    setMinimumSize(100, 80);
    setMaximumHeight(80);
}

void SentimentGauge::setScore(double score)
{
    m_score = qBound(-100.0, score, 100.0);
    update();
    emit scoreChanged(m_score);
}

void SentimentGauge::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    QRect rect(5, 5, width() - 10, height() - 10);
    drawGauge(painter, rect);
}

void SentimentGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 5;
    int radius = qMin(rect.width() / 2, rect.height() - 5) - 5;

    // Background arc
    painter.setPen(QPen(QColor("#0f3460"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Color segments: Red (left) -> Yellow (center) -> Green (right)
    // Left half: Red
    painter.setPen(QPen(QColor("#ff4757"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 90 * 16);

    // Center: Yellow
    painter.setPen(QPen(QColor("#ffc107"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    90 * 16, 15 * 16);

    // Right half: Green
    painter.setPen(QPen(QColor("#00d989"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    105 * 16, 75 * 16);

    // Needle (-100 to +100 mapped to 180 to 0 degrees)
    double normalized = (m_score + 100.0) / 200.0; // 0.0 to 1.0
    double angle = 180.0 - (normalized * 180.0);
    double rad = angle * M_PI / 180.0;
    int needleLen = radius - 10;

    QPoint needleEnd(
        centerX + static_cast<int>(needleLen * cos(rad)),
        centerY - static_cast<int>(needleLen * sin(rad))
    );

    QColor needleColor;
    if (m_score > 20) needleColor = QColor("#00d989");
    else if (m_score < -20) needleColor = QColor("#ff4757");
    else needleColor = QColor("#ffc107");

    painter.setPen(QPen(needleColor, 2));
    painter.drawLine(centerX, centerY, needleEnd);

    // Center dot
    painter.setBrush(QColor("#e94560"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 3, centerY - 3, 6, 6);

    // Score
    painter.setPen(needleColor);
    painter.setFont(QFont("monospace", 12, QFont::Bold));
    painter.drawText(QRect(centerX - 30, centerY - 40, 60, 20), Qt::AlignCenter,
                     QString::number(m_score, 'f', 0));

    // Label
    QString label;
    if (m_score > 20) label = "BULLISH";
    else if (m_score < -20) label = "BEARISH";
    else label = "NEUTRAL";

    painter.setPen(QColor("#888888"));
    painter.setFont(QFont("monospace", 8));
    painter.drawText(QRect(centerX - 30, centerY - 25, 60, 15), Qt::AlignCenter, label);
}
