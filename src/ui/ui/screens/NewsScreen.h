#pragma once

#include <QWidget>
#include <QListWidget>
#include <QLineEdit>
#include <QComboBox>

class NewsScreen : public QWidget
{
    Q_OBJECT

public:
    explicit NewsScreen(QWidget *parent = nullptr);

private slots:
    void onFilterChanged();

private:
    void setupUI();
    void populateData();

    QListWidget *m_newsList = nullptr;
    QComboBox *m_sourceFilter = nullptr;
    QComboBox *m_sentimentFilter = nullptr;
    QLineEdit *m_searchEdit = nullptr;
};
