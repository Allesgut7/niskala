#include "DashboardScreen.h"
#include "../widgets/BreakingNewsTicker.h"
#include "../widgets/MarketIndicesStrip.h"
#include "../widgets/LightweightChartWidget.h"
#include "../widgets/FinancialChart.h"
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
    mainContent->setContentsMargins(12, 4, 12, 12);
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
    m_chart = new LightweightChartWidget();
    leftLayout->addWidget(m_chart, 1);

    // Chart Toolbar connections
    connect(chartToolbar, &ChartToolbarWidget::timeframeChanged,
            this, [this](const QString &tf) {
        m_chart->setTimeframe(tf);
        m_rtTimeframe = tf;
        int candles = 252;
        if (tf == "1m" || tf == "5m" || tf == "15m") candles = 300;
        else if (tf == "1h") candles = 200;
        else if (tf == "D") candles = 252;
        else if (tf == "W") candles = 104;
        else if (tf == "M") candles = 60;
        QString sym = m_chart->symbol().isEmpty() ? "JKSE" : m_chart->symbol();
        m_dataManager->fetchChartData(sym, tf, candles);
    });

    connect(chartToolbar, &ChartToolbarWidget::symbolRequested,
            this, [this](const QString &symbol) {
        if (symbol.trimmed().isEmpty()) return;
        m_chart->loadSymbol(symbol);
        m_dataManager->fetchChartData(symbol, "D", 250);
    });

    connect(m_chart, &LightweightChartWidget::loadMoreData,
            this, [this](const QString &symbol, const QString &direction) {
        qDebug() << "Dashboard: loadMoreData" << symbol << direction;
        if (symbol.trimmed().isEmpty()) {
            qDebug() << "Dashboard: loadMoreData skipped — empty symbol";
            return;
        }
        m_dataManager->fetchChartData(symbol, "D", 100);
    });

    // Chart type switching
    connect(chartToolbar, &ChartToolbarWidget::chartTypeChanged,
            m_chart, &LightweightChartWidget::setChartType);

    // Indicator toggles
    connect(chartToolbar, &ChartToolbarWidget::indicatorToggled,
            m_chart, &LightweightChartWidget::setIndicatorVisible);

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
    fgLayout->setContentsMargins(12, 4, 12, 12);
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
    fgWidget->setMinimumHeight(180);

    // Commodity Table
    auto *commodityWidget = new QWidget();
    commodityWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 6px; }");
    auto *commodityLayout = new QVBoxLayout(commodityWidget);
    commodityLayout->setContentsMargins(12, 10, 12, 12);
    commodityLayout->setSpacing(6);

    m_commodityTable = new CommodityTable();
    commodityLayout->addWidget(m_commodityTable);

    rightLayout->addWidget(commodityWidget);

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
    rightLayout->addWidget(m_aiRegime, 1);

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
    m_gainersLabel = new QLabel("Loading...");
    m_gainersLabel->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(m_gainersLabel);

    btLayout->addStretch();

    // Losers badge
    auto *losersBadge = new QLabel("TOP LOSERS");
    losersBadge->setStyleSheet(
        "QLabel { color: #FFB3AE; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(losersBadge);

    // Losers data (dynamic)
    m_losersLabel = new QLabel("Loading...");
    m_losersLabel->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono', monospace; font-size: 11px;");
    btLayout->addWidget(m_losersLabel);

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
    connect(m_dataManager, &DataManager::topMoversUpdated,
            this, &DashboardScreen::onTopMoversUpdated);
    connect(m_dataManager, &DataManager::newsUpdated,
            this, &DashboardScreen::onNewsUpdated);
    connect(m_dataManager, &DataManager::tradingViewUpdated,
            this, &DashboardScreen::onTradingViewUpdated);
    connect(m_dataManager, &DataManager::realTimeUpdate,
            this, &DashboardScreen::onRealTimeUpdate);

    // Start auto-refresh every 30 seconds
    m_dataManager->startAutoRefresh(120);
    
    // Start real-time stream untuk watchlist + market indices + commodities
    QStringList symbols = m_dataManager->watchlist();
    symbols << "^JKSE" << "^N225" << "^HSI" << "^KS11" 
            << "^GSPC" << "^IXIC" << "USDIDR=X"
            << "GC=F" << "CL=F" << "SI=F" << "NI=F" << "HG=F" << "PL=F" << "NG=F";
    m_dataManager->startRealTimeStream(symbols);
    
    // Fetch initial chart data
    m_chart->loadSymbol("JKSE");
    m_dataManager->fetchChartData("JKSE", "D", 250);
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
        {"SI=F", 2},     // Silver
        {"PL=F", 6},     // Platinum
        {"NI=F", 3},    // Nickel
        {"HG=F", 4},    // Copper
        {"NG=F", 5},    // Natural Gas
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
        QJsonArray emptySteps;
        m_aiRegime->updateData(
            regime["regime"].toString(),
            regime["confidence"].toInt(),
            regime["next1h"].toString(),
            regime["next1h_conf"].toInt(),
            regime["next_day"].toString(),
            regime["next_day_conf"].toInt(),
            regime["analysis"].toString(),
            emptySteps
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
    QString next1hRegime, nextDayRegime;
    int next1hConfidence = 0, nextDayConfidence = 0;
    QJsonArray forecastSteps;
    QString analysis = data["analysis"].toString();

    // NEXT 1H: from intraday_forecast[0] if available, else from forecast.next_regime
    if (data.contains("intraday_forecast")) {
        QJsonArray intraFc = data["intraday_forecast"].toArray();
        if (!intraFc.isEmpty()) {
            QJsonObject ih = intraFc[0].toObject();
            next1hRegime = ih["bias"].toString();
            next1hConfidence = static_cast<int>(ih["confidence"].toDouble());
        }
    }

    if (data.contains("forecast")) {
        QJsonObject forecast = data["forecast"].toObject();
        if (next1hRegime.isEmpty()) {
            next1hRegime = forecast["next_regime"].toString();
            next1hConfidence = forecast["next_confidence"].toInt();
        }
        forecastSteps = forecast["steps"].toArray();
    }

    // NEXT DAY: from forecast steps[0] or current regime
    if (!forecastSteps.isEmpty()) {
        QJsonObject step1 = forecastSteps[0].toObject();
        nextDayRegime = step1["regime"].toString();
        nextDayConfidence = static_cast<int>(step1["probability"].toDouble());
    } else {
        nextDayRegime = data["regime"].toString();
        nextDayConfidence = data["confidence"].toInt();
    }

    // Override + divergence + accuracy + market status
    bool overrideActive = false;
    QString overrideRegime;
    int overrideHours = 0;
    bool divergence = false;
    double acc7d = 0, acc30d = 0, accTotal = 0;
    QString marketStatus = data["market_status"].toString("UNKNOWN");

    if (data.contains("override") && data["override"].isObject()) {
        QJsonObject ov = data["override"].toObject();
        overrideActive = ov["active"].toBool();
        overrideRegime = ov["regime"].toString();
        overrideHours = ov["consecutive_hours"].toInt();
    }

    if (data.contains("divergence")) {
        divergence = data["divergence"].toBool();
    }

    if (data.contains("accuracy")) {
        QJsonObject acc = data["accuracy"].toObject();
        acc7d = acc["7d"].toDouble();
        acc30d = acc["30d"].toDouble();
        accTotal = acc["total"].toDouble();
    }

    m_aiRegime->updateData(
        data["regime"].toString(),
        data["confidence"].toInt(),
        next1hRegime, next1hConfidence,
        nextDayRegime, nextDayConfidence,
        analysis, forecastSteps,
        overrideActive, overrideRegime, overrideHours,
        divergence,
        acc7d, acc30d, accTotal,
        marketStatus
    );
}

void DashboardScreen::onTopMoversUpdated(const QJsonObject &data)
{
    QJsonArray gainers = data["gainers"].toArray();
    QJsonArray losers = data["losers"].toArray();

    QStringList gainersText;
    for (const auto &item : gainers) {
        QJsonObject g = item.toObject();
        QString code = g["Code"].toString();
        if (code.isEmpty()) code = g["code"].toString();
        double pct = g["Percent"].toDouble();
        if (pct == 0) pct = g["ChangePct"].toDouble();
        if (pct == 0) pct = g["changePct"].toDouble();
        gainersText.append(QString("%1 +%2%").arg(code).arg(pct, 0, 'f', 2));
    }

    QStringList losersText;
    for (const auto &item : losers) {
        QJsonObject l = item.toObject();
        QString code = l["Code"].toString();
        if (code.isEmpty()) code = l["code"].toString();
        double pct = l["Percent"].toDouble();
        if (pct == 0) pct = l["ChangePct"].toDouble();
        if (pct == 0) pct = l["changePct"].toDouble();
        losersText.append(QString("%1 %2%").arg(code).arg(pct, 0, 'f', 2));
    }

    if (!gainersText.isEmpty()) {
        m_gainersLabel->setText(gainersText.join("  |  "));
    }
    if (!losersText.isEmpty()) {
        m_losersLabel->setText(losersText.join("  |  "));
    }
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
    
    // Hide drawing toolbar on dashboard — only shown in ChartScreen
    m_chart->setDrawingToolbarVisible(false);

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
    
    m_chart->loadData(ohlcData);
}

void DashboardScreen::onRealTimeUpdate(const QString &symbol, const QJsonObject &data)
{
    // Route commodity symbols to CommodityTable
    static const QStringList commodities = {"GC=F", "CL=F", "SI=F", "NI=F", "HG=F", "PL=F", "NG=F"};
    if (commodities.contains(symbol) && data.contains("price")) {
        m_commodityTable->updateBySymbol(symbol,
            data["price"].toDouble(),
            data["change"].toDouble(),
            data["changePct"].toDouble());
        return;
    }
    
    // Update market indices with real-time price
    if (data.contains("price")) {
        m_indicesStrip->updateData(symbol, 
            data["price"].toDouble(),
            data["change"].toDouble(),
            data["changePct"].toDouble());
    }
    
    // Update chart with real-time candle (TradingView-style OHLC)
    if (m_chart && data.contains("price")) {
        double price = data["price"].toDouble();
        int ts = data.contains("timestamp") ? data["timestamp"].toInt() : 0;
        int vol = data.contains("volume") ? data["volume"].toInt() : 0;

        if (ts <= 0 || price <= 0) return;

        // Round timestamp ke timeframe interval
        int ts_rounded = ts;
        if (m_rtTimeframe == "1m")       ts_rounded = ts - (ts % 60);
        else if (m_rtTimeframe == "5m")  ts_rounded = ts - (ts % 300);
        else if (m_rtTimeframe == "15m") ts_rounded = ts - (ts % 900);
        else if (m_rtTimeframe == "1h")  ts_rounded = ts - (ts % 3600);

        // Reset session jika symbol BERUBAH atau time slot BERUBAH
        if (symbol != m_rtSymbol || ts_rounded != m_rtLastSlot) {
            m_rtSymbol = symbol;
            m_rtLastSlot = ts_rounded;
            m_rtSessionOpen = price;
            m_rtSessionHigh = price;
            m_rtSessionLow = price;
        } else {
            // Update high/low dalam candle yang sama
            if (price > m_rtSessionHigh) m_rtSessionHigh = price;
            if (price < m_rtSessionLow || m_rtSessionLow <= 0) m_rtSessionLow = price;
        }

        OHLCData candle;
        candle.open = m_rtSessionOpen;
        candle.high = m_rtSessionHigh;
        candle.low = m_rtSessionLow;
        candle.close = price;
        candle.volume = vol;
        candle.timestamp = ts_rounded;

        m_chart->addRealTimeCandle(candle);
    }
}
