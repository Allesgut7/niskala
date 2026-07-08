# Niskala Dashboard UI Documentation

> Complete reference for all dashboard widgets, layout structure, and design system.

---

## Table of Contents

1. [Color Palette](#color-palette)
2. [Layout Structure](#layout-structure)
3. [Widget Reference](#widget-reference)
4. [DashboardScreen](#dashboardscreen)
5. [ThemeManager Constants](#thememanager-constants)

---

## Color Palette

### Obsidian Terminal Theme (from Stitch Design System)

| Token | Hex | Fungsi |
|-------|-----|--------|
| `BG_PRIMARY` | `#060B16` | Workspace utama |
| `BG_SECONDARY` | `#111417` | Panel besar, navbar |
| `BG_SURFACE` | `#1D2023` | Card & Widget background |
| `SURFACE_LOW` | `#191C1F` | Input field background |
| `SURFACE_HOVER` | `#272A2E` | Hover state |
| `SURFACE_ACTIVE` | `#323538` | Active state, footer |
| `BORDER` | `#3B4A3D` | Garis pemisah, borders |
| `BULL` | `#75FF9E` | Kenaikan harga (green) |
| `BEAR` | `#FFB3AE` | Penurunan harga (red) |
| `ACCENT_CYAN` | `#CEE8FF` | Accent, info, headers |
| `TEXT_PRIMARY` | `#E1E2E7` | Judul, nilai utama |
| `TEXT_SECONDARY` | `#BACBB9` | Label, isi sekunder |
| `TEXT_MUTED` | `#859585` | Metadata, timestamp |
| `ERROR` | `#FFB4AB` | Error/alert |

### Font Families

| Context | Font | Fallback |
|---------|------|----------|
| **UI/Labels** | Inter | Ubuntu, Segoe UI, Noto Sans, sans-serif |
| **Data/Numbers** | JetBrains Mono | Consolas, monospace |

### Border Radius

| Element | Radius |
|---------|--------|
| Cards/Containers | 6px |
| Buttons/Inputs | 4px |
| Badges | 4px |
| Gauges | Round |

---

## Layout Structure

### Dashboard Layout (70/30 Split)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [1] NavigationBar (55px)                                                    │
│   Logo | Tabs | Search | Icons                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ [2] BreakingNewsTicker (36px)                                               │
│   [BREAKING] scrolling headlines...                              10:24 WIB │
├─────────────────────────────────────────────────────────────────────────────┤
│ [3] MarketIndicesStrip (90px)                                               │
│   [IHSG] [NIKKEI] [NASDAQ] [LQ45] [S&P500] [USD/IDR] (scrollable)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────┬───────────────────────────────────┐ │
│ │ LEFT PANEL (70%)                   │ RIGHT PANEL (30%, scrollable)     │ │
│ │                                    │                                   │ │
│ │ [4a] ChartToolbarWidget (40px)     │ [5] FearGreedGauge x3            │ │
│ │ Symbol | Timeframe | Icons | Price │   Indo/63  Asia/55  Global/48    │ │
│ │                                    ├───────────────────────────────────┤ │
│ │ [4b] CandlestickChart (flex)       │ [6] CommodityTable               │ │
│ │ OHLC + MA5/MA20 + volume           │   Gold, Oil, Coal, Nickel...     │ │
│ │                                    │   (extends with stretch)         │ │
│ │                                    ├───────────────────────────────────┤ │
│ │                                    │ [7] MarketBreadthWidget          │ │
│ │                                    │   Gauge + Naik/Turun/Stagnan     │ │
│ │                                    ├───────────────────────────────────┤ │
│ │ [4c] NewsScreen    │ [4d] Sector  │ [8] AIMarketRegimeWidget         │ │
│ │ News + sentiment   │ Performance  │   [LIVE] MODERATE BULL 82%       │ │
│ │                    │ 11 sectors   │                                   │ │
│ ├────────────────────┴───────────────┴───────────────────────────────────┤ │
│ │ [9] BottomTicker (44px)                                                 │ │
│ │ TOP GAINERS: DCII +24.2% ... │ TOP LOSERS: BUKA -7.8% ...             │ │
│ ├────────────────────────────────────────────────────────────────────────┤ │
│ │ [10] FooterWidget (24px)                                               │ │
│ │ NISKALA TERMINAL v1.0.0-STABLE | System Status | API Docs | Legal     │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Section Mapping

| # | Section | File | Height |
|---|---------|------|--------|
| 1 | NavigationBar | `widgets/NavigationBar.cpp` | 55px |
| 2 | BreakingNewsTicker | `widgets/BreakingNewsTicker.cpp` | 36px |
| 3 | MarketIndicesStrip | `widgets/MarketIndicesStrip.cpp` | 90px |
| 4a | ChartToolbar | `widgets/ChartToolbarWidget.cpp` | 40px |
| 4b | CandlestickChart | `widgets/CandlestickChart.cpp` | flex |
| 4c | NewsScreen | `screens/NewsScreen.cpp` | flex |
| 4d | SectorPerformance | `widgets/SectorPerformanceWidget.cpp` | flex |
| 5 | FearGreedGauge x3 | `widgets/FearGreedGauge.cpp` | 90px |
| 6 | CommodityTable | `widgets/CommodityTable.cpp` | stretch |
| 7 | MarketBreadth | `widgets/MarketBreadthWidget.cpp` | 180px |
| 8 | AIMarketRegime | `widgets/AIMarketRegimeWidget.cpp` | 140px |
| 9 | BottomTicker | `screens/DashboardScreen.cpp` (inline) | 44px |
| 10 | FooterWidget | `widgets/FooterWidget.cpp` | 24px |

---

## Widget Reference

### 1. NavigationBar

**File:** `ui/widgets/NavigationBar.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `NavigationBar` |
| Parent | `QWidget` |
| Height | 55px (fixed) |

**Signals:**
- `tabClicked(int index)` — Emit when tab clicked

**Member Variables:**
- `QList<QPushButton*> m_tabs` — Tab buttons
- `int m_activeTab = 0` — Currently selected tab

**Tabs:**
| Index | Label |
|-------|-------|
| 0 | Dashboard |
| 1 | Market |
| 2 | News |
| 3 | Screener |
| 4 | Kalender Market |
| 5 | Portofolio |
| 6 | Settings |

**Visual Elements:**
- Logo (image: `Logo-fix.png`)
- Tab buttons with active indicator (green underline)
- Search input (`QLineEdit`)
- Notification icon
- User icon

---

### 2. BreakingNewsTicker

**File:** `ui/widgets/BreakingNewsTicker.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `BreakingNewsTicker` |
| Parent | `QWidget` |
| Height | 36px (fixed) |

**Member Variables:**
- `QStringList m_headlines` — News headlines to scroll
- `int m_scrollOffset = 0` — Current scroll position
- `QTimer *m_timer` — Scroll animation timer (60ms)

**Sample Headlines:**
```
BBRI Buyback approved
BI Pertahankan Suku Bunga di 6.25%
Foreign Net Buy IDR 1.24T (All Market)
The Fed Minutes Tonight
Oil Menguat 1.8%
Nvidia +2.6% After Hours
```

**Visual Elements:**
- `[ BREAKING ]` badge (red text)
- Scrolling headlines (left to right)
- Current time display (right-aligned)

---

### 3. MarketIndicesStrip

**File:** `ui/widgets/MarketIndicesStrip.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `MarketIndicesStrip` |
| Parent | `QWidget` |
| Height | 90px (fixed) |

**Member Variables:**
- `QList<MarketIndexCard*> m_cards` — 7 market index cards

**Dependencies:**
- `MarketIndexCard` (7 instances)

---

### 4. MarketIndexCard

**File:** `ui/widgets/MarketIndexCard.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `MarketIndexCard` |
| Parent | `QWidget` |
| Min Size | 140x80 |
| Max Height | 80px |

**Constructor:**
```cpp
MarketIndexCard(const QString &name, double value, double change, double changePct, QWidget *parent = nullptr)
```

**Public Methods:**
- `void updateData(double value, double change, double changePct)` — Update card data

**Member Variables:**
- `QString m_name` — Index name (e.g., "IHSG")
- `double m_value` — Current value
- `double m_change` — Change value
- `double m_changePct` — Change percentage

**Rendering:**
- Name (gray, 9pt)
- Value (white, 14pt bold)
- Change + % (green/red based on sign)
- Mini sparkline chart (40x30px, top-right)

**Colors:**
| Element | Color |
|---------|-------|
| Background | `#111417` |
| Border | `#3B4A3D` |
| Name text | `#BACBB9` |
| Value text | `#E1E2E7` |
| Positive | `#75FF9E` |
| Negative | `#FFB3AE` |

---

### 5. ChartToolbarWidget

**File:** `ui/widgets/ChartToolbarWidget.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `ChartToolbarWidget` |
| Parent | `QWidget` |
| Height | 40px (fixed) |

**Signals:**
- `timeframeChanged(const QString &tf)` — Timeframe button clicked
- `chartTypeChanged(const QString &type)` — Chart type changed

**Member Variables:**
- `QList<QPushButton*> m_tfButtons` — Timeframe buttons
- `int m_activeTf = 3` — Active timeframe (D = Daily)

**Timeframe Options:**
| Index | Label |
|-------|-------|
| 0 | 1m |
| 1 | 5m |
| 2 | 15m |
| 3 | 1h |
| 4 | D |
| 5 | W |
| 6 | M |

**Visual Elements:**
- Symbol name (green, bold)
- Timeframe buttons
- Chart type icons (📈 📊 📉)
- Current price (green, JetBrains Mono)
- Settings icon
- Fullscreen icon

---

### 6. CandlestickChart

**File:** `ui/widgets/CandlestickChart.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `CandlestickChart` |
| Parent | `QWidget` |
| Dependencies | Qt Charts (QChart, QChartView, QCandlestickSeries, QLineSeries, QValueAxis) |

**Signals:**
- `symbolClicked(const QString &symbol)` — Symbol clicked

**Public Methods:**
- `void loadSymbol(const QString &symbol)` — Load new symbol data
- `void setTimeframe(const QString &tf)` — Change timeframe
- `void setMA5Visible(bool visible)` — Toggle MA5 line visibility
- `void setMA20Visible(bool visible)` — Toggle MA20 line visibility

**Member Variables:**
- `QChart *m_chart` — Chart object
- `QChartView *m_chartView` — Chart view widget
- `QCandlestickSeries *m_candleSeries` — Candlestick data
- `QLineSeries *m_ma5Series` — MA5 line
- `QLineSeries *m_ma20Series` - MA20 line
- `QValueAxis *m_axisX`, `*m_axisY` — Chart axes
- `QString m_currentSymbol = "BBCA"` — Current symbol
- `QString m_timeframe = "1D"` — Current timeframe
- `QTimer *m_refreshTimer` — Auto-refresh timer (5s)

**Colors:**
| Element | Color |
|---------|-------|
| Background | `#1D2023` |
| Increasing candle | `#75FF9E` |
| Decreasing candle | `#FFB3AE` |
| MA5 line | `#CEE8FF` |
| MA20 line | `#859585` |
| Grid lines | `#3B4A3D` |

---

### 7. FearGreedGauge

**File:** `ui/widgets/FearGreedGauge.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `FearGreedGauge` |
| Parent | `QWidget` |
| Min Size | 100x80 |
| Max Height | 90px |

**Constructor:**
```cpp
FearGreedGauge(const QString &label = "ID", QWidget *parent = nullptr)
```

**Signals:**
- `scoreChanged(int score)` — Score changed

**Public Methods:**
- `void setScore(int score)` — Set gauge score (0-100)
- `void setDelta(int delta)` — Set delta change value
- `int score() const` — Get current score

**Member Variables:**
- `int m_score = 50` — Current score
- `int m_delta = 0` — Delta change
- `QString m_label` — Gauge label (e.g., "Indonesia")

**Score Color Mapping:**
| Range | Color | Label |
|-------|-------|-------|
| 0-20 | `#FFB3AE` | Extreme Fear |
| 21-40 | `#CEE8FF` | Fear |
| 41-60 | `#859585` | Neutral |
| 61-80 | `#CEE8FF` | Greed |
| 81-100 | `#75FF9E` | Extreme Greed |

**Visual Elements:**
- Mini semicircle gauge (6px arc)
- Center dot
- Score number (JetBrains Mono, 14pt bold)
- Delta text ("+8 dari kemarin")
- Label (Inter, 8pt)

---

### 8. CommodityTable

**File:** `ui/widgets/CommodityTable.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `CommodityTable` |
| Parent | `QWidget` |

**Table Configuration:**
- 7 rows x 4 columns
- Columns: Commodity, Price, Change, %
- Alternating row colors
- No grid, no vertical header

**Commodity Data:**
| Commodity | Price | Change | % |
|-----------|-------|--------|---|
| Gold (XAU/USD) | 2,344.75 | +18.45 | +0.79% |
| Crude Oil (WTI) | 78.64 | +1.42 | +1.84% |
| Coal (Newcastle) | 134.80 | -1.20 | -0.88% |
| Nickel (LME) | 16,742 | -112 | -0.66% |
| Copper (LME) | 9,563 | +67 | +0.71% |
| CPO (MYR/Ton) | 3,890 | +36 | +0.93% |
| Natural Gas | 2.31 | +0.04 | +1.77% |

**Colors:**
| Element | Color |
|---------|-------|
| Header text | `#CEE8FF` |
| Table text | `#E1E2E7` |
| Positive change | `#75FF9E` |
| Negative change | `#FFB3AE` |

---

### 9. MarketBreadthWidget

**File:** `ui/widgets/MarketBreadthWidget.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `MarketBreadthWidget` |
| Parent | `QWidget` |
| Min Size | 200x180 |

**Member Variables:**
- `int m_naik = 272` — Advancing stocks
- `int m_turun = 158` — Declining stocks
- `int m_stagnan = 46` — Unchanged stocks
- `int m_total = 476` — Total stocks (auto-calculated)

**Rendering:**
- Semi-circle gauge (center at 35% width)
- Arc thickness: 12px
- 3 colored segments: Naik (green), Stagnan (gray), Turun (red)
- Right side: 3 stat columns (count, label, %)
- Bottom: "Total Saham 476"

**Colors:**
| Element | Color |
|---------|-------|
| Naik arc | `#75FF9E` |
| Turun arc | `#FFB3AE` |
| Stagnan arc | `#859585` |
| Background arc | `#3B4A3D` |
| Stats labels | `#BACBB9` |
| Total text | `#E1E2E7` |

---

### 10. AIMarketRegimeWidget

**File:** `ui/widgets/AIMarketRegimeWidget.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `AIMarketRegimeWidget` |
| Parent | `QWidget` |
| Min Height | 140px |

**Member Variables:**
- `QString m_regime = "MODERATE BULL"` — Market regime text
- `int m_confidence = 82` — Confidence score
- `QString m_analysis` — Analysis description

**Default Analysis:**
```
Momentum indicates sustained accumulation in Blue Chip stocks.
RSI divergence suggests a potential cooling period near 7,200.
```

**Visual Elements:**
- `[ AI MARKET REGIME ]` header (green)
- `[LIVE]` badge (green background)
- Spinning icon (circle with arrow)
- Regime text (white, 16pt bold)
- Confidence score (muted)
- Analysis text (secondary color)

**Colors:**
| Element | Color |
|---------|-------|
| Border | `#75FF9E` (primary green) |
| Header text | `#75FF9E` |
| LIVE badge bg | `#75FF9E` |
| Regime text | `#E1E2E7` |
| Analysis text | `#BACBB9` |

---

### 11. SectorPerformanceWidget

**File:** `ui/widgets/SectorPerformanceWidget.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `SectorPerformanceWidget` |
| Parent | `QWidget` |
| Min Height | 250px |

**Data Structure:**
```cpp
struct SectorData {
    QString name;
    double changePct;
};
```

**Sector Data (11 sectors):**
| Rank | Sector | Change % |
|------|--------|----------|
| 1 | Teknologi | +2.45% |
| 2 | Energi | +1.87% |
| 3 | Keuangan | +1.56% |
| 4 | Industri | +1.21% |
| 5 | Bahan Baku | +0.98% |
| 6 | Infrastruktur | +0.72% |
| 7 | Konsumen Primer | +0.45% |
| 8 | Properti | -0.21% |
| 9 | Kesehatan | -0.33% |
| 10 | Konsumen Non-Primer | -0.65% |
| 11 | Transportasi | -0.91% |

**Rendering:**
- Horizontal bar chart
- Positive: green bar from center
- Negative: red bar from center
- Rank number, sector name, bar, percentage

---

### 12. NewsScreen

**File:** `ui/screens/NewsScreen.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `NewsScreen` |
| Parent | `QWidget` |

**Member Variables:**
- `QListWidget *m_newsList` — News items list
- `QComboBox *m_sourceFilter` — Source filter dropdown
- `QComboBox *m_sentimentFilter` — Sentiment filter dropdown
- `QLineEdit *m_searchEdit` — Search input

**Filter Options:**
| Filter | Options |
|--------|---------|
| Source | All Sources, CNBC, IDX, Kontan, Bisnis, Reuters, Tempo |
| Sentiment | All, Bullish ↑, Bearish ↓, Neutral → |

**Sentiment Badge Colors:**
| Sentiment | Background | Text |
|-----------|------------|------|
| Positive | `#005226` | `#75FF9E` |
| Negative | `#A00118` | `#FFB3AE` |
| Neutral | `#00344F` | `#CEE8FF` |

**News Items Structure:**
- Time (JetBrains Mono, primary color)
- Source (secondary color, bold)
- Sentiment badge (colored)
- Headline (primary, bold)
- AI Analisis (muted)
- Dampak Sektor (secondary)

---

### 13. FooterWidget

**File:** `ui/widgets/FooterWidget.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `FooterWidget` |
| Parent | `QWidget` |
| Height | 24px (fixed) |

**Visual Elements:**
- Left: `NISKALA TERMINAL v1.0.0-STABLE | CONNECTED: SG-RT-01`
- Right: `System Status    API Documentation    Legal`

**Colors:**
| Element | Color |
|---------|-------|
| Background | `#323538` |
| Text | `#859585` |

---

## DashboardScreen

**File:** `ui/screens/DashboardScreen.h` / `.cpp`

| Property | Value |
|----------|-------|
| Class | `DashboardScreen` |
| Parent | `QWidget` |
| Layout | QVBoxLayout (main) → QHBoxLayout (70/30) |

### Layout Structure

```
QVBoxLayout (main, spacing=0)
├── NavigationBar (55px)
├── BreakingNewsTicker (36px)
├── MarketIndicesStrip (90px)
├── QHBoxLayout (mainContent, spacing=12)
│   ├── Left Panel (70%)
│   │   ├── ChartToolbarWidget (40px)
│   │   ├── CandlestickChart (flex)
│   │   └── QHBoxLayout
│   │       ├── NewsScreen (50%)
│   │       └── SectorPerformanceWidget (50%)
│   └── Right Panel (30%, QScrollArea)
│       ├── FearGreedGauge x3
│       ├── CommodityTable (stretch=1)
│       ├── MarketBreadthWidget
│       ├── AIMarketRegimeWidget
│       └── stretch
├── BottomTicker (44px)
└── FooterWidget (24px)
```

### Member Variables

| Variable | Type | Description |
|----------|------|-------------|
| `m_navBar` | `NavigationBar*` | Navigation bar |
| `m_ticker` | `BreakingNewsTicker*` | News ticker |
| `m_indicesStrip` | `MarketIndicesStrip*` | Market indices |
| `m_chart` | `CandlestickChart*` | Candlestick chart |
| `m_fgIndo` | `FearGreedGauge*` | Fear & Greed - Indonesia |
| `m_fgAsia` | `FearGreedGauge*` | Fear & Greed - Asia |
| `m_fgGlobal` | `FearGreedGauge*` | Fear & Greed - Global |
| `m_commodityTable` | `CommodityTable*` | Commodity prices |
| `m_breadth` | `MarketBreadthWidget*` | Market breadth |
| `m_news` | `NewsScreen*` | News feed |
| `m_sectorPerf` | `SectorPerformanceWidget*` | Sector performance |

### Default Values

| Widget | Default |
|--------|---------|
| FearGreedGauge (Indo) | Score: 63, Delta: +8 |
| FearGreedGauge (Asia) | Score: 55, Delta: +3 |
| FearGreedGauge (Global) | Score: 48, Delta: -2 |

---

## ThemeManager Constants

**File:** `ui/theme/ThemeManager.h`

```cpp
class ThemeManager {
    // Background
    static constexpr const char *BG_PRIMARY = "#060B16";
    static constexpr const char *BG_SECONDARY = "#111417";
    static constexpr const char *BG_SURFACE = "#1D2023";
    static constexpr const char *SURFACE_LOW = "#191C1F";
    static constexpr const char *SURFACE_HOVER = "#272A2E";
    static constexpr const char *SURFACE_ACTIVE = "#323538";

    // Border
    static constexpr const char *BORDER = "#3B4A3D";

    // Brand
    static constexpr const char *BRAND_CYAN = "#CEE8FF";
    static constexpr const char *BRAND_GREEN = "#75FF9E";
    static constexpr const char *ACCENT_RED = "#FFB4AB";

    // Text
    static constexpr const char *TEXT_PRIMARY = "#E1E2E7";
    static constexpr const char *TEXT_SECONDARY = "#BACBB9";
    static constexpr const char *TEXT_MUTED = "#859585";

    // Market
    static constexpr const char *BULL = "#75FF9E";
    static constexpr const char *BEAR = "#FFB3AE";
    static constexpr const char *WARNING = "#CEE8FF";
    static constexpr const char *ERROR = "#FFB4AB";
    static constexpr const char *INFO = "#8DCDFF";
};
```

---

## Quick Reference Card

### Widget Instantiation

```cpp
// In DashboardScreen.cpp
auto *navBar = new NavigationBar();
auto *ticker = new BreakingNewsTicker();
auto *indices = new MarketIndicesStrip();
auto *chart = new CandlestickChart();
auto *toolbar = new ChartToolbarWidget();
auto *fgIndo = new FearGreedGauge("Indonesia");
auto *commodity = new CommodityTable();
auto *breadth = new MarketBreadthWidget();
auto *aiRegime = new AIMarketRegimeWidget();
auto *news = new NewsScreen();
auto *sector = new SectorPerformanceWidget();
auto *footer = new FooterWidget();
```

### Common Patterns

**Bordered Container:**
```cpp
auto *widget = new QWidget();
widget->setStyleSheet(
    "QWidget { background-color: #1D2023; border: 1px solid #3B4A3D; border-radius: 6px; }");
auto *layout = new QVBoxLayout(widget);
layout->setContentsMargins(12, 10, 12, 12);
layout->setSpacing(6);
```

**Section Header:**
```cpp
auto *header = new QLabel("[ SECTION NAME ]");
header->setStyleSheet("color: #CEE8FF; font-size: 12px; font-weight: bold;");
layout->addWidget(header);
```

**Positive/Negative Coloring:**
```cpp
QColor color = (value >= 0) ? QColor("#75FF9E") : QColor("#FFB3AE");
```

---

*Last updated: July 2026*
*Niskala Terminal v2.0.0*
