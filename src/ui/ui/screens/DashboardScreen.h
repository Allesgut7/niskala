#pragma once

#include <QWidget>

class NavigationBar;
class BreakingNewsTicker;
class MarketIndicesStrip;
class CandlestickChart;
class FearGreedGauge;
class CommodityTable;
class MarketBreadthWidget;
class NewsScreen;
class SectorPerformanceWidget;

class DashboardScreen : public QWidget
{
    Q_OBJECT

public:
    explicit DashboardScreen(QWidget *parent = nullptr);

private:
    void setupUI();

    NavigationBar *m_navBar = nullptr;
    BreakingNewsTicker *m_ticker = nullptr;
    MarketIndicesStrip *m_indicesStrip = nullptr;
    CandlestickChart *m_chart = nullptr;
    FearGreedGauge *m_fgIndo = nullptr;
    FearGreedGauge *m_fgAsia = nullptr;
    FearGreedGauge *m_fgGlobal = nullptr;
    CommodityTable *m_commodityTable = nullptr;
    MarketBreadthWidget *m_breadth = nullptr;
    NewsScreen *m_news = nullptr;
    SectorPerformanceWidget *m_sectorPerf = nullptr;
};
