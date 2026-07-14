#include "ChartScreen.h"
#include "../widgets/LightweightChartWidget.h"
#include "../widgets/FinancialChart.h"
#include "../widgets/ChartToolbarWidget.h"
#include "../core/DataManager.h"

#include <QVBoxLayout>

ChartScreen::ChartScreen(QWidget *parent)
    : QWidget(parent)
{
    setupDataManager();
    setupUI();
}

void ChartScreen::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    // Toolbar at top with semi-transparent overlay look
    m_toolbar = new ChartToolbarWidget();
    layout->addWidget(m_toolbar);

    // Chart fills remaining space
    m_chart = new LightweightChartWidget();
    layout->addWidget(m_chart, 1);

    // Toolbar connections
    connect(m_toolbar, &ChartToolbarWidget::symbolRequested,
            this, &ChartScreen::onSymbolRequested);
    connect(m_toolbar, &ChartToolbarWidget::timeframeChanged,
            this, &ChartScreen::onTimeframeChanged);
    connect(m_toolbar, &ChartToolbarWidget::chartTypeChanged,
            this, &ChartScreen::onChartTypeChanged);
    connect(m_toolbar, &ChartToolbarWidget::indicatorToggled,
            this, &ChartScreen::onIndicatorToggled);
    connect(m_toolbar, &ChartToolbarWidget::templateApplied,
            this, &ChartScreen::onTemplateApplied);

    // Scroll-to-load
    connect(m_chart, &LightweightChartWidget::loadMoreData,
            this, [this](const QString &symbol, const QString &) {
        if (!symbol.trimmed().isEmpty())
            m_dataManager->fetchChartData(symbol, m_currentTf, 100);
    });

    // Load default symbol
    loadSymbol("JKSE");
}

void ChartScreen::setupDataManager()
{
    m_dataManager = new DataManager(this);

    connect(m_dataManager, &DataManager::tradingViewUpdated,
            this, &ChartScreen::onTradingViewUpdated);
    connect(m_dataManager, &DataManager::realTimeUpdate,
            this, &ChartScreen::onRealTimeUpdate);
}

void ChartScreen::fetchChartData(const QString &symbol, const QString &tf, int candles)
{
    m_currentSymbol = symbol;
    m_currentTf = tf;
    m_dataManager->fetchChartData(symbol, tf, candles);
}

void ChartScreen::loadSymbol(const QString &symbol)
{
    if (symbol.trimmed().isEmpty()) return;
    m_chart->loadSymbol(symbol);
    fetchChartData(symbol, "D", 252);
}

void ChartScreen::onSymbolRequested(const QString &symbol)
{
    loadSymbol(symbol);
}

void ChartScreen::onTimeframeChanged(const QString &tf)
{
    m_chart->setTimeframe(tf);
    int candles = 252;
    if (tf == "1m" || tf == "5m" || tf == "15m") candles = 300;
    else if (tf == "1h") candles = 200;
    else if (tf == "D") candles = 252;
    else if (tf == "W") candles = 104;
    else if (tf == "M") candles = 60;
    QString sym = m_currentSymbol.isEmpty() ? "JKSE" : m_currentSymbol;
    fetchChartData(sym, tf, candles);
}

void ChartScreen::onChartTypeChanged(const QString &type)
{
    m_chart->setChartType(type);
}

void ChartScreen::onIndicatorToggled(const QString &name, bool visible)
{
    m_chart->setIndicatorVisible(name, visible);
}

void ChartScreen::onTradingViewUpdated(const QJsonArray &data)
{
    QVector<OHLCData> ohlcData;
    for (const auto &item : data) {
        QJsonObject obj = item.toObject();
        OHLCData candle;
        candle.timestamp = obj["timestamp"].toInt();
        candle.open = obj["open"].toDouble();
        candle.high = obj["high"].toDouble();
        candle.low = obj["low"].toDouble();
        candle.close = obj["close"].toDouble();
        candle.volume = obj["volume"].toDouble();
        ohlcData.append(candle);
    }
    m_chart->loadData(ohlcData);
}

void ChartScreen::onRealTimeUpdate(const QString &symbol, const QJsonObject &data)
{
    if (symbol != m_currentSymbol) return;
    if (data.contains("open") && data.contains("close")) {
        OHLCData candle;
        candle.timestamp = data["timestamp"].toInt();
        candle.open = data["open"].toDouble();
        candle.high = data["high"].toDouble();
        candle.low = data["low"].toDouble();
        candle.close = data["close"].toDouble();
        candle.volume = data["volume"].toDouble();
        m_chart->addRealTimeCandle(candle);
    }
}

void ChartScreen::onTemplateApplied(const QJsonObject &config)
{
    Q_UNUSED(config);
}
