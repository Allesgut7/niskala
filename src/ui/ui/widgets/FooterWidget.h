#pragma once

#include <QWidget>
#include <QLabel>

class FooterWidget : public QWidget
{
    Q_OBJECT

public:
    explicit FooterWidget(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;
};
