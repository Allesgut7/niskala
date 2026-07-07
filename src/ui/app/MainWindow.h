#pragma once

#include <QMainWindow>
#include <QDockWidget>
#include <QMenuBar>
#include <QToolBar>
#include <QStatusBar>
#include <QTabWidget>

class CommandBar;
class DashboardScreen;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private slots:
    void onCommandEntered(const QString &command);
    void onThemeChanged();

private:
    void setupMenuBar();
    void setupToolBar();
    void setupCommandBar();
    void setupDockWidgets();
    void setupStatusBar();
    void setupConnections();

    QToolBar *m_toolBar = nullptr;
    CommandBar *m_commandBar = nullptr;
    QTabWidget *m_tabWidget = nullptr;
    QDockWidget *m_stockDock = nullptr;
    QDockWidget *m_newsDock = nullptr;
    QDockWidget *m_chartDock = nullptr;
    DashboardScreen *m_dashboard = nullptr;
};
