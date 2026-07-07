#pragma once

#include <QWidget>
#include <QTimer>
#include <QStringList>

class RunningTradeTicker : public QWidget
{
    Q_OBJECT

public:
    explicit RunningTradeTicker(QWidget *parent = nullptr);

    void setTrades(const QStringList &trades);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void scroll();

private:
    QStringList m_trades;
    int m_scrollOffset = 0;
    QTimer *m_timer = nullptr;
};
