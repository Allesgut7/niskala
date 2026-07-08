#include "DataManager.h"
#include "PythonBridge.h"

DataManager::DataManager(QObject *parent)
    : QObject(parent)
{
    m_bridge = new PythonBridge(this);
    m_refreshTimer = new QTimer(this);

    connect(m_refreshTimer, &QTimer::timeout, this, &DataManager::onAutoRefresh);
    connect(m_bridge, &PythonBridge::marketDataReceived,
            this, &DataManager::onMarketDataReceived);
    connect(m_bridge, &PythonBridge::fearGreedReceived,
            this, &DataManager::onFearGreedReceived);
    connect(m_bridge, &PythonBridge::marketBreadthReceived,
            this, [this](const QJsonObject &data) {
        emit marketBreadthUpdated(data);
    });
    connect(m_bridge, &PythonBridge::sectorPerformanceReceived,
            this, [this](const QJsonArray &data) {
        QJsonObject obj;
        obj["sectors"] = data;
        emit sectorPerformanceUpdated(obj);
    });
    connect(m_bridge, &PythonBridge::aiRegimeReceived,
            this, [this](const QJsonObject &data) {
        emit aiRegimeUpdated(data);
    });
    connect(m_bridge, &PythonBridge::commandError,
            this, &DataManager::onCommandError);

    m_watchlist = {"BBCA", "BBRI", "BMRI", "TLKM", "GOTO", "ADRO", "UNVR", "ICBP"};
}

void DataManager::startAutoRefresh(int intervalSec)
{
    m_refreshTimer->start(intervalSec * 1000);
}

void DataManager::stopAutoRefresh()
{
    m_refreshTimer->stop();
}

void DataManager::refreshAll()
{
    emit refreshStarted();
    m_refreshing = true;

    refreshWatchlist();
    refreshFearGreedIndex();
    refreshMarketBreadth();
    refreshSectorPerformance();
    refreshAIRegime();
}

void DataManager::refreshWatchlist()
{
    for (const auto &symbol : m_watchlist) {
        m_bridge->fetchMarketData(symbol);
    }
}

void DataManager::refreshMarketOverview()
{
    m_bridge->fetchMarketData("^JKSE"); // IHSG
    m_bridge->fetchMarketData("GC=F");  // Gold
    m_bridge->fetchMarketData("CL=F");  // Crude Oil
    m_bridge->fetchMarketData("USDIDR=X"); // USD/IDR
}

void DataManager::refreshFearGreedIndex()
{
    m_bridge->fetchFearGreedIndex();
}

void DataManager::refreshMarketBreadth()
{
    m_bridge->fetchMarketBreadth();
}

void DataManager::refreshSectorPerformance()
{
    m_bridge->fetchSectorPerformance();
}

void DataManager::refreshAIRegime()
{
    m_bridge->fetchAIRegime();
}

void DataManager::onAutoRefresh()
{
    refreshAll();
}

void DataManager::onMarketDataReceived(const QJsonObject &data)
{
    QString symbol = data["symbol"].toString();
    emit watchlistUpdated(data);
    m_refreshing = false;
    emit refreshFinished();
}

void DataManager::onFearGreedReceived(const QJsonObject &data)
{
    emit fearGreedUpdated(data);
}

void DataManager::onCommandError(const QString &error)
{
    emit errorOccurred(error);
    m_refreshing = false;
    emit refreshFinished();
}
