#include "AIMarketRegimeWidget.h"

AIMarketRegimeWidget::AIMarketRegimeWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(50);
}

void AIMarketRegimeWidget::updateData(const QString &regime, int confidence, const QString &analysis)
{
    m_regime = regime;
    m_confidence = confidence;
    Q_UNUSED(analysis);
    update();
}

void AIMarketRegimeWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background dengan border hijau tipis
    painter.fillRect(rect(), QColor("#060B16"));
    painter.setPen(QPen(QColor("#75FF9E"), 1));
    painter.setBrush(Qt::NoBrush);
    painter.drawRoundedRect(rect().adjusted(0, 0, -1, -1), 4, 4);

    // [LIVE] badge
    QRect liveRect(12, 8, 45, 18);
    painter.setBrush(QColor("#75FF9E"));
    painter.setPen(Qt::NoPen);
    painter.drawRoundedRect(liveRect, 3, 3);
    painter.setPen(QColor("#060B16"));
    painter.setFont(QFont("Inter", 8, QFont::Bold));
    painter.drawText(liveRect, Qt::AlignCenter, "LIVE");

    // Regime name (tengah)
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("Inter", 14, QFont::Bold));
    painter.drawText(QRect(65, 0, width() - 120, height()), Qt::AlignVCenter, m_regime);

    // Confidence percentage (kanan)
    QColor confColor = m_confidence >= 70 ? QColor("#75FF9E") : 
                       m_confidence >= 50 ? QColor("#CEE8FF") : QColor("#859585");
    painter.setPen(confColor);
    painter.setFont(QFont("JetBrains Mono", 14, QFont::Bold));
    painter.drawText(QRect(width() - 70, 0, 55, height()), Qt::AlignVCenter,
                     QString::number(m_confidence) + "%");
}
