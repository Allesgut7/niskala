#include "FooterWidget.h"
#include <QPainter>
#include <QDateTime>

FooterWidget::FooterWidget(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(28);

    // Timer untuk update datetime setiap detik
    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &FooterWidget::updateDateTime);
    m_timer->start(1000);

    updateDateTime();
}

void FooterWidget::setVersion(const QString &version)
{
    m_version = version;
    update();
}

void FooterWidget::setConnectionStatus(const QString &status)
{
    m_connectionStatus = status;
    update();
}

void FooterWidget::updateDateTime()
{
    QDateTime now = QDateTime::currentDateTime();
    // GMT+7 (WIB)
    now.setTimeSpec(Qt::LocalTime);
    // Format: "Senin, 08 Jul 2026 08:24:15 WIB"
    m_currentTime = now.toString("dddd, dd MMM yyyy HH:mm:ss") + " WIB";
    update();
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

    // Left: NISKALA version
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 9));
    QString leftText = "NISKALA " + m_version;
    painter.drawText(QRect(16, 0, 200, height()), Qt::AlignVCenter, leftText);

    // Center: Connection status
    QColor connColor = (m_connectionStatus == "Connected") ? QColor("#75FF9E") : QColor("#FFB3AE");
    painter.setPen(connColor);
    painter.setFont(QFont("JetBrains Mono", 9));
    QString connText = "● " + m_connectionStatus;
    painter.drawText(QRect(width()/2 - 80, 0, 160, height()), Qt::AlignVCenter, connText);

    // Right: DateTime + DYOR
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("JetBrains Mono", 9));
    QString rightText = m_currentTime + "  |  Do Your Own Research!";
    painter.drawText(QRect(width() - 550, 0, 534, height()), Qt::AlignVCenter | Qt::AlignRight, rightText);
}
