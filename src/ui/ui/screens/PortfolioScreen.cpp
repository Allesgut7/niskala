#include "PortfolioScreen.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QGroupBox>

PortfolioScreen::PortfolioScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateSampleData();
}

void PortfolioScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(8);

    // Title
    auto *title = new QLabel("PORTFOLIO");
    title->setStyleSheet("color: #e94560; font-size: 16px; font-weight: bold;");
    mainLayout->addWidget(title);

    // Summary cards
    auto *summaryLayout = new QHBoxLayout();
    summaryLayout->setSpacing(8);

    auto createCard = [](const QString &label, const QString &value, const QString &color) -> QWidget * {
        auto *card = new QWidget();
        card->setStyleSheet(QString(
            "QWidget { background-color: #16213e; border: 1px solid #0f3460; border-radius: 6px; padding: 8px; }"
        ));
        auto *layout = new QVBoxLayout(card);
        layout->setContentsMargins(12, 8, 12, 8);

        auto *lbl = new QLabel(label);
        lbl->setStyleSheet("color: #888888; font-size: 10px;");
        layout->addWidget(lbl);

        auto *val = new QLabel(value);
        val->setStyleSheet(QString("color: %1; font-size: 18px; font-weight: bold;").arg(color));
        layout->addWidget(val);

        return card;
    };

    m_balanceLabel = new QLabel("Rp 150,000,000");
    m_investedLabel = new QLabel("Rp 85,000,000");
    m_unrealizedLabel = new QLabel("+Rp 12,500,000");
    m_realizedLabel = new QLabel("+Rp 3,200,000");

    summaryLayout->addWidget(createCard("BALANCE", "Rp 150,000,000", "#e0e0e0"));
    summaryLayout->addWidget(createCard("INVESTED", "Rp 85,000,000", "#00bcd4"));
    summaryLayout->addWidget(createCard("UNREALIZED P&L", "+Rp 12,500,000", "#00d989"));
    summaryLayout->addWidget(createCard("REALIZED P&L", "+Rp 3,200,000", "#ffc107"));

    mainLayout->addLayout(summaryLayout);

    // Positions table
    auto *posLabel = new QLabel("OPEN POSITIONS");
    posLabel->setStyleSheet("color: #00d989; font-weight: bold; font-size: 12px;");
    mainLayout->addWidget(posLabel);

    m_positionsTable = new QTableWidget(0, 7);
    m_positionsTable->setHorizontalHeaderLabels(
        {"Symbol", "Qty", "Avg Price", "Current", "P&L", "P&L %", "Value"});
    m_positionsTable->horizontalHeader()->setSectionResizeMode(0, QHeaderView::ResizeToContents);
    m_positionsTable->horizontalHeader()->setSectionResizeMode(4, QHeaderView::Stretch);
    m_positionsTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_positionsTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_positionsTable->setAlternatingRowColors(true);
    m_positionsTable->verticalHeader()->setVisible(false);
    m_positionsTable->setStyleSheet(
        "QTableWidget { background-color: #1a1a2e; alternate-background-color: #16213e; }");
    mainLayout->addWidget(m_positionsTable);

    // Recent trades
    auto *tradesLabel = new QLabel("RECENT TRADES");
    tradesLabel->setStyleSheet("color: #ffc107; font-weight: bold; font-size: 12px;");
    mainLayout->addWidget(tradesLabel);

    m_tradesTable = new QTableWidget(0, 6);
    m_tradesTable->setHorizontalHeaderLabels(
        {"Date", "Symbol", "Side", "Qty", "Price", "P&L"});
    m_tradesTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_tradesTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_tradesTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_tradesTable->setAlternatingRowColors(true);
    m_tradesTable->verticalHeader()->setVisible(false);
    m_tradesTable->setStyleSheet(
        "QTableWidget { background-color: #1a1a2e; alternate-background-color: #16213e; }");
    m_tradesTable->setMaximumHeight(150);
    mainLayout->addWidget(m_tradesTable);
}

void PortfolioScreen::populateSampleData()
{
    // Positions
    QList<Position> positions = {
        {"BBCA", 500, 8800, 9200, 200000, 4.55, 4600000},
        {"BBRI", 1000, 4900, 4800, -100000, -2.04, 4800000},
        {"BMRI", 300, 5800, 6150, 105000, 6.03, 1845000},
        {"TLKM", 400, 2700, 2850, 60000, 5.56, 1140000},
        {"GOTO", 5000, 90, 85, -25000, -5.56, 425000},
    };

    m_positionsTable->setRowCount(positions.size());
    for (int i = 0; i < positions.size(); ++i) {
        const auto &p = positions[i];
        m_positionsTable->setItem(i, 0, new QTableWidgetItem(p.symbol));
        m_positionsTable->setItem(i, 1, new QTableWidgetItem(QString::number(p.quantity)));

        auto *avgItem = new QTableWidgetItem(QString::number(p.avgPrice, 'f', 0));
        avgItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_positionsTable->setItem(i, 2, avgItem);

        auto *curItem = new QTableWidgetItem(QString::number(p.currentPrice, 'f', 0));
        curItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_positionsTable->setItem(i, 3, curItem);

        QString pnlStr = (p.unrealizedPnl >= 0 ? "+" : "") +
                         QString::number(p.unrealizedPnl, 'f', 0);
        auto *pnlItem = new QTableWidgetItem(pnlStr);
        pnlItem->setForeground(p.unrealizedPnl >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        pnlItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_positionsTable->setItem(i, 4, pnlItem);

        QString pctStr = (p.unrealizedPnlPct >= 0 ? "+" : "") +
                         QString::number(p.unrealizedPnlPct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(p.unrealizedPnlPct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        pctItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_positionsTable->setItem(i, 5, pctItem);

        auto *valItem = new QTableWidgetItem(
            "Rp " + QString::number((int)p.value));
        valItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_positionsTable->setItem(i, 6, valItem);
    }

    // Recent trades
    QList<Trade> trades = {
        {"2026-07-06", "BBCA", "BUY", 200, 8900, 0},
        {"2026-07-05", "BBRI", "SELL", 500, 4950, 25000},
        {"2026-07-04", "GOTO", "BUY", 2000, 88, 0},
        {"2026-07-03", "BMRI", "BUY", 300, 5800, 0},
        {"2026-07-02", "TLKM", "SELL", 100, 2800, 10000},
    };

    m_tradesTable->setRowCount(trades.size());
    for (int i = 0; i < trades.size(); ++i) {
        const auto &t = trades[i];
        m_tradesTable->setItem(i, 0, new QTableWidgetItem(t.date));
        m_tradesTable->setItem(i, 1, new QTableWidgetItem(t.symbol));

        auto *sideItem = new QTableWidgetItem(t.side);
        sideItem->setForeground(t.side == "BUY" ? QColor("#00d989") : QColor("#ff4757"));
        m_tradesTable->setItem(i, 2, sideItem);

        m_tradesTable->setItem(i, 3, new QTableWidgetItem(QString::number(t.quantity)));
        m_tradesTable->setItem(i, 4, new QTableWidgetItem(QString::number(t.price)));

        QString pnlStr = t.pnl != 0 ?
            ((t.pnl >= 0 ? "+" : "") + QString::number(t.pnl, 'f', 0)) : "-";
        auto *pnlItem = new QTableWidgetItem(pnlStr);
        if (t.pnl > 0) pnlItem->setForeground(QColor("#00d989"));
        else if (t.pnl < 0) pnlItem->setForeground(QColor("#ff4757"));
        m_tradesTable->setItem(i, 5, pnlItem);
    }
}
