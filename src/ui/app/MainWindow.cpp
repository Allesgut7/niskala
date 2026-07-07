#include "MainWindow.h"
#include "../ui/widgets/CommandBar.h"
#include "../ui/screens/DashboardScreen.h"
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

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setWindowTitle("Niskala - Indonesian Stock Market Terminal");
    setMinimumSize(1200, 800);

    setupMenuBar();
    setupToolBar();
    setupCommandBar();
    setupDockWidgets();
    setupStatusBar();
    setupConnections();
}

MainWindow::~MainWindow() = default;

void MainWindow::setupMenuBar()
{
    QMenuBar *menuBar = this->menuBar();

    QMenu *fileMenu = menuBar->addMenu("&File");
    fileMenu->addAction("&New Watchlist", this, [](){}, QKeySequence::New);
    fileMenu->addAction("&Open...", this, [](){}, QKeySequence::Open);
    fileMenu->addSeparator();
    fileMenu->addAction("E&xit", this, &QWidget::close, QKeySequence::Quit);

    QMenu *viewMenu = menuBar->addMenu("&View");
    viewMenu->addAction("&Dashboard", this, [](){});
    viewMenu->addAction("&Chart", this, [](){});
    viewMenu->addAction("&Screener", this, [](){});
    viewMenu->addAction("&Portfolio", this, [](){});
    viewMenu->addSeparator();
    viewMenu->addAction("&Settings", this, [](){});

    QMenu *toolsMenu = menuBar->addMenu("&Tools");
    toolsMenu->addAction("&Refresh Data", this, [](){}, QKeySequence::Refresh);
    toolsMenu->addAction("&Export...", this, [](){});

    QMenu *helpMenu = menuBar->addMenu("&Help");
    helpMenu->addAction("&About Niskala", this, [this](){
        QMessageBox::about(this, "About Niskala",
            "Niskala v2.0.0\n\n"
            "Professional Indonesian Stock Market Terminal\n"
            "with AI-powered sentiment analysis.\n\n"
            "Built with Qt6");
    });
    helpMenu->addAction("&Keyboard Shortcuts", this, [](){});
}

void MainWindow::setupToolBar()
{
    m_toolBar = addToolBar("Main");
    m_toolBar->setMovable(false);
    m_toolBar->setIconSize(QSize(16, 16));

    m_toolBar->addAction("Dashboard", this, [](){});
    m_toolBar->addAction("Chart", this, [](){});
    m_toolBar->addAction("Screener", this, [](){});
    m_toolBar->addAction("Portfolio", this, [](){});
    m_toolBar->addSeparator();
    m_toolBar->addAction("Refresh", this, [](){});
    m_toolBar->addSeparator();
    m_toolBar->addAction("Settings", this, [](){});
}

void MainWindow::setupCommandBar()
{
    m_commandBar = new CommandBar(this);
    addToolBar(Qt::BottomToolBarArea, m_commandBar);
}

void MainWindow::setupDockWidgets()
{
    // Stock Table Dock (left)
    m_stockDock = new QDockWidget("Watchlist", this);
    m_stockDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *stockWidget = new QWidget();
    auto *stockLayout = new QVBoxLayout(stockWidget);
    auto *stockTable = new QTableWidget(10, 7);
    stockTable->setHorizontalHeaderLabels({"Symbol", "Price", "Change", "Chg%", "Volume", "High", "Low"});
    stockTable->horizontalHeader()->setStretchLastSection(true);
    stockTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    stockTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    stockTable->setAlternatingRowColors(true);
    stockLayout->addWidget(stockTable);
    m_stockDock->setWidget(stockWidget);
    addDockWidget(Qt::LeftDockWidgetArea, m_stockDock);

    // News Dock (right)
    m_newsDock = new QDockWidget("News & Sentiment", this);
    m_newsDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    auto *newsWidget = new QWidget();
    auto *newsLayout = new QVBoxLayout(newsWidget);
    auto *newsList = new QListWidget();
    newsList->addItem("BBRI: Laba bersih Q3 naik 15% YoY");
    newsList->addItem("TLKM: Dividen final ditetapkan Rp 200/saham");
    newsList->addItem("GOTO: Revenue Q3 tembus Rp 7T");
    newsLayout->addWidget(newsList);
    m_newsDock->setWidget(newsWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_newsDock);

    // Chart Dock (center bottom)
    m_chartDock = new QDockWidget("Chart", this);
    m_chartDock->setAllowedAreas(Qt::BottomDockWidgetArea | Qt::TopDockWidgetArea);
    auto *chartWidget = new QWidget();
    auto *chartLayout = new QVBoxLayout(chartWidget);
    auto *chartLabel = new QLabel("Candlestick Chart - Select a stock");
    chartLabel->setAlignment(Qt::AlignCenter);
    chartLabel->setStyleSheet("font-size: 14px; color: #888;");
    chartLayout->addWidget(chartLabel);
    m_chartDock->setWidget(chartWidget);
    addDockWidget(Qt::BottomDockWidgetArea, m_chartDock);

    // Tabify dock widgets
    tabifyDockWidget(m_stockDock, m_chartDock);
    m_stockDock->raise();
}

void MainWindow::setupStatusBar()
{
    QStatusBar *statusBar = this->statusBar();

    auto *marketLabel = new QLabel("  IHSG: 7,123.45 (+0.5%)  ");
    marketLabel->setStyleSheet("color: #00d989; font-weight: bold;");
    statusBar->addWidget(marketLabel);

    auto *connectionLabel = new QLabel("  Connected  ");
    connectionLabel->setStyleSheet("color: #00d989;");
    statusBar->addWidget(connectionLabel);

    statusBar->addPermanentWidget(new QLabel("Niskala v2.0.0  "));
}

void MainWindow::setupConnections()
{
    connect(m_commandBar, &CommandBar::commandEntered,
            this, &MainWindow::onCommandEntered);
    connect(&ThemeManager::instance(), &ThemeManager::themeChanged,
            this, &MainWindow::onThemeChanged);
}

void MainWindow::onCommandEntered(const QString &command)
{
    QString cmd = command.toUpper().trimmed();

    if (cmd == "DASH" || cmd == "DASHBOARD") {
        m_stockDock->raise();
    } else if (cmd == "CHART") {
        m_chartDock->raise();
    } else if (cmd == "NEWS") {
        m_newsDock->raise();
    } else if (cmd == "HELP") {
        statusBar()->showMessage("Commands: DASH, CHART, NEWS, SCREENER, PORT, SETTINGS, HELP", 5000);
    } else {
        statusBar()->showMessage("Unknown command: " + command, 3000);
    }
}

void MainWindow::onThemeChanged()
{
    ThemeManager::instance().applyTheme(qApp);
}
