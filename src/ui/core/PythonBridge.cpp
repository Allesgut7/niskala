#include "PythonBridge.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QCoreApplication>
#include <QDir>
#include <QDebug>

PythonBridge::PythonBridge(QObject *parent)
    : QObject(parent)
{
    m_process = new QProcess(this);
    
    // Set working directory to niskala root
    QDir appDir(QCoreApplication::applicationDirPath());
    m_workDir = appDir.absoluteFilePath("../../../../..");
    m_process->setWorkingDirectory(m_workDir);
    
    // Set Python executable path (use venv)
    m_pythonPath = m_workDir + "/.venv/bin/python3";
    qDebug() << "PythonBridge: Python path:" << m_pythonPath;
    qDebug() << "PythonBridge: Working dir:" << m_workDir;
    
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
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    data = client.get_stock('%1'); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
             ).arg(symbol);
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchWatchlistBatch(const QStringList &symbols)
{
    QString symbolsStr = symbols.join("','");
    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "from python.data_sources.yfinance_client import YFinanceClient; "
                "client = YFinanceClient(); "
                "results = [] "
                "for sym in ['%1']: "
                "    try: "
                "        data = client.get_stock(sym) "
                "        results.append(data) "
                "    except: "
                "        pass "
                "print(json.dumps(results)) "
             ).arg(symbolsStr);
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchSentiment(const QString &symbol)
{
    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.ai.sentiment_pipeline import SentimentPipeline; "
                "    pipeline = SentimentPipeline(use_llm=False); "
                "    result = pipeline.analyze('%1'); "
                "    print(json.dumps(result)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
             ).arg(symbol);
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchFearGreedIndex()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.fear_greed.calculator import FearGreedCalculator; "
                "    calc = FearGreedCalculator(); "
                "    data = calc.calculate(); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'error': str(e)})) "
            );
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchMarketBreadth()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
                "    data = client.get_market_breadth(); "
                "    print(json.dumps(data)) "
                "except Exception as e: "
                "    print(json.dumps({'naik': 0, 'turun': 0, 'stagnan': 0, 'error': str(e)})) "
            );
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchSectorPerformance()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
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
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchAIRegime()
{
    QStringList args;
    args << "-c"
         << (
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "try: "
                "    from python.data_sources.yfinance_client import YFinanceClient; "
                "    client = YFinanceClient(); "
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
    executeCommand(m_pythonPath, args);
}

void PythonBridge::startWebSocket(const QStringList &symbols)
{
    if (m_webSocketProcess->state() == QProcess::Running) {
        m_webSocketProcess->kill();
        m_webSocketProcess->waitForFinished(2000);
    }

    QStringList args;
    args << "-c"
         << QString(
                "import json; "
                "import sys; "
                "sys.path.insert(0, '.'); "
                "from python.data_sources.yfinance_websocket import YFinanceWebSocket; "
                "ws = YFinanceWebSocket(); "
                "ws.connect(['%1']); "
                "ws.run() "
             ).arg(symbols.join("', '"));

    m_webSocketProcess->start(m_pythonPath, args);
}

void PythonBridge::stopWebSocket()
{
    if (m_webSocketProcess->state() == QProcess::Running) {
        m_webSocketProcess->kill();
    }
}

void PythonBridge::executeCommand(const QString &command, const QStringList &args)
{
    // Queue the command
    m_commandQueue.enqueue(qMakePair(command, args));
    
    // Process next if not already processing
    if (!m_processingCommand) {
        processNextCommand();
    }
}

void PythonBridge::processNextCommand()
{
    if (m_commandQueue.isEmpty()) {
        m_processingCommand = false;
        return;
    }
    
    m_processingCommand = true;
    
    // Kill any running process
    if (m_process->state() == QProcess::Running) {
        m_process->kill();
        m_process->waitForFinished(1000);
    }
    
    // Get next command
    auto cmd = m_commandQueue.dequeue();
    qDebug() << "PythonBridge: Processing command:" << cmd.first;
    qDebug() << "PythonBridge: Working dir:" << m_workDir;
    
    // Start new process
    m_process->start(cmd.first, cmd.second);
}

void PythonBridge::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    QByteArray output = m_process->readAllStandardOutput();
    QByteArray error = m_process->readAllStandardError();

    QString outputStr = QString::fromUtf8(output).trimmed();
    qDebug() << "PythonBridge: Exit code:" << exitCode;
    qDebug() << "PythonBridge: Output length:" << outputStr.length();
    if (!outputStr.isEmpty()) {
        qDebug() << "PythonBridge: Output:" << outputStr.left(500);
    }
    
    if (exitStatus == QProcess::NormalExit && exitCode == 0) {
        QJsonDocument doc = QJsonDocument::fromJson(outputStr.toUtf8());

        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            if (obj.contains("error")) {
                emit commandError(obj["error"].toString());
            } else {
                emit commandOutput(outputStr);
                emit marketDataReceived(obj);
                
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
            
            // Handle batch watchlist response
            for (const auto &item : arr) {
                QJsonObject obj = item.toObject();
                if (obj.contains("symbol")) {
                    emit watchlistUpdated(obj);
                }
            }
        }
    } else if (!error.isEmpty()) {
        emit commandError(QString::fromUtf8(error));
    }
    
    // Process next command in queue
    processNextCommand();
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
    
    // Process next command even on error
    processNextCommand();
}

void PythonBridge::onWebSocketReadyRead()
{
    QByteArray output = m_webSocketProcess->readAllStandardOutput();
    QString outputStr = QString::fromUtf8(output).trimmed();
    
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

void PythonBridge::onWebSocketFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    Q_UNUSED(exitCode);
    Q_UNUSED(exitStatus);
    
    QByteArray output = m_webSocketProcess->readAllStandardOutput();
    QString outputStr = QString::fromUtf8(output).trimmed();
    
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
