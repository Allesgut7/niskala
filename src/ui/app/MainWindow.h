#pragma once

#include <QMainWindow>
#include <QDockWidget>
#include <QToolBar>
#include <QStatusBar>
#include <QTabWidget>
#include <QSettings>

class CommandBar;
class TopBannerWidget;
class RunningTradeTicker;
class BottomBanner;
class ChartScreen;
class ScreenerScreen;
class SettingsScreen;
class PortfolioScreen;
class MarketOverviewScreen;
class NewsScreen;

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
    RunningTradeTicker *m_ticker = nullptr;
    BottomBanner *m_bottomBanner = nullptr;

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

    QSettings *m_settings = nullptr;
    int m_currentScreen = 1;
};
