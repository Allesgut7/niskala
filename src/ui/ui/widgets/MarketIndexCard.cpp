#include "MarketIndexCard.h"
#include <cmath>

MarketIndexCard::MarketIndexCard(const QString &name, double value, double change,
                                 double changePct, QWidget *parent)
    : QWidget(parent), m_name(name), m_value(value), m_change(change), m_changePct(changePct)
{
    setMinimumSize(140, 80);
    setMaximumHeight(80);
}

void MarketIndexCard::updateData(double value, double change, double changePct)
{
    m_value = value;
    m_change = change;
    m_changePct = changePct;
    update();
}

void MarketIndexCard::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#111417"));
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.drawRect(rect().adjusted(0, 0, -1, -1));

    // Name
    painter.setPen(QColor("#BACBB9"));
    painter.setFont(QFont("monospace", 9));
    QRect nameRect(8, 6, width() - 16, 16);
    painter.drawText(nameRect, Qt::AlignLeft | Qt::AlignVCenter, m_name);

    // Value
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("monospace", 14, QFont::Bold));
    QRect valueRect(8, 22, width() - 16, 22);
    QString valueStr = QString::number(m_value, 'f', 2);
    painter.drawText(valueRect, Qt::AlignLeft | Qt::AlignVCenter, valueStr);

    // Change
    QColor changeColor = m_change >= 0 ? QColor("#75FF9E") : QColor("#FFB3AE");
    painter.setPen(changeColor);
    painter.setFont(QFont("monospace", 10));

    QString changeStr = (m_change >= 0 ? "+" : "") + QString::number(m_change, 'f', 2);
    QString pctStr = (m_changePct >= 0 ? "+" : "") + QString::number(m_changePct, 'f', 2) + "%";
    QRect changeRect(8, 46, width() - 16, 16);
    painter.drawText(changeRect, Qt::AlignLeft | Qt::AlignVCenter, changeStr + "  " + pctStr);

    // Mini sparkline chart (simple)
    int chartX = width() - 50;
    int chartY = 10;
    int chartW = 40;
    int chartH = 30;

    QList<double> points;
    double base = m_value * 0.99;
    for (int i = 0; i < 10; ++i) {
        points.append(base + (rand() % 100 - 50));
    }

    QPainterPath path;
    for (int i = 0; i < points.size(); ++i) {
        int x = chartX + (i * chartW / (points.size() - 1));
        int y = chartY + chartH - ((points[i] - *std::min_element(points.begin(), points.end())) /
                (*std::max_element(points.begin(), points.end()) - *std::min_element(points.begin(), points.end()) + 1) * chartH);
        if (i == 0) path.moveTo(x, y);
        else path.lineTo(x, y);
    }

    painter.setPen(QPen(changeColor, 1.5));
    painter.drawPath(path);
}
