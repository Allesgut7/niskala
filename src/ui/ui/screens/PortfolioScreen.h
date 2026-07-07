#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QLabel>

struct Position {
    QString symbol;
    int quantity;
    double avgPrice;
    double currentPrice;
    double unrealizedPnl;
    double unrealizedPnlPct;
};

struct Trade {
    QString date;
    QString symbol;
    QString side;
    int quantity;
    double price;
    double pnl;
};

class PortfolioScreen : public QWidget
{
    Q_OBJECT

public:
    explicit PortfolioScreen(QWidget *parent = nullptr);

signals:
    void symbolClicked(const QString &symbol);

private:
    void setupUI();
    void populateSampleData();

    QTableWidget *m_positionsTable = nullptr;
    QTableWidget *m_tradesTable = nullptr;
    QLabel *m_balanceLabel = nullptr;
    QLabel *m_investedLabel = nullptr;
    QLabel *m_unrealizedLabel = nullptr;
    QLabel *m_realizedLabel = nullptr;
};
