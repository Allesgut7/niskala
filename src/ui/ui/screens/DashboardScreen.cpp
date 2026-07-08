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
#include "../widgets/ForeignFlowWidget.h"
#include "../widgets/SectorPerformanceWidget.h"
#include "../widgets/FooterWidget.h"
#include "NewsScreen.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QScrollArea>
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

    // === Navigation Bar (64px) ===
    m_navBar = new NavigationBar();
    mainLayout->addWidget(m_navBar);

    // === Breaking News Ticker (36px) ===
    m_ticker = new BreakingNewsTicker();
    mainLayout->addWidget(m_ticker);

    // === Market Indices Strip (100px) ===
    m_indicesStrip = new MarketIndicesStrip();
    mainLayout->addWidget(m_indicesStrip);

    // === Main Content (70% left + 30% right) ===
    auto *mainContent = new QHBoxLayout();
    mainContent->setContentsMargins(8, 8, 8, 0);
    mainContent->setSpacing(8);

    // --- Left Panel (70%) ---
    auto *leftPanel = new QWidget();
    auto *leftLayout = new QVBoxLayout(leftPanel);
    leftLayout->setContentsMargins(0, 0, 0, 0);
    leftLayout->setSpacing(6);

    // Chart Toolbar
    auto *chartToolbar = new ChartToolbarWidget();
    leftLayout->addWidget(chartToolbar);

    // Candlestick Chart (flex)
    m_chart = new CandlestickChart();
    leftLayout->addWidget(m_chart, 1);

    // News + Sector Performance (bottom row)
    auto *bottomRow = new QHBoxLayout();
    bottomRow->setSpacing(6);

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

    auto *rightWidget = new QWidget();
    auto *rightLayout = new QVBoxLayout(rightWidget);
    rightLayout->setContentsMargins(0, 0, 0, 0);
    rightLayout->setSpacing(6);

    // Fear & Greed Index
    auto *fgWidget = new QWidget();
    fgWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 4px; }");
    auto *fgLayout = new QVBoxLayout(fgWidget);
    fgLayout->setContentsMargins(8, 8, 8, 8);
    fgLayout->setSpacing(4);

    auto *fgHeader = new QLabel("[ FEAR & GREED INDEX ]");
    fgHeader->setStyleSheet("color: #CEE8FF; font-family: 'Inter'; font-size: 11px; font-weight: bold;");
    fgLayout->addWidget(fgHeader);

    auto *fgGauges = new QHBoxLayout();
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
    commodityWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 4px; }");
    auto *commodityLayout = new QVBoxLayout(commodityWidget);
    commodityLayout->setContentsMargins(8, 8, 8, 8);

    auto *commodityHeader = new QLabel("[ COMMODITY MONITOR ]");
    commodityHeader->setStyleSheet("color: #CEE8FF; font-family: 'Inter'; font-size: 11px; font-weight: bold;");
    commodityLayout->addWidget(commodityHeader);

    m_commodityTable = new CommodityTable();
    commodityLayout->addWidget(m_commodityTable);

    rightLayout->addWidget(commodityWidget);

    // Market Breadth
    auto *breadthWidget = new QWidget();
    breadthWidget->setStyleSheet("QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 4px; }");
    auto *breadthLayout = new QVBoxLayout(breadthWidget);
    breadthLayout->setContentsMargins(8, 8, 8, 8);

    auto *breadthHeader = new QLabel("[ MARKET BREADTH ]");
    breadthHeader->setStyleSheet("color: #CEE8FF; font-family: 'Inter'; font-size: 11px; font-weight: bold;");
    breadthLayout->addWidget(breadthHeader);

    m_breadth = new MarketBreadthWidget();
    breadthLayout->addWidget(m_breadth);

    rightLayout->addWidget(breadthWidget);

    // AI Market Regime
    auto *aiWidget = new AIMarketRegimeWidget();
    rightLayout->addWidget(aiWidget);

    // Foreign Flow
    auto *flowWidget = new ForeignFlowWidget();
    rightLayout->addWidget(flowWidget);

    rightLayout->addStretch();

    rightScroll->setWidget(rightWidget);
    mainContent->addWidget(rightScroll, 3);

    mainLayout->addLayout(mainContent, 1);

    // === Bottom Ticker (40px floating) ===
    auto *bottomTicker = new QWidget();
    bottomTicker->setFixedHeight(40);
    bottomTicker->setStyleSheet(
        "QWidget { background-color: #272A2E; border-top: 1px solid #3B4A3D; }");
    auto *btLayout = new QHBoxLayout(bottomTicker);
    btLayout->setContentsMargins(8, 4, 8, 4);

    // Gainers badge
    auto *gainersBadge = new QLabel("🚀 TOP GAINERS");
    gainersBadge->setStyleSheet(
        "QLabel { background-color: rgba(117,255,158,0.1); color: #75FF9E; "
        "padding: 2px 8px; border-radius: 4px; font-family: 'Inter'; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(gainersBadge);

    // Gainers data
    auto *gainersData = new QLabel("DCII +24.2%  CUAN +16.7%  BREN +13.1%  BRMS +11.8%  ADRO +9.6%");
    gainersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono'; font-size: 10px;");
    btLayout->addWidget(gainersData);

    // Separator
    auto *sep = new QFrame();
    sep->setFrameShape(QFrame::VLine);
    sep->setStyleSheet("color: #3B4A3D;");
    sep->setFixedHeight(20);
    btLayout->addWidget(sep);

    // Losers badge
    auto *losersBadge = new QLabel("TOP LOSERS");
    losersBadge->setStyleSheet(
        "QLabel { color: #FFB3AE; font-family: 'Inter'; font-size: 10px; font-weight: bold; }");
    btLayout->addWidget(losersBadge);

    // Losers data
    auto *losersData = new QLabel("BUKA -7.8%  EMTK -6.2%  SMGR -4.1%  INCO -3.8%  TLKM -3.2%");
    losersData->setStyleSheet("color: #E1E2E7; font-family: 'JetBrains Mono'; font-size: 10px;");
    btLayout->addWidget(losersData);

    btLayout->addStretch();

    mainLayout->addWidget(bottomTicker);

    // === Footer (24px) ===
    auto *footer = new FooterWidget();
    mainLayout->addWidget(footer);
}
