#include "CommandBar.h"
#include <QHBoxLayout>
#include <QKeyEvent>

CommandBar::CommandBar(QWidget *parent)
    : QToolBar(parent)
{
    setupUI();
    loadCommands();
}

void CommandBar::setupUI()
{
    setObjectName("CommandBar");
    setMovable(false);
    setAllowedAreas(Qt::BottomToolBarArea);
    setFixedHeight(36);

    auto *layout = new QHBoxLayout();
    layout->setContentsMargins(8, 2, 8, 2);
    layout->setSpacing(6);

    m_promptLabel = new QLabel(">");
    m_promptLabel->setStyleSheet("color: #FFB4AB; font-weight: bold; font-size: 14px;");

    m_input = new QLineEdit();
    m_input->setPlaceholderText("Type command... (DASH, CHART, NEWS, SCREENER, HELP)");
    m_input->setStyleSheet(
        "QLineEdit {"
        "  background-color: #1D2023;"
        "  color: #CEE8FF;"
        "  border: 1px solid #3B4A3D;"
        "  border-radius: 3px;"
        "  padding: 4px 8px;"
        "  font-family: 'SF Mono', 'Consolas', monospace;"
        "  font-size: 13px;"
        "}"
        "QLineEdit:focus {"
        "  border-color: #FFB4AB;"
        "}"
    );

    layout->addWidget(m_promptLabel);
    layout->addWidget(m_input);

    auto *container = new QWidget();
    container->setLayout(layout);
    addWidget(container);

    connect(m_input, &QLineEdit::returnPressed,
            this, &CommandBar::onReturnPressed);
}

void CommandBar::loadCommands()
{
    m_commands << "DASH" << "DASHBOARD"
              << "CHART" << "NEWS"
              << "SCREENER" << "PORT" << "PORTFOLIO"
              << "SETTINGS" << "HELP"
              << "REFRESH" << "EXIT";
}

void CommandBar::onReturnPressed()
{
    QString command = m_input->text().trimmed();
    if (command.isEmpty()) return;

    m_history.append(command);
    m_historyIndex = m_history.size();
    m_input->clear();

    emit commandEntered(command);
}

void CommandBar::keyPressEvent(QKeyEvent *event)
{
    if (event->key() == Qt::Key_Up) {
        if (m_historyIndex > 0) {
            m_historyIndex--;
            m_input->setText(m_history.at(m_historyIndex));
        }
    } else if (event->key() == Qt::Key_Down) {
        if (m_historyIndex < m_history.size() - 1) {
            m_historyIndex++;
            m_input->setText(m_history.at(m_historyIndex));
        } else {
            m_historyIndex = m_history.size();
            m_input->clear();
        }
    }

    QToolBar::keyPressEvent(event);
}
