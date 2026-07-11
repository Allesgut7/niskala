#pragma once

#include <QWidget>
#include <QPainter>
#include <QJsonArray>
#include <QJsonObject>

class AIMarketRegimeWidget : public QWidget
{
    Q_OBJECT

public:
    explicit AIMarketRegimeWidget(QWidget *parent = nullptr);

    void updateData(const QString &regime, int confidence,
                    const QString &next1hRegime, int next1hConfidence,
                    const QString &nextDayRegime, int nextDayConfidence,
                    const QString &analysis, const QJsonArray &forecastSteps);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_regime = "LOADING...";
    int m_confidence = 0;
    QString m_next1hRegime;
    int m_next1hConfidence = 0;
    QString m_nextDayRegime;
    int m_nextDayConfidence = 0;
    QString m_analysis;
    QJsonArray m_forecastSteps;
};
