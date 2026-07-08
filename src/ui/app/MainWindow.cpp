#include "MainWindow.h"
#include "../ui/widgets/NavigationBar.h"
#include "../ui/widgets/FooterWidget.h"
#include "../ui/screens/DashboardScreen.h"
#include "../ui/screens/ChartScreen.h"
#include "../ui/screens/ScreenerScreen.h"
#include "../ui/screens/PortfolioScreen.h"
#include "../ui/screens/MarketOverviewScreen.h"
#include "../ui/screens/NewsScreen.h"
#include "../ui/screens/SettingsScreen.h"

#include <QShortcut>
#include <QCloseEvent>
#include <QApplication>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    m_settings = new QSettings("Niskala", "Niskala", this);
    setWindowTitle("Niskala - Indonesian Stock Market Terminal");
    setMinimumSize(1400, 900);

    setupScreens();
    setupKeyboardShortcuts();

    // Restore geometry
    QByteArray geometry = m_settings->value("geometry").toByteArray();
    if (!geometry.isEmpty()) {
        restoreGeometry(geometry);
    }
}

MainWindow::~MainWindow() = default;

void MainWindow::closeEvent(QCloseEvent *event)
{
    m_settings->setValue("geometry", saveGeometry());
    event->accept();
}

void MainWindow::setupScreens()
{
    // Central widget dengan layout
    auto *centralWidget = new QWidget();
    auto *mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);

    // NavigationBar (widget biasa, di atas)
    m_navBar = new NavigationBar();
    mainLayout->addWidget(m_navBar);

    // QStackedWidget (di bawah)
    m_stackedWidget = new QStackedWidget();

    m_dashboardScreen = new DashboardScreen();
    m_chartScreen = new ChartScreen();
    m_screenerScreen = new ScreenerScreen();
    m_portfolioScreen = new PortfolioScreen();
    m_marketOverviewScreen = new MarketOverviewScreen();
    m_newsScreen = new NewsScreen();
    m_settingsScreen = new SettingsScreen();

    m_stackedWidget->addWidget(m_dashboardScreen);      // 0
    m_stackedWidget->addWidget(m_chartScreen);          // 1
    m_stackedWidget->addWidget(m_screenerScreen);       // 2
    m_stackedWidget->addWidget(m_portfolioScreen);      // 3
    m_stackedWidget->addWidget(m_marketOverviewScreen); // 4
    m_stackedWidget->addWidget(m_newsScreen);           // 5
    m_stackedWidget->addWidget(m_settingsScreen);       // 6

    mainLayout->addWidget(m_stackedWidget, 1);

    // FooterWidget (bottom)
    m_footer = new FooterWidget();
    m_footer->setVersion("v2.0.0");
    mainLayout->addWidget(m_footer);

    setCentralWidget(centralWidget);

    // Connect NavigationBar ke screen switching
    connect(m_navBar, &NavigationBar::tabClicked,
            this, &MainWindow::switchToScreen);
}

void MainWindow::switchToScreen(int index)
{
    if (index >= 0 && index < m_stackedWidget->count()) {
        m_stackedWidget->setCurrentIndex(index);

        QStringList screenNames = {
            "Dashboard", "Chart", "Screener", "Portfolio",
            "Market Overview", "News", "Settings"
        };

        if (index < screenNames.size()) {
            setWindowTitle("Niskala - " + screenNames[index]);
        }
    }
}

void MainWindow::setupKeyboardShortcuts()
{
    // F1-F7 screen switching
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

    // Number keys
    QShortcut *key1 = new QShortcut(QKeySequence(Qt::Key_1), this);
    connect(key1, &QShortcut::activated, this, [this]() { switchToScreen(0); });

    QShortcut *key2 = new QShortcut(QKeySequence(Qt::Key_2), this);
    connect(key2, &QShortcut::activated, this, [this]() { switchToScreen(1); });

    QShortcut *key3 = new QShortcut(QKeySequence(Qt::Key_3), this);
    connect(key3, &QShortcut::activated, this, [this]() { switchToScreen(2); });

    QShortcut *key4 = new QShortcut(QKeySequence(Qt::Key_4), this);
    connect(key4, &QShortcut::activated, this, [this]() { switchToScreen(3); });

    QShortcut *key5 = new QShortcut(QKeySequence(Qt::Key_5), this);
    connect(key5, &QShortcut::activated, this, [this]() { switchToScreen(4); });

    QShortcut *key6 = new QShortcut(QKeySequence(Qt::Key_6), this);
    connect(key6, &QShortcut::activated, this, [this]() { switchToScreen(5); });

    QShortcut *key7 = new QShortcut(QKeySequence(Qt::Key_7), this);
    connect(key7, &QShortcut::activated, this, [this]() { switchToScreen(6); });

    // Quit
    QShortcut *quit = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_Q), this);
    connect(quit, &QShortcut::activated, this, &QWidget::close);
}
