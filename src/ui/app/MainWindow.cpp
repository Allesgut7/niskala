#include "MainWindow.h"
#include "../ui/widgets/CommandBar.h"
#include "../ui/widgets/TopBannerWidget.h"
#include "../ui/widgets/CandlestickChart.h"
#include "../ui/widgets/OrderBookWidget.h"
#include "../ui/widgets/FearGreedGauge.h"
#include "../ui/widgets/SectorHeatmap.h"
#include "../ui/screens/ChartScreen.h"
#include "../ui/screens/ScreenerScreen.h"
#include "../ui/screens/SettingsScreen.h"
#include "../ui/theme/ThemeManager.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QAction>
#include <QMenuBar>
#include <QToolBar>
#include <QStatusBar>
#include <QDockWidget>
#include <QTabWidget>
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
}

void MainWindow::setupCommandBar()
{
    m_commandBar = new CommandBar(this);
    addToolBar(Qt::BottomToolBarArea, m_commandBar);
}

void MainWindow::setupDockWidgets()
{
    // === Left: Watchlist + Fear/Greed ===
    m_stockDock = new QDockWidget("Watchlist & Fear/Greed", this);
    m_stockDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *stockWidget = new QWidget();
    auto *stockLayout = new QVBoxLayout(stockWidget);
    stockLayout->setContentsMargins(4, 4, 4, 4);
    stockLayout->setSpacing(4);

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

    // === Right: News ===
    m_newsDock = new QDockWidget("News & Sentiment", this);
    m_newsDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *newsWidget = new QWidget();
    auto *newsLayout = new QVBoxLayout(newsWidget);
    newsLayout->setContentsMargins(4, 4, 4, 4);

    auto *newsList = new QListWidget();
    newsList->setStyleSheet("QListWidget { alternate-background-color: #16213e; }");
    QStringList news = {
        "[CNBC]  BBRI: Laba bersih Q3 naik 15% YoY  [↑]",
        "[IDX]   TLKM: Dividen final Rp 200/saham  [↑]",
        "[Kontan] GOTO: Revenue Q3 tembus Rp 7T  [↑]",
        "[Bisnis] BMRI: Target profit growth 12%  [→]",
        "[Reuters] ADRO: Coal prices rebound  [↑]",
        "[Tempo] UNVR: Penjualan turun 5% Q3  [↓]",
    };
    for (const auto &n : news) {
        auto *item = new QListWidgetItem(n);
        if (n.contains("[↑]")) item->setForeground(QColor("#00d989"));
        else if (n.contains("[↓]")) item->setForeground(QColor("#ff4757"));
        else item->setForeground(QColor("#ffc107"));
        newsList->addItem(item);
    }
    newsLayout->addWidget(newsList);

    m_newsDock->setWidget(newsWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_newsDock);

    // === Center Bottom: Chart Screen ===
    m_chartDock = new QDockWidget("Chart", this);
    m_chartDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                 Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_chartScreen = new ChartScreen();
    m_chartDock->setWidget(m_chartScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_chartDock);

    // === Right Bottom: Order Book ===
    m_orderBookDock = new QDockWidget("Order Book", this);
    m_orderBookDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_orderBook = new OrderBookWidget();
    m_orderBookDock->setWidget(m_orderBook);
    addDockWidget(Qt::RightDockWidgetArea, m_orderBookDock);
    tabifyDockWidget(m_newsDock, m_orderBookDock);

    // === Bottom: Screener ===
    m_screenerDock = new QDockWidget("Screener", this);
    m_screenerDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea |
                                    Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    m_screenerScreen = new ScreenerScreen();
    m_screenerDock->setWidget(m_screenerScreen);
    addDockWidget(Qt::BottomDockWidgetArea, m_screenerDock);
    tabifyDockWidget(m_chartDock, m_screenerDock);

    // === Bottom: Heatmap ===
    m_heatmapDock = new QDockWidget("Sector Heatmap", this);
    m_heatmapDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea);
    m_heatmap = new SectorHeatmap();
    m_heatmapDock->setWidget(m_heatmap);
    addDockWidget(Qt::BottomDockWidgetArea, m_heatmapDock);
    tabifyDockWidget(m_chartDock, m_heatmapDock);

    // === Settings (hidden by default) ===
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
    // F1-F7 screen switching
    new QShortcut(QKeySequence(Qt::Key_F1), this, [this]() { switchToScreen(0); });
    new QShortcut(QKeySequence(Qt::Key_F2), this, [this]() { switchToScreen(1); });
    new QShortcut(QKeySequence(Qt::Key_F3), this, [this]() { switchToScreen(2); });
    new QShortcut(QKeySequence(Qt::Key_F4), this, [this]() { switchToScreen(3); });
    new QShortcut(QKeySequence(Qt::Key_F5), this, [this]() { statusBar()->showMessage("Refreshing...", 2000); });
    new QShortcut(QKeySequence(Qt::Key_F6), this, [this]() { switchToScreen(4); });
    new QShortcut(QKeySequence(Qt::Key_F7), this, [this]() { switchToScreen(5); });

    // Number keys
    new QShortcut(QKeySequence(Qt::Key_1), this, [this]() { switchToScreen(0); });
    new QShortcut(QKeySequence(Qt::Key_2), this, [this]() { switchToScreen(1); });
    new QShortcut(QKeySequence(Qt::Key_3), this, [this]() { switchToScreen(2); });
    new QShortcut(QKeySequence(Qt::Key_4), this, [this]() { switchToScreen(3); });
    new QShortcut(QKeySequence(Qt::Key_6), this, [this]() { switchToScreen(4); });
    new QShortcut(QKeySequence(Qt::Key_7), this, [this]() { switchToScreen(5); });

    // Save/Restore layout
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
            statusBar()->showMessage("Screen: Dashboard (F1)", 2000);
            break;
        case 1: // Chart
            m_chartDock->raise();
            statusBar()->showMessage("Screen: Chart (F2)", 2000);
            break;
        case 2: // Screener
            m_screenerDock->raise();
            statusBar()->showMessage("Screen: Screener (F3)", 2000);
            break;
        case 3: // Portfolio
            statusBar()->showMessage("Screen: Portfolio (F4)", 2000);
            break;
        case 4: // News
            m_newsDock->raise();
            statusBar()->showMessage("Screen: News (F6)", 2000);
            break;
        case 5: // Settings
            m_settingsDock->show();
            m_settingsDock->raise();
            statusBar()->showMessage("Screen: Settings (F7)", 2000);
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
    else if (cmd == "NEWS") switchToScreen(4);
    else if (cmd == "SETTINGS" || cmd == "CONFIG") switchToScreen(5);
    else if (cmd == "BOOK" || cmd == "ORDERBOOK") {
        m_orderBookDock->raise();
        statusBar()->showMessage("Order Book", 2000);
    } else if (cmd == "HEAT" || cmd == "HEATMAP") {
        m_heatmapDock->raise();
        statusBar()->showMessage("Sector Heatmap", 2000);
    } else if (cmd == "HELP") {
        statusBar()->showMessage(
            "Commands: DASH, CHART, SCREENER, PORT, NEWS, SETTINGS, BOOK, HEAT, HELP", 5000);
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

    if (!geometry.isEmpty()) {
        restoreGeometry(geometry);
    }
    if (!state.isEmpty()) {
        restoreState(state);
    }

    int screen = m_settings->value("currentScreen", 1).toInt();
    switchToScreen(screen);

    statusBar()->showMessage("Layout restored", 2000);
}
