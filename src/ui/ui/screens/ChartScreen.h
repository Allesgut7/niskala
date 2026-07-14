#pragma once

#include <QWidget>
#include <QJsonArray>
#include <QJsonObject>
#include <QVector>

class LightweightChartWidget;
class ChartToolbarWidget;
class DataManager;
struct OHLCData;

class ChartScreen : public QWidget
{
    Q_OBJECT

public:
    explicit ChartScreen(QWidget *parent = nullptr);

    void loadSymbol(const QString &symbol);

private slots:
    void onSymbolRequested(const QString &symbol);
    void onTimeframeChanged(const QString &tf);
    void onChartTypeChanged(const QString &type);
    void onIndicatorToggled(const QString &name, bool visible);
    void onTradingViewUpdated(const QJsonArray &data);
    void onRealTimeUpdate(const QString &symbol, const QJsonObject &data);
    void onTemplateApplied(const QJsonObject &config);

private:
    void setupUI();
    void setupDataManager();
    void fetchChartData(const QString &symbol, const QString &tf, int candles);
    LightweightChartWidget *m_chart = nullptr;
    ChartToolbarWidget *m_toolbar = nullptr;
    DataManager *m_dataManager = nullptr;
    QString m_currentSymbol;
    QString m_currentTf = "D";
};
