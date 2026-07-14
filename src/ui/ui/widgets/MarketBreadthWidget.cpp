#include "MarketBreadthWidget.h"
#include <QPainterPath>
#include <cmath>

MarketBreadthWidget::MarketBreadthWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumSize(200, 150);
    setupData();
}

void MarketBreadthWidget::setupData()
{
    m_total = m_naik + m_turun + m_stagnan;
}

void MarketBreadthWidget::updateData(int naik, int turun, int stagnan)
{
    m_naik = naik;
    m_turun = turun;
    m_stagnan = stagnan;
    m_total = m_naik + m_turun + m_stagnan;
    update();
}

void MarketBreadthWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Header
    painter.setPen(QColor("#CEE8FF"));
    painter.setFont(QFont("monospace", 11, QFont::Bold));
    painter.drawText(QRect(8, 4, width() - 16, 20), Qt::AlignLeft, "MARKET BREADTH (IHSG)");

    // Semi-circle gauge (shifted left for more room on right)
    int centerX = static_cast<int>(width() * 0.35);
    int centerY = 103;
    int radius = 55;

    // Background arc
    painter.setPen(QPen(QColor("#3B4A3D"), 12, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, 180 * 16);

    // Naik (green) - 57.1%
    double naikAngle = 180.0 * (m_naik / (double)m_total);
    painter.setPen(QPen(QColor("#75FF9E"), 12, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    0, static_cast<int>(naikAngle * 16));

    // Turun (red) - 33.1%
    double turunAngle = 180.0 * (m_turun / (double)m_total);
    painter.setPen(QPen(QColor("#FFB3AE"), 12, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    static_cast<int>(naikAngle * 16), static_cast<int>(turunAngle * 16));

    // Stagnan (gray) - 9.8%
    double stagnanAngle = 180.0 * (m_stagnan / (double)m_total);
    painter.setPen(QPen(QColor("#859585"), 12, Qt::SolidLine, Qt::RoundCap));
    painter.drawArc(centerX - radius, centerY - radius, radius * 2, radius * 2,
                    static_cast<int>((naikAngle + turunAngle) * 16), static_cast<int>(stagnanAngle * 16));

    // Stats on right - 3 separate columns
    int statsX = static_cast<int>(width() * 0.6);
    int statsY = 48;

    // Naik
    painter.setPen(QColor("#75FF9E"));
    painter.setFont(QFont("monospace", 12, QFont::Bold));
    painter.drawText(QRect(statsX, statsY, 35, 20), Qt::AlignRight, QString::number(m_naik));
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(QRect(statsX + 40, statsY, 50, 20), Qt::AlignLeft, "Naik");
    painter.drawText(QRect(statsX + 95, statsY, 50, 20), Qt::AlignRight,
                     QString::number(m_naik * 100.0 / m_total, 'f', 1) + "%");

    // Turun
    statsY += 28;
    painter.setPen(QColor("#FFB3AE"));
    painter.setFont(QFont("monospace", 12, QFont::Bold));
    painter.drawText(QRect(statsX, statsY, 35, 20), Qt::AlignRight, QString::number(m_turun));
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(QRect(statsX + 40, statsY, 50, 20), Qt::AlignLeft, "Turun");
    painter.drawText(QRect(statsX + 95, statsY, 50, 20), Qt::AlignRight,
                     QString::number(m_turun * 100.0 / m_total, 'f', 1) + "%");

    // Stagnan
    statsY += 28;
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("monospace", 12, QFont::Bold));
    painter.drawText(QRect(statsX, statsY, 35, 20), Qt::AlignRight, QString::number(m_stagnan));
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("monospace", 9));
    painter.drawText(QRect(statsX + 40, statsY, 50, 20), Qt::AlignLeft, "Stagnan");
    painter.drawText(QRect(statsX + 95, statsY, 50, 20), Qt::AlignRight,
                     QString::number(m_stagnan * 100.0 / m_total, 'f', 1) + "%");

    // Total
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("monospace", 10));
    painter.drawText(QRect(centerX - 60, centerY + 10, 120, 20), Qt::AlignCenter,
                     "Total Saham " + QString::number(m_total));
}
