#pragma once

#include <QWidget>
#include <QVector>
#include <QSet>
#include <QObject>

struct OHLCData;

#ifdef HAS_QTWEBENGINE
class QWebEngineView;
class QWebChannel;
#endif

class ChartBridge : public QObject
{
    Q_OBJECT
public:
    explicit ChartBridge(QObject *parent = nullptr) : QObject(parent) {}
public slots:
    void requestMoreData(const QString &direction) { emit dataRequested(direction); }
signals:
    void dataRequested(const QString &direction);
};

class LightweightChartWidget : public QWidget
{
    Q_OBJECT

public:
    explicit LightweightChartWidget(QWidget *parent = nullptr);
    ~LightweightChartWidget() override;

    void loadData(const QVector<OHLCData> &data);
    void addRealTimeCandle(const OHLCData &candle);
    void clearChart();
    void loadSymbol(const QString &symbol);
    QString symbol() const { return m_currentSymbol; }
    void setTimeframe(const QString &tf);
    void setChartType(const QString &type);
    void setIndicatorVisible(const QString &name, bool visible);
    void setMA5Visible(bool visible);
    void setMA20Visible(bool visible);
    void setVolumeVisible(bool visible);
    void setActiveDrawingTool(const QString &tool);
    void setDrawingToolbarVisible(bool visible);
    void clearAllDrawings();
    void undoLastDrawing();
    QString getDrawingsJson();
    void loadDrawingsJson(const QString &json);

signals:
    void symbolClicked(const QString &symbol);
    void loadMoreData(const QString &symbol, const QString &direction);

private:
    void setupUI();
    void sendDataToJs(const QVector<OHLCData> &data);

#ifdef HAS_QTWEBENGINE
    QWebEngineView *m_webView = nullptr;
    QWebChannel *m_channel = nullptr;
#endif
    bool m_pageLoaded = false;
    QVector<OHLCData> m_queuedData;
    QString m_currentSymbol;
    QString m_timeframe = "1D";
    QString m_currentChartType = "candlestick";
    QSet<QString> m_activeIndicators;
};
