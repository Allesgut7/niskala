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
#include <QSplitter>
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

    // Main Content Area (Chart + Right Panel)
    auto *contentWidget = new QWidget();
    auto *contentLayout = new QHBoxLayout(contentWidget);
    contentLayout->setContentsMargins(8, 8, 8, 0);
    contentLayout->setSpacing(8);

    // Left: Chart
    auto *chartWidget = new QWidget();
    auto *chartLayout = new QVBoxLayout(chartWidget);
    chartLayout->setContentsMargins(0, 0, 0, 0);

    m_chart = new CandlestickChart();
    chartLayout->addWidget(m_chart);

    contentLayout->addWidget(chartWidget, 6);

    // Right Panel
    auto *rightPanel = new QWidget();
    auto *rightLayout = new QVBoxLayout(rightPanel);
    rightLayout->setContentsMargins(0, 0, 0, 0);
    rightLayout->setSpacing(6);

    // Fear & Greed Index
    auto *fgHeader = new QLabel("FEAR & GREED INDEX");
    fgHeader->setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 12px;");
    rightLayout->addWidget(fgHeader);

    auto *fgLayout = new QHBoxLayout();
    m_fgIndo = new FearGreedGauge("INDONESIA");
    m_fgIndo->setScore(63);
    m_fgIndo->setDelta(8);
    m_fgAsia = new FearGreedGauge("ASIA");
    m_fgAsia->setScore(55);
    m_fgAsia->setDelta(3);
    m_fgGlobal = new FearGreedGauge("GLOBAL");
    m_fgGlobal->setScore(48);
    m_fgGlobal->setDelta(-2);
    fgLayout->addWidget(m_fgIndo);
    fgLayout->addWidget(m_fgAsia);
    fgLayout->addWidget(m_fgGlobal);
    rightLayout->addLayout(fgLayout);

    // Commodity Table
    m_commodityTable = new CommodityTable();
    rightLayout->addWidget(m_commodityTable);

    // Market Breadth
    m_breadth = new MarketBreadthWidget();
    rightLayout->addWidget(m_breadth);

    contentLayout->addWidget(rightPanel, 4);

    mainLayout->addWidget(contentWidget, 1);

    // Bottom Section (News + Sector Performance)
    auto *bottomWidget = new QWidget();
    auto *bottomLayout = new QHBoxLayout(bottomWidget);
    bottomLayout->setContentsMargins(8, 4, 8, 4);
    bottomLayout->setSpacing(8);

    // News
    m_news = new NewsScreen();
    bottomLayout->addWidget(m_news, 5);

    // Sector Performance
    m_sectorPerf = new SectorPerformanceWidget();
    bottomLayout->addWidget(m_sectorPerf, 5);

    mainLayout->addWidget(bottomWidget, 1);

    // Bottom Ticker
    auto *bottomTicker = new QWidget();
    bottomTicker->setFixedHeight(32);
    bottomTicker->setStyleSheet("background-color: #0a0e17; border-top: 1px solid #1f2937;");
    auto *btLayout = new QHBoxLayout(bottomTicker);
    btLayout->setContentsMargins(8, 4, 8, 4);

    auto *gainersLabel = new QLabel("TOP GAINERS  1. DCII +24.2%  2. CUAN +16.7%  3. BREN +13.1%  4. BRMS +11.8%  5. ADRO +9.6%");
    gainersLabel->setStyleSheet("color: #10b981; font-family: monospace; font-size: 10px;");
    btLayout->addWidget(gainersLabel);

    auto *losersLabel = new QLabel("TOP LOSERS  1. BUKA -7.8%  2. EMTK -6.2%  3. SMGR -4.1%  4. INCO -3.8%  5. TLKM -3.2%");
    losersLabel->setStyleSheet("color: #ef4444; font-family: monospace; font-size: 10px;");
    btLayout->addWidget(losersLabel);

    btLayout->addStretch();

    auto *foreignLabel = new QLabel("FOREIGN FLOW (ALL MARKET)");
    foreignLabel->setStyleSheet("color: #9ca3af; font-family: monospace; font-size: 9px;");
    btLayout->addWidget(foreignLabel);

    auto *foreignValue = new QLabel("Net Buy +1.24 T");
    foreignValue->setStyleSheet("color: #10b981; font-family: monospace; font-size: 10px; font-weight: bold;");
    btLayout->addWidget(foreignValue);

    btLayout->addSpacing(20);

    auto *versionLabel = new QLabel("NISKALA Terminal v1.0.0");
    versionLabel->setStyleSheet("color: #6b7280; font-family: monospace; font-size: 9px;");
    btLayout->addWidget(versionLabel);

    mainLayout->addWidget(bottomTicker);
}
