#pragma once

#include <QWidget>
#include <QPainter>

class SentimentGauge : public QWidget
{
    Q_OBJECT

public:
    explicit SentimentGauge(QWidget *parent = nullptr);

    void setScore(double score);
    double score() const { return m_score; }

signals:
    void scoreChanged(double score);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void drawGauge(QPainter &painter, const QRect &rect);

    double m_score = 0.0;
};
