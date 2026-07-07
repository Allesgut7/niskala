#include "PythonBridge.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>

PythonBridge::PythonBridge(QObject *parent)
    : QObject(parent)
{
    m_process = new QProcess(this);
    connect(m_process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &PythonBridge::onProcessFinished);
    connect(m_process, &QProcess::errorOccurred,
            this, &PythonBridge::onProcessError);
}

void PythonBridge::fetchMarketData(const QString &symbol)
{
    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    data = client.get_stock_data('%1'); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
             ).arg(symbol);

    executeCommand("python3", args);
}

void PythonBridge::fetchSentiment(const QString &symbol)
{
    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../'); "
                "try: "
                "    from python.ai.sentiment_pipeline import SentimentPipeline; "
                "    pipeline = SentimentPipeline(use_llm=False); "
                "    result = pipeline.analyze('%1'); "
                "    print(json.dumps(result)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
             ).arg(symbol);

    executeCommand("python3", args);
}

void PythonBridge::fetchFearGreedIndex()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../'); "
                "try: "
                "    from python.fear_greed.calculator import FearGreedCalculator; "
                "    calc = FearGreedCalculator(); "
                "    data = calc.calculate(); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
            );

    executeCommand("python3", args);
}

void PythonBridge::executeCommand(const QString &command, const QStringList &args)
{
    if (m_process->state() == QProcess::Running) {
        m_process->kill();
    }

    m_process->start(command, args);
}

void PythonBridge::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    QByteArray output = m_process->readAllStandardOutput();
    QByteArray error = m_process->readAllStandardError();

    if (exitStatus == QProcess::NormalExit && exitCode == 0) {
        QString outputStr = QString::fromUtf8(output).trimmed();
        QJsonDocument doc = QJsonDocument::fromJson(outputStr.toUtf8());

        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            if (obj.contains("error")) {
                emit commandError(obj["error"].toString());
            } else {
                emit commandOutput(outputStr);
                emit marketDataReceived(obj);
            }
        }
    } else {
        emit commandError(QString::fromUtf8(error));
    }
}

void PythonBridge::onProcessError(QProcess::ProcessError error)
{
    QString errorMsg;
    switch (error) {
        case QProcess::FailedToStart:
            errorMsg = "Python process failed to start";
            break;
        case QProcess::Crashed:
            errorMsg = "Python process crashed";
            break;
        case QProcess::Timedout:
            errorMsg = "Python process timed out";
            break;
        case QProcess::WriteError:
            errorMsg = "Write error to Python process";
            break;
        case QProcess::ReadError:
            errorMsg = "Read error from Python process";
            break;
        default:
            errorMsg = "Unknown Python process error";
    }
    emit commandError(errorMsg);
}
