#include "NewsScreen.h"
#include <QVBoxLayout>
#include <QHBoxLayout>

NewsScreen::NewsScreen(QWidget *parent)
    : QWidget(parent)
{
    setupUI();
    populateData();
}

void NewsScreen::setupUI()
{
    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(8);

    auto *title = new QLabel("NEWS & SENTIMENT");
    title->setStyleSheet("color: #e94560; font-size: 16px; font-weight: bold;");
    mainLayout->addWidget(title);

    // Filters
    auto *filterLayout = new QHBoxLayout();

    m_searchEdit = new QLineEdit();
    m_searchEdit->setPlaceholderText("Search news...");
    m_searchEdit->setStyleSheet(
        "QLineEdit { background-color: #16213e; color: #00d989; border: 1px solid #0f3460; "
        "padding: 6px; font-family: monospace; }");
    connect(m_searchEdit, &QLineEdit::textChanged, this, &NewsScreen::onFilterChanged);
    filterLayout->addWidget(m_searchEdit);

    m_sourceFilter = new QComboBox();
    m_sourceFilter->addItems({"All Sources", "CNBC", "IDX", "Kontan", "Bisnis", "Reuters", "Tempo"});
    connect(m_sourceFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &NewsScreen::onFilterChanged);
    filterLayout->addWidget(m_sourceFilter);

    m_sentimentFilter = new QComboBox();
    m_sentimentFilter->addItems({"All Sentiment", "Bullish ↑", "Bearish ↓", "Neutral →"});
    connect(m_sentimentFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &NewsScreen::onFilterChanged);
    filterLayout->addWidget(m_sentimentFilter);

    mainLayout->addLayout(filterLayout);

    // News list
    m_newsList = new QListWidget();
    m_newsList->setAlternatingRowColors(true);
    m_newsList->setStyleSheet(
        "QListWidget { background-color: #1a1a2e; alternate-background-color: #16213e; }");
    mainLayout->addWidget(m_newsList);
}

void NewsScreen::populateData()
{
    struct NewsItem {
        QString source;
        QString headline;
        QString tickers;
        int sentiment; // -1, 0, 1
    };

    QList<NewsItem> news = {
        {"CNBC", "BBRI: Laba bersih Q3 naik 15% YoY ke Rp 13.2 triliun", "BBRI", 1},
        {"IDX", "TLKM: Dividen final ditetapkan Rp 200 per saham, ex-date 15 Jul", "TLKM", 1},
        {"Kontan", "GOTO: Revenue Q3 tembus Rp 7 triliun, pertumbuhan 25%", "GOTO", 1},
        {"Bisnis", "BMRI: Target pertumbuhan laba 12% di FY2026", "BMRI", 0},
        {"Reuters", "ADRO: Harga batu bara rebound, outlook membaik", "ADRO", 1},
        {"Tempo", "UNVR: Penjualan turun 5% di Q3, tantangan demand", "UNVR", -1},
        {"CNBC", "ICBP: Laba bersih naik 18% didukung margin improved", "ICBP", 1},
        {"IDX", "ASII: Penjualan mobil Q3 stagnan, target 550K unit", "ASII", 0},
        {"Kontan", "GOTO: Saham mencatat rebound 3% setelah earnings beat", "GOTO", 1},
        {"Bisnis", "BBCA: NPL ratio turun ke 2.1%, kualitas aset membaik", "BBCA", 1},
        {"Reuters", "PGAS: Gas prices stable, revenue growth moderate", "PGAS", 0},
        {"Tempo", "EXCL: Subscriber loss Q3, kompetisi telkom makin ketat", "EXCL", -1},
        {"CNBC", "MDKA: Copper prices surge, outlook bullish for miners", "MDKA", 1},
        {"IDX", "BREN: Renewable energy push, baru saja IPO", "BREN", 1},
        {"Kontan", "BBNI: Provisions increase 10%, cautiously optimistic", "BBNI", 0},
    };

    for (const auto &n : news) {
        QString sentimentIcon;
        QColor sentimentColor;

        if (n.sentiment == 1) {
            sentimentIcon = "↑";
            sentimentColor = QColor("#00d989");
        } else if (n.sentiment == -1) {
            sentimentIcon = "↓";
            sentimentColor = QColor("#ff4757");
        } else {
            sentimentIcon = "→";
            sentimentColor = QColor("#ffc107");
        }

        QString displayText = QString("[%1]  %2  [%3]  %4")
            .arg(n.source)
            .arg(n.headline)
            .arg(n.tickers)
            .arg(sentimentIcon);

        auto *item = new QListWidgetItem(displayText);
        item->setForeground(sentimentColor);
        item->setData(Qt::UserRole, n.source);
        m_newsList->addItem(item);
    }
}

void NewsScreen::onFilterChanged()
{
    QString search = m_searchEdit->text().toUpper();
    int sourceIdx = m_sourceFilter->currentIndex();
    int sentimentIdx = m_sentimentFilter->currentIndex();

    for (int i = 0; i < m_newsList->count(); ++i) {
        auto *item = m_newsList->item(i);
        QString text = item->text().toUpper();
        QString source = item->data(Qt::UserRole).toString();
        bool visible = true;

        // Search
        if (!search.isEmpty() && !text.contains(search)) {
            visible = false;
        }

        // Source filter
        if (sourceIdx > 0) {
            QStringList sources = {"CNBC", "IDX", "Kontan", "Bisnis", "Reuters", "Tempo"};
            if (sourceIdx - 1 < sources.size() && source != sources[sourceIdx - 1]) {
                visible = false;
            }
        }

        // Sentiment filter
        if (sentimentIdx > 0) {
            if (sentimentIdx == 1 && !text.contains("↑")) visible = false;
            if (sentimentIdx == 2 && !text.contains("↓")) visible = false;
            if (sentimentIdx == 3 && !text.contains("→")) visible = false;
        }

        item->setHidden(!visible);
    }
}
