#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QMap>
#include <QPainter>

class CommodityTable : public QWidget
{
    Q_OBJECT

public:
    explicit CommodityTable(QWidget *parent = nullptr);

    void updateData(int row, double price, double change, double changePct);
    void updateBySymbol(const QString &symbol, double price, double change, double changePct);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void setupUI();
    void populateData();
    void initSymbolMap();

    QTableWidget *m_table = nullptr;
    QMap<QString, int> m_symbolToRow;
};
