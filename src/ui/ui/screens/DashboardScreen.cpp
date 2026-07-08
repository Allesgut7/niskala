#include "DashboardScreen.h"
#include "../widgets/NavigationBar.h"
#include "../widgets/BreakingNewsTicker.h"
#include "../widgets/MarketIndicesStrip.h"
#include "../widgets/CandlestickChart.h"
#include "../widgets/FearGreedGauge.h"
#include "../widgets/CommodityTable.h"
#include "../widgets/MarketBreadthWidget.h"
#include "../widgets/SectorPerformanceWidget.h"
#include "NewsScreen.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>

DashboardScreen::DashboardScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
}

void DashboardScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);

    // Navigation Bar
    m_navBar = new NavigationBar();
    mainLayout->addWidget(m_navBar);

    // Breaking News Ticker
    m_ticker = new BreakingNewsTicker();
    mainLayout->addWidget(m_ticker);

    // Market Indices Strip
    m_indicesStrip = new MarketIndicesStrip();
    mainLayout->addWidget(m_indicesStrip);

    // Main Content Area (QGridLayout)
    auto *mainContent = new QGridLayout();
    mainContent->setContentsMargins(8, 8, 8, 0);
    mainContent->setSpacing(6);

    // Row 0-4, Col 0-1: CandlestickChart (spans 2 columns)
    m_chart = new CandlestickChart();
    mainContent->addWidget(m_chart, 0, 0, 5, 2);

    // Row 0-1, Col 2: Fear & Greed Index
    auto *fgWidget = new QWidget();
    auto *fgLayout = new QVBoxLayout(fgWidget);
    fgLayout->setContentsMargins(0, 0, 0, 0);
    fgLayout->setSpacing(4);

    auto *fgHeader = new QLabel("FEAR & GREED INDEX");
    fgHeader->setStyleSheet("color: #CEE8FF; font-weight: bold; font-size: 12px;");
    fgLayout->addWidget(fgHeader);

    auto *fgGauges = new QHBoxLayout();
    m_fgIndo = new FearGreedGauge("INDONESIA");
    m_fgIndo->setScore(63);
    m_fgIndo->setDelta(8);
    m_fgAsia = new FearGreedGauge("ASIA");
    m_fgAsia->setScore(55);
    m_fgAsia->setDelta(3);
    m_fgGlobal = new FearGreedGauge("GLOBAL");
    m_fgGlobal->setScore(48);
    m_fgGlobal->setDelta(-2);
    fgGauges->addWidget(m_fgIndo);
    fgGauges->addWidget(m_fgAsia);
    fgGauges->addWidget(m_fgGlobal);
    fgLayout->addLayout(fgGauges);

    mainContent->addWidget(fgWidget, 0, 2, 2, 1);

    // Row 2-4, Col 2: Commodity Table
    m_commodityTable = new CommodityTable();
    mainContent->addWidget(m_commodityTable, 2, 2, 3, 1);

    // Row 5-6, Col 0: News & AI Sentiment
    m_news = new NewsScreen();
    mainContent->addWidget(m_news, 5, 0, 2, 1);

    // Row 5-6, Col 1: Sector Performance
    m_sectorPerf = new SectorPerformanceWidget();
    mainContent->addWidget(m_sectorPerf, 5, 1, 2, 1);

    // Row 5-6, Col 2: Market Breadth
    m_breadth = new MarketBreadthWidget();
    mainContent->addWidget(m_breadth, 5, 2, 2, 1);

    mainContent->setColumnStretch(0, 3);
    mainContent->setColumnStretch(1, 3);
    mainContent->setColumnStretch(2, 4);

    mainLayout->addLayout(mainContent, 1);

    // Bottom Ticker
    auto *bottomTicker = new QWidget();
    bottomTicker->setFixedHeight(32);
    bottomTicker->setStyleSheet("background-color: #060B16; border-top: 1px solid #3B4A3D;");
    auto *btLayout = new QHBoxLayout(bottomTicker);
    btLayout->setContentsMargins(8, 4, 8, 4);

    auto *gainersLabel = new QLabel("TOP GAINERS  1. DCII +24.2%  2. CUAN +16.7%  3. BREN +13.1%  4. BRMS +11.8%  5. ADRO +9.6%");
    gainersLabel->setStyleSheet("color: #75FF9E; font-family: 'JetBrains Mono', monospace; font-size: 10px;");
    btLayout->addWidget(gainersLabel);

    auto *losersLabel = new QLabel("TOP LOSERS  1. BUKA -7.8%  2. EMTK -6.2%  3. SMGR -4.1%  4. INCO -3.8%  5. TLKM -3.2%");
    losersLabel->setStyleSheet("color: #FFB3AE; font-family: 'JetBrains Mono', monospace; font-size: 10px;");
    btLayout->addWidget(losersLabel);

    btLayout->addStretch();

    auto *foreignLabel = new QLabel("FOREIGN FLOW (ALL MARKET)");
    foreignLabel->setStyleSheet("color: #859585; font-family: 'JetBrains Mono', monospace; font-size: 9px;");
    btLayout->addWidget(foreignLabel);

    auto *foreignValue = new QLabel("Net Buy +1.24 T");
    foreignValue->setStyleSheet("color: #75FF9E; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: bold;");
    btLayout->addWidget(foreignValue);

    btLayout->addSpacing(20);

    auto *versionLabel = new QLabel("NISKALA Terminal v1.0.0");
    versionLabel->setStyleSheet("color: #859585; font-family: 'JetBrains Mono', monospace; font-size: 9px;");
    btLayout->addWidget(versionLabel);

    mainLayout->addWidget(bottomTicker);
}
