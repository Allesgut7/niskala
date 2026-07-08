#include "OrderBookWidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QHeaderView>

OrderBookWidget::OrderBookWidget(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateSampleData();
}

void OrderBookWidget::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);
    mainLayout->setSpacing(2);

    // Header
    auto *headerLayout = new QHBoxLayout();
    m_symbolLabel = new QLabel("ORDER BOOK - BBCA");
    m_symbolLabel->setStyleSheet("color: #FFB4AB; font-weight: bold; font-size: 12px;");
    headerLayout->addWidget(m_symbolLabel);

    m_spreadLabel = new QLabel("Spread: 50 (0.54%)");
    m_spreadLabel->setStyleSheet("color: #859585; font-size: 10px;");
    m_spreadLabel->setAlignment(Qt::AlignRight);
    headerLayout->addWidget(m_spreadLabel);
    mainLayout->addLayout(headerLayout);

    // ASKS table
    m_askTable = new QTableWidget(8, 3);
    m_askTable->setHorizontalHeaderLabels({"Price", "Volume", "Total"});
    m_askTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_askTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_askTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_askTable->verticalHeader()->setVisible(false);
    m_askTable->setShowGrid(false);
    m_askTable->setFocusPolicy(Qt::NoFocus);
    m_askTable->setStyleSheet(
        "QTableWidget { background-color: #1D2023; alternate-background-color: #111417; }"
    );
    mainLayout->addWidget(m_askTable);

    // Spread indicator
    auto *spreadBar = new QLabel("───── SPREAD ─────");
    spreadBar->setAlignment(Qt::AlignCenter);
    spreadBar->setStyleSheet("color: #CEE8FF; font-weight: bold; background-color: #323538; padding: 2px;");
    mainLayout->addWidget(spreadBar);

    // BIDS table
    m_bidTable = new QTableWidget(8, 3);
    m_bidTable->setHorizontalHeaderLabels({"Price", "Volume", "Total"});
    m_bidTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_bidTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_bidTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_bidTable->verticalHeader()->setVisible(false);
    m_bidTable->setShowGrid(false);
    m_bidTable->setFocusPolicy(Qt::NoFocus);
    m_bidTable->setStyleSheet(
        "QTableWidget { background-color: #1D2023; alternate-background-color: #111417; }"
    );
    mainLayout->addWidget(m_bidTable);
}

void OrderBookWidget::populateSampleData()
{
    // ASKS (red - sell orders)
    double askStart = 9200;
    int askVolumes[] = {150, 230, 180, 320, 450, 280, 190, 120};
    double askTotal = 0;

    for (int i = 0; i < 8; ++i) {
        double price = askStart + (i * 50);
        askTotal += askVolumes[i];

        auto *priceItem = new QTableWidgetItem(QString::number(price, 'f', 0));
        priceItem->setForeground(QColor("#FFB3AE"));
        priceItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_askTable->setItem(i, 0, priceItem);

        auto *volItem = new QTableWidgetItem(QString::number(askVolumes[i]));
        volItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_askTable->setItem(i, 1, volItem);

        auto *totalItem = new QTableWidgetItem(QString::number((int)askTotal));
        totalItem->setForeground(QColor("#859585"));
        totalItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_askTable->setItem(i, 2, totalItem);
    }

    // BIDS (green - buy orders)
    double bidStart = 9150;
    int bidVolumes[] = {200, 310, 150, 280, 420, 350, 210, 180};
    double bidTotal = 0;

    for (int i = 0; i < 8; ++i) {
        double price = bidStart - (i * 50);
        bidTotal += bidVolumes[i];

        auto *priceItem = new QTableWidgetItem(QString::number(price, 'f', 0));
        priceItem->setForeground(QColor("#75FF9E"));
        priceItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_bidTable->setItem(i, 0, priceItem);

        auto *volItem = new QTableWidgetItem(QString::number(bidVolumes[i]));
        volItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_bidTable->setItem(i, 1, volItem);

        auto *totalItem = new QTableWidgetItem(QString::number((int)bidTotal));
        totalItem->setForeground(QColor("#859585"));
        totalItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_bidTable->setItem(i, 2, totalItem);
    }
}

void OrderBookWidget::setSymbol(const QString &symbol)
{
    m_currentSymbol = symbol;
    m_symbolLabel->setText("ORDER BOOK - " + symbol);
}

void OrderBookWidget::updateOrders(const QList<OrderBookEntry> &bids,
                                   const QList<OrderBookEntry> &asks)
{
    // TODO: Update with real data
    Q_UNUSED(bids);
    Q_UNUSED(asks);
}
