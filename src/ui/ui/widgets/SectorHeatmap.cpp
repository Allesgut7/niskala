#include "SectorHeatmap.h"
#include <QPainter>
#include <QPainterPath>
#include <QMouseEvent>

SectorHeatmap::SectorHeatmap(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(150);
    populateSampleData();
}

void SectorHeatmap::populateSampleData()
{
    m_sectors = {
        {"FIN", "Finance", 2.1},
        {"BSC", "Basic Cycles", -0.5},
        {"CON", "Consumer", 1.3},
        {"IND", "Industrial", 0.8},
        {"HEA", "Healthcare", -1.2},
        {"TEC", "Technology", 3.4},
        {"ENE", "Energy", 0.2},
        {"PRO", "Properties", -0.3},
        {"TRA", "Transport", 1.7}
    };
}

void SectorHeatmap::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#1D2023"));

    int cols = 3;
    int rows = 3;
    int cellW = (width() - 20) / cols;
    int cellH = (height() - 40) / rows;
    int offsetX = 10;
    int offsetY = 5;

    // Title
    painter.setPen(QColor("#FFB4AB"));
    painter.setFont(QFont("monospace", 10, QFont::Bold));
    painter.drawText(QRect(0, 0, width(), 20), Qt::AlignCenter, "SECTOR HEATMAP");

    for (int i = 0; i < m_sectors.size() && i < 9; ++i) {
        int row = i / cols;
        int col = i % cols;

        int x = offsetX + col * cellW;
        int y = offsetY + 25 + row * cellH;

        QRect cellRect(x + 2, y + 2, cellW - 4, cellH - 4);

        // Cell background
        QColor bgColor = getHeatColor(m_sectors[i].changePct);
        bgColor.setAlpha(180);
        painter.setBrush(bgColor);
        painter.setPen(QPen(QColor("#323538"), 1));
        painter.drawRoundedRect(cellRect, 4, 4);

        // Sector code
        painter.setPen(QColor("#ffffff"));
        painter.setFont(QFont("monospace", 11, QFont::Bold));
        painter.drawText(QRect(x + 2, y + 8, cellW - 4, 20), Qt::AlignCenter,
                         m_sectors[i].code);

        // Change percentage
        QString pctStr = (m_sectors[i].changePct >= 0 ? "+" : "") +
                         QString::number(m_sectors[i].changePct, 'f', 1) + "%";
        painter.setPen(m_sectors[i].changePct >= 0 ? QColor("#ffffff") : QColor("#ffffff"));
        painter.setFont(QFont("monospace", 10));
        painter.drawText(QRect(x + 2, y + 28, cellW - 4, 20), Qt::AlignCenter, pctStr);
    }
}

void SectorHeatmap::updateData(const QList<SectorData> &sectors)
{
    m_sectors = sectors;
    update();
}

QColor SectorHeatmap::getHeatColor(double pct) const
{
    if (pct >= 2.0) return QColor("#00d989");
    if (pct >= 1.0) return QColor("#00a676");
    if (pct >= 0.0) return QColor("#323538");
    if (pct >= -1.0) return QColor("#5c3d2e");
    return QColor("#8b2500");
}
