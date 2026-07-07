#pragma once

#include <QWidget>
#include <QGridLayout>
#include <QLabel>

struct SectorData {
    QString code;
    QString name;
    double changePct;
};

class SectorHeatmap : public QWidget
{
    Q_OBJECT

public:
    explicit SectorHeatmap(QWidget *parent = nullptr);

    void updateData(const QList<SectorData> &sectors);

signals:
    void sectorClicked(const QString &code);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    void setupUI();
    void populateSampleData();
    QColor getHeatColor(double pct) const;

    QList<SectorData> m_sectors;
};
