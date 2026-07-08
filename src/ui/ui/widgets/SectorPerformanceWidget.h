#pragma once

#include <QWidget>
#include <QPainter>

class SectorPerformanceWidget : public QWidget
{
    Q_OBJECT

public:
    explicit SectorPerformanceWidget(QWidget *parent = nullptr);

    void updateData(const QJsonArray &sectors);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    struct SectorData {
        QString name;
        double changePct;
    };

    QList<SectorData> m_sectors;
};
