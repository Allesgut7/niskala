#pragma once

#include <QMainWindow>
#include <QDockWidget>
#include <QToolBar>
#include <QStatusBar>
#include <QTabWidget>
#include <QSettings>

class CommandBar;
class TopBannerWidget;
class CandlestickChart;
class OrderBookWidget;
class FearGreedGauge;
class SectorHeatmap;
class ChartScreen;
class ScreenerScreen;
class SettingsScreen;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

protected:
    void closeEvent(QCloseEvent *event) override;

private slots:
    void onCommandEntered(const QString &command);
    void switchToScreen(int screenIndex);
    void saveLayout();
    void restoreLayout();

private:
    void setupTopBanner();
    void setupCommandBar();
    void setupDockWidgets();
    void setupStatusBar();
    void setupKeyboardShortcuts();
    void setupConnections();

    TopBannerWidget *m_topBanner = nullptr;
    CommandBar *m_commandBar = nullptr;
    QDockWidget *m_stockDock = nullptr;
    QDockWidget *m_newsDock = nullptr;
    QDockWidget *m_chartDock = nullptr;
    QDockWidget *m_orderBookDock = nullptr;
    QDockWidget *m_heatmapDock = nullptr;
    QDockWidget *m_screenerDock = nullptr;
    QDockWidget *m_settingsDock = nullptr;
    CandlestickChart *m_chart = nullptr;
    OrderBookWidget *m_orderBook = nullptr;
    SectorHeatmap *m_heatmap = nullptr;
    ChartScreen *m_chartScreen = nullptr;
    ScreenerScreen *m_screenerScreen = nullptr;
    SettingsScreen *m_settingsScreen = nullptr;
    QSettings *m_settings = nullptr;
    int m_currentScreen = 1;
};
