#include "MainWindow.h"
#include "../ui/widgets/CommandBar.h"
#include "../ui/screens/ChartScreen.h"
#include "../ui/screens/ScreenerScreen.h"
#include "../ui/screens/SettingsScreen.h"
#include "../ui/screens/PortfolioScreen.h"
#include "../ui/screens/MarketOverviewScreen.h"
#include "../ui/screens/NewsScreen.h"
#include "../ui/theme/ThemeManager.h"
#include "../core/DataManager.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMenuBar>
#include <QStatusBar>
#include <QDockWidget>
#include <QMessageBox>
#include <QApplication>
#include <QTableWidget>
#include <QHeaderView>
#include <QShortcut>
#include <QCloseEvent>
#include <QFileDialog>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    m_settings = new QSettings("Niskala", "Niskala", this);
    setWindowTitle("Niskala - Indonesian Stock Market Terminal");
    setMinimumSize(1400, 900);

    setupMenuBar();
    setupToolBars();
    setupDockWidgets();
    setupStatusBar();
    setupKeyboardShortcuts();
    setupDataManager();
    setupConnections();
    restoreLayout();
}

MainWindow::~MainWindow() = default;

void MainWindow::closeEvent(QCloseEvent *event)
{
    saveLayout();
    m_dataManager->stopAutoRefresh();
    event->accept();
}

void MainWindow::setupMenuBar()
{
    m_menuBar = menuBar();
    m_menuBar->setStyleSheet(
        "QMenuBar { background-color: #0f3460; color: #e0e0e0; border-bottom: 1px solid #e94560; }"
        "QMenuBar::item:selected { background-color: #e94560; }"
        "QMenu { background-color: #16213e; border: 1px solid #0f3460; color: #e0e0e0; }"
        "QMenu::item:selected { background-color: #e94560; }");

    auto *fileMenu = m_menuBar->addMenu("&File");
    QAction *refreshAction = fileMenu->addAction("&Refresh Data");
    connect(refreshAction, &QAction::triggered, this, [this]() {
        m_dataManager->refreshAll();
    });

    fileMenu->addSeparator();
    QAction *exitAction = fileMenu->addAction("E&xit");
    connect(exitAction, &QAction::triggered, this, &QWidget::close);

    auto *viewMenu = m_menuBar->addMenu("&View");
    QAction *dashAction = viewMenu->addAction("&Dashboard (F1)");
    connect(dashAction, &QAction::triggered, this, [this]() { switchToScreen(0); });
    QAction *chartAction = viewMenu->addAction("&Chart (F2)");
    connect(chartAction, &QAction::triggered, this, [this]() { switchToScreen(1); });
    QAction *screenAction = viewMenu->addAction("&Screener (F3)");
    connect(screenAction, &QAction::triggered, this, [this]() { switchToScreen(2); });
    QAction *portAction = viewMenu->addAction("&Portfolio (F4)");
    connect(portAction, &QAction::triggered, this, [this]() { switchToScreen(3); });
    QAction *mktAction = viewMenu->addAction("&Market Overview (F5)");
    connect(mktAction, &QAction::triggered, this, [this]() { switchToScreen(4); });
    QAction *newsAction = viewMenu->addAction("&News (F6)");
    connect(newsAction, &QAction::triggered, this, [this]() { switchToScreen(5); });
    viewMenu->addSeparator();
    QAction *settingsAction = viewMenu->addAction("&Settings (F7)");
    connect(settingsAction, &QAction::triggered, this, [this]() { switchToScreen(6); });

    auto *toolsMenu = m_menuBar->addMenu("&Tools");
    QAction *autoOnAction = toolsMenu->addAction("Auto-Refresh &On");
    connect(autoOnAction, &QAction::triggered, this, [this]() {
        m_dataManager->startAutoRefresh(30);
        statusBar()->showMessage("Auto-refresh enabled (30s)", 3000);
    });
    QAction *autoOffAction = toolsMenu->addAction("Auto-Refresh &Off");
    connect(autoOffAction, &QAction::triggered, this, [this]() {
        m_dataManager->stopAutoRefresh();
        statusBar()->showMessage("Auto-refresh disabled", 3000);
    });
    toolsMenu->addSeparator();
    QAction *saveAction = toolsMenu->addAction("&Save Layout");
    connect(saveAction, &QAction::triggered, this, &MainWindow::saveLayout);
    QAction *restoreAction = toolsMenu->addAction("&Restore Layout");
    connect(restoreAction, &QAction::triggered, this, &MainWindow::restoreLayout);

    auto *helpMenu = m_menuBar->addMenu("&Help");
    QAction *shortcutsAction = helpMenu->addAction("&Keyboard Shortcuts");
    connect(shortcutsAction, &QAction::triggered, this, [this]() {
        QMessageBox::information(this, "Keyboard Shortcuts",
            "F1 - Dashboard\nF2 - Chart\nF3 - Screener\nF4 - Portfolio\n"
            "F5 - Market Overview\nF6 - News\nF7 - Settings\n"
            "Ctrl+S - Save Layout\nCtrl+R - Restore Layout");
    });
    QAction *aboutAction = helpMenu->addAction("&About Niskala");
    connect(aboutAction, &QAction::triggered, this, [this]() {
        QMessageBox::about(this, "About Niskala",
            "<h2>Niskala Trading Terminal</h2>"
            "<p>Version 2.0.0</p>"
            "<p>Professional Indonesian Stock Market Terminal</p>"
            "<p>Built with Qt6</p>");
    });
}

void MainWindow::setupToolBars()
{
    m_topToolBar = addToolBar("Market");
    m_topToolBar->setMovable(false);
    m_topToolBar->setStyleSheet("background-color: #0f3460; border-bottom: 1px solid #e94560;");

    auto *marketLabel = new QLabel("  IHSG 7,123.45 +0.50%  |  S&P500 5,432.10 +1.20%  |  Gold 2,050.30 +0.20%  |  USD/IDR 15,600 +0.30%  ");
    marketLabel->setStyleSheet("color: #e0e0e0; font-family: monospace; font-size: 11px;");
    m_topToolBar->addWidget(marketLabel);

    m_tickerToolBar = addToolBar("Ticker");
    m_tickerToolBar->setMovable(false);
    m_tickerToolBar->setStyleSheet("background-color: #16213e; border-bottom: 1px solid #0f3460;");

    auto *tickerLabel = new QLabel("  BBCA 9200 150K  BBRI 4800 200K  BMRI 6150 80K  TLKM 2850 120K  GOTO 85 500K  ADRO 1520 90K  ");
    tickerLabel->setStyleSheet("color: #ffc107; font-family: monospace; font-size: 11px; font-weight: bold;");
    m_tickerToolBar->addWidget(tickerLabel);

    m_bottomToolBar = new QToolBar("Gainers/Losers", this);
    addToolBar(Qt::BottomToolBarArea, m_bottomToolBar);
    m_bottomToolBar->setMovable(false);
    m_bottomToolBar->setStyleSheet("background-color: #0f3460; border-top: 1px solid #e94560;");

    auto *glLabel = new QLabel("  GAINERS: ICBP +1.82%  ADRO +2.01%  BBCA +1.66%  BREN +1.80%    |    LOSERS: GOTO -2.30%  UNVR -1.73%  BBRI -1.03%  ");
    glLabel->setStyleSheet("color: #e0e0e0; font-family: monospace; font-size: 10px;");
    m_bottomToolBar->addWidget(glLabel);

    auto *cmdToolBar = new QToolBar("Command", this);
    addToolBar(Qt::BottomToolBarArea, cmdToolBar);
    cmdToolBar->setMovable(false);
    auto *cmdBar = new CommandBar();
    connect(cmdBar, &CommandBar::commandEntered, this, &MainWindow::onCommandEntered);
    cmdToolBar->addWidget(cmdBar);
}

void MainWindow::setupDockWidgets()
{
    m_stockDock = new QDockWidget("Watchlist", this);
    m_stockDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *stockWidget = new QWidget();
    auto *stockLayout = new QVBoxLayout(stockWidget);
    stockLayout->setContentsMargins(4, 4, 4, 4);

    auto *stockTable = new QTableWidget(10, 7);
    stockTable->setHorizontalHeaderLabels({"Symbol", "Price", "Chg", "Chg%", "Vol", "High", "Low"});
    stockTable->horizontalHeader()->setSectionResizeMode(0, QHeaderView::ResizeToContents);
    stockTable->horizontalHeader()->setSectionResizeMode(4, QHeaderView::Stretch);
    stockTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    stockTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    stockTable->setAlternatingRowColors(true);
    stockTable->verticalHeader()->setVisible(false);

    struct StockData { QString sym; double price; double chg; double pct; QString vol; };
    StockData stocks[] = {
        {"BBCA", 9200, 150, 1.66, "45M"},
        {"BBRI", 4800, -50, -1.03, "38M"},
        {"BMRI", 6150, 75, 1.23, "28M"},
        {"TLKM", 2850, 25, 0.88, "22M"},
        {"GOTO", 85, -2, -2.30, "156M"},
        {"ADRO", 1520, 30, 2.01, "18M"},
        {"UNVR", 4250, -75, -1.73, "12M"},
        {"ICBP", 11200, 200, 1.82, "8M"},
    };

    stockTable->setRowCount(8);
    for (int i = 0; i < 8; ++i) {
        stockTable->setItem(i, 0, new QTableWidgetItem(stocks[i].sym));
        stockTable->setItem(i, 1, new QTableWidgetItem(QString::number(stocks[i].price)));
        auto *chgItem = new QTableWidgetItem(QString::number(stocks[i].chg));
        chgItem->setForeground(stocks[i].chg >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        stockTable->setItem(i, 2, chgItem);
        QString pctStr = (stocks[i].pct >= 0 ? "+" : "") + QString::number(stocks[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(stocks[i].pct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        stockTable->setItem(i, 3, pctItem);
        stockTable->setItem(i, 4, new QTableWidgetItem(stocks[i].vol));
    }
    stockLayout->addWidget(stockTable);
    m_stockDock->setWidget(stockWidget);
    addDockWidget(Qt::LeftDockWidgetArea, m_stockDock);

    m_chartDock = new QDockWidget("Chart", this);
    m_chartDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                 Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_chartScreen = new ChartScreen();
    m_chartDock->setWidget(m_chartScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_chartDock);

    m_screenerDock = new QDockWidget("Screener", this);
    m_screenerDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                    Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_screenerScreen = new ScreenerScreen();
    m_screenerDock->setWidget(m_screenerScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_screenerDock);
    tabifyDockWidget(m_chartDock, m_screenerDock);

    m_portfolioDock = new QDockWidget("Portfolio", this);
    m_portfolioDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                     Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_portfolioScreen = new PortfolioScreen();
    m_portfolioDock->setWidget(m_portfolioScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_portfolioDock);
    tabifyDockWidget(m_chartDock, m_portfolioDock);

    m_marketDock = new QDockWidget("Market", this);
    m_marketDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                  Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_marketScreen = new MarketOverviewScreen();
    m_marketDock->setWidget(m_marketScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_marketDock);
    tabifyDockWidget(m_chartDock, m_marketDock);

    m_newsDock = new QDockWidget("News", this);
    m_newsDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_newsScreen = new NewsScreen();
    m_newsDock->setWidget(m_newsScreen);
    addDockWidget(Qt::RightDockWidgetArea, m_newsDock);

    m_orderBookDock = new QDockWidget("Order Book", this);
    m_orderBookDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *obWidget = new QWidget();
    auto *obLayout = new QVBoxLayout(obWidget);
    obLayout->setContentsMargins(4, 4, 4, 4);
    auto *obLabel = new QLabel("ORDER BOOK - BBCA");
    obLabel->setStyleSheet("color: #e94560; font-weight: bold;");
    obLayout->addWidget(obLabel);

    auto *obTable = new QTableWidget(8, 2);
    obTable->setHorizontalHeaderLabels({"Bid", "Ask"});
    obTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    obTable->verticalHeader()->setVisible(false);
    obTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    double bidStart = 9150, askStart = 9200;
    for (int i = 0; i < 8; ++i) {
        auto *bidItem = new QTableWidgetItem(QString::number(bidStart - (i * 50), 'f', 0));
        bidItem->setForeground(QColor("#00d989"));
        bidItem->setTextAlignment(Qt::AlignRight);
        obTable->setItem(i, 0, bidItem);

        auto *askItem = new QTableWidgetItem(QString::number(askStart + (i * 50), 'f', 0));
        askItem->setForeground(QColor("#ff4757"));
        askItem->setTextAlignment(Qt::AlignRight);
        obTable->setItem(i, 1, askItem);
    }
    obLayout->addWidget(obTable);
    m_orderBookDock->setWidget(obWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_orderBookDock);
    tabifyDockWidget(m_newsDock, m_orderBookDock);

    m_settingsDock = new QDockWidget("Settings", this);
    m_settingsDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                    Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_settingsScreen = new SettingsScreen();
    m_settingsDock->setWidget(m_settingsScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_settingsDock);
    tabifyDockWidget(m_chartDock, m_settingsDock);
    m_settingsDock->hide();

    m_stockDock->raise();
    m_chartDock->raise();
}

void MainWindow::setupStatusBar()
{
    QStatusBar *statusBar = this->statusBar();

    auto *marketLabel = new QLabel("  IHSG: 7,123.45 (+0.50%)  ");
    marketLabel->setStyleSheet("color: #00d989; font-weight: bold;");
    statusBar->addWidget(marketLabel);

    auto *connectionLabel = new QLabel("  Connected  ");
    connectionLabel->setStyleSheet("color: #00d989;");
    statusBar->addWidget(connectionLabel);

    statusBar->addPermanentWidget(new QLabel("Niskala v2.0.0  "));
}

void MainWindow::setupKeyboardShortcuts()
{
    QShortcut *f1 = new QShortcut(QKeySequence(Qt::Key_F1), this);
    connect(f1, &QShortcut::activated, this, [this]() { switchToScreen(0); });

    QShortcut *f2 = new QShortcut(QKeySequence(Qt::Key_F2), this);
    connect(f2, &QShortcut::activated, this, [this]() { switchToScreen(1); });

    QShortcut *f3 = new QShortcut(QKeySequence(Qt::Key_F3), this);
    connect(f3, &QShortcut::activated, this, [this]() { switchToScreen(2); });

    QShortcut *f4 = new QShortcut(QKeySequence(Qt::Key_F4), this);
    connect(f4, &QShortcut::activated, this, [this]() { switchToScreen(3); });

    QShortcut *f5 = new QShortcut(QKeySequence(Qt::Key_F5), this);
    connect(f5, &QShortcut::activated, this, [this]() { switchToScreen(4); });

    QShortcut *f6 = new QShortcut(QKeySequence(Qt::Key_F6), this);
    connect(f6, &QShortcut::activated, this, [this]() { switchToScreen(5); });

    QShortcut *f7 = new QShortcut(QKeySequence(Qt::Key_F7), this);
    connect(f7, &QShortcut::activated, this, [this]() { switchToScreen(6); });

    QShortcut *ctrlS = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_S), this);
    connect(ctrlS, &QShortcut::activated, this, &MainWindow::saveLayout);

    QShortcut *ctrlR = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_R), this);
    connect(ctrlR, &QShortcut::activated, this, &MainWindow::restoreLayout);

    QShortcut *ctrlQ = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_Q), this);
    connect(ctrlQ, &QShortcut::activated, this, &QWidget::close);
}

void MainWindow::setupDataManager()
{
    m_dataManager = new DataManager(this);
    m_dataManager->startAutoRefresh(30);
}

void MainWindow::setupConnections()
{
    connect(&ThemeManager::instance(), &ThemeManager::themeChanged,
            this, [this]() { ThemeManager::instance().applyTheme(qApp); });
    connect(m_dataManager, &DataManager::refreshFinished,
            this, &MainWindow::onDataUpdated);
    connect(m_dataManager, &DataManager::errorOccurred,
            this, &MainWindow::onRefreshError);
}

void MainWindow::switchToScreen(int screenIndex)
{
    m_currentScreen = screenIndex;

    switch (screenIndex) {
        case 0:
            m_stockDock->raise();
            m_chartDock->raise();
            statusBar()->showMessage("Dashboard (F1)", 2000);
            break;
        case 1:
            m_chartDock->raise();
            statusBar()->showMessage("Chart (F2)", 2000);
            break;
        case 2:
            m_screenerDock->raise();
            statusBar()->showMessage("Screener (F3)", 2000);
            break;
        case 3:
            m_portfolioDock->raise();
            statusBar()->showMessage("Portfolio (F4)", 2000);
            break;
        case 4:
            m_marketDock->raise();
            statusBar()->showMessage("Market Overview (F5)", 2000);
            break;
        case 5:
            m_newsDock->raise();
            statusBar()->showMessage("News (F6)", 2000);
            break;
        case 6:
            m_settingsDock->show();
            m_settingsDock->raise();
            statusBar()->showMessage("Settings (F7)", 2000);
            break;
    }
}

void MainWindow::onCommandEntered(const QString &command)
{
    QString cmd = command.toUpper().trimmed();

    if (cmd == "DASH" || cmd == "DASHBOARD") switchToScreen(0);
    else if (cmd == "CHART") switchToScreen(1);
    else if (cmd == "SCREENER" || cmd == "SCREEN") switchToScreen(2);
    else if (cmd == "PORT" || cmd == "PORTFOLIO") switchToScreen(3);
    else if (cmd == "MARKET" || cmd == "MKT") switchToScreen(4);
    else if (cmd == "NEWS") switchToScreen(5);
    else if (cmd == "SETTINGS" || cmd == "CONFIG") switchToScreen(6);
    else if (cmd == "BOOK" || cmd == "ORDERBOOK") {
        m_orderBookDock->raise();
        statusBar()->showMessage("Order Book", 2000);
    } else if (cmd == "REFRESH") {
        m_dataManager->refreshAll();
        statusBar()->showMessage("Refreshing...", 2000);
    } else if (cmd == "HELP") {
        statusBar()->showMessage(
            "DASH CHART SCREENER PORT MARKET NEWS SETTINGS BOOK REFRESH HELP", 5000);
    } else {
        statusBar()->showMessage("Unknown: " + command, 3000);
    }
}

void MainWindow::onDataUpdated()
{
    statusBar()->showMessage("Data updated", 2000);
}

void MainWindow::onRefreshError(const QString &error)
{
    statusBar()->showMessage("Error: " + error, 5000);
}

void MainWindow::saveLayout()
{
    m_settings->setValue("geometry", saveGeometry());
    m_settings->setValue("windowState", saveState());
    m_settings->setValue("currentScreen", m_currentScreen);
    statusBar()->showMessage("Layout saved", 2000);
}

void MainWindow::restoreLayout()
{
    QByteArray geometry = m_settings->value("geometry").toByteArray();
    QByteArray state = m_settings->value("windowState").toByteArray();

    if (!geometry.isEmpty()) restoreGeometry(geometry);
    if (!state.isEmpty()) restoreState(state);

    int screen = m_settings->value("currentScreen", 1).toInt();
    switchToScreen(screen);
}
