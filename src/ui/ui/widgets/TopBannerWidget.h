#pragma once

#include <QWidget>
#include <QLabel>
#include <QTimer>

class TopBannerWidget : public QWidget
{
    Q_OBJECT

public:
    explicit TopBannerWidget(QWidget *parent = nullptr);

    void setIndices(const QStringList &indices);
    void setCommodities(const QStringList &commodities);
    void setForex(const QStringList &forex);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void scrollTicker();

private:
    void setupUI();

    QStringList m_indices;
    QStringList m_commodities;
    QStringList m_forex;
    int m_scrollOffset = 0;
    QTimer *m_scrollTimer = nullptr;
};
