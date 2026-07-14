#include "FearGreedGauge.h"
#include <QPainterPath>
#include <QJsonObject>
#include <cmath>

FearGreedGauge::FearGreedGauge(const QString &label, QWidget *parent)
    : QWidget(parent), m_label(label)
{
    setMinimumSize(100, 120);
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

void FearGreedGauge::setScoreFromJson(const QJsonObject &data)
{
    if (data.contains("score")) {
        setScore(data["score"].toInt());
    }
    if (data.contains("delta")) {
        setDelta(data["delta"].toInt());
    }
}

void FearGreedGauge::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    if (m_label == "Indonesia") {
        painter.setPen(QColor("#CEE8FF"));
        painter.setFont(QFont("monospace", 11, QFont::Bold));
        painter.drawText(QRect(8, 8, width() - 16, 20), Qt::AlignLeft, "FEAR & GREED");
    }

    int centerX = width() / 2;
    int gaugeAreaH = height() - 30;
    int radius = qMin(width() / 2 - 10, gaugeAreaH / 3);
    int gaugeY = radius + 46;

    // 1. Background arc (full gray semicircle)
    painter.setPen(QPen(QColor("#3B4A3D"), 6, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, gaugeY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // 2. Fill arc sesuai score
    double scoreAngle = (m_score / 100.0) * 180.0;
    if (scoreAngle > 0) {
        QColor fillColor = getScoreColor(m_score);
        painter.setPen(QPen(fillColor, 6, Qt::SolidLine, Qt::RoundCap));
        painter.drawArc(centerX - radius, gaugeY - radius, radius * 2, radius * 2,
                        0, static_cast<int>(scoreAngle * 16));
    }

    // 3. Pointer di ujung fill arc
    double rad = scoreAngle * M_PI / 180.0;
    int px = centerX + static_cast<int>(radius * cos(rad));
    int py = gaugeY - static_cast<int>(radius * sin(rad));
    painter.setBrush(getScoreColor(m_score));
    painter.setPen(QPen(QColor("#1D2023"), 2));
    painter.drawEllipse(px - 5, py - 5, 10, 10);

    // 4. Center dot
    painter.setBrush(QColor("#1D2023"));
    painter.setPen(QPen(QColor("#75FF9E"), 1));
    painter.drawEllipse(centerX - 3, gaugeY - 3, 6, 6);

    // 5. Score
    int scoreY = gaugeY + radius - 18;
    painter.setPen(getScoreColor(m_score));
    painter.setFont(QFont("JetBrains Mono", 18, QFont::Bold));
    painter.drawText(QRect(centerX - 30, scoreY, 60, 24), Qt::AlignCenter,
                     QString::number(m_score));

    // 6. Delta arrow
    if (m_delta != 0) {
        QColor deltaColor = m_delta > 0 ? QColor("#75FF9E") : QColor("#FFB3AE");
        painter.setPen(deltaColor);
        painter.setFont(QFont("JetBrains Mono", 10, QFont::Bold));
        QString dText = m_delta > 0
            ? QString("\u25B2 +%1").arg(m_delta)
            : QString("\u25BC %1").arg(m_delta);
        painter.drawText(QRect(centerX + 30, scoreY - 2, 40, 20), Qt::AlignLeft, dText);
    }

    // 7. Label
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 9));
    QRect labelRect(0, height() - 18, width(), 16);
    painter.drawText(labelRect, Qt::AlignCenter, m_label);
}

QColor FearGreedGauge::getScoreColor(int score) const
{
    if (score < 25) return QColor("#FFB3AE");   // 0-24: Extreme Fear → merah
    if (score < 45) return QColor("#FFD700");   // 25-44: Fear → kuning
    if (score > 75) return QColor("#2E7D32");   // 76-100: Extreme Greed → hijau pekat
    if (score > 55) return QColor("#75FF9E");   // 56-75: Greed → hijau
    return QColor("#859585");                     // 45-55: Neutral → abu
}

QString FearGreedGauge::getScoreLabel(int score) const
{
    if (score <= 20) return "Extreme Fear";
    if (score <= 40) return "Fear";
    if (score <= 60) return "Neutral";
    if (score <= 80) return "Greed";
    return "Extreme Greed";
}
