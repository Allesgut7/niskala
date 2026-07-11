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
#endif

LightweightChartWidget::LightweightChartWidget(QWidget *parent)
    : QWidget(parent), m_pageLoaded(false)
{
    setupUI();
}

LightweightChartWidget::~LightweightChartWidget() = default;

void LightweightChartWidget::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);

#ifdef HAS_QTWEBENGINE
    m_webView = new QWebEngineView();
    
    // Load chart HTML from resources
    m_webView->setUrl(QUrl("qrc:/chart.html"));
    m_webView->setStyleSheet("background-color: transparent; border: none;");
    
    // Wait for page to load before sending data
    connect(m_webView, &QWebEngineView::loadFinished, this, [this](bool ok) {
        m_pageLoaded = ok;
        if (ok) {
            qDebug() << "LightweightChart: Page loaded successfully";
            // Send queued data
            if (!m_queuedData.isEmpty()) {
                sendDataToJs(m_queuedData);
                m_queuedData.clear();
            }
        } else {
            qDebug() << "LightweightChart: Page load FAILED";
        }
    });
    
    layout->addWidget(m_webView);
#else
    auto *placeholder = new QLabel("Lightweight Charts unavailable\nInstall Qt6 WebEngine");
    placeholder->setAlignment(Qt::AlignCenter);
    placeholder->setStyleSheet("color: #859585; font-size: 14px; background-color: #1D2023;");
    layout->addWidget(placeholder);
#endif
}

void LightweightChartWidget::loadData(const QVector<OHLCData> &data)
{
    if (m_pageLoaded) {
        sendDataToJs(data);
    } else {
        m_queuedData = data; // Queue until page loads
    }
}

void LightweightChartWidget::loadSymbol(const QString &symbol)
{
    m_currentSymbol = symbol;
}

void LightweightChartWidget::setTimeframe(const QString &tf)
{
    m_timeframe = tf;
}

void LightweightChartWidget::setMA5Visible(bool visible)
{
    Q_UNUSED(visible);
}

void LightweightChartWidget::setMA20Visible(bool visible)
{
    Q_UNUSED(visible);
}

void LightweightChartWidget::setVolumeVisible(bool visible)
{
    Q_UNUSED(visible);
}

void LightweightChartWidget::sendDataToJs(const QVector<OHLCData> &data)
{
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
    
    // Escape single quotes for JavaScript
    jsonStr.replace("'", "\\'");
    
    // Call JavaScript function after page is loaded
    m_webView->page()->runJavaScript(
        QString("onQtDataReceived('%1');").arg(jsonStr),
        [](const QVariant &result) {
            qDebug() << "LightweightChart: JS result:" << result;
        });
#endif
}
