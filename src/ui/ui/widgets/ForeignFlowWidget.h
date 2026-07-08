#pragma once

#include <QWidget>
#include <QPainter>

class ForeignFlowWidget : public QWidget
{
    Q_OBJECT

public:
    explicit ForeignFlowWidget(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;
};
