#pragma once

#include <QWidget>
#include <QVector>

struct OHLCData;

class QWebEngineView;
class QWebChannel;

class LightweightChartWidget : public QWidget
{
    Q_OBJECT

public:
    explicit LightweightChartWidget(QWidget *parent = nullptr);
    ~LightweightChartWidget() override;

    void loadData(const QVector<OHLCData> &data);
    void loadSymbol(const QString &symbol);
    void setTimeframe(const QString &tf);
    void setMA5Visible(bool visible);
    void setMA20Visible(bool visible);
    void setVolumeVisible(bool visible);

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();
    void sendDataToJs(const QVector<OHLCData> &data);

    QWebEngineView *m_webView = nullptr;
    QWebChannel *m_channel = nullptr;
    QString m_currentSymbol;
    QString m_timeframe = "1D";
};
