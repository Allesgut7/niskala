#include "MainWindow.h"
#include "../ui/screens/DashboardScreen.h"

#include <QShortcut>
#include <QCloseEvent>
#include <QApplication>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    m_settings = new QSettings("Niskala", "Niskala", this);
    setWindowTitle("Niskala - Indonesian Stock Market Terminal");
    setMinimumSize(1400, 900);

    // DashboardScreen sebagai central widget
    auto *dashboard = new DashboardScreen();
    setCentralWidget(dashboard);

    setupKeyboardShortcuts();
}

MainWindow::~MainWindow() = default;

void MainWindow::closeEvent(QCloseEvent *event)
{
    m_settings->setValue("geometry", saveGeometry());
    event->accept();
}

void MainWindow::setupKeyboardShortcuts()
{
    QShortcut *f1 = new QShortcut(QKeySequence(Qt::Key_F1), this);
    connect(f1, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Dashboard");
    });

    QShortcut *f2 = new QShortcut(QKeySequence(Qt::Key_F2), this);
    connect(f2, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Chart");
    });

    QShortcut *f3 = new QShortcut(QKeySequence(Qt::Key_F3), this);
    connect(f3, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Screener");
    });

    QShortcut *f4 = new QShortcut(QKeySequence(Qt::Key_F4), this);
    connect(f4, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Portfolio");
    });

    QShortcut *f5 = new QShortcut(QKeySequence(Qt::Key_F5), this);
    connect(f5, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Market");
    });

    QShortcut *f6 = new QShortcut(QKeySequence(Qt::Key_F6), this);
    connect(f6, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - News");
    });

    QShortcut *f7 = new QShortcut(QKeySequence(Qt::Key_F7), this);
    connect(f7, &QShortcut::activated, this, [this]() {
        setWindowTitle("Niskala - Settings");
    });

    QShortcut *ctrlQ = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_Q), this);
    connect(ctrlQ, &QShortcut::activated, this, &QWidget::close);
}
