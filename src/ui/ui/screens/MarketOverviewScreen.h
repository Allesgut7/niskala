#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QLabel>

class MarketOverviewScreen : public QWidget
{
    Q_OBJECT

public:
    explicit MarketOverviewScreen(QWidget *parent = nullptr);

private:
    void setupUI();
    void populateData();

    QTableWidget *m_indicesTable = nullptr;
    QTableWidget *m_commoditiesTable = nullptr;
    QTableWidget *m_forexTable = nullptr;
    QTableWidget *m_gainersTable = nullptr;
    QTableWidget *m_losersTable = nullptr;
};
