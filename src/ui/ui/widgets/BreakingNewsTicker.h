#pragma once

#include <QWidget>
#include <QTimer>
#include <QStringList>

class BreakingNewsTicker : public QWidget
{
    Q_OBJECT

public:
    explicit BreakingNewsTicker(QWidget *parent = nullptr);

    void updateHeadlines(const QStringList &headlines);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void scroll();

private:
    QStringList m_headlines;
    int m_scrollOffset = 0;
    QTimer *m_timer = nullptr;
};
