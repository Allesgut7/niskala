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
    void executeCommand(const QString &command, const QStringList &args = {});

signals:
    void marketDataReceived(const QJsonObject &data);
    void sentimentReceived(const QJsonObject &data);
    void fearGreedReceived(const QJsonObject &data);
    void commandOutput(const QString &output);
    void commandError(const QString &error);

private slots:
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onProcessError(QProcess::ProcessError error);

private:
    QProcess *m_process = nullptr;
};
