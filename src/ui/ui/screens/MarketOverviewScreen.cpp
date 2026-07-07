#include "MarketOverviewScreen.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QHeaderView>

MarketOverviewScreen::MarketOverviewScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateData();
}

void MarketOverviewScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(8);

    auto *title = new QLabel("MARKET OVERVIEW");
    title->setStyleSheet("color: #e94560; font-size: 16px; font-weight: bold;");
    mainLayout->addWidget(title);

    auto *topLayout = new QHBoxLayout();

    // Indices
    auto *idxWidget = new QWidget();
    auto *idxLayout = new QVBoxLayout(idxWidget);
    idxLayout->setContentsMargins(0, 0, 0, 0);

    auto *idxLabel = new QLabel("INDICES");
    idxLabel->setStyleSheet("color: #00bcd4; font-weight: bold;");
    idxLayout->addWidget(idxLabel);

    m_indicesTable = new QTableWidget(6, 4);
    m_indicesTable->setHorizontalHeaderLabels({"Name", "Value", "Change", "Chg%"});
    m_indicesTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_indicesTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_indicesTable->verticalHeader()->setVisible(false);
    m_indicesTable->setAlternatingRowColors(true);
    idxLayout->addWidget(m_indicesTable);
    topLayout->addWidget(idxWidget);

    // Commodities
    auto *cmdWidget = new QWidget();
    auto *cmdLayout = new QVBoxLayout(cmdWidget);
    cmdLayout->setContentsMargins(0, 0, 0, 0);

    auto *cmdLabel = new QLabel("COMMODITIES");
    cmdLabel->setStyleSheet("color: #ffc107; font-weight: bold;");
    cmdLayout->addWidget(cmdLabel);

    m_commoditiesTable = new QTableWidget(5, 4);
    m_commoditiesTable->setHorizontalHeaderLabels({"Name", "Price", "Change", "Chg%"});
    m_commoditiesTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_commoditiesTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_commoditiesTable->verticalHeader()->setVisible(false);
    m_commoditiesTable->setAlternatingRowColors(true);
    cmdLayout->addWidget(m_commoditiesTable);
    topLayout->addWidget(cmdWidget);

    // Forex
    auto *fxWidget = new QWidget();
    auto *fxLayout = new QVBoxLayout(fxWidget);
    fxLayout->setContentsMargins(0, 0, 0, 0);

    auto *fxLabel = new QLabel("FOREX");
    fxLabel->setStyleSheet("color: #e94560; font-weight: bold;");
    fxLayout->addWidget(fxLabel);

    m_forexTable = new QTableWidget(5, 4);
    m_forexTable->setHorizontalHeaderLabels({"Pair", "Rate", "Change", "Chg%"});
    m_forexTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_forexTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_forexTable->verticalHeader()->setVisible(false);
    m_forexTable->setAlternatingRowColors(true);
    fxLayout->addWidget(m_forexTable);
    topLayout->addWidget(fxWidget);

    mainLayout->addLayout(topLayout);

    // Gainers/Losers
    auto *glLayout = new QHBoxLayout();

    auto *gainWidget = new QWidget();
    auto *gainLayout = new QVBoxLayout(gainWidget);
    gainLayout->setContentsMargins(0, 0, 0, 0);

    auto *gainLabel = new QLabel("TOP GAINERS");
    gainLabel->setStyleSheet("color: #00d989; font-weight: bold;");
    gainLayout->addWidget(gainLabel);

    m_gainersTable = new QTableWidget(5, 3);
    m_gainersTable->setHorizontalHeaderLabels({"Symbol", "Price", "Chg%"});
    m_gainersTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_gainersTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_gainersTable->verticalHeader()->setVisible(false);
    gainLayout->addWidget(m_gainersTable);
    glLayout->addWidget(gainWidget);

    auto *loseWidget = new QWidget();
    auto *loseLayout = new QVBoxLayout(loseWidget);
    loseLayout->setContentsMargins(0, 0, 0, 0);

    auto *loseLabel = new QLabel("TOP LOSERS");
    loseLabel->setStyleSheet("color: #ff4757; font-weight: bold;");
    loseLayout->addWidget(loseLabel);

    m_losersTable = new QTableWidget(5, 3);
    m_losersTable->setHorizontalHeaderLabels({"Symbol", "Price", "Chg%"});
    m_losersTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_losersTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_losersTable->verticalHeader()->setVisible(false);
    loseLayout->addWidget(m_losersTable);
    glLayout->addWidget(loseWidget);

    mainLayout->addLayout(glLayout);
}

void MarketOverviewScreen::populateData()
{
    // Indices
    struct { QString name; double val; double chg; double pct; } indices[] = {
        {"IHSG", 7123.45, 35.20, 0.50},
        {"S&P 500", 5432.10, 64.80, 1.20},
        {"Nikkei", 38450.00, -115.50, -0.30},
        {"STI", 3245.67, 25.80, 0.80},
        {"HSI", 18234.50, -202.30, -1.10},
        {"KOSPI", 2650.30, 12.40, 0.47},
    };

    m_indicesTable->setRowCount(6);
    for (int i = 0; i < 6; ++i) {
        m_indicesTable->setItem(i, 0, new QTableWidgetItem(indices[i].name));
        m_indicesTable->setItem(i, 1, new QTableWidgetItem(
            QString::number(indices[i].val, 'f', 2)));
        auto *chgItem = new QTableWidgetItem(
            QString::number(indices[i].chg, 'f', 2));
        chgItem->setForeground(indices[i].chg >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_indicesTable->setItem(i, 2, chgItem);
        QString pctStr = (indices[i].pct >= 0 ? "+" : "") +
                         QString::number(indices[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(indices[i].pct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_indicesTable->setItem(i, 3, pctItem);
    }

    // Commodities
    struct { QString name; double price; double chg; double pct; } commodities[] = {
        {"Gold", 2050.30, 4.20, 0.20},
        {"Silver", 24.50, -0.30, -1.21},
        {"Crude Oil", 78.50, -0.65, -0.82},
        {"Copper", 4.25, 0.06, 1.50},
        {"Palm Oil", 3850.00, 15.00, 0.39},
    };

    m_commoditiesTable->setRowCount(5);
    for (int i = 0; i < 5; ++i) {
        m_commoditiesTable->setItem(i, 0, new QTableWidgetItem(commodities[i].name));
        m_commoditiesTable->setItem(i, 1, new QTableWidgetItem(
            QString::number(commodities[i].price, 'f', 2)));
        auto *chgItem = new QTableWidgetItem(
            QString::number(commodities[i].chg, 'f', 2));
        chgItem->setForeground(commodities[i].chg >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_commoditiesTable->setItem(i, 2, chgItem);
        QString pctStr = (commodities[i].pct >= 0 ? "+" : "") +
                         QString::number(commodities[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(commodities[i].pct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_commoditiesTable->setItem(i, 3, pctItem);
    }

    // Forex
    struct { QString pair; double rate; double chg; double pct; } forex[] = {
        {"USD/IDR", 15600, 47, 0.30},
        {"EUR/IDR", 17050, -25, -0.15},
        {"GBP/IDR", 19800, 30, 0.15},
        {"SGD/IDR", 11700, 12, 0.10},
        {"JPY/IDR", 104.50, -0.25, -0.24},
    };

    m_forexTable->setRowCount(5);
    for (int i = 0; i < 5; ++i) {
        m_forexTable->setItem(i, 0, new QTableWidgetItem(forex[i].pair));
        m_forexTable->setItem(i, 1, new QTableWidgetItem(
            QString::number(forex[i].rate, 'f', 2)));
        auto *chgItem = new QTableWidgetItem(
            QString::number(forex[i].chg, 'f', 2));
        chgItem->setForeground(forex[i].chg >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_forexTable->setItem(i, 2, chgItem);
        QString pctStr = (forex[i].pct >= 0 ? "+" : "") +
                         QString::number(forex[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(forex[i].pct >= 0 ? QColor("#00d989") : QColor("#ff4757"));
        m_forexTable->setItem(i, 3, pctItem);
    }

    // Gainers
    struct { QString sym; double price; double pct; } gainers[] = {
        {"MDKA", 1350, 3.44},
        {"ADRO", 1520, 2.01},
        {"ICBP", 11200, 1.82},
        {"BREN", 8500, 1.80},
        {"BBCA", 9200, 1.66},
    };

    m_gainersTable->setRowCount(5);
    for (int i = 0; i < 5; ++i) {
        auto *symItem = new QTableWidgetItem(gainers[i].sym);
        symItem->setFont(QFont("monospace", 11, QFont::Bold));
        m_gainersTable->setItem(i, 0, symItem);
        m_gainersTable->setItem(i, 1, new QTableWidgetItem(
            QString::number(gainers[i].price, 'f', 0)));
        QString pctStr = "+" + QString::number(gainers[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(QColor("#00d989"));
        m_gainersTable->setItem(i, 2, pctItem);
    }

    // Losers
    struct { QString sym; double price; double pct; } losers[] = {
        {"GOTO", 85, -2.30},
        {"UNVR", 4250, -1.73},
        {"BBNI", 5200, -0.57},
        {"EXCL", 2100, -0.71},
        {"BBRI", 4800, -1.03},
    };

    m_losersTable->setRowCount(5);
    for (int i = 0; i < 5; ++i) {
        auto *symItem = new QTableWidgetItem(losers[i].sym);
        symItem->setFont(QFont("monospace", 11, QFont::Bold));
        m_losersTable->setItem(i, 0, symItem);
        m_losersTable->setItem(i, 1, new QTableWidgetItem(
            QString::number(losers[i].price, 'f', 0)));
        QString pctStr = QString::number(losers[i].pct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(QColor("#ff4757"));
        m_losersTable->setItem(i, 2, pctItem);
    }
}
