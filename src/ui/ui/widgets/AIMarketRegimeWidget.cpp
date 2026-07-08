#include "AIMarketRegimeWidget.h"
#include <QPainterPath>
#include <cmath>

AIMarketRegimeWidget::AIMarketRegimeWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(140);
}

void AIMarketRegimeWidget::updateData(const QString &regime, int confidence, const QString &analysis)
{
    m_regime = regime;
    m_confidence = confidence;
    m_analysis = analysis;
    update();
}

void AIMarketRegimeWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background with subtle primary tint
    painter.fillRect(rect(), QColor("#060B16"));

    // Border
    painter.setPen(QPen(QColor("#75FF9E"), 1));
    painter.setBrush(Qt::NoBrush);
    painter.drawRoundedRect(rect().adjusted(0, 0, -1, -1), 4, 4);

    // Header with bracket accents
    painter.setPen(QColor("#75FF9E"));
    painter.setFont(QFont("Inter", 11, QFont::Bold));
    painter.drawText(QRect(12, 8, 200, 18), Qt::AlignLeft, "[ AI MARKET REGIME ]");

    // LIVE badge
    QRect liveRect(width() - 60, 8, 45, 16);
    painter.setBrush(QColor("#75FF9E"));
    painter.setPen(Qt::NoPen);
    painter.drawRoundedRect(liveRect, 3, 3);
    painter.setPen(QColor("#060B16"));
    painter.setFont(QFont("JetBrains Mono", 7, QFont::Bold));
    painter.drawText(liveRect, Qt::AlignCenter, "LIVE");

    // Spinning icon (simplified as rotating circle)
    int iconX = 24;
    int iconY = 40;
    int iconR = 16;
    painter.setPen(QPen(QColor("#75FF9E"), 2));
    painter.setBrush(Qt::NoBrush);
    painter.drawEllipse(iconX - iconR, iconY - iconR, iconR * 2, iconR * 2);

    // Arrow indicator inside circle
    double arrowAngle = 45.0 * M_PI / 180.0;
    QPoint arrowCenter(iconX, iconY);
    QPoint arrowEnd(
        iconX + static_cast<int>((iconR - 4) * cos(arrowAngle)),
        iconY - static_cast<int>((iconR - 4) * sin(arrowAngle))
    );
    painter.drawLine(arrowCenter, arrowEnd);

    // Regime text
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("Inter", 16, QFont::Bold));
    painter.drawText(QRect(50, 30, 200, 24), Qt::AlignLeft, m_regime);

    // Confidence score
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 9));
    painter.drawText(QRect(50, 55, 200, 14), Qt::AlignLeft,
                     "Confidence Score: " + QString::number(m_confidence) + "%");

    // Analysis text
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("Inter", 9));
    QRect analysisRect(12, 80, width() - 24, 50);
    painter.drawText(analysisRect, Qt::AlignLeft | Qt::TextWordWrap, m_analysis);
}
