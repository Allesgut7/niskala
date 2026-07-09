#include "SectorPerformanceWidget.h"
#include <QPainter>
#include <QJsonArray>
#include <QJsonObject>

SectorPerformanceWidget::SectorPerformanceWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(250);
    // No hardcoded data - widget starts empty and gets data from API
}

void SectorPerformanceWidget::updateData(const QJsonArray &sectors)
{
    m_sectors.clear();
    for (const auto &item : sectors) {
        QJsonObject obj = item.toObject();
        m_sectors.append({obj["name"].toString(), obj["changePct"].toDouble()});
    }
    update();
}

void SectorPerformanceWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Header
    painter.setPen(QColor("#CEE8FF"));
    painter.setFont(QFont("monospace", 11, QFont::Bold));
    painter.drawText(QRect(8, 4, width() - 16, 20), Qt::AlignLeft, "SECTOR PERFORMANCE (IHSG)");

    // Timeframe selector
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(QRect(width() - 50, 4, 40, 20), Qt::AlignRight, "1D ▾");

    int startY = 30;
    int rowHeight = 20;
    int maxBarWidth = width() - 200;

    double maxPct = 0;
    for (const auto &s : m_sectors) {
        maxPct = qMax(maxPct, qAbs(s.changePct));
    }

    for (int i = 0; i < m_sectors.size(); ++i) {
        int y = startY + i * rowHeight;
        const auto &sector = m_sectors[i];

        // Rank
        painter.setPen(QColor("#BACBB9"));
        painter.setFont(QFont("monospace", 9));
        painter.drawText(QRect(8, y, 20, rowHeight), Qt::AlignLeft | Qt::AlignVCenter,
                         QString::number(i + 1) + ".");

        // Name
        painter.setPen(QColor("#E1E2E7"));
        painter.drawText(QRect(30, y, 140, rowHeight), Qt::AlignLeft | Qt::AlignVCenter,
                         sector.name);

        // Bar
        int barX = 175;
        int barWidth = static_cast<int>((sector.changePct / maxPct) * maxBarWidth / 2);
        QColor barColor = sector.changePct >= 0 ? QColor("#75FF9E") : QColor("#FFB3AE");

        if (sector.changePct >= 0) {
            painter.setBrush(barColor);
            painter.setPen(Qt::NoPen);
            painter.drawRoundedRect(barX, y + 4, barWidth, rowHeight - 8, 2, 2);
        } else {
            int negBarX = barX + maxBarWidth / 2 - qAbs(barWidth);
            painter.setBrush(barColor);
            painter.setPen(Qt::NoPen);
            painter.drawRoundedRect(negBarX, y + 4, qAbs(barWidth), rowHeight - 8, 2, 2);
        }

        // Percentage
        painter.setPen(barColor);
        painter.setFont(QFont("monospace", 9, QFont::Bold));
        QString pctStr = (sector.changePct >= 0 ? "+" : "") +
                         QString::number(sector.changePct, 'f', 2) + "%";
        painter.drawText(QRect(barX + maxBarWidth / 2 + 10, y, 60, rowHeight),
                         Qt::AlignLeft | Qt::AlignVCenter, pctStr);
    }
}
