#pragma once

#include <QWidget>
#include <QLabel>
#include <QTimer>

class BreakingNewsTicker : public QWidget
{
    Q_OBJECT

public:
    explicit BreakingNewsTicker(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void scroll();

private:
    QStringList m_headlines;
    int m_scrollOffset = 0;
    QTimer *m_timer = nullptr;
};
