#pragma once

#include <QToolBar>
#include <QLineEdit>
#include <QLabel>
#include <QStringList>

class CommandBar : public QToolBar
{
    Q_OBJECT

public:
    explicit CommandBar(QWidget *parent = nullptr);

signals:
    void commandEntered(const QString &command);

private slots:
    void onReturnPressed();

    void keyPressEvent(QKeyEvent *event) override;

private:
    void setupUI();
    void loadCommands();

    QLineEdit *m_input = nullptr;
    QLabel *m_promptLabel = nullptr;
    QStringList m_commands;
    QStringList m_history;
    int m_historyIndex = -1;
};
