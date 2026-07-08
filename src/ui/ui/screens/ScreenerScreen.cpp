#include "ScreenerScreen.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QGroupBox>

ScreenerScreen::ScreenerScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateData();
}

void ScreenerScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);
    mainLayout->setSpacing(4);

    // Title
    auto *title = new QLabel("STOCK SCREENER");
    title->setStyleSheet("color: #D84B63; font-weight: bold; font-size: 14px;");
    mainLayout->addWidget(title);

    // Filters
    auto *filterLayout = new QHBoxLayout();

    m_searchEdit = new QLineEdit();
    m_searchEdit->setPlaceholderText("Search symbol...");
    m_searchEdit->setStyleSheet(
        "QLineEdit { background-color: #101827; color: #25D9FF; border: 1px solid #1D2B40; "
        "padding: 6px; font-family: monospace; }"
    );
    connect(m_searchEdit, &QLineEdit::textChanged, this, &ScreenerScreen::onSearchTextChanged);
    filterLayout->addWidget(m_searchEdit);

    m_sectorCombo = new QComboBox();
    m_sectorCombo->addItems({"All Sectors", "Finance", "Consumer", "Industrial", "Technology", "Energy"});
    connect(m_sectorCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &ScreenerScreen::onFilterChanged);
    filterLayout->addWidget(m_sectorCombo);

    m_changeCombo = new QComboBox();
    m_changeCombo->addItems({"All Change", "Gainers (>0%)", "Losers (<0%)", "Big Gainers (>2%)"});
    connect(m_changeCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &ScreenerScreen::onFilterChanged);
    filterLayout->addWidget(m_changeCombo);

    m_volumeCombo = new QComboBox();
    m_volumeCombo->addItems({"All Volume", "High (>50M)", "Medium (10-50M)", "Low (<10M)"});
    connect(m_volumeCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &ScreenerScreen::onFilterChanged);
    filterLayout->addWidget(m_volumeCombo);

    mainLayout->addLayout(filterLayout);

    // Result count
    m_resultCount = new QLabel("Found: 0 stocks");
    m_resultCount->setStyleSheet("color: #7E8AA3; font-size: 11px;");
    mainLayout->addWidget(m_resultCount);

    // Table
    m_table = new QTableWidget();
    m_table->setColumnCount(8);
    m_table->setHorizontalHeaderLabels(
        {"Symbol", "Name", "Price", "Chg", "Chg%", "Volume", "Market Cap", "Sector"});
    m_table->horizontalHeader()->setSectionResizeMode(1, QHeaderView::Stretch);
    m_table->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_table->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_table->setAlternatingRowColors(true);
    m_table->verticalHeader()->setVisible(false);
    m_table->setStyleSheet(
        "QTableWidget { background-color: #101827; alternate-background-color: #101827; }"
    );
    connect(m_table, &QTableWidget::cellClicked, this, &ScreenerScreen::onRowClicked);
    mainLayout->addWidget(m_table);
}

void ScreenerScreen::populateData()
{
    struct StockInfo {
        QString symbol, name, sector;
        double price, change, changePct;
        QString volume, marketCap;
    };

    QList<StockInfo> stocks = {
        {"BBCA", "Bank Central Asia", "Finance", 9200, 150, 1.66, "45M", "1,080T"},
        {"BBRI", "Bank Rakyat Indonesia", "Finance", 4800, -50, -1.03, "38M", "590T"},
        {"BMRI", "Bank Mandiri", "Finance", 6150, 75, 1.23, "28M", "520T"},
        {"BBNI", "Bank Negara Indonesia", "Finance", 5200, -30, -0.57, "22M", "310T"},
        {"TLKM", "Telkom Indonesia", "Technology", 2850, 25, 0.88, "22M", "280T"},
        {"GOTO", "GoTo Gojek", "Technology", 85, -2, -2.30, "156M", "125T"},
        {"ADRO", "Adaro Energy", "Energy", 1520, 30, 2.01, "18M", "89T"},
        {"UNVR", "Unilever Indonesia", "Consumer", 4250, -75, -1.73, "12M", "98T"},
        {"ICBP", "Indofood CBP", "Consumer", 11200, 200, 1.82, "8M", "145T"},
        {"ASII", "Astra International", "Industrial", 5400, 50, 0.93, "15M", "220T"},
        {"PGAS", "Petamina Gas", "Energy", 1890, 10, 0.53, "25M", "45T"},
        {"EXCL", "XL Axiata", "Technology", 2100, -15, -0.71, "8M", "48T"},
        {"ISAT", "Indosat Ooredoo", "Technology", 5200, 40, 0.78, "10M", "52T"},
        {"MDKA", "Merdeka Copper", "Industrial", 1350, 45, 3.44, "20M", "67T"},
        {"BREN", "Barito Renewables", "Energy", 8500, 150, 1.80, "5M", "180T"},
    };

    m_allSymbols.clear();
    m_table->setRowCount(stocks.size());

    for (int i = 0; i < stocks.size(); ++i) {
        const auto &s = stocks[i];
        m_allSymbols.append(s.symbol);

        m_table->setItem(i, 0, new QTableWidgetItem(s.symbol));
        m_table->setItem(i, 1, new QTableWidgetItem(s.name));

        auto *priceItem = new QTableWidgetItem(QString::number(s.price, 'f', 0));
        priceItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 2, priceItem);

        auto *chgItem = new QTableWidgetItem(
            QString::number(s.change, 'f', 0));
        chgItem->setForeground(s.change >= 0 ? QColor("#25D9FF") : QColor("#ff4757"));
        chgItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 3, chgItem);

        QString pctStr = (s.changePct >= 0 ? "+" : "") +
                         QString::number(s.changePct, 'f', 2) + "%";
        auto *pctItem = new QTableWidgetItem(pctStr);
        pctItem->setForeground(s.changePct >= 0 ? QColor("#25D9FF") : QColor("#ff4757"));
        pctItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 4, pctItem);

        auto *volItem = new QTableWidgetItem(s.volume);
        volItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 5, volItem);

        auto *capItem = new QTableWidgetItem(s.marketCap);
        capItem->setTextAlignment(Qt::AlignRight | Qt::AlignVCenter);
        m_table->setItem(i, 6, capItem);

        m_table->setItem(i, 7, new QTableWidgetItem(s.sector));
    }

    m_resultCount->setText(QString("Found: %1 stocks").arg(stocks.size()));
}

void ScreenerScreen::onFilterChanged()
{
    applyFilters();
}

void ScreenerScreen::onSearchTextChanged(const QString &text)
{
    Q_UNUSED(text);
    applyFilters();
}

void ScreenerScreen::applyFilters()
{
    QString search = m_searchEdit->text().toUpper();
    int sectorIdx = m_sectorCombo->currentIndex();
    int changeIdx = m_changeCombo->currentIndex();
    int volumeIdx = m_volumeCombo->currentIndex();

    for (int i = 0; i < m_table->rowCount(); ++i) {
        bool visible = true;

        // Search filter
        if (!search.isEmpty()) {
            QString symbol = m_table->item(i, 0)->text().toUpper();
            QString name = m_table->item(i, 1)->text().toUpper();
            if (!symbol.contains(search) && !name.contains(search)) {
                visible = false;
            }
        }

        // Sector filter
        if (sectorIdx > 0) {
            QString sector = m_table->item(i, 7)->text();
            QStringList sectors = {"Finance", "Consumer", "Industrial", "Technology", "Energy"};
            if (sectorIdx - 1 < sectors.size() && sector != sectors[sectorIdx - 1]) {
                visible = false;
            }
        }

        // Change filter
        if (changeIdx > 0) {
            double pct = m_table->item(i, 4)->text().replace("%", "").toDouble();
            if (changeIdx == 1 && pct <= 0) visible = false;
            if (changeIdx == 2 && pct >= 0) visible = false;
            if (changeIdx == 3 && pct <= 2.0) visible = false;
        }

        m_table->setRowHidden(i, !visible);
    }

    int visibleCount = 0;
    for (int i = 0; i < m_table->rowCount(); ++i) {
        if (!m_table->isRowHidden(i)) visibleCount++;
    }
    m_resultCount->setText(QString("Found: %1 stocks").arg(visibleCount));
}

void ScreenerScreen::onRowClicked(int row, int col)
{
    Q_UNUSED(col);
    if (row >= 0) {
        emit symbolSelected(m_table->item(row, 0)->text());
    }
}
