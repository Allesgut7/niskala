#pragma once

#include <QWidget>
#include <QPushButton>
#include <QHBoxLayout>

class ChartToolbarWidget : public QWidget
{
    Q_OBJECT

public:
    explicit ChartToolbarWidget(QWidget *parent = nullptr);

signals:
    void timeframeChanged(const QString &tf);
    void chartTypeChanged(const QString &type);

private slots:
    void onTimeframeClicked();

private:
    void setupUI();
    void updateTimeframeStyles();

    QList<QPushButton*> m_tfButtons;
    int m_activeTf = 3; // D (daily)
};
