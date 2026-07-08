#include "DashboardScreen.h"
#include "../widgets/NavigationBar.h"
#include "../widgets/BreakingNewsTicker.h"
#include "../widgets/MarketIndicesStrip.h"
#include "../widgets/CandlestickChart.h"
#include "../widgets/ChartToolbarWidget.h"
#include "../widgets/FearGreedGauge.h"
#include "../widgets/CommodityTable.h"
#include "../widgets/MarketBreadthWidget.h"
#include "../widgets/AIMarketRegimeWidget.h"
#include "../widgets/SectorPerformanceWidget.h"
#include "../widgets/FooterWidget.h"
#include "../core/DataManager.h"
#include "NewsScreen.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QScrollArea>
#include <QLabel>
#include <QJsonArray>
#include <QJsonObject>

DashboardScreen::DashboardScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
}

void DashboardScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(12, 12, 12, 12);
    mainLayout->setSpacing(0);

    // === Navigation Bar ===
    m_navBar = new NavigationBar();
    mainLayout->addWidget(m_navBar);

    // === Breaking News Ticker ===
    m_ticker = new BreakingNewsTicker();
    mainLayout->addWidget(m_ticker);

    // === Market Indices Strip ===
    m_indicesStrip = new MarketIndicesStrip();
    mainLayout->addWidget(m_indicesStrip);

    // === Main Content (70% left + 30% right) ===
    auto *mainContent = new QHBoxLayout();
    mainContent->setContentsMargins(12, 12, 12, 12);
    mainContent->setSpacing(12);

    // --- Left Panel (70%) ---
    auto *leftPanel = new QWidget();
    leftPanel->setStyleSheet("background-color: transparent;");
    auto *leftLayout = new QVBoxLayout(leftPanel);
    leftLayout->setContentsMargins(12, 12, 12, 12);
    leftLayout->setSpacing(8);

    // Chart Toolbar
    auto *chartToolbar = new ChartToolbarWidget();
    leftLayout->addWidget(chartToolbar);

    // Candlestick Chart (flex)
    m_chart = new CandlestickChart();
    leftLayout->addWidget(m_chart, 1);

    // News + Sector Performance (bottom row)
    auto *bottomRow = new QHBoxLayout();
    bottomRow->setSpacing(8);

    m_news = new NewsScreen();
    bottomRow->addWidget(m_news, 1);

    m_sectorPerf = new SectorPerformanceWidget();
    bottomRow->addWidget(m_sectorPerf, 1);

    leftLayout->addLayout(bottomRow);

    mainContent->addWidget(leftPanel, 7);

    // --- Right Panel (30%) with Scroll ---
    auto *rightScroll = new QScrollArea();
    rightScroll->setWidgetResizable(true);
    rightScroll->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    rightScroll->setFrameShape(QFrame::NoFrame);
    rightScroll->setStyleSheet("QScrollArea { background-color: transparent; border: none; }");
    rightScroll->setMinimumWidth(280);

    auto *rightWidget = new QWidget();
    rightWidget->setStyleSheet("background-color: transparent;");
    auto *rightLayout = new QVBoxLayout(rightWidget);
    rightLayout->setContentsMargins(12, 12, 12, 12);
    rightLayout->setSpacing(8);

    // Fear & Greed Index
    auto *fgWidget = new QWidget();
    fgWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 6px; }");
    auto *fgLayout = new QVBoxLayout(fgWidget);
    fgLayout->setContentsMargins(12, 10, 12, 12);
    fgLayout->setSpacing(6);

    auto *fgGauges = new QHBoxLayout();
    fgGauges->setSpacing(4);
    m_fgIndo = new FearGreedGauge("Indonesia");
    m_fgIndo->setScore(63);
    m_fgIndo->setDelta(8);
    m_fgAsia = new FearGreedGauge("Asia");
    m_fgAsia->setScore(55);
    m_fgAsia->setDelta(3);
    m_fgGlobal = new FearGreedGauge("Global");
    m_fgGlobal->setScore(48);
    m_fgGlobal->setDelta(-2);
    fgGauges->addWidget(m_fgIndo);
    fgGauges->addWidget(m_fgAsia);
    fgGauges->addWidget(m_fgGlobal);
    fgLayout->addLayout(fgGauges);

    rightLayout->addWidget(fgWidget);

    // Commodity Table
    auto *commodityWidget = new QWidget();
    commodityWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 6px; }");
    auto *commodityLayout = new QVBoxLayout(commodityWidget);
    commodityLayout->setContentsMargins(12, 10, 12, 12);
    commodityLayout->setSpacing(6);

    m_commodityTable = new CommodityTable();
    commodityLayout->addWidget(m_commodityTable);

    rightLayout->addWidget(commodityWidget, 1);

    // Market Breadth
    auto *breadthWidget = new QWidget();
    breadthWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 6px; }");
    auto *breadthLayout = new QVBoxLayout(breadthWidget);
    breadthLayout->setContentsMargins(12, 10, 12, 12);
    breadthLayout->setSpacing(6);

    m_breadth = new MarketBreadthWidget();
    breadthLayout->addWidget(m_breadth);

    rightLayout->addWidget(breadthWidget);

    // AI Market Regime
    auto *aiWidget = new AIMarketRegimeWidget();
    rightLayout->addWidget(aiWidget);

    rightLayout->addStretch();

    rightScroll->setWidget(rightWidget);
    mainContent->addWidget(rightScroll, 3);

    mainLayout->addLayout(mainContent, 1);

    // === Bottom Ticker ===
    auto *bottomTicker = new QWidget();
    bottomTicker->setFixedHeight(44);
    bottomTicker->setStyleSheet(
        "QWidget { background-color: #272A2E; border-top: 1px solid #3B4A3D; }");
    auto *btLayout = new QHBoxLayout(bottomTicker);
    btLayout->setContentsMargins(12, 6, 12, 6);
    btLayout->setSpacing(12);

    // Gainers badge
    auto *gainersBadge = new QLabel("TOP GAINERS");
    gainersBadge->setStyleSheet(
        "QLabel { background-color: rgba(117,255,158,0.1); color: #75FF9E; "
        "padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(gainersBadge);

    // Gainers data
    auto *gainersData = new QLabel("DCII +24.2%  CUAN +16.7%  BREN +13.1%  BRMS +11.8%  ADRO +9.6%");
    gainersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(gainersData);

    btLayout->addStretch();

    // Losers badge
    auto *losersBadge = new QLabel("TOP LOSERS");
    losersBadge->setStyleSheet(
        "QLabel { color: #FFB3AE; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(losersBadge);

    // Losers data
    auto *losersData = new QLabel("BUKA -7.8%  EMTK -6.2%  SMGR -4.1%  INCO -3.8%  TLKM -3.2%");
    losersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(losersData);

    mainLayout->addWidget(bottomTicker);

    // === Footer ===
    auto *footer = new FooterWidget();
    mainLayout->addWidget(footer);

    // === Data Manager Integration ===
    setupDataManager();
}

void DashboardScreen::setupDataManager()
{
    m_dataManager = new DataManager(this);

    // Connect DataManager signals to widget updates
    connect(m_dataManager, &DataManager::watchlistUpdated,
            this, &DashboardScreen::onWatchlistUpdated);
    connect(m_dataManager, &DataManager::marketOverviewUpdated,
            this, &DashboardScreen::onMarketOverviewUpdated);
    connect(m_dataManager, &DataManager::fearGreedUpdated,
            this, &DashboardScreen::onFearGreedUpdated);
    connect(m_dataManager, &DataManager::sentimentUpdated,
            this, &DashboardScreen::onSentimentUpdated);

    // Start auto-refresh every 30 seconds
    m_dataManager->startAutoRefresh(30);
}

void DashboardScreen::onWatchlistUpdated(const QJsonObject &data)
{
    QJsonArray indices = data["indices"].toArray();
    for (const auto &item : indices) {
        QJsonObject obj = item.toObject();
        m_indicesStrip->updateData(
            obj["name"].toString(),
            obj["value"].toDouble(),
            obj["change"].toDouble(),
            obj["changePct"].toDouble()
        );
    }
}

void DashboardScreen::onMarketOverviewUpdated(const QJsonObject &data)
{
    QJsonArray commodities = data["commodities"].toArray();
    for (int i = 0; i < commodities.size() && i < 7; ++i) {
        QJsonObject obj = commodities[i].toObject();
        m_commodityTable->updateData(
            i,
            obj["price"].toDouble(),
            obj["change"].toDouble(),
            obj["changePct"].toDouble()
        );
    }
}

void DashboardScreen::onFearGreedUpdated(const QJsonObject &data)
{
    if (data.contains("indo")) {
        QJsonObject indo = data["indo"].toObject();
        m_fgIndo->setScore(indo["score"].toInt());
        m_fgIndo->setDelta(indo["delta"].toInt());
    }
    if (data.contains("asia")) {
        QJsonObject asia = data["asia"].toObject();
        m_fgAsia->setScore(asia["score"].toInt());
        m_fgAsia->setDelta(asia["delta"].toInt());
    }
    if (data.contains("global")) {
        QJsonObject global = data["global"].toObject();
        m_fgGlobal->setScore(global["score"].toInt());
        m_fgGlobal->setDelta(global["delta"].toInt());
    }
    if (data.contains("breadth")) {
        QJsonObject breadth = data["breadth"].toObject();
        m_breadth->updateData(
            breadth["naik"].toInt(),
            breadth["turun"].toInt(),
            breadth["stagnan"].toInt()
        );
    }
    if (data.contains("regime")) {
        QJsonObject regime = data["regime"].toObject();
        m_aiRegime->updateData(
            regime["regime"].toString(),
            regime["confidence"].toInt(),
            regime["analysis"].toString()
        );
    }
}

void DashboardScreen::onSentimentUpdated(const QString &symbol, const QJsonObject &data)
{
    // Update news sentiment for specific symbol
    Q_UNUSED(symbol);
    Q_UNUSED(data);
    // NewsScreen handles its own data
}
