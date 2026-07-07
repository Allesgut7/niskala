#pragma once

#include <QWidget>
#include <QPainter>

class SectorPerformanceWidget : public QWidget
{
    Q_OBJECT

public:
    explicit SectorPerformanceWidget(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    struct SectorData {
        QString name;
        double changePct;
    };

    QList<SectorData> m_sectors;
};
