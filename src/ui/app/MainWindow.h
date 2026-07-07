#pragma once

#include <QMainWindow>
#include <QDockWidget>
#include <QToolBar>
#include <QStatusBar>
#include <QTabWidget>

class CommandBar;
class TopBannerWidget;
class CandlestickChart;
class OrderBookWidget;
class FearGreedGauge;
class SectorHeatmap;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private slots:
    void onCommandEntered(const QString &command);

private:
    void setupTopBanner();
    void setupCommandBar();
    void setupDockWidgets();
    void setupStatusBar();
    void setupConnections();

    TopBannerWidget *m_topBanner = nullptr;
    CommandBar *m_commandBar = nullptr;
    QDockWidget *m_stockDock = nullptr;
    QDockWidget *m_newsDock = nullptr;
    QDockWidget *m_chartDock = nullptr;
    QDockWidget *m_orderBookDock = nullptr;
    QDockWidget *m_heatmapDock = nullptr;
    CandlestickChart *m_chart = nullptr;
    OrderBookWidget *m_orderBook = nullptr;
    SectorHeatmap *m_heatmap = nullptr;
};
