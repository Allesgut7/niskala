#include "MainWindow.h"
#include "../ui/widgets/CommandBar.h"
#include "../ui/widgets/TopBannerWidget.h"
#include "../ui/widgets/RunningTradeTicker.h"
#include "../ui/widgets/BottomBanner.h"
#include "../ui/widgets/FearGreedGauge.h"
#include "../ui/screens/ChartScreen.h"
#include "../ui/screens/ScreenerScreen.h"
#include "../ui/screens/SettingsScreen.h"
#include "../ui/screens/PortfolioScreen.h"
#include "../ui/screens/MarketOverviewScreen.h"
#include "../ui/screens/NewsScreen.h"
#include "../ui/theme/ThemeManager.h"

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

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    m_settings = new QSettings("Niskala", "Niskala", this);
    setWindowTitle("Niskala - Indonesian Stock Market Terminal");
    setMinimumSize(1400, 900);

    setupTopBanner();
    setupCommandBar();
    setupDockWidgets();
    setupStatusBar();
    setupKeyboardShortcuts();
    setupConnections();
    restoreLayout();
}

MainWindow::~MainWindow() = default;

void MainWindow::closeEvent(QCloseEvent *event)
{
    saveLayout();
    event->accept();
}

void MainWindow::setupTopBanner()
{
    m_topBanner = new TopBannerWidget(this);
    addToolBar(Qt::TopToolBarArea, m_topBanner);

    m_ticker = new RunningTradeTicker(this);
    addToolBar(Qt::TopToolBarArea, m_ticker);

    m_bottomBanner = new BottomBanner(this);
    addToolBar(Qt::BottomToolBarArea, m_bottomBanner);
}

void MainWindow::setupCommandBar()
{
    m_commandBar = new CommandBar(this);
    addToolBar(Qt::BottomToolBarArea, m_commandBar);
}

void MainWindow::setupDockWidgets()
{
    // === Left: Watchlist + Fear/Greed ===
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

    struct { QString sym; double price; double chg; double pct; QString vol; } stocks[] = {
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

    auto *gaugeLayout = new QHBoxLayout();
    auto *fgID = new FearGreedGauge("ID");
    fgID->setScore(55);
    auto *fgAsia = new FearGreedGauge("ASIA");
    fgAsia->setScore(48);
    auto *fgGlobal = new FearGreedGauge("GLOBAL");
    fgGlobal->setScore(62);
    gaugeLayout->addWidget(fgID);
    gaugeLayout->addWidget(fgAsia);
    gaugeLayout->addWidget(fgGlobal);
    stockLayout->addLayout(gaugeLayout);

    m_stockDock->setWidget(stockWidget);
    addDockWidget(Qt::LeftDockWidgetArea, m_stockDock);

    // === Center: Chart ===
    m_chartDock = new QDockWidget("Chart", this);
    m_chartDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                 Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_chartScreen = new ChartScreen();
    m_chartDock->setWidget(m_chartScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_chartDock);

    // === Center: Screener ===
    m_screenerDock = new QDockWidget("Screener", this);
    m_screenerDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                    Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_screenerScreen = new ScreenerScreen();
    m_screenerDock->setWidget(m_screenerScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_screenerDock);
    tabifyDockWidget(m_chartDock, m_screenerDock);

    // === Center: Portfolio ===
    m_portfolioDock = new QDockWidget("Portfolio", this);
    m_portfolioDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                     Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_portfolioScreen = new PortfolioScreen();
    m_portfolioDock->setWidget(m_portfolioScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_portfolioDock);
    tabifyDockWidget(m_chartDock, m_portfolioDock);

    // === Center: Market Overview ===
    m_marketDock = new QDockWidget("Market", this);
    m_marketDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                  Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_marketScreen = new MarketOverviewScreen();
    m_marketDock->setWidget(m_marketScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_marketDock);
    tabifyDockWidget(m_chartDock, m_marketDock);

    // === Right: News ===
    m_newsDock = new QDockWidget("News", this);
    m_newsDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_newsScreen = new NewsScreen();
    m_newsDock->setWidget(m_newsScreen);
    addDockWidget(Qt::RightDockWidgetArea, m_newsDock);

    // === Right: Order Book ===
    m_orderBookDock = new QDockWidget("Order Book", this);
    m_orderBookDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *obWidget = new QWidget();
    auto *obLayout = new QVBoxLayout(obWidget);
    obLayout->setContentsMargins(4, 4, 4, 4);
    auto *obLabel = new QLabel("ORDER BOOK");
    obLabel->setStyleSheet("color: #e94560; font-weight: bold;");
    obLayout->addWidget(obLabel);

    auto *obTable = new QTableWidget(8, 2);
    obTable->setHorizontalHeaderLabels({"Bid", "Ask"});
    obTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    obTable->verticalHeader()->setVisible(false);
    obTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    double bidStart = 9150;
    double askStart = 9200;
    for (int i = 0; i < 8; ++i) {
        double bid = bidStart - (i * 50);
        double ask = askStart + (i * 50);
        auto *bidItem = new QTableWidgetItem(QString::number(bid, 'f', 0));
        bidItem->setForeground(QColor("#00d989"));
        bidItem->setTextAlignment(Qt::AlignRight);
        obTable->setItem(i, 0, bidItem);

        auto *askItem = new QTableWidgetItem(QString::number(ask, 'f', 0));
        askItem->setForeground(QColor("#ff4757"));
        askItem->setTextAlignment(Qt::AlignRight);
        obTable->setItem(i, 1, askItem);
    }
    obLayout->addWidget(obTable);
    m_orderBookDock->setWidget(obWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_orderBookDock);
    tabifyDockWidget(m_newsDock, m_orderBookDock);

    // === Settings (hidden) ===
    m_settingsDock = new QDockWidget("Settings", this);
    m_settingsDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                    Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_settingsScreen = new SettingsScreen();
    m_settingsDock->setWidget(m_settingsScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_settingsDock);
    tabifyDockWidget(m_chartDock, m_settingsDock);
    m_settingsDock->hide();

    // Raise defaults
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
    new QShortcut(QKeySequence(Qt::Key_F1), this, [this]() { switchToScreen(0); });
    new QShortcut(QKeySequence(Qt::Key_F2), this, [this]() { switchToScreen(1); });
    new QShortcut(QKeySequence(Qt::Key_F3), this, [this]() { switchToScreen(2); });
    new QShortcut(QKeySequence(Qt::Key_F4), this, [this]() { switchToScreen(3); });
    new QShortcut(QKeySequence(Qt::Key_F5), this, [this]() { switchToScreen(4); });
    new QShortcut(QKeySequence(Qt::Key_F6), this, [this]() { switchToScreen(5); });
    new QShortcut(QKeySequence(Qt::Key_F7), this, [this]() { switchToScreen(6); });

    new QShortcut(QKeySequence(Qt::Key_1), this, [this]() { switchToScreen(0); });
    new QShortcut(QKeySequence(Qt::Key_2), this, [this]() { switchToScreen(1); });
    new QShortcut(QKeySequence(Qt::Key_3), this, [this]() { switchToScreen(2); });
    new QShortcut(QKeySequence(Qt::Key_4), this, [this]() { switchToScreen(3); });
    new QShortcut(QKeySequence(Qt::Key_5), this, [this]() { switchToScreen(4); });
    new QShortcut(QKeySequence(Qt::Key_6), this, [this]() { switchToScreen(5); });
    new QShortcut(QKeySequence(Qt::Key_7), this, [this]() { switchToScreen(6); });

    new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_S), this, &MainWindow::saveLayout);
    new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_R), this, &MainWindow::restoreLayout);
}

void MainWindow::setupConnections()
{
    connect(m_commandBar, &CommandBar::commandEntered,
            this, &MainWindow::onCommandEntered);
    connect(&ThemeManager::instance(), &ThemeManager::themeChanged,
            this, [this]() { ThemeManager::instance().applyTheme(qApp); });
}

void MainWindow::switchToScreen(int screenIndex)
{
    m_currentScreen = screenIndex;

    switch (screenIndex) {
        case 0: // Dashboard
            m_stockDock->raise();
            m_chartDock->raise();
            statusBar()->showMessage("Dashboard (F1)", 2000);
            break;
        case 1: // Chart
            m_chartDock->raise();
            statusBar()->showMessage("Chart (F2)", 2000);
            break;
        case 2: // Screener
            m_screenerDock->raise();
            statusBar()->showMessage("Screener (F3)", 2000);
            break;
        case 3: // Portfolio
            m_portfolioDock->raise();
            statusBar()->showMessage("Portfolio (F4)", 2000);
            break;
        case 4: // Market
            m_marketDock->raise();
            statusBar()->showMessage("Market Overview (F5)", 2000);
            break;
        case 5: // News
            m_newsDock->raise();
            statusBar()->showMessage("News (F6)", 2000);
            break;
        case 6: // Settings
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
    } else if (cmd == "HELP") {
        statusBar()->showMessage(
            "DASH CHART SCREENER PORT MARKET NEWS SETTINGS BOOK HELP", 5000);
    } else {
        statusBar()->showMessage("Unknown: " + command, 3000);
    }
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
