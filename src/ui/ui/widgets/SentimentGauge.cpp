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

    QRect gaugeRect(5, 5, width() - 10, height() - 10);
    drawGauge(painter, gaugeRect);
}

void SentimentGauge::drawGauge(QPainter &painter, const QRect &rect)
{
    int centerX = rect.center().x();
    int centerY = rect.bottom() - 5;
    int radius = qMin(rect.width() / 2, rect.height() - 5) - 5;

    painter.setPen(QPen(QColor("#1B2940"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    painter.setPen(QPen(QColor("#FF5C72"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 90 * 16);

    painter.setPen(QPen(QColor("#E6874C"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    90 * 16, 15 * 16);

    painter.setPen(QPen(QColor("#1AF37B"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    105 * 16, 75 * 16);

    double normalized = (m_score + 100.0) / 200.0;
    double angle = 180.0 - (normalized * 180.0);
    double rad = angle * M_PI / 180.0;
    int needleLen = radius - 10;

    QPoint needleStart(centerX, centerY);
    QPoint needleEnd(
        centerX + static_cast<int>(needleLen * cos(rad)),
        centerY - static_cast<int>(needleLen * sin(rad))
    );

    QColor needleColor;
    if (m_score > 20) needleColor = QColor("#1AF37B");
    else if (m_score < -20) needleColor = QColor("#FF5C72");
    else needleColor = QColor("#E6874C");

    painter.setPen(QPen(needleColor, 2));
    painter.drawLine(needleStart, needleEnd);

    painter.setBrush(QColor("#D84B63"));
    painter.setPen(Qt::NoPen);
    painter.drawEllipse(centerX - 3, centerY - 3, 6, 6);

    QRect scoreRect(centerX - 30, centerY - 40, 60, 20);
    painter.setPen(needleColor);
    painter.setFont(QFont("monospace", 12, QFont::Bold));
    painter.drawText(scoreRect, Qt::AlignCenter, QString::number(m_score, 'f', 0));

    QString label;
    if (m_score > 20) label = "BULLISH";
    else if (m_score < -20) label = "BEARISH";
    else label = "NEUTRAL";

    QRect labelRect(centerX - 30, centerY - 25, 60, 15);
    painter.setPen(QColor("#7E8AA3"));
    painter.setFont(QFont("monospace", 8));
    painter.drawText(labelRect, Qt::AlignCenter, label);
}
