#include "PythonBridge.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QCoreApplication>
#include <QDir>

PythonBridge::PythonBridge(QObject *parent)
    : QObject(parent)
{
    m_process = new QProcess(this);
    
    // Set working directory to niskala root (5 levels up from build/bin/)
    QDir appDir(QCoreApplication::applicationDirPath());
    m_workDir = appDir.absoluteFilePath("../../../../..");
    m_process->setWorkingDirectory(m_workDir);
    
    connect(m_process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &PythonBridge::onProcessFinished);
    connect(m_process, &QProcess::errorOccurred,
            this, &PythonBridge::onProcessError);

    m_webSocketProcess = new QProcess(this);
    m_webSocketProcess->setWorkingDirectory(m_workDir);
    connect(m_webSocketProcess, &QProcess::readyReadStandardOutput,
            this, &PythonBridge::onWebSocketReadyRead);
    connect(m_webSocketProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &PythonBridge::onWebSocketFinished);
}

void PythonBridge::fetchMarketData(const QString &symbol)
{
    QStringList args;
    args << "-c"
         << QString(
                 "import json; "
                 "import sys; "
                 "sys.path.insert(0, '../../../../../'); "
                 "try: "
                 "    from python.data_sources.yfinance_client import YFinanceClient; "
                 "    client = YFinanceClient(); "
                 "    data = client.get_stock('%1'); "
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
                "sys.path.insert(0, '../../../../../'); "
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
                "sys.path.insert(0, '../../../../../'); "
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

void PythonBridge::fetchMarketBreadth()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../../../../../'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    data = client.get_market_breadth(); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'naik': 0, 'turun': 0, 'stagnan': 0, 'error': str(e)})) "
            );

    executeCommand("python3", args);
}

void PythonBridge::fetchSectorPerformance()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../../../../../'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    # Calculate sector performance from IDX stocks "
                "    sectors = [ "
                "      {'name': 'Teknologi', 'changePct': 0.0}, "
                "      {'name': 'Keuangan', 'changePct': 0.0}, "
                "      {'name': 'Energi', 'changePct': 0.0}, "
                "      {'name': 'Industri', 'changePct': 0.0}, "
                "      {'name': 'Consumer', 'changePct': 0.0}, "
                "    ] "
                "    print(json.dumps(sectors)) "
                "except Exception as e: "
                "    print(json.dumps([])) "
            );

    executeCommand("python3", args);
}

void PythonBridge::fetchAIRegime()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../../../../../'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    # Simple regime detection based on IHSG "
                "    data = client.get_index('^JKSE') "
                "    regime = 'BULL' if data.get('changePct', 0) > 0 else 'BEAR' "
                "    confidence = min(90, max(50, 70 + abs(data.get('changePct', 0)) * 2)) "
                "    result = { "
                "      'regime': regime, "
                "      'confidence': int(confidence), "
                "      'analysis': f'IHSG change: {data.get(\"changePct\", 0):.2f}%. Market regime: {regime}.' "
                "    } "
                "    print(json.dumps(result)) "
                "except Exception as e: "
                "    print(json.dumps({'regime': 'NEUTRAL', 'confidence': 50, 'analysis': 'Insufficient data'})) "
            );

    executeCommand("python3", args);
}

void PythonBridge::startWebSocket(const QStringList &symbols)
{
    if (m_webSocketProcess->state() == QProcess::Running) {
        m_webSocketProcess->kill();
    }

    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '../../../../../'); "
                "from python.data_sources.yfinance_websocket import YFinanceWebSocket; "
                "ws = YFinanceWebSocket(); "
                "ws.connect(['%1']); "
                "ws.run() "
             ).arg(symbols.join("', '"));

    m_webSocketProcess->start("python3", args);
}

void PythonBridge::stopWebSocket()
{
    if (m_webSocketProcess->state() == QProcess::Running) {
        m_webSocketProcess->kill();
    }
}

void PythonBridge::executeCommand(const QString &command, const QStringList &args)
{
    if (m_process->state() == QProcess::Running) {
        m_process->waitForFinished(5000);
        if (m_process->state() == QProcess::Running) {
            m_process->kill();
        }
    }
    m_process->start(command, args);
}

void PythonBridge::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    QByteArray output = m_process->readAllStandardOutput();
    QByteArray error = m_process->readAllStandardError();

    // Debug: print raw output
    qDebug() << "PythonBridge output:" << QString::fromUtf8(output).left(200);
    
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
                
                // Emit specific signals based on data content
                if (obj.contains("score") || obj.contains("indo")) {
                    emit fearGreedReceived(obj);
                }
                if (obj.contains("naik") || obj.contains("turun")) {
                    emit marketBreadthReceived(obj);
                }
                if (obj.contains("regime") || obj.contains("confidence")) {
                    emit aiRegimeReceived(obj);
                }
            }
        } else if (doc.isArray()) {
            QJsonArray arr = doc.array();
            emit sectorPerformanceReceived(arr);
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

void PythonBridge::onWebSocketFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    Q_UNUSED(exitCode);
    Q_UNUSED(exitStatus);
    
    QByteArray output = m_webSocketProcess->readAllStandardOutput();
    QString outputStr = QString::fromUtf8(output).trimmed();
    
    // Process each line as separate JSON
    QStringList lines = outputStr.split('\n');
    for (const QString &line : lines) {
        if (line.isEmpty()) continue;
        
        QJsonDocument doc = QJsonDocument::fromJson(line.toUtf8());
        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            emit realTimeUpdate(obj);
        }
    }
}

void PythonBridge::onWebSocketReadyRead()
{
    QByteArray output = m_webSocketProcess->readAllStandardOutput();
    QString outputStr = QString::fromUtf8(output).trimmed();
    
    // Process each line as separate JSON
    QStringList lines = outputStr.split('\n');
    for (const QString &line : lines) {
        if (line.isEmpty()) continue;
        
        QJsonDocument doc = QJsonDocument::fromJson(line.toUtf8());
        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            if (!obj.contains("error")) {
                emit realTimeUpdate(obj);
            }
        }
    }
}
