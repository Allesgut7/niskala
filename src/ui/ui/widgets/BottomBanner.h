#pragma once

#include <QWidget>
#include <QLabel>

class BottomBanner : public QWidget
{
    Q_OBJECT

public:
    explicit BottomBanner(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void setupData();

    QStringList m_gainers;
    QStringList m_losers;
};
