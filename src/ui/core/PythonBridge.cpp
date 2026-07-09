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
    
    // Set working directory to niskala root (absolute path)
    QDir appDir(QCoreApplication::applicationDirPath());
    QString buildBinDir = appDir.absolutePath();
    // Go up 5 levels to reach niskala root
    m_workDir = buildBinDir;
    for (int i = 0; i < 4; ++i) {
        m_workDir = QFileInfo(m_workDir).absolutePath();
    }
    m_process->setWorkingDirectory(m_workDir);
    
    // Set Python executable path (use venv)
    m_pythonPath = m_workDir + "/.venv/bin/python3";
    
    // Check if Python exists, fallback to system python3
    QFile pythonFile(m_pythonPath);
    if (!pythonFile.exists()) {
        qDebug() << "PythonBridge: Venv Python NOT FOUND, using system python3";
        m_pythonPath = "python3";
    }
    
    // Set scripts directory (absolute path)
    m_scriptsDir = m_workDir + "/python/scripts";
    
    qDebug() << "PythonBridge: Python path:" << m_pythonPath;
    qDebug() << "PythonBridge: Scripts dir:" << m_scriptsDir;
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
    args << m_scriptsDir + "/fetch_stock.py" << symbol;
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchWatchlistBatch(const QStringList &symbols)
{
    QStringList args;
    args << m_scriptsDir + "/fetch_watchlist.py" << symbols.join(",");
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchSentiment(const QString &symbol)
{
    // Sentiment script not yet created, use placeholder
    QStringList args;
    args << "-c" << QString("import json; print(json.dumps({'symbol': '%1', 'sentiment': 0}))").arg(symbol);
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchFearGreedIndex()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_fear_greed.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchMarketBreadth()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_breadth.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchSectorPerformance()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_sectors.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchAIRegime()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_regime.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::startWebSocket(const QStringList &symbols)
{
    if (m_webSocketProcess->state() == QProcess::Running) {
        m_webSocketProcess->kill();
        m_webSocketProcess->waitForFinished(2000);
    }

    // Use Python script for websocket
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
    qDebug() << "PythonBridge: Processing:" << cmd.first << cmd.second;
    
    // Start new process (non-blocking)
    m_process->start(cmd.first, cmd.second);
    // Don't wait - onProcessFinished signal will handle the result
}

void PythonBridge::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    QByteArray output = m_process->readAllStandardOutput();
    QByteArray error = m_process->readAllStandardError();

    QString outputStr = QString::fromUtf8(output).trimmed();
    QString errorStr = QString::fromUtf8(error).trimmed();
    
    qDebug() << "PythonBridge: Exit:" << exitCode << "Output:" << outputStr.length() << "Error:" << errorStr.length();
    if (!errorStr.isEmpty()) {
        qDebug() << "PythonBridge: STDERR:" << errorStr.left(300);
    }
    if (!outputStr.isEmpty()) {
        qDebug() << "PythonBridge: Output:" << outputStr.left(300);
    }
    
    if (exitStatus == QProcess::NormalExit && exitCode == 0 && !outputStr.isEmpty()) {
        QJsonDocument doc = QJsonDocument::fromJson(outputStr.toUtf8());

        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            if (!obj.contains("error")) {
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
            
            // Check if this is actually sector data (has "name" and "changePct" keys, but NO "symbol")
            bool isSectorData = false;
            if (!arr.isEmpty()) {
                QJsonObject firstItem = arr[0].toObject();
                isSectorData = firstItem.contains("name") && 
                               firstItem.contains("changePct") && 
                               !firstItem.contains("symbol");
            }
            
            if (isSectorData) {
                emit sectorPerformanceReceived(arr);
            }
            
            for (const auto &item : arr) {
                QJsonObject obj = item.toObject();
                if (obj.contains("symbol")) {
                    emit watchlistUpdated(obj);
                }
            }
        }
    } else if (!errorStr.isEmpty()) {
        emit commandError(errorStr);
    }
    
    // Process next command
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
    qDebug() << "PythonBridge ERROR:" << errorMsg;
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
