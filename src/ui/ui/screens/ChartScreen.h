#pragma once

#include <QWidget>
#include <QComboBox>
#include <QPushButton>
#include <QLabel>
#include <QTableWidget>

class CandlestickChart;

class ChartScreen : public QWidget
{
    Q_OBJECT

public:
    explicit ChartScreen(QWidget *parent = nullptr);

    void loadSymbol(const QString &symbol);

private slots:
    void onTimeframeChanged(int index);
    void onIndicatorToggled();

private:
    void setupUI();

    CandlestickChart *m_chart = nullptr;
    QComboBox *m_symbolCombo = nullptr;
    QComboBox *m_timeframeCombo = nullptr;
    QCheckBox *m_ma5Check = nullptr;
    QCheckBox *m_ma20Check = nullptr;
    QCheckBox *m_volumeCheck = nullptr;
};
