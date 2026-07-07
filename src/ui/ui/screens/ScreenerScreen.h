#pragma once

#include <QWidget>
#include <QComboBox>
#include <QPushButton>
#include <QTableWidget>
#include <QLabel>
#include <QLineEdit>

class ScreenerScreen : public QWidget
{
    Q_OBJECT

public:
    explicit ScreenerScreen(QWidget *parent = nullptr);

signals:
    void symbolSelected(const QString &symbol);

private slots:
    void onFilterChanged();
    void onSearchTextChanged(const QString &text);
    void onRowClicked(int row, int col);

private:
    void setupUI();
    void populateData();
    void applyFilters();

    QTableWidget *m_table = nullptr;
    QLineEdit *m_searchEdit = nullptr;
    QComboBox *m_sectorCombo = nullptr;
    QComboBox *m_changeCombo = nullptr;
    QComboBox *m_volumeCombo = nullptr;
    QLabel *m_resultCount = nullptr;
    QStringList m_allSymbols;
};
