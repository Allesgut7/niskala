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
    connect(m_bridge, &PythonBridge::newsReceived,
            this, [this](const QJsonArray &data) {
        emit newsUpdated(data);
    });
    connect(m_bridge, &PythonBridge::realTimeUpdate,
            this, &DataManager::onRealTimeUpdate);
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
    refreshMarketOverview();
    refreshFearGreedIndex();
    refreshMarketBreadth();
    refreshSectorPerformance();
    refreshAIRegime();
    refreshNews();
}

void DataManager::refreshWatchlist()
{
    m_bridge->fetchWatchlistBatch(m_watchlist);
}

void DataManager::refreshMarketOverview()
{
    m_bridge->fetchWatchlistBatch({
        "^JKSE", "GC=F", "CL=F", "USDIDR=X",
        "MTXF=F", "NI=F", "HG=F", "NG=F"
    });
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

void DataManager::refreshNews()
{
    m_bridge->fetchNews();
}

void DataManager::startRealTimeStream(const QStringList &symbols)
{
    m_bridge->startWebSocket(symbols);
}

void DataManager::stopRealTimeStream()
{
    m_bridge->stopWebSocket();
}

void DataManager::onAutoRefresh()
{
    refreshAll();
}

void DataManager::onMarketDataReceived(const QJsonObject &data)
{
    qDebug() << "DataManager: Received data, keys:" << data.keys();
    
    // Handle single symbol response
    if (data.contains("symbol")) {
        QString symbol = data["symbol"].toString();
        qDebug() << "DataManager: Symbol:" << symbol << "Price:" << data["price"];
        QStringList overviewSymbols = {"^JKSE", "GC=F", "CL=F", "USDIDR=X", "^N225", "^HSI", "^KS11", "^GSPC", "^IXIC"};
        if (overviewSymbols.contains(symbol)) {
            qDebug() << "DataManager: Emitting marketOverviewUpdated";
            emit marketOverviewUpdated(data);
        } else {
            qDebug() << "DataManager: Emitting watchlistUpdated";
            emit watchlistUpdated(data);
        }
    }
    
    m_refreshing = false;
    emit refreshFinished();
}

void DataManager::onFearGreedReceived(const QJsonObject &data)
{
    emit fearGreedUpdated(data);
}

void DataManager::onRealTimeUpdate(const QJsonObject &data)
{
    QString symbol = data["symbol"].toString();
    emit realTimeUpdate(symbol, data);
}

void DataManager::onCommandError(const QString &error)
{
    emit errorOccurred(error);
    m_refreshing = false;
    emit refreshFinished();
}
