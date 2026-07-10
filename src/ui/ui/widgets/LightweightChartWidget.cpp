#include "LightweightChartWidget.h"
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
    : QWidget(parent)
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
    m_channel = new QWebChannel(this);
    
    // Load chart HTML
    m_webView->setUrl(QUrl("qrc:/chart.html"));
    m_webView->setStyleSheet("background-color: transparent; border: none;");
    
    m_webView->page()->setWebChannel(m_channel);
    
    layout->addWidget(m_webView);
#else
    // Fallback: show placeholder
    auto *placeholder = new QLabel("Lightweight Charts unavailable\nInstall Qt6 WebEngine");
    placeholder->setAlignment(Qt::AlignCenter);
    placeholder->setStyleSheet("color: #859585; font-size: 14px; background-color: #1D2023;");
    layout->addWidget(placeholder);
#endif
}

void LightweightChartWidget::loadData(const QVector<OHLCData> &data)
{
#ifdef HAS_QTWEBENGINE
    sendDataToJs(data);
#endif
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
    
    // Call JavaScript function
    m_webView->page()->runJavaScript(
        QString("onQtDataReceived('%1');").arg(jsonStr));
#endif
}
