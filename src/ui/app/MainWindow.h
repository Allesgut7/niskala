#pragma once

#include <QMainWindow>
#include <QStackedWidget>
#include <QSettings>

class DashboardScreen;
class ChartScreen;
class ScreenerScreen;
class PortfolioScreen;
class MarketOverviewScreen;
class NewsScreen;
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
    void switchToScreen(int index);

private:
    void setupScreens();
    void setupKeyboardShortcuts();

    QStackedWidget *m_stackedWidget = nullptr;
    DashboardScreen *m_dashboardScreen = nullptr;
    ChartScreen *m_chartScreen = nullptr;
    ScreenerScreen *m_screenerScreen = nullptr;
    PortfolioScreen *m_portfolioScreen = nullptr;
    MarketOverviewScreen *m_marketOverviewScreen = nullptr;
    NewsScreen *m_newsScreen = nullptr;
    SettingsScreen *m_settingsScreen = nullptr;
    QSettings *m_settings = nullptr;
};
