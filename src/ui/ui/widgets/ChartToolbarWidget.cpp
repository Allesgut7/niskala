#include "ChartToolbarWidget.h"
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QFile>
#include <QAbstractItemView>
#include <QMenu>
#include <QAction>
#include <QButtonGroup>
#include <QStandardPaths>
#include <QDir>

ChartToolbarWidget::ChartToolbarWidget(QWidget *parent)
    : QWidget(parent)
{
    setFixedHeight(40);
    setupUI();
    loadSymbols();
}

void ChartToolbarWidget::setupUI()
{
    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(8, 4, 8, 4);
    layout->setSpacing(4);

    // Search icon
    auto *searchIcon = new QLabel("🔍");
    searchIcon->setStyleSheet("font-size: 13px; padding-right: 2px;");
    layout->addWidget(searchIcon);

    // Editable symbol combo — TradingView style
    m_symbolCombo = new QComboBox();
    m_symbolCombo->setEditable(true);
    m_symbolCombo->setInsertPolicy(QComboBox::NoInsert);
    m_symbolCombo->lineEdit()->setPlaceholderText("Search ticker...");
    m_symbolCombo->setMinimumWidth(120);
    m_symbolCombo->setMaximumWidth(250);

    m_symbolCombo->setStyleSheet(
        "QComboBox { background-color: #1D2023; border: 1px solid #3B4A3D; "
        "border-radius: 4px; color: #E1E2E7; font-size: 12px; padding: 4px 8px; }"
        "QComboBox::drop-down { border: none; }"
        "QComboBox::down-arrow { image: none; }"
        "QComboBox QAbstractItemView { background-color: #1D2023; border: 1px solid #3B4A3D; "
        "selection-background-color: #272A2E; selection-color: #E1E2E7; max-height: 300px; }");
    m_symbolCombo->lineEdit()->setStyleSheet(
        "QLineEdit { background: transparent; border: none; color: #E1E2E7; font-size: 12px; }");

    connect(m_symbolCombo, QOverload<int>::of(&QComboBox::activated),
            this, &ChartToolbarWidget::onSymbolActivated);
    connect(m_symbolCombo->lineEdit(), &QLineEdit::returnPressed, this, [this]() {
        QString text = m_symbolCombo->currentText().trimmed().toUpper();
        QString symbol = text.section(" ", 0, 0);
        if (!symbol.isEmpty()) emit symbolRequested(symbol);
    });
    layout->addWidget(m_symbolCombo, 0);

    layout->addSpacing(8);

    // Timeframe buttons
    QStringList timeframes = {"1m", "5m", "15m", "1h", "D", "W", "M"};
    for (int i = 0; i < timeframes.size(); ++i) {
        auto *btn = new QPushButton(timeframes[i]);
        btn->setFixedSize(28, 24);
        btn->setCheckable(true);
        btn->setChecked(i == m_activeTf);
        connect(btn, &QPushButton::clicked, this, &ChartToolbarWidget::onTimeframeClicked);
        m_tfButtons.append(btn);
        layout->addWidget(btn);
    }

    updateTimeframeStyles();

    setupChartTypeButtons(layout);
    setupIndicatorMenu(layout);
    setupTemplateMenu(layout);

    layout->addStretch();

    setStyleSheet("ChartToolbarWidget { background-color: #272A2E; border-bottom: 1px solid #3B4A3D; }");
}

void ChartToolbarWidget::loadSymbols()
{
    // Load from resource JSON
    QFile file(":/config/idx_tickers.json");
    if (!file.exists()) {
        qWarning() << "ChartToolbar: idx_tickers.json not found in resources";
        return;
    }

    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "ChartToolbar: Cannot open idx_tickers.json";
        return;
    }

    QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();

    QJsonObject rootObj = doc.object();
    QJsonArray arr = rootObj.value("tickers").toArray();
    QStringList displayItems;

    // Add IHSG index first
    m_symbolCombo->addItem("JKSE   IHSG Index", "JKSE");
    displayItems << "JKSE   IHSG Index";
    m_symbolCombo->addItem("^GSPC  S&P 500", "^GSPC");
    displayItems << "^GSPC  S&P 500";
    m_symbolCombo->addItem("^N225  Nikkei 225", "^N225");
    displayItems << "^N225  Nikkei 225";
    m_symbolCombo->addItem("GC=F   Gold", "GC=F");
    displayItems << "GC=F   Gold";
    m_symbolCombo->addItem("CL=F   Oil", "CL=F");
    displayItems << "CL=F   Oil";

    // Add IDX tickers from JSON
    for (const auto &item : arr) {
        QJsonObject obj = item.toObject();
        QString symbol = obj["symbol"].toString();
        QString name = obj["name"].toString();
        if (symbol.isEmpty()) continue;
        QString display = symbol + "   " + name;
        m_symbolCombo->addItem(display, symbol);
        displayItems << display;
    }

    m_symbolCombo->setCurrentText("JKSE   IHSG Index");

    // Setup QCompleter for autocomplete filtering
    m_completer = new QCompleter(displayItems, this);
    m_completer->setCaseSensitivity(Qt::CaseInsensitive);
    m_completer->setFilterMode(Qt::MatchContains);
    m_completer->setCompletionMode(QCompleter::PopupCompletion);
    m_symbolCombo->lineEdit()->setCompleter(m_completer);

    // Style the completer popup
    m_completer->popup()->setStyleSheet(
        "QListView { background-color: #1D2023; color: #E1E2E7; border: 1px solid #3B4A3D; "
        "selection-background-color: #272A2E; selection-color: #75FF9E; font-size: 11px; }");

    qDebug() << "ChartToolbar: Loaded" << displayItems.size() << "symbols";
}

void ChartToolbarWidget::setupChartTypeButtons(QHBoxLayout *layout)
{
    layout->addSpacing(4);
    auto *sep = new QLabel("|");
    sep->setStyleSheet("color: #3B4A3D; font-size: 14px;");
    layout->addWidget(sep);

    m_typeGroup = new QButtonGroup(this);
    struct TypeDef { QString icon; QString type; QString tooltip; };
    QList<TypeDef> types = {
        {"🕯", "candlestick", "Candlestick"},
        {"📈", "line", "Line"},
        {"▲", "area", "Area"},
        {"🔥", "heikin_ashi", "Heikin Ashi"},
    };
    for (int i = 0; i < types.size(); ++i) {
        auto *btn = new QPushButton(types[i].icon);
        btn->setFixedSize(24, 22);
        btn->setCheckable(true);
        btn->setChecked(i == 0);
        btn->setToolTip(types[i].tooltip);
        btn->setProperty("chartType", types[i].type);
        m_typeGroup->addButton(btn, i);
        m_typeButtons.append(btn);
        layout->addWidget(btn);
    }
    connect(m_typeGroup, &QButtonGroup::idClicked, this, &ChartToolbarWidget::onChartTypeClicked);

    // Style for chart type buttons
    QString baseStyle = "QPushButton { background-color: transparent; border: none; border-radius: 3px; "
                        "font-size: 13px; padding: 0 2px; }";
    QString activeStyle = baseStyle + "QPushButton:checked { background-color: #3B4A3D; }";
    for (auto *btn : m_typeButtons) {
        btn->setStyleSheet(activeStyle);
    }
}

void ChartToolbarWidget::setupIndicatorMenu(QHBoxLayout *layout)
{
    layout->addSpacing(4);
    auto *sep = new QLabel("|");
    sep->setStyleSheet("color: #3B4A3D; font-size: 14px;");
    layout->addWidget(sep);

    m_indicatorBtn = new QPushButton("📊 Indicators");
    m_indicatorBtn->setFixedHeight(22);
    m_indicatorBtn->setStyleSheet(
        "QPushButton { background-color: transparent; color: #859585; border: none; "
        "font-size: 11px; padding: 0 6px; }"
        "QPushButton:hover { color: #E1E2E7; }");
    layout->addWidget(m_indicatorBtn);

    m_indicatorMenu = new QMenu(this);
    m_indicatorMenu->setStyleSheet(
        "QMenu { background-color: #1D2023; border: 1px solid #3B4A3D; padding: 4px 0; }"
        "QMenu::item { color: #E1E2E7; font-size: 11px; padding: 4px 24px 4px 12px; }"
        "QMenu::item:selected { background-color: #272A2E; }"
        "QMenu::separator { height: 1px; background: #3B4A3D; margin: 4px 8px; }"
        "QMenu::indicator { width: 12px; height: 12px; }");

    // Overlay indicators
    auto *overlayTitle = m_indicatorMenu->addAction("Overlay");
    overlayTitle->setEnabled(false);
    addIndicatorAction(m_indicatorMenu, "SMA 5",     "sma_5", true);
    addIndicatorAction(m_indicatorMenu, "SMA 10",    "sma_10", false);
    addIndicatorAction(m_indicatorMenu, "SMA 20",    "sma_20", true);
    addIndicatorAction(m_indicatorMenu, "SMA 50",    "sma_50", true);
    addIndicatorAction(m_indicatorMenu, "SMA 200",   "sma_200", false);
    addIndicatorAction(m_indicatorMenu, "EMA 12",    "ema_12", false);
    addIndicatorAction(m_indicatorMenu, "EMA 26",    "ema_26", false);
    addIndicatorAction(m_indicatorMenu, "Bollinger Bands", "bollinger", false);
    addIndicatorAction(m_indicatorMenu, "VWAP",      "vwap", false);

    m_indicatorMenu->addSeparator();

    // Oscillator indicators
    auto *oscTitle = m_indicatorMenu->addAction("Oscillator");
    oscTitle->setEnabled(false);
    addIndicatorAction(m_indicatorMenu, "RSI (14)",          "rsi", false);
    addIndicatorAction(m_indicatorMenu, "MACD (12,26,9)",    "macd", true);
    addIndicatorAction(m_indicatorMenu, "Stochastic (14,3,3)", "stochastic", false);
    addIndicatorAction(m_indicatorMenu, "ATR (14)",          "atr", false);

    m_indicatorBtn->setMenu(m_indicatorMenu);
}

QAction *ChartToolbarWidget::addIndicatorAction(QMenu *menu, const QString &label,
                                                 const QString &name, bool checked)
{
    auto *action = menu->addAction(label);
    action->setCheckable(true);
    action->setChecked(checked);
    action->setData(name);
    connect(action, &QAction::toggled, this, &ChartToolbarWidget::onIndicatorToggled);
    return action;
}

void ChartToolbarWidget::onChartTypeClicked(int id)
{
    if (id >= 0 && id < m_typeButtons.size()) {
        QString type = m_typeButtons[id]->property("chartType").toString();
        emit chartTypeChanged(type);
    }
}

void ChartToolbarWidget::onIndicatorToggled()
{
    auto *action = qobject_cast<QAction*>(sender());
    if (!action) return;
    QString name = action->data().toString();
    if (name.isEmpty()) return;
    emit indicatorToggled(name, action->isChecked());
}

void ChartToolbarWidget::setupTemplateMenu(QHBoxLayout *layout)
{
    layout->addSpacing(4);
    auto *sep = new QLabel("|");
    sep->setStyleSheet("color: #3B4A3D; font-size: 14px;");
    layout->addWidget(sep);

    m_templateBtn = new QPushButton("Templates");
    m_templateBtn->setFixedHeight(22);
    m_templateBtn->setStyleSheet(
        "QPushButton { background-color: transparent; color: #859585; border: none; "
        "font-size: 11px; padding: 0 6px; }"
        "QPushButton:hover { color: #E1E2E7; }");
    layout->addWidget(m_templateBtn);

    m_templateMenu = new QMenu(this);
    m_templateMenu->setStyleSheet(
        "QMenu { background-color: #1D2023; border: 1px solid #3B4A3D; padding: 4px 0; }"
        "QMenu::item { color: #E1E2E7; font-size: 11px; padding: 4px 24px 4px 12px; }"
        "QMenu::item:selected { background-color: #272A2E; }"
        "QMenu::separator { height: 1px; background: #3B4A3D; margin: 4px 8px; }");

    // Predefined templates
    auto addTmpl = [this](const QString &label, const QString &name) {
        auto *a = m_templateMenu->addAction(label);
        a->setData(name);
        connect(a, &QAction::triggered, this, &ChartToolbarWidget::onTemplateSelected);
    };

    addTmpl("Default", "Default");
    addTmpl("Trend Following", "TrendFollowing");
    addTmpl("Momentum", "Momentum");
    addTmpl("Volatility", "Volatility");
    addTmpl("Clean", "Clean");

    m_templateMenu->addSeparator();

    // Custom templates section
    m_templateMenu->addAction("Save Current...")->setData("__save__");
    connect(m_templateMenu->actions().last(), &QAction::triggered,
            this, &ChartToolbarWidget::onSaveTemplate);

    m_templateMenu->addSeparator();
    m_templateMenu->addAction("Manage Templates...")->setEnabled(false);

    loadCustomTemplates();

    m_templateBtn->setMenu(m_templateMenu);
}

void ChartToolbarWidget::onTemplateSelected()
{
    auto *action = qobject_cast<QAction*>(sender());
    if (!action) return;
    QString name = action->data().toString();
    if (name.isEmpty() || name == "__save__") return;
    applyTemplate(name);
}

void ChartToolbarWidget::onSaveTemplate()
{
    // Collect current indicator state from indicator menu
    QJsonObject config;
    QJsonObject indicators;
    for (auto *a : m_indicatorMenu->actions()) {
        if (a->isCheckable()) {
            QString name = a->data().toString();
            if (!name.isEmpty())
                indicators[name] = a->isChecked();
        }
    }
    config["indicators"] = indicators;
    config["chartType"] = "candlestick";

    QString name = "Custom " + QString::number(m_customTemplates.size() + 1);
    config["name"] = name;

    m_customTemplates.append(config);
    saveCustomTemplates();

    // Add to menu
    auto *a = m_templateMenu->addAction(name);
    a->setData(name);
    connect(a, &QAction::triggered, this, &ChartToolbarWidget::onTemplateSelected);
}

void ChartToolbarWidget::applyTemplate(const QString &name)
{
    QJsonObject config;

    if (name == "Default") {
        QJsonObject ind;
        ind["sma_5"] = true; ind["sma_20"] = true;
        ind["sma_50"] = true; ind["macd"] = true;
        config["indicators"] = ind;
        config["chartType"] = "candlestick";
    } else if (name == "TrendFollowing") {
        QJsonObject ind;
        ind["ema_12"] = true; ind["ema_26"] = true;
        ind["sma_200"] = true; ind["rsi"] = true;
        config["indicators"] = ind;
        config["chartType"] = "candlestick";
    } else if (name == "Momentum") {
        QJsonObject ind;
        ind["rsi"] = true; ind["macd"] = true;
        ind["stochastic"] = true; ind["atr"] = true;
        config["indicators"] = ind;
        config["chartType"] = "candlestick";
    } else if (name == "Volatility") {
        QJsonObject ind;
        ind["bollinger"] = true; ind["atr"] = true;
        ind["vwap"] = true; ind["sma_20"] = true;
        config["indicators"] = ind;
        config["chartType"] = "candlestick";
    } else if (name == "Clean") {
        QJsonObject ind;
        config["indicators"] = ind;
        config["chartType"] = "candlestick";
    } else {
        // Custom template
        for (const auto &ct : m_customTemplates) {
            QJsonObject ctObj = ct.toObject();
            if (ctObj["name"].toString() == name) {
                config = ctObj;
                break;
            }
        }
    }

    if (config.isEmpty()) return;

    // Update indicator menu checkboxes
    QJsonObject inds = config["indicators"].toObject();
    for (auto *a : m_indicatorMenu->actions()) {
        if (a->isCheckable()) {
            QString name = a->data().toString();
            if (inds.contains(name)) {
                bool checked = inds[name].toBool();
                a->setChecked(checked);
                emit indicatorToggled(name, checked);
            } else {
                a->setChecked(false);
                emit indicatorToggled(a->data().toString(), false);
            }
        }
    }

    emit templateApplied(config);
}

void ChartToolbarWidget::loadCustomTemplates()
{
    QString path = QStandardPaths::writableLocation(QStandardPaths::ConfigLocation)
                   + "/niskala/chart_templates.json";
    QFile file(path);
    if (file.open(QIODevice::ReadOnly)) {
        QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
        if (doc.isArray()) {
            m_customTemplates = doc.array();
            for (const auto &ct : m_customTemplates) {
                QJsonObject obj = ct.toObject();
                QString name = obj["name"].toString();
                if (!name.isEmpty()) {
                    auto *a = m_templateMenu->addAction(name);
                    a->setData(name);
                    connect(a, &QAction::triggered, this, &ChartToolbarWidget::onTemplateSelected);
                }
            }
        }
        file.close();
    }
}

void ChartToolbarWidget::saveCustomTemplates()
{
    QString dirPath = QStandardPaths::writableLocation(QStandardPaths::ConfigLocation)
                      + "/niskala";
    QDir().mkpath(dirPath);
    QString path = dirPath + "/chart_templates.json";
    QFile file(path);
    if (file.open(QIODevice::WriteOnly)) {
        QJsonDocument doc(m_customTemplates);
        file.write(doc.toJson());
        file.close();
    }
}

QStringList ChartToolbarWidget::templateNames() const
{
    QStringList names = {"Default", "TrendFollowing", "Momentum", "Volatility", "Clean"};
    for (const auto &ct : m_customTemplates) {
        names.append(ct.toObject()["name"].toString());
    }
    return names;
}

void ChartToolbarWidget::onSymbolActivated(int index)
{
    QString symbol = m_symbolCombo->itemData(index).toString();
    if (symbol.isEmpty())
        symbol = m_symbolCombo->currentText().section(' ', 0, 0).trimmed().toUpper();
    if (!symbol.isEmpty()) {
        emit symbolRequested(symbol);
    }
}

void ChartToolbarWidget::onTimeframeClicked()
{
    auto *btn = qobject_cast<QPushButton*>(sender());
    if (!btn) return;

    int index = m_tfButtons.indexOf(btn);
    if (index >= 0) {
        m_activeTf = index;
        updateTimeframeStyles();
        QStringList tfs = {"1m", "5m", "15m", "1h", "D", "W", "M"};
        emit timeframeChanged(tfs[index]);
    }
}

void ChartToolbarWidget::updateTimeframeStyles()
{
    for (int i = 0; i < m_tfButtons.size(); ++i) {
        if (i == m_activeTf) {
            m_tfButtons[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #75FF9E; border: none; "
                "font-weight: bold; font-size: 11px; }");
        } else {
            m_tfButtons[i]->setStyleSheet(
                "QPushButton { background-color: transparent; color: #859585; border: none; "
                "font-size: 11px; }"
                "QPushButton:hover { color: #E1E2E7; }");
        }
    }
}
