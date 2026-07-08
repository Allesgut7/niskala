#include "ChartScreen.h"
#include "../widgets/CandlestickChart.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>

ChartScreen::ChartScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
}

void ChartScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(6);

    // Top bar
    auto *topBar = new QHBoxLayout();

    auto *symbolLabel = new QLabel("Symbol:");
    symbolLabel->setStyleSheet("color: #7E8AA3;");
    topBar->addWidget(symbolLabel);

    m_symbolCombo = new QComboBox();
    m_symbolCombo->addItems({"BBCA", "BBRI", "BMRI", "TLKM", "GOTO", "ADRO", "UNVR", "ICBP", "ASII"});
    m_symbolCombo->setMinimumWidth(80);
    connect(m_symbolCombo, &QComboBox::currentTextChanged, this, &ChartScreen::loadSymbol);
    topBar->addWidget(m_symbolCombo);

    auto *tfLabel = new QLabel("  Timeframe:");
    tfLabel->setStyleSheet("color: #7E8AA3;");
    topBar->addWidget(tfLabel);

    m_timeframeCombo = new QComboBox();
    m_timeframeCombo->addItems({"1D", "1W", "1M", "3M", "6M", "1Y"});
    connect(m_timeframeCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &ChartScreen::onTimeframeChanged);
    topBar->addWidget(m_timeframeCombo);

    topBar->addStretch();

    // Indicators
    m_ma5Check = new QCheckBox("MA5");
    m_ma5Check->setChecked(true);
    m_ma5Check->setStyleSheet("color: #E6874C;");
    connect(m_ma5Check, &QCheckBox::toggled, this, &ChartScreen::onIndicatorToggled);
    topBar->addWidget(m_ma5Check);

    m_ma20Check = new QCheckBox("MA20");
    m_ma20Check->setChecked(true);
    m_ma20Check->setStyleSheet("color: #25D9FF;");
    connect(m_ma20Check, &QCheckBox::toggled, this, &ChartScreen::onIndicatorToggled);
    topBar->addWidget(m_ma20Check);

    m_volumeCheck = new QCheckBox("Volume");
    m_volumeCheck->setChecked(true);
    m_volumeCheck->setStyleSheet("color: #F7FAFC;");
    topBar->addWidget(m_volumeCheck);

    mainLayout->addLayout(topBar);

    // Chart
    m_chart = new CandlestickChart();
    mainLayout->addWidget(m_chart);
}

void ChartScreen::loadSymbol(const QString &symbol)
{
    m_chart->loadSymbol(symbol);
}

void ChartScreen::onTimeframeChanged(int index)
{
    QStringList tfs = {"1D", "1W", "1M", "3M", "6M", "1Y"};
    if (index >= 0 && index < tfs.size()) {
        m_chart->setTimeframe(tfs[index]);
    }
}

void ChartScreen::onIndicatorToggled()
{
    m_chart->setMA5Visible(m_ma5Check->isChecked());
    m_chart->setMA20Visible(m_ma20Check->isChecked());
}
