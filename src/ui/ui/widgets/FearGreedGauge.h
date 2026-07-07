#pragma once

#include <QWidget>
#include <QPainter>

class FearGreedGauge : public QWidget
{
    Q_OBJECT

public:
    explicit FearGreedGauge(const QString &label = "ID", QWidget *parent = nullptr);

    void setScore(int score);
    int score() const { return m_score; }

signals:
    void scoreChanged(int score);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void drawGauge(QPainter &painter, const QRect &rect);
    QColor getScoreColor(int score) const;
    QString getScoreLabel(int score) const;

    int m_score = 50;
    QString m_label;
};
