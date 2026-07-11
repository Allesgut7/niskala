#pragma once

#include <QWidget>
#include <QPainter>

class AIMarketRegimeWidget : public QWidget
{
    Q_OBJECT

public:
    explicit AIMarketRegimeWidget(QWidget *parent = nullptr);

    void updateData(const QString &regime, int confidence, const QString &analysis = "");

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_regime = "LOADING...";
    int m_confidence = 0;
};
