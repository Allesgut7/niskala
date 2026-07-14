#include "LightweightChartWidget.h"
#include "FinancialChart.h"
#include <QVBoxLayout>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QLabel>

#ifdef HAS_QTWEBENGINE
#include <QWebEngineView>
#include <QWebChannel>
#include <QTimer>
#endif

LightweightChartWidget::LightweightChartWidget(QWidget *parent)
    : QWidget(parent), m_pageLoaded(false)
{
    setupUI();
}

LightweightChartWidget::~LightweightChartWidget() = default;

void LightweightChartWidget::setupUI()
{
    qDebug() << "LightweightChart: setupUI";
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);

#ifdef HAS_QTWEBENGINE
    m_webView = new QWebEngineView();
    m_webView->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    m_webView->setMinimumWidth(0);
    m_webView->setMinimumHeight(0);
    
    // Load chart HTML from resources
    m_webView->setUrl(QUrl("qrc:/chart.html"));
    m_webView->setStyleSheet("background-color: transparent; border: none;");
    
    // Wait for page to load before sending data
    connect(m_webView, &QWebEngineView::loadFinished, this, [this](bool ok) {
        m_pageLoaded = ok;
            if (ok) {
                qDebug() << "LightweightChart: Page loaded successfully";
                // Force resize after layout settles
                QTimer::singleShot(300, this, [this]() {
                    if (m_webView && parentWidget())
                        m_webView->resize(this->size());
                });
                // Send queued data
                if (!m_queuedData.isEmpty()) {
                sendDataToJs(m_queuedData);
                m_queuedData.clear();
            }
        } else {
            qDebug() << "LightweightChart: Page load FAILED";
        }
    });
    
    m_channel = new QWebChannel(this);
    auto *bridge = new ChartBridge(this);
    m_channel->registerObject(QStringLiteral("bridge"), bridge);
    m_webView->page()->setWebChannel(m_channel);

    connect(bridge, &ChartBridge::dataRequested, this, [this](const QString &dir) {
        qDebug() << "LightweightChart: requestMoreData" << dir << "for" << m_currentSymbol;
        if (m_currentSymbol.trimmed().isEmpty()) {
            qDebug() << "LightweightChart: requestMoreData skipped — empty symbol";
            return;
        }
        emit loadMoreData(m_currentSymbol, dir);
    });

    layout->addWidget(m_webView);
#else
    qDebug() << "LightweightChart: WebEngine NOT available, using placeholder";
    auto *placeholder = new QLabel("Lightweight Charts unavailable\nInstall Qt6 WebEngine");
    placeholder->setAlignment(Qt::AlignCenter);
    placeholder->setStyleSheet("color: #859585; font-size: 14px; background-color: #1D2023;");
    layout->addWidget(placeholder);
#endif
}

void LightweightChartWidget::loadData(const QVector<OHLCData> &data)
{
    qDebug() << "LightweightChart: loadData" << data.size() << "candles, pageLoaded:" << m_pageLoaded;
    if (m_pageLoaded) {
        sendDataToJs(data);
    } else {
        m_queuedData = data; // Queue until page loads
    }
}

void LightweightChartWidget::addRealTimeCandle(const OHLCData &candle)
{
#ifdef HAS_QTWEBENGINE
    if (!m_webView || !m_pageLoaded) return;
    int ts = candle.timestamp;
    if (m_timeframe == "1m")       ts = ts - (ts % 60);
    else if (m_timeframe == "5m")  ts = ts - (ts % 300);
    else if (m_timeframe == "15m") ts = ts - (ts % 900);
    else if (m_timeframe == "1h")  ts = ts - (ts % 3600);
    QJsonObject obj;
    obj["timestamp"] = ts;
    obj["open"] = candle.open;
    obj["high"] = candle.high;
    obj["low"] = candle.low;
    obj["close"] = candle.close;
    obj["volume"] = candle.volume;
    QJsonDocument doc(obj);
    QString jsonStr = QString::fromUtf8(doc.toJson(QJsonDocument::Compact));
    jsonStr.replace("'", "\\'");
    m_webView->page()->runJavaScript(
        QString("if(typeof onAddCandle==='function')onAddCandle('%1');").arg(jsonStr));
#endif
}

void LightweightChartWidget::clearChart()
{
#ifdef HAS_QTWEBENGINE
    if (m_pageLoaded && m_webView) {
        m_webView->page()->runJavaScript("clearChart()");
        qDebug() << "LightweightChart: clearChart called";
    }
#endif
    m_queuedData.clear();
}

void LightweightChartWidget::loadSymbol(const QString &symbol)
{
    qDebug() << "LightweightChart: loadSymbol" << symbol;
    m_currentSymbol = symbol;
    // Mark new ticker BEFORE clearing chart so updateData knows to replace data
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded)
        m_webView->page()->runJavaScript("markNewTicker()");
#endif
    clearChart();
}

void LightweightChartWidget::setTimeframe(const QString &tf)
{
    qDebug() << "LightweightChart: setTimeframe" << tf;
    m_timeframe = tf;
}

void LightweightChartWidget::setChartType(const QString &type)
{
    m_currentChartType = type;
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded) {
        QString escaped = type;
        escaped.replace("'", "\\'");
        m_webView->page()->runJavaScript(
            QString("setChartType('%1')").arg(escaped));
    }
#endif
}

void LightweightChartWidget::setIndicatorVisible(const QString &name, bool visible)
{
    if (visible) m_activeIndicators.insert(name);
    else m_activeIndicators.remove(name);
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded) {
        QString n = name;
        n.replace("'", "\\'");
        m_webView->page()->runJavaScript(
            QString("setIndicatorVisible('%1', %2)").arg(n, visible ? "true" : "false"));
    }
#endif
}

void LightweightChartWidget::setMA5Visible(bool visible)
{
    setIndicatorVisible("sma_5", visible);
}

void LightweightChartWidget::setMA20Visible(bool visible)
{
    setIndicatorVisible("sma_20", visible);
}

void LightweightChartWidget::setVolumeVisible(bool visible)
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded)
        m_webView->page()->runJavaScript(visible ? "setVolumeVisible(true)" : "setVolumeVisible(false)");
#endif
}

void LightweightChartWidget::sendDataToJs(const QVector<OHLCData> &data)
{
    qDebug() << "LightweightChart: sendDataToJs" << data.size() << "candles";
#ifdef HAS_QTWEBENGINE
    if (!m_webView || !m_pageLoaded) {
        m_queuedData = data;
        return;
    }

    QJsonArray arr;
    for (const auto &candle : data) {
        QJsonObject obj;
        obj["timestamp"] = candle.timestamp;
        obj["open"] = candle.open;
        obj["high"] = candle.high;
        obj["low"] = candle.low;
        obj["close"] = candle.close;
        obj["volume"] = candle.volume;
        arr.append(obj);
    }
    
    QJsonDocument doc(arr);
    QString jsonStr = QString::fromUtf8(doc.toJson(QJsonDocument::Compact));
    jsonStr.replace("'", "\\'");
    
    // Combine clear + send in ONE js call so execution order is guaranteed
    static QString lastSymbol;
    QString js;
    if (!m_currentSymbol.isEmpty() && m_currentSymbol != lastSymbol) {
        lastSymbol = m_currentSymbol;
        js = QString("clearChart(); newTickerLoaded = true; onQtDataReceived('%1');").arg(jsonStr);
    } else {
        js = QString("onQtDataReceived('%1');").arg(jsonStr);
    }
    
    m_webView->page()->runJavaScript(js,
        [](const QVariant &result) {
            qDebug() << "LightweightChart: JS result:" << result;
        });
#endif
}

void LightweightChartWidget::setActiveDrawingTool(const QString &tool)
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded) {
        QString t = tool;
        t.replace("'", "\\'");
        m_webView->page()->runJavaScript(
            QString("setActiveDrawingToolFromCpp('%1')").arg(t));
    }
#endif
}

void LightweightChartWidget::clearAllDrawings()
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded)
        m_webView->page()->runJavaScript("clearAllDrawings()");
#endif
}

void LightweightChartWidget::setDrawingToolbarVisible(bool visible)
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded)
        m_webView->page()->runJavaScript(
            visible ? "setDrawingToolbarVisible(true)" : "setDrawingToolbarVisible(false)");
#endif
}

void LightweightChartWidget::undoLastDrawing()
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded)
        m_webView->page()->runJavaScript("undoLastDrawing()");
#endif
}

QString LightweightChartWidget::getDrawingsJson()
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded) {
        QVariant result;
        m_webView->page()->runJavaScript("getDrawingsJson()", [](const QVariant &r) {
            return r.toString();
        });
    }
#endif
    return "[]";
}

void LightweightChartWidget::loadDrawingsJson(const QString &json)
{
#ifdef HAS_QTWEBENGINE
    if (m_webView && m_pageLoaded) {
        QString j = json;
        j.replace("'", "\\'");
        m_webView->page()->runJavaScript(
            QString("loadDrawingsJson('%1')").arg(j));
    }
#endif
}
