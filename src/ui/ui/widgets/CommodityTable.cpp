#include "CommodityTable.h"
#include <QVBoxLayout>
#include <QHeaderView>

CommodityTable::CommodityTable(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateData();
}

void CommodityTable::setupUI()
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(12, 12, 12, 12);
    layout->setSpacing(4);

    auto *header = new QLabel("COMMODITY");
    header->setStyleSheet("color: #CEE8FF; font-weight: bold; font-size: 12px; padding-left: 8px;");
    layout->addWidget(header);

    m_table = new QTableWidget(7, 4);
    m_table->setHorizontalHeaderLabels({"Commodity", "Price", "Change", "%"});
    m_table->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_table->horizontalHeader()->setSectionResizeMode(0, QHeaderView::ResizeToContents);
    m_table->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_table->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_table->verticalHeader()->setVisible(false);
    m_table->setShowGrid(false);
    m_table->setAlternatingRowColors(true);
    m_table->setStyleSheet(
        "QTableWidget { background-color: transparent; color: #E1E2E7; border: none; }"
        "QTableWidget::item { padding: 4px; }"
        "QHeaderView::section { background-color: transparent; color: #BACBB9; border: none; font-weight: bold; }");
    layout->addWidget(m_table);
}

void CommodityTable::populateData()
{
    struct Commodity { QString name; double price; double change; double pct; };
    QList<Commodity> commodities = {
        {"Gold (XAU/USD)", 2344.75, 18.45, 0.79},
        {"Crude Oil (WTI)", 78.64, 1.42, 1.84},
        {"Coal (Newcastle)", 134.80, -1.20, -0.88},
        {"Nickel (LME)", 16742, -112, -0.66},
        {"Copper (LME)", 9563, 67, 0.71},
        {"CPO (MYR/Ton)", 3890, 36, 0.93},
        {"Natural Gas", 2.31, 0.04, 1.77}
    };

    m_table->setRowCount(commodities.size());
    for (int i = 0; i < commodities.size(); ++i) {
        const auto &c = commodities[i];
        m_table->setItem(i, 0, new QTableWidgetItem(c.name));

        auto *priceItem = new QTableWidgetItem(QString::number(c.price, 'f', 2));
        priceItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 1, priceItem);

        auto *chgItem = new QTableWidgetItem(QString::number(c.change, 'f', 2));
        chgItem->setForeground(c.change >= 0 ? QColor("#75FF9E") : QColor("#FFB3AE"));
        chgItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 2, chgItem);

        QString pctStr = (c.pct >= 0 ? "+" : "") + QString::number(c.pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(c.pct >= 0 ? QColor("#75FF9E") : QColor("#FFB3AE"));
        pctItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 3, pctItem);
    }
}
