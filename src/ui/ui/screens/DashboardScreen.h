#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QListWidget>
#include <QLabel>

class DashboardScreen : public QWidget
{
    Q_OBJECT

public:
    explicit DashboardScreen(QWidget *parent = nullptr);

private:
    void setupUI();
    void setupStockTable();
    void setupNewsFeed();
    void setupGainersLosers();
    void populateSampleData();

    QTableWidget *m_stockTable = nullptr;
    QListWidget *m_newsList = nullptr;
    QLabel *m_gainersLabel = nullptr;
    QLabel *m_losersLabel = nullptr;
};
