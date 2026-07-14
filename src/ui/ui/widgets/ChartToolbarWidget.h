#pragma once

#include <QWidget>
#include <QPushButton>
#include <QHBoxLayout>
#include <QComboBox>
#include <QCompleter>
#include <QMenu>
#include <QButtonGroup>
#include <QJsonObject>
#include <QJsonArray>

class ChartToolbarWidget : public QWidget
{
    Q_OBJECT

public:
    explicit ChartToolbarWidget(QWidget *parent = nullptr);

    void applyTemplate(const QString &name);
    QStringList templateNames() const;

signals:
    void timeframeChanged(const QString &tf);
    void symbolRequested(const QString &symbol);
    void chartTypeChanged(const QString &type);
    void indicatorToggled(const QString &name, bool visible);
    void templateApplied(const QJsonObject &config);

private slots:
    void onTimeframeClicked();
    void onSymbolActivated(int index);
    void onChartTypeClicked(int id);
    void onIndicatorToggled();
    void onTemplateSelected();
    void onSaveTemplate();

private:
    void setupUI();
    void loadSymbols();
    void updateTimeframeStyles();
    void setupChartTypeButtons(QHBoxLayout *layout);
    void setupIndicatorMenu(QHBoxLayout *layout);
    void setupTemplateMenu(QHBoxLayout *layout);
    QAction *addIndicatorAction(QMenu *menu, const QString &label, const QString &name, bool checked);
    void loadCustomTemplates();
    void saveCustomTemplates();

    QComboBox *m_symbolCombo = nullptr;
    QCompleter *m_completer = nullptr;
    QList<QPushButton*> m_tfButtons;
    int m_activeTf = 4; // D (daily)
    QButtonGroup *m_typeGroup = nullptr;
    QList<QPushButton*> m_typeButtons;
    QPushButton *m_indicatorBtn = nullptr;
    QMenu *m_indicatorMenu = nullptr;
    QPushButton *m_templateBtn = nullptr;
    QMenu *m_templateMenu = nullptr;
    QJsonArray m_customTemplates;
};
