#include "DashboardScreen.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QHeaderView>

DashboardScreen::DashboardScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateSampleData();
}

void DashboardScreen::setupUI()
{
    auto *mainLayout = new QHBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(4);

    // Left: Stock Table
    auto *leftPanel = new QWidget();
    auto *leftLayout = new QVBoxLayout(leftPanel);
    leftLayout->setContentsMargins(4, 4, 4, 4);

    m_stockTable = new QTableWidget();
    setupStockTable();
    leftLayout->addWidget(m_stockTable);

    // Right: News + Gainers/Losers
    auto *rightPanel = new QWidget();
    auto *rightLayout = new QVBoxLayout(rightPanel);
    rightLayout->setContentsMargins(4, 4, 4, 4);

    auto *newsLabel = new QLabel("NEWS & SENTIMENT");
    newsLabel->setStyleSheet("color: #e94560; font-weight: bold; font-size: 13px;");
    rightLayout->addWidget(newsLabel);

    m_newsList = new QListWidget();
    setupNewsFeed();
    rightLayout->addWidget(m_newsList);

    auto *glLabel = new QLabel("TOP GAINERS / LOSERS");
    glLabel->setStyleSheet("color: #00bcd4; font-weight: bold; font-size: 11px; margin-top: 8px;");
    rightLayout->addWidget(glLabel);

    auto *glWidget = new QWidget();
    auto *glLayout = new QHBoxLayout(glWidget);
    glLayout->setContentsMargins(0, 0, 0, 0);

    m_gainersLabel = new QLabel();
    m_gainersLabel->setStyleSheet("color: #00d989;");
    m_gainersLabel->setWordWrap(true);
    glLayout->addWidget(m_gainersLabel);

    m_losersLabel = new QLabel();
    m_losersLabel->setStyleSheet("color: #ff4757;");
    m_losersLabel->setWordWrap(true);
    glLayout->addWidget(m_losersLabel);

    rightLayout->addWidget(glWidget);

    mainLayout->addWidget(leftPanel, 3);
    mainLayout->addWidget(rightPanel, 2);
}

void DashboardScreen::setupStockTable()
{
    m_stockTable->setColumnCount(7);
    m_stockTable->setHorizontalHeaderLabels(
        {"Symbol", "Price", "Change", "Chg%", "Volume", "High", "Low"});

    m_stockTable->horizontalHeader()->setSectionResizeMode(0, QHeaderView::ResizeToContents);
    m_stockTable->horizontalHeader()->setSectionResizeMode(1, QHeaderView::ResizeToContents);
    m_stockTable->horizontalHeader()->setSectionResizeMode(2, QHeaderView::ResizeToContents);
    m_stockTable->horizontalHeader()->setSectionResizeMode(3, QHeaderView::ResizeToContents);
    m_stockTable->horizontalHeader()->setSectionResizeMode(4, QHeaderView::Stretch);
    m_stockTable->horizontalHeader()->setSectionResizeMode(5, QHeaderView::ResizeToContents);
    m_stockTable->horizontalHeader()->setSectionResizeMode(6, QHeaderView::ResizeToContents);

    m_stockTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_stockTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_stockTable->setAlternatingRowColors(true);
    m_stockTable->verticalHeader()->setVisible(false);
    m_stockTable->setShowGrid(false);
    m_stockTable->setFocusPolicy(Qt::NoFocus);
}

void DashboardScreen::setupNewsFeed()
{
    m_newsList->setAlternatingRowColors(true);
}

void DashboardScreen::populateSampleData()
{
    struct StockData {
        QString symbol;
        double price;
        double change;
        double changePct;
        QString volume;
        double high;
        double low;
    };

    QList<StockData> stocks = {
        {"BBCA", 9200, 150, 1.66, "45.2M", 9250, 9050},
        {"BBRI", 4800, -50, -1.03, "38.7M", 4850, 4780},
        {"BMRI", 6150, 75, 1.23, "28.3M", 6200, 6075},
        {"TLKM", 2850, 25, 0.88, "22.1M", 2870, 2825},
        {"GOTO", 85, -2, -2.30, "156.8M", 87, 84},
        {"ADRO", 1520, 30, 2.01, "18.5M", 1535, 1490},
        {"UNVR", 4250, -75, -1.73, "12.4M", 4325, 4225},
        {"ICBP", 11200, 200, 1.82, "8.9M", 11250, 11000},
        {"ASII", 5400, 50, 0.93, "15.6M", 5425, 5350},
        {"PGAS", 1890, 10, 0.53, "25.3M", 1900, 1880},
    };

    m_stockTable->setRowCount(stocks.size());

    for (int i = 0; i < stocks.size(); ++i) {
        const auto &s = stocks[i];

        auto *symbolItem = new QTableWidgetItem(s.symbol);
        symbolItem->setFont(QFont("monospace", 11, QFont::Bold));
        m_stockTable->setItem(i, 0, symbolItem);

        auto *priceItem = new QTableWidgetItem(
            QString::number(s.price, 'f', 0));
        priceItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 1, priceItem);

        QString chgStr = (s.change >= 0 ? "+" : "") + QString::number(s.change, 'f', 0);
        auto *chgItem = new QTableWidgetItem(chgStr);
        chgItem->setForeground(s.change >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        chgItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 2, chgItem);

        QString pctStr = (s.changePct >= 0 ? "+" : "") + QString::number(s.changePct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(s.changePct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        pctItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 3, pctItem);

        auto *volItem = new QTableWidgetItem(s.volume);
        volItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 4, volItem);

        auto *highItem = new QTableWidgetItem(
            QString::number(s.high, 'f', 0));
        highItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 5, highItem);

        auto *lowItem = new QTableWidgetItem(
            QString::number(s.low, 'f', 0));
        lowItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_stockTable->setItem(i, 6, lowItem);
    }

    // News
    m_newsList->addItem("[CNBC]  BBRI: Laba bersih Q3 naik 15% YoY ke Rp 13.2T");
    m_newsList->addItem("[IDX]   TLKM: Dividen final Rp 200/saham, ex-date 15 Jul");
    m_newsList->addItem("[Kontan] GOTO: Revenue Q3 tembus Rp 7T, pertumbuhan 25%");
    m_newsList->addItem("[Bisnis] BMRI: Target profit growth 12% di FY2026");
    m_newsList->addItem("[Reuters] ADRO: Coal prices rebound, outlook improved");

    // Gainers/Losers
    m_gainersLabel->setText("ICBP +1.82%\nADRO +2.01%\nBBCA +1.66%");
    m_losersLabel->setText("GOTO -2.30%\nUNVR -1.73%\nBBRI -1.03%");
}
