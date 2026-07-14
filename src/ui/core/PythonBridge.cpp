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
    
    // Set working directory to niskala root (dynamic detection)
    QDir appDir(QCoreApplication::applicationDirPath());
    m_workDir = appDir.absolutePath();
    while (!m_workDir.isEmpty() && !QDir(m_workDir + "/python/scripts").exists()) {
        QString parent = QFileInfo(m_workDir).absolutePath();
        if (parent == m_workDir) break;
        m_workDir = parent;
    }
    if (!QDir(m_workDir + "/python/scripts").exists()) {
        m_workDir = appDir.absolutePath();
        for (int i = 0; i < 2; ++i)
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

void PythonBridge::fetchNews()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_news.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchTopMovers()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_top_movers.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchTradingViewData(const QString &symbol, const QString &timeframe, int candles)
{
    QStringList args;
    args << m_scriptsDir + "/tradingview_data.py" << symbol << timeframe << QString::number(candles);
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchCommodities()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_commodities.py";
    executeCommand(m_pythonPath, args);
}

void PythonBridge::fetchIndices()
{
    QStringList args;
    args << m_scriptsDir + "/fetch_indices.py";
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
    QString cacheKey = command + "|" + args.join("|");

    // Check cache first
    if (m_cache.contains(cacheKey)) {
        QPair<QDateTime, QString> cached = m_cache.value(cacheKey);
        if (cached.first.secsTo(QDateTime::currentDateTime()) < m_cacheTtlSec) {
            qDebug() << "PythonBridge: Cache HIT for" << args.join(" ").right(50);
            if (!cached.second.isEmpty()) {
                QJsonDocument doc = QJsonDocument::fromJson(cached.second.toUtf8());
                if (doc.isObject()) {
                    QJsonObject obj = doc.object();
                    emit marketDataReceived(obj);
                    if (obj.contains("score") || obj.contains("indo"))
                        emit fearGreedReceived(obj);
                    if (obj.contains("naik") || obj.contains("turun"))
                        emit marketBreadthReceived(obj);
                    if (obj.contains("regime") || obj.contains("confidence"))
                        emit aiRegimeReceived(obj);
                    if (obj.contains("gainers") || obj.contains("losers"))
                        emit topMoversReceived(obj);
                } else if (doc.isArray()) {
                    QJsonArray arr = doc.array();
                    if (!arr.isEmpty()) {
                        QJsonObject first = arr[0].toObject();
                        if (first.contains("score") || first.contains("indo"))
                            emit fearGreedReceived(first);
                        if (first.contains("naik") || first.contains("turun"))
                            emit marketBreadthReceived(first);
                        if (first.contains("gainers") || first.contains("losers"))
                            emit topMoversReceived(first);
                        // TradingView OHLCV data
                        if (first.contains("timestamp") && first.contains("open") && first.contains("close")) {
                            // Don't emit stale cache if newer commands are queued
                            if (!m_commandQueue.isEmpty()) {
                                processNextCommand();
                                return;
                            }
                            emit tradingViewDataReceived(arr);
                            return;
                        }
                        bool isSector = first.contains("name") && first.contains("changePct") && !first.contains("symbol");
                        bool isNews = first.contains("title") && first.contains("source");
                        bool isStock = first.contains("symbol") && !isSector;
                        if (isSector) {
                            emit sectorPerformanceReceived(arr);
                        } else if (isNews) {
                            emit newsReceived(arr);
                        } else if (isStock) {
                            for (const auto &item : arr) emit watchlistUpdated(item.toObject());
                        }
                    }
                }
            }
            return;
        }
        m_cache.remove(cacheKey);
    }

    // Store command for retry
    m_lastCommand = command;
    m_lastArgs = args;

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
    m_currentCommand = cmd.first;
    m_currentArgs = cmd.second;
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

        // Cache successful result (use actual command processed, not last requested)
        QString cacheKey = m_currentCommand + "|" + m_currentArgs.join("|");
        m_cache[cacheKey] = {QDateTime::currentDateTime(), outputStr};
        m_retryCount.remove(cacheKey);

        // If there are newer commands queued, skip emitting this stale result
        if (!m_commandQueue.isEmpty()) {
            processNextCommand();
            return;
        }

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
                if (obj.contains("gainers") || obj.contains("losers")) {
                    emit topMoversReceived(obj);
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
            
            // Check if this is news data (has "title" and "source" keys)
            bool isNewsData = false;
            if (!arr.isEmpty()) {
                QJsonObject firstItem = arr[0].toObject();
                isNewsData = firstItem.contains("title") && firstItem.contains("source");
            }
            
            // Check if this is TradingView OHLCV data (has "timestamp", "open", "close")
            bool isTradingViewData = false;
            if (!arr.isEmpty()) {
                QJsonObject firstItem = arr[0].toObject();
                isTradingViewData = firstItem.contains("timestamp") && 
                                    firstItem.contains("open") && 
                                    firstItem.contains("close");
            }
            
            // Detect data type by symbol pattern
            bool isCommodityData = false;
            bool isIndexData = false;
            bool isStockData = false;
            
            if (!arr.isEmpty() && !isSectorData && !isNewsData && !isTradingViewData) {
                QJsonObject firstItem = arr[0].toObject();
                if (firstItem.contains("symbol")) {
                    QString sym = firstItem["symbol"].toString();
                    isCommodityData = sym.contains("=");    // GC=F, CL=F
                    isIndexData = sym.startsWith("^");      // ^JKSE, ^N225
                    isStockData = !isCommodityData && !isIndexData;  // BBCA, BBRI
                }
            }
            
            if (isSectorData) {
                emit sectorPerformanceReceived(arr);
            } else if (isNewsData) {
                emit newsReceived(arr);
            } else if (isTradingViewData) {
                emit tradingViewDataReceived(arr);
            } else if (isCommodityData) {
                emit commoditiesReceived(arr);
            } else if (isIndexData) {
                emit indicesReceived(arr);
            }
            
            // For stock data, emit individual watchlist updates
            if (isStockData || isCommodityData || isIndexData) {
                for (const auto &item : arr) {
                    QJsonObject obj = item.toObject();
                    if (obj.contains("symbol")) {
                        emit watchlistUpdated(obj);
                    }
                }
            }
        }
    } else if (!errorStr.isEmpty()) {
        // Detect rate limit and retry
        if (errorStr.contains("Too Many Requests", Qt::CaseInsensitive) ||
            errorStr.contains("rate limited", Qt::CaseInsensitive)) {
            QString cacheKey = m_lastCommand + "|" + m_lastArgs.join("|");
            int retries = m_retryCount.value(cacheKey, 0);
            if (retries < 3) {
                m_retryCount[cacheKey] = retries + 1;
                int delay = 15000 * (retries + 1);
                qDebug() << "PythonBridge: Rate limited, retry in" << delay << "ms (attempt" << retries + 1 << "/3)";
                QTimer::singleShot(delay, this, [this]() {
                    executeCommand(m_lastCommand, m_lastArgs);
                });
                processNextCommand();
                return;
            }
            qDebug() << "PythonBridge: Rate limit retry exhausted, giving up";
        }
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
