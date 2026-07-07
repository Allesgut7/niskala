#pragma once

#include <QWidget>
#include <QTableWidget>
#include <QLabel>

struct OrderBookEntry {
    double price;
    int volume;
    double total;
};

class OrderBookWidget : public QWidget
{
    Q_OBJECT

public:
    explicit OrderBookWidget(QWidget *parent = nullptr);

    void setSymbol(const QString &symbol);
    void updateOrders(const QList<OrderBookEntry> &bids,
                      const QList<OrderBookEntry> &asks);

signals:
    void priceClicked(double price);

private:
    void setupUI();
    void populateSampleData();

    QTableWidget *m_bidTable = nullptr;
    QTableWidget *m_askTable = nullptr;
    QLabel *m_symbolLabel = nullptr;
    QLabel *m_spreadLabel = nullptr;
    QString m_currentSymbol = "BBCA";
};
