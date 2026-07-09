#pragma once

#include <QObject>
#include <QTimer>
#include <QJsonObject>
#include <QMap>

class PythonBridge;

class DataManager : public QObject
{
    Q_OBJECT

public:
    explicit DataManager(QObject *parent = nullptr);

    void startAutoRefresh(int intervalSec = 30);
    void stopAutoRefresh();
    void refreshAll();
    void refreshWatchlist();
    void refreshMarketOverview();
    void refreshFearGreedIndex();
    void refreshMarketBreadth();
    void refreshSectorPerformance();
    void refreshAIRegime();
    void refreshNews();
    void startRealTimeStream(const QStringList &symbols);
    void stopRealTimeStream();

    bool isRefreshing() const { return m_refreshing; }
    QStringList watchlist() const { return m_watchlist; }

signals:
    void watchlistUpdated(const QJsonObject &data);
    void marketOverviewUpdated(const QJsonObject &data);
    void fearGreedUpdated(const QJsonObject &data);
    void marketBreadthUpdated(const QJsonObject &data);
    void sectorPerformanceUpdated(const QJsonObject &data);
    void aiRegimeUpdated(const QJsonObject &data);
    void newsUpdated(const QJsonArray &data);
    void sentimentUpdated(const QString &symbol, const QJsonObject &data);
    void realTimeUpdate(const QString &symbol, const QJsonObject &data);
    void refreshStarted();
    void refreshFinished();
    void errorOccurred(const QString &error);

private slots:
    void onAutoRefresh();
    void onMarketDataReceived(const QJsonObject &data);
    void onFearGreedReceived(const QJsonObject &data);
    void onCommandError(const QString &error);
    void onRealTimeUpdate(const QJsonObject &data);

private:
    PythonBridge *m_bridge = nullptr;
    QTimer *m_refreshTimer = nullptr;
    bool m_refreshing = false;
    QStringList m_watchlist;
};
