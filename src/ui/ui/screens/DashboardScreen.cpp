#include "DashboardScreen.h"
#include "../widgets/BreakingNewsTicker.h"
#include "../widgets/MarketIndicesStrip.h"
#include "../widgets/CandlestickChart.h"
#include "../widgets/ChartToolbarWidget.h"
#include "../widgets/FearGreedGauge.h"
#include "../widgets/CommodityTable.h"
#include "../widgets/MarketBreadthWidget.h"
#include "../widgets/AIMarketRegimeWidget.h"
#include "../widgets/SectorPerformanceWidget.h"
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

    // Chart Toolbar connections
    connect(chartToolbar, &ChartToolbarWidget::timeframeChanged,
            this, [this](const QString &tf) {
        m_chart->setTimeframe(tf);
        // Request chart data from TradingView
        m_dataManager->fetchChartData("IHSG INDEX", tf, 50);
    });

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
    m_fgIndo->setScore(0);
    m_fgIndo->setDelta(0);
    m_fgAsia = new FearGreedGauge("Asia");
    m_fgAsia->setScore(0);
    m_fgAsia->setDelta(0);
    m_fgGlobal = new FearGreedGauge("Global");
    m_fgGlobal->setScore(0);
    m_fgGlobal->setDelta(0);
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
    m_aiRegime = new AIMarketRegimeWidget();
    rightLayout->addWidget(m_aiRegime);

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

    // Gainers data (dynamic - will be updated by data)
    auto *gainersData = new QLabel("Loading...");
    gainersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(gainersData);

    btLayout->addStretch();

    // Losers badge
    auto *losersBadge = new QLabel("TOP LOSERS");
    losersBadge->setStyleSheet(
        "QLabel { color: #FFB3AE; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(losersBadge);

    // Losers data (dynamic)
    auto *losersData = new QLabel("Loading...");
    losersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(losersData);

    mainLayout->addWidget(bottomTicker);

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
    connect(m_dataManager, &DataManager::marketBreadthUpdated,
            this, &DashboardScreen::onMarketBreadthUpdated);
    connect(m_dataManager, &DataManager::sectorPerformanceUpdated,
            this, &DashboardScreen::onSectorPerformanceUpdated);
    connect(m_dataManager, &DataManager::aiRegimeUpdated,
            this, &DashboardScreen::onAIRegimeUpdated);
    connect(m_dataManager, &DataManager::newsUpdated,
            this, &DashboardScreen::onNewsUpdated);
    connect(m_dataManager, &DataManager::tradingViewUpdated,
            this, &DashboardScreen::onTradingViewUpdated);
    connect(m_dataManager, &DataManager::realTimeUpdate,
            this, &DashboardScreen::onRealTimeUpdate);

    // Start auto-refresh every 30 seconds
    m_dataManager->startAutoRefresh(30);
    
    // Start real-time stream untuk watchlist + market indices
    QStringList symbols = m_dataManager->watchlist();
    symbols << "^JKSE" << "^N225" << "^HSI" << "^KS11" 
            << "^GSPC" << "^IXIC" << "USDIDR=X";
    m_dataManager->startRealTimeStream(symbols);
    
    // Fetch initial chart data
    m_dataManager->fetchChartData("IHSG INDEX", "D", 50);
}

void DashboardScreen::onWatchlistUpdated(const QJsonObject &data)
{
    qDebug() << "DashboardScreen: onWatchlistUpdated, keys:" << data.keys();
    
    // Handle single symbol update (from real-time)
    if (data.contains("symbol") && data.contains("price")) {
        QString symbol = data["symbol"].toString();
        qDebug() << "DashboardScreen: Updating index" << symbol << "price:" << data["price"];
        m_indicesStrip->updateData(symbol,
            data["price"].toDouble(),
            data["change"].toDouble(),
            data["changePct"].toDouble());
    }
    
    // Handle batch update (from refreshWatchlist)
    if (data.contains("indices")) {
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
}

void DashboardScreen::onMarketOverviewUpdated(const QJsonObject &data)
{
    QString symbol = data["symbol"].toString();
    
    // Map Yahoo Finance symbols ke row index
    QMap<QString, int> symbolToRow = {
        {"GC=F", 0},    // Gold
        {"CL=F", 1},    // Crude Oil
        {"MTXF=F", 2},  // Coal
        {"NI=F", 3},    // Nickel
        {"HG=F", 4},    // Copper
        {"NG=F", 6}     // Natural Gas
    };
    
    if (symbolToRow.contains(symbol)) {
        int row = symbolToRow[symbol];
        m_commodityTable->updateData(row,
            data["price"].toDouble(),
            data["change"].toDouble(),
            data["changePct"].toDouble());
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
            regime["confidence"].toInt()
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

void DashboardScreen::onMarketBreadthUpdated(const QJsonObject &data)
{
    m_breadth->updateData(
        data["naik"].toInt(),
        data["turun"].toInt(),
        data["stagnan"].toInt()
    );
}

void DashboardScreen::onSectorPerformanceUpdated(const QJsonObject &data)
{
    qDebug() << "DashboardScreen: onSectorPerformanceUpdated called, keys:" << data.keys();
    QJsonArray sectors = data["sectors"].toArray();
    qDebug() << "DashboardScreen: Sectors count:" << sectors.size();
    m_sectorPerf->updateData(sectors);
}

void DashboardScreen::onAIRegimeUpdated(const QJsonObject &data)
{
    m_aiRegime->updateData(
        data["regime"].toString(),
        data["confidence"].toInt()
    );
}

void DashboardScreen::onNewsUpdated(const QJsonArray &data)
{
    QStringList headlines;
    for (const auto &item : data) {
        QJsonObject obj = item.toObject();
        headlines.append(obj["title"].toString());
    }
    if (!headlines.isEmpty()) {
        m_ticker->updateHeadlines(headlines);
    }
}

void DashboardScreen::onTradingViewUpdated(const QJsonArray &data)
{
    if (data.isEmpty() || !m_chart) return;
    
    QVector<OHLCData> ohlcData;
    for (const auto &item : data) {
        QJsonObject obj = item.toObject();
        OHLCData candle;
        candle.open = obj["open"].toDouble();
        candle.high = obj["high"].toDouble();
        candle.low = obj["low"].toDouble();
        candle.close = obj["close"].toDouble();
        candle.volume = obj["volume"].toInt();
        candle.timestamp = obj["timestamp"].toInt();
        ohlcData.append(candle);
    }
    
    m_chart->loadOHLCVData(ohlcData);
}

void DashboardScreen::onRealTimeUpdate(const QString &symbol, const QJsonObject &data)
{
    // Update market indices with real-time price
    if (data.contains("price")) {
        m_indicesStrip->updateData(symbol, 
            data["price"].toDouble(),
            data["change"].toDouble(),
            data["changePct"].toDouble());
    }
    
    // Update chart with new candle data (top-level keys)
    if (m_chart && data.contains("open") && data.contains("close")) {
        OHLCData candle;
        candle.open = data["open"].toDouble();
        candle.high = data["high"].toDouble();
        candle.low = data["low"].toDouble();
        candle.close = data["close"].toDouble();
        candle.volume = data["volume"].toInt();
        candle.timestamp = data["timestamp"].toInt();
        m_chart->addRealTimeCandle(candle);
    }
}
