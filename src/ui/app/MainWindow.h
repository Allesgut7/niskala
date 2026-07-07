#pragma once

#include <QMainWindow>
#include <QDockWidget>
#include <QToolBar>
#include <QStatusBar>
#include <QSettings>

class CommandBar;
class ChartScreen;
class ScreenerScreen;
class SettingsScreen;
class PortfolioScreen;
class MarketOverviewScreen;
class NewsScreen;
class DataManager;

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
    void onDataUpdated();
    void onRefreshError(const QString &error);

private:
    void setupMenuBar();
    void setupToolBars();
    void setupDockWidgets();
    void setupStatusBar();
    void setupKeyboardShortcuts();
    void setupConnections();
    void setupDataManager();

    QToolBar *m_topToolBar = nullptr;
    QToolBar *m_tickerToolBar = nullptr;
    QToolBar *m_bottomToolBar = nullptr;
    QWidget *m_topBanner = nullptr;
    QWidget *m_ticker = nullptr;
    QWidget *m_bottomBanner = nullptr;
    QMenuBar *m_menuBar = nullptr;

    QDockWidget *m_stockDock = nullptr;
    QDockWidget *m_chartDock = nullptr;
    QDockWidget *m_screenerDock = nullptr;
    QDockWidget *m_portfolioDock = nullptr;
    QDockWidget *m_marketDock = nullptr;
    QDockWidget *m_newsDock = nullptr;
    QDockWidget *m_orderBookDock = nullptr;
    QDockWidget *m_settingsDock = nullptr;

    ChartScreen *m_chartScreen = nullptr;
    ScreenerScreen *m_screenerScreen = nullptr;
    SettingsScreen *m_settingsScreen = nullptr;
    PortfolioScreen *m_portfolioScreen = nullptr;
    MarketOverviewScreen *m_marketScreen = nullptr;
    NewsScreen *m_newsScreen = nullptr;

    DataManager *m_dataManager = nullptr;
    QSettings *m_settings = nullptr;
    int m_currentScreen = 1;
};
