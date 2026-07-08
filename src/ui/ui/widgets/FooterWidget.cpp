#include "FooterWidget.h"
#include <QPainter>

FooterWidget::FooterWidget(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(24);
}

void FooterWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#323538"));

    // Top border
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.drawLine(0, 0, width(), 0);

    // Left text
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 8));
    painter.drawText(QRect(16, 0, 400, height()), Qt::AlignVCenter,
                     "NISKALA TERMINAL v1.0.0-STABLE | CONNECTED: SG-RT-01");

    // Right links
    painter.drawText(QRect(width() - 300, 0, 300, height()), Qt::AlignVCenter | Qt::AlignRight,
                     "System Status    API Documentation    Legal");
}
