#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QLabel>

class CommodityTable : public QWidget
{
    Q_OBJECT

public:
    explicit CommodityTable(QWidget *parent = nullptr);

private:
    void setupUI();
    void populateData();

    QTableWidget *m_table = nullptr;
};
