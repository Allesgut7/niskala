#pragma once

#include <QObject>
#include <QProcess>
#include <QJsonObject>
#include <QJsonArray>

class PythonBridge : public QObject
{
    Q_OBJECT

public:
    explicit PythonBridge(QObject *parent = nullptr);

    void fetchMarketData(const QString &symbol);
    void fetchSentiment(const QString &symbol);
    void fetchFearGreedIndex();
    void fetchMarketBreadth();
    void fetchSectorPerformance();
    void fetchAIRegime();
    void startWebSocket(const QStringList &symbols);
    void stopWebSocket();
    void executeCommand(const QString &command, const QStringList &args = {});

signals:
    void marketDataReceived(const QJsonObject &data);
    void sentimentReceived(const QJsonObject &data);
    void fearGreedReceived(const QJsonObject &data);
    void marketBreadthReceived(const QJsonObject &data);
    void sectorPerformanceReceived(const QJsonArray &data);
    void aiRegimeReceived(const QJsonObject &data);
    void realTimeUpdate(const QJsonObject &data);
    void commandOutput(const QString &output);
    void commandError(const QString &error);

private slots:
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onProcessError(QProcess::ProcessError error);
    void onWebSocketFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onWebSocketReadyRead();

private:
    QProcess *m_process = nullptr;
    QProcess *m_webSocketProcess = nullptr;
};
