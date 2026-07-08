#include "NewsScreen.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>

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
    mainLayout->setSpacing(6);

    auto *headerLayout = new QHBoxLayout();
    auto *title = new QLabel("NEWS & AI SENTIMENT");
    title->setStyleSheet("color: #FFB4AB; font-weight: bold; font-size: 12px;");
    headerLayout->addWidget(title);

    headerLayout->addStretch();

    auto *seeAll = new QLabel("Lihat Semua");
    seeAll->setStyleSheet("color: #CEE8FF; font-size: 10px;");
    headerLayout->addWidget(seeAll);

    mainLayout->addLayout(headerLayout);

    // Filters
    auto *filterLayout = new QHBoxLayout();
    filterLayout->setSpacing(6);

    m_searchEdit = new QLineEdit();
    m_searchEdit->setPlaceholderText("Search news...");
    m_searchEdit->setStyleSheet(
        "QLineEdit { background-color: #1D2023; color: #E1E2E7; border: 1px solid #3B4A3D; "
        "padding: 6px; font-size: 11px; border-radius: 4px; }");
    connect(m_searchEdit, &QLineEdit::textChanged, this, &NewsScreen::onFilterChanged);
    filterLayout->addWidget(m_searchEdit);

    m_sourceFilter = new QComboBox();
    m_sourceFilter->addItems({"All Sources", "CNBC", "IDX", "Kontan", "Bisnis", "Reuters", "Tempo"});
    m_sourceFilter->setStyleSheet(
        "QComboBox { background-color: #1D2023; color: #E1E2E7; border: 1px solid #3B4A3D; "
        "padding: 4px; font-size: 11px; border-radius: 4px; }");
    connect(m_sourceFilter, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, &NewsScreen::onFilterChanged);
    filterLayout->addWidget(m_sourceFilter);

    mainLayout->addLayout(filterLayout);

    // News list
    m_newsList = new QListWidget();
    m_newsList->setStyleSheet(
        "QListWidget { background-color: transparent; border: none; }"
        "QListWidget::item { padding: 8px; border-bottom: 1px solid #3B4A3D; }"
        "QListWidget::item:selected { background-color: #3B4A3D; }");
    mainLayout->addWidget(m_newsList);
}

void NewsScreen::populateData()
{
    struct NewsItem {
        QString time;
        QString source;
        QString headline;
        QString aiAnalisis;
        QString dampakSektor;
        int sentiment; // -1, 0, 1
    };

    QList<NewsItem> news = {
        {"10:12 WIB", "CNBC Indonesia", "BI Putuskan Pertahankan Suku Bunga di 6,25%",
         "Neutral cenderung positif untuk sektor perbankan. Likuiditas stabil, NIM terjaga.",
         "Perbankan ++  Properti +  Konsumsi +", 1},
        {"09:45 WIB", "Kontan", "Harga Komoditas Menguat, Batu Bara Naik 1%",
         "Positif untuk emiten batubara. Potensi peningkatan margin pada Q2.",
         "Batubara +++  Energi ++", 1},
        {"09:20 WIB", "Detik Finance", "Rupiah Menguat Tipis ke Level 16.140 per USD",
         "Penguatan rupiah terbatas, masih dalam range konsolidasi.",
         "Eksportir -  Importir +  Perbankan 0", 0},
        {"08:30 WIB", "Reuters", "Nvidia +2.6% After Hours, Tech Rally Continues",
         "Sentimen positif untuk sektor teknologi global.",
         "Teknologi ++  Semikonduktor ++", 1},
        {"08:15 WIB", "Bloomberg", "Oil Prices Rise 1.8% on Supply Concerns",
         "Menguatnya harga minyak mendukung sektor energi.",
         "Energi ++  Pertambangan +", 1},
    };

    for (const auto &n : news) {
        QWidget *itemWidget = new QWidget();
        auto *itemLayout = new QVBoxLayout(itemWidget);
        itemLayout->setContentsMargins(8, 8, 8, 8);
        itemLayout->setSpacing(4);

        // Time + Source + Sentiment Badge
        auto *topLayout = new QHBoxLayout();
        auto *timeLabel = new QLabel(n.time);
        timeLabel->setStyleSheet("color: #859585; font-size: 10px;");
        topLayout->addWidget(timeLabel);

        auto *sourceLabel = new QLabel(n.source);
        sourceLabel->setStyleSheet("color: #BACBB9; font-size: 10px; font-weight: bold;");
        topLayout->addWidget(sourceLabel);

        topLayout->addStretch();

        // Sentiment Badge
        auto *badge = new QLabel();
        if (n.sentiment == 1) {
            badge->setText("Positive");
            badge->setStyleSheet(
                "QLabel { background-color: #005226; color: #75FF9E; padding: 2px 8px; "
                "border-radius: 4px; font-size: 10px; font-weight: bold; }");
        } else if (n.sentiment == -1) {
            badge->setText("Negative");
            badge->setStyleSheet(
                "QLabel { background-color: #A00118; color: #FFB3AE; padding: 2px 8px; "
                "border-radius: 4px; font-size: 10px; font-weight: bold; }");
        } else {
            badge->setText("Neutral");
            badge->setStyleSheet(
                "QLabel { background-color: #00344F; color: #CEE8FF; padding: 2px 8px; "
                "border-radius: 4px; font-size: 10px; font-weight: bold; }");
        }
        topLayout->addWidget(badge);

        itemLayout->addLayout(topLayout);

        // Headline
        auto *headlineLabel = new QLabel(n.headline);
        headlineLabel->setStyleSheet("color: #E1E2E7; font-size: 13px; font-weight: bold;");
        headlineLabel->setWordWrap(true);
        itemLayout->addWidget(headlineLabel);

        // AI Analisis
        auto *aiLabel = new QLabel("AI Analisis: " + n.aiAnalisis);
        aiLabel->setStyleSheet("color: #859585; font-size: 10px;");
        aiLabel->setWordWrap(true);
        itemLayout->addWidget(aiLabel);

        // Dampak Sektor
        auto *dampakLabel = new QLabel("Dampak Sektor: " + n.dampakSektor);
        dampakLabel->setStyleSheet("color: #BACBB9; font-size: 10px;");
        dampakLabel->setWordWrap(true);
        itemLayout->addWidget(dampakLabel);

        auto *listItem = new QListWidgetItem();
        listItem->setData(Qt::UserRole, n.source);
        listItem->setSizeHint(QSize(0, 200));
        m_newsList->addItem(listItem);
        m_newsList->setItemWidget(listItem, itemWidget);
    }
}

void NewsScreen::onFilterChanged()
{
    QString search = m_searchEdit->text().toUpper();
    int sourceIdx = m_sourceFilter->currentIndex();
    QStringList sources = {"All Sources", "CNBC", "IDX", "Kontan", "Bisnis", "Reuters", "Tempo"};

    for (int i = 0; i < m_newsList->count(); ++i) {
        auto *item = m_newsList->item(i);
        if (!item) continue;

        bool visible = true;

        // Source filter
        if (sourceIdx > 0 && sourceIdx < sources.size()) {
            QString itemSource = item->data(Qt::UserRole).toString();
            if (!itemSource.contains(sources[sourceIdx], Qt::CaseInsensitive)) {
                visible = false;
            }
        }

        // Search filter
        if (!search.isEmpty()) {
            auto *widget = m_newsList->itemWidget(item);
            if (widget) {
                QList<QLabel*> labels = widget->findChildren<QLabel*>();
                bool found = false;
                for (auto *label : labels) {
                    if (label->text().toUpper().contains(search)) {
                        found = true;
                        break;
                    }
                }
                if (!found) visible = false;
            }
        }

        item->setHidden(!visible);
    }
}
