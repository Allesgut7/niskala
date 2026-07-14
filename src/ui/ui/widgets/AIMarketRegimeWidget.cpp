#include "AIMarketRegimeWidget.h"

AIMarketRegimeWidget::AIMarketRegimeWidget(QWidget *parent)
    : QWidget(parent)
{
    setMinimumHeight(140);
    setMaximumHeight(180);
}

void AIMarketRegimeWidget::updateData(const QString &regime, int confidence,
                                       const QString &next1hRegime, int next1hConfidence,
                                       const QString &nextDayRegime, int nextDayConfidence,
                                       const QString &analysis, const QJsonArray &forecastSteps,
                                       bool overrideActive,
                                       const QString &overrideRegime,
                                       int overrideHours,
                                       bool divergence,
                                       double acc7d, double acc30d, double accTotal,
                                       const QString &marketStatus)
{
    m_regime = regime;
    m_confidence = confidence;
    m_next1hRegime = next1hRegime;
    m_next1hConfidence = next1hConfidence;
    m_nextDayRegime = nextDayRegime;
    m_nextDayConfidence = nextDayConfidence;
    m_analysis = analysis;
    m_forecastSteps = forecastSteps;
    m_overrideActive = overrideActive;
    m_overrideRegime = overrideRegime;
    m_overrideHours = overrideHours;
    m_divergence = divergence;
    m_acc7d = acc7d;
    m_acc30d = acc30d;
    m_accTotal = accTotal;
    m_marketStatus = marketStatus;
    update();
}

static QColor colorForRegime(const QString &regime)
{
    if (regime.contains("BULL")) return QColor("#75FF9E");
    if (regime.contains("BEAR")) return QColor("#FFB3AE");
    return QColor("#859585");
}

static QString arrowForRegime(const QString &regime)
{
    if (regime.contains("BULL")) return "\u25B2";  // ▲
    if (regime.contains("BEAR")) return "\u25BC";  // ▼
    return "\u25C6";  // ◆
}

void AIMarketRegimeWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Background
    painter.fillRect(rect(), QColor("#060B16"));
    painter.setPen(QPen(QColor("#75FF9E"), 1));
    painter.setBrush(Qt::NoBrush);
    painter.drawRoundedRect(rect().adjusted(0, 0, -1, -1), 4, 4);

    int y = 12;
    int colW = (width() - 16) / 3;

    // ========== ROW 1: 3 COLUMNS ==========

    // --- COL 1: Current Regime ---
    int cx = 8;

    // Market status badge
    QColor statusBg;
    QString statusText;
    if (m_marketStatus == "OPEN") {
        statusBg = QColor("#75FF9E");
        statusText = "LIVE";
    } else if (m_marketStatus == "CLOSED_HOURS") {
        statusBg = QColor("#FFD700");
        statusText = "CLOSED";
    } else if (m_marketStatus == "CLOSED_WEEKEND") {
        statusBg = QColor("#859585");
        statusText = "WEEKEND";
    } else {
        statusBg = QColor("#859585");
        statusText = "UNKNOWN";
    }

    QRect statusRect(cx + 4, y, 54, 18);
    painter.setPen(Qt::NoPen);
    painter.setBrush(statusBg);
    painter.drawRoundedRect(statusRect, 3, 3);
    painter.setPen(QColor("#060B16"));
    painter.setFont(QFont("Inter", 8, QFont::Bold));
    painter.drawText(statusRect, Qt::AlignCenter, statusText);

    // Override badge (only during OPEN market)
    if (m_overrideActive && m_marketStatus == "OPEN") {
        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor("#FFD700"));
        QRect ovRect(cx + 62, y, 60, 18);
        painter.drawRoundedRect(ovRect, 3, 3);
        painter.setPen(QColor("#1A1A1A"));
        painter.setFont(QFont("JetBrains Mono", 7, QFont::Bold));
        painter.drawText(ovRect, Qt::AlignCenter, "\u26A0 OVERRIDE");
    } else if (m_divergence && m_marketStatus == "OPEN") {
        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor("#FFB3AE"));
        QRect dvRect(cx + 62, y, 40, 18);
        painter.drawRoundedRect(dvRect, 3, 3);
        painter.setPen(QColor("#1A1A1A"));
        painter.setFont(QFont("Inter", 7, QFont::Bold));
        painter.drawText(dvRect, Qt::AlignCenter, "DIVERGE");
    }

    // "REGIME" label
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 8));
    painter.drawText(QRect(cx + 58, y, colW, 18), Qt::AlignVCenter, "REGIME");

    // Regime name
    painter.setPen(QColor("#E1E2E7"));
    painter.setFont(QFont("Inter", 14, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 24, colW, 22), Qt::AlignLeft, m_regime);

    // Confidence
    QColor confColor = m_confidence >= 70 ? QColor("#75FF9E") :
                       m_confidence >= 50 ? QColor("#CEE8FF") : QColor("#859585");
    painter.setPen(confColor);
    painter.setFont(QFont("JetBrains Mono", 12, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 48, colW, 18), Qt::AlignLeft,
                     QString::number(m_confidence) + "%");

    // --- COL 2: Next 1h ---
    cx = 8 + colW + 4;

    // "NEXT 1H" label
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 8));
    painter.drawText(QRect(cx + 4, y, colW, 18), Qt::AlignLeft, "NEXT 1H");

    // Arrow + Regime
    QColor nc = colorForRegime(m_next1hRegime);
    painter.setPen(nc);
    painter.setFont(QFont("Inter", 12, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 24, 24, 22), Qt::AlignCenter, arrowForRegime(m_next1hRegime));
    painter.drawText(QRect(cx + 28, y + 24, colW - 28, 22), Qt::AlignVCenter, m_next1hRegime);

    // Confidence
    QColor nc1 = m_next1hConfidence >= 70 ? QColor("#75FF9E") :
                 m_next1hConfidence >= 50 ? QColor("#CEE8FF") : QColor("#859585");
    painter.setPen(nc1);
    painter.setFont(QFont("JetBrains Mono", 12, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 48, colW, 18), Qt::AlignLeft,
                     QString::number(m_next1hConfidence) + "%");

    // --- COL 3: Next Day ---
    cx = 8 + colW * 2 + 8;

    // "NEXT DAY" label
    painter.setPen(QColor("#859585"));
    painter.setFont(QFont("Inter", 8));
    painter.drawText(QRect(cx + 4, y, colW, 18), Qt::AlignLeft, "NEXT DAY");

    // Arrow + Regime
    QColor nd = colorForRegime(m_nextDayRegime);
    painter.setPen(nd);
    painter.setFont(QFont("Inter", 12, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 24, 24, 22), Qt::AlignCenter, arrowForRegime(m_nextDayRegime));
    painter.drawText(QRect(cx + 28, y + 24, colW - 28, 22), Qt::AlignVCenter, m_nextDayRegime);

    // Confidence
    QColor ndc = m_nextDayConfidence >= 70 ? QColor("#75FF9E") :
                 m_nextDayConfidence >= 50 ? QColor("#CEE8FF") : QColor("#859585");
    painter.setPen(ndc);
    painter.setFont(QFont("JetBrains Mono", 12, QFont::Bold));
    painter.drawText(QRect(cx + 4, y + 48, colW, 18), Qt::AlignLeft,
                     QString::number(m_nextDayConfidence) + "%");

    // ========== ROW 2: ANALYSIS + FORECAST ==========

    y = 82;

    // Separator
    painter.setPen(QPen(QColor("#3B4A3D"), 1));
    painter.drawLine(8, y, width() - 8, y);
    y += 8;

    // Analysis text
    if (!m_analysis.isEmpty()) {
        painter.setPen(QColor("#BACBB9"));
        painter.setFont(QFont("Inter", 9));
        QRect ar(12, y, width() - 24, 30);
        painter.drawText(ar, Qt::AlignLeft | Qt::TextWordWrap, m_analysis);
        y += painter.boundingRect(ar, Qt::AlignLeft | Qt::TextWordWrap, m_analysis).height() + 4;
    }

    // Forecast bars (skip index 0 = next day, show day 2+)
    if (!m_forecastSteps.isEmpty()) {
        painter.setPen(QColor("#859585"));
        painter.setFont(QFont("Inter", 8));
        painter.drawText(QRect(12, y, 100, 16), Qt::AlignLeft, "Forecast:");

        int barX = 80;
        for (int i = 1; i < m_forecastSteps.size() && i <= 5; ++i) {
            QJsonObject step = m_forecastSteps[i].toObject();
            QString regime = step["regime"].toString();
            double prob = step["probability"].toDouble();

            QColor fc = colorForRegime(regime);
            painter.setPen(fc);
            painter.setFont(QFont("JetBrains Mono", 8, QFont::Bold));
            painter.drawText(QRect(barX, y, 16, 16), Qt::AlignCenter, arrowForRegime(regime));

            painter.setFont(QFont("Inter", 8));
            painter.drawText(QRect(barX + 16, y, 60, 16), Qt::AlignLeft,
                             regime + " " + QString::number(prob, 'f', 0) + "%");

            barX += 120;
        }
        y += 18;
    }

    // Accuracy stats
    if (m_accTotal > 0) {
        painter.setPen(QColor("#859585"));
        painter.setFont(QFont("Inter", 8));
        QString accText = QString("Accuracy: 7d %1% | 30d %2% | All %3%")
            .arg(m_acc7d, 0, 'f', 0)
            .arg(m_acc30d, 0, 'f', 0)
            .arg(m_accTotal, 0, 'f', 0);
        painter.drawText(QRect(8, y, width() - 16, 14), Qt::AlignLeft, accText);
    }
}
