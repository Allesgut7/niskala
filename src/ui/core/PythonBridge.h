#pragma once

#include <QObject>
#include <QProcess>
#include <QJsonObject>
#include <QJsonArray>
#include <QQueue>
#include <QTimer>

class PythonBridge : public QObject
{
    Q_OBJECT

public:
    explicit PythonBridge(QObject *parent = nullptr);

    void fetchMarketData(const QString &symbol);
    void fetchWatchlistBatch(const QStringList &symbols);
    void fetchSentiment(const QString &symbol);
    void fetchFearGreedIndex();
    void fetchMarketBreadth();
    void fetchSectorPerformance();
    void fetchCommodities();
    void fetchIndices();
    void fetchAIRegime();
    void fetchNews();
    void fetchTradingViewData(const QString &symbol, const QString &timeframe = "1D", int candles = 50);
    void startWebSocket(const QStringList &symbols);
    void stopWebSocket();

signals:
    void marketDataReceived(const QJsonObject &data);
    void watchlistUpdated(const QJsonObject &data);
    void sentimentReceived(const QJsonObject &data);
    void fearGreedReceived(const QJsonObject &data);
    void marketBreadthReceived(const QJsonObject &data);
    void sectorPerformanceReceived(const QJsonArray &data);
    void commoditiesReceived(const QJsonArray &data);
    void indicesReceived(const QJsonArray &data);
    void aiRegimeReceived(const QJsonObject &data);
    void newsReceived(const QJsonArray &data);
    void tradingViewDataReceived(const QJsonArray &data);
    void realTimeUpdate(const QJsonObject &data);
    void commandOutput(const QString &output);
    void commandError(const QString &error);

private slots:
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onProcessError(QProcess::ProcessError error);
    void onWebSocketReadyRead();
    void onWebSocketFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void processNextCommand();

private:
    void executeCommand(const QString &command, const QStringList &args);

    QProcess *m_process = nullptr;
    QProcess *m_webSocketProcess = nullptr;
    QString m_workDir;
    QString m_pythonPath;
    QString m_scriptsDir;
    QQueue<QPair<QString, QStringList>> m_commandQueue;
    bool m_processingCommand = false;
};
