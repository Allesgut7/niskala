#include "ForeignFlowWidget.h"

ForeignFlowWidget::ForeignFlowWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(120);
}

void ForeignFlowWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#1D2023"));

    // Border
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.setBrush(Qt::NoBrush);
    painter.drawRoundedRect(rect().adjusted(0, 0, -1, -1), 4, 4);

    // Header with bracket accents
    painter.setPen(QColor("#CEE8FF"));
    painter.setFont(QFont("Inter", 11, QFont::Bold));
    painter.drawText(QRect(12, 8, 200, 18), Qt::AlignLeft, "[ FOREIGN FLOW ]");

    // Total Net Buy card
    QRect cardRect(12, 32, width() - 24, 40);
    painter.setBrush(QColor("#191C1F"));
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.drawRoundedRect(cardRect, 4, 4);

    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 8));
    painter.drawText(QRect(20, 38, 200, 14), Qt::AlignLeft, "TOTAL NET BUY (YTD)");

    painter.setPen(QColor("#75FF9E"));
    painter.setFont(QFont("JetBrains Mono", 14, QFont::Bold));
    painter.drawText(QRect(20, 52, 200, 18), Qt::AlignLeft, "IDR +24.8T");

    // Globe icon placeholder
    painter.setPen(QColor("#75FF9E"));
    painter.setBrush(Qt::NoBrush);
    painter.drawEllipse(width() - 45, 40, 24, 24);

    // Stock breakdown
    int y = 80;
    painter.setFont(QFont("JetBrains Mono", 9));

    painter.setPen(QColor("#E1E2E7"));
    painter.drawText(QRect(20, y, 80, 14), Qt::AlignLeft, "BBCA");
    painter.setPen(QColor("#75FF9E"));
    painter.drawText(QRect(100, y, 80, 14), Qt::AlignRight, "+1.2T");

    y += 18;
    painter.setPen(QColor("#E1E2E7"));
    painter.drawText(QRect(20, y, 80, 14), Qt::AlignLeft, "TLKM");
    painter.setPen(QColor("#FFB3AE"));
    painter.drawText(QRect(100, y, 80, 14), Qt::AlignRight, "-450B");

    y += 18;
    painter.setPen(QColor("#E1E2E7"));
    painter.drawText(QRect(20, y, 80, 14), Qt::AlignLeft, "BMRI");
    painter.setPen(QColor("#75FF9E"));
    painter.drawText(QRect(100, y, 80, 14), Qt::AlignRight, "+890B");
}
