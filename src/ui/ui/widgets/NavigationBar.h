#pragma once

#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QHBoxLayout>

class NavigationBar : public QWidget
{
    Q_OBJECT

public:
    explicit NavigationBar(QWidget *parent = nullptr);

signals:
    void tabClicked(int index);

private slots:
    void onTabClicked();

private:
    void setupUI();

    QList<QPushButton*> m_tabs;
    int m_activeTab = 0;
};
