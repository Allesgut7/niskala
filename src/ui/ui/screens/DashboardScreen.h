#pragma once

#include <QWidget>

class BreakingNewsTicker;
class MarketIndicesStrip;
class CandlestickChart;
class FearGreedGauge;
class CommodityTable;
class MarketBreadthWidget;
class AIMarketRegimeWidget;
class NewsScreen;
class SectorPerformanceWidget;
class DataManager;

class DashboardScreen : public QWidget
{
    Q_OBJECT

public:
    explicit DashboardScreen(QWidget *parent = nullptr);

signals:
    void screenChanged(int index);

private slots:
    void onWatchlistUpdated(const QJsonObject &data);
    void onMarketOverviewUpdated(const QJsonObject &data);
    void onFearGreedUpdated(const QJsonObject &data);
    void onSentimentUpdated(const QString &symbol, const QJsonObject &data);
    void onMarketBreadthUpdated(const QJsonObject &data);
    void onSectorPerformanceUpdated(const QJsonObject &data);
    void onAIRegimeUpdated(const QJsonObject &data);
    void onNewsUpdated(const QJsonArray &data);
    void onRealTimeUpdate(const QString &symbol, const QJsonObject &data);

private:
    void setupUI();
    void setupDataManager();

    BreakingNewsTicker *m_ticker = nullptr;
    MarketIndicesStrip *m_indicesStrip = nullptr;
    CandlestickChart *m_chart = nullptr;
    FearGreedGauge *m_fgIndo = nullptr;
    FearGreedGauge *m_fgAsia = nullptr;
    FearGreedGauge *m_fgGlobal = nullptr;
    CommodityTable *m_commodityTable = nullptr;
    MarketBreadthWidget *m_breadth = nullptr;
    AIMarketRegimeWidget *m_aiRegime = nullptr;
    NewsScreen *m_news = nullptr;
    SectorPerformanceWidget *m_sectorPerf = nullptr;
    DataManager *m_dataManager = nullptr;
};
