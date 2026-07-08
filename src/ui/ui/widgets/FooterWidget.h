#pragma once

#include <QWidget>
#include <QTimer>

class FooterWidget : public QWidget
{
    Q_OBJECT

public:
    explicit FooterWidget(QWidget *parent = nullptr);

    void setVersion(const QString &version);
    void setConnectionStatus(const QString &status);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void updateDateTime();

private:
    QString m_version = "v2.0.0";
    QString m_connectionStatus = "Connected";
    QString m_currentTime;
    QTimer *m_timer = nullptr;
};
