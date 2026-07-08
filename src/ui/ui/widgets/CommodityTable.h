#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QLabel>

class CommodityTable : public QWidget
{
    Q_OBJECT

public:
    explicit CommodityTable(QWidget *parent = nullptr);

    void updateData(int row, double price, double change, double changePct);

private:
    void setupUI();
    void populateData();

    QTableWidget *m_table = nullptr;
};
