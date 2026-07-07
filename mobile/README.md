![NISKALA](../../Logo-fix.png)

# Niskala Mobile App

React Native companion app for Niskala trading terminal.

**Version:** 1.0.0  
**Platform:** iOS & Android (via Expo)  
**Framework:** React Native 0.72+  

---

## Features

### Screens

| Screen | Description |
|--------|-------------|
| **Watchlist** | Track stocks with real-time prices |
| **Price Alerts** | Set price alerts for stocks |
| **News Feed** | News with AI sentiment analysis |
| **Fear & Greed** | Market sentiment index (3 regions) |
| **Settings** | App configuration |

### Screenshots

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Watchlist     │  │   Price Alerts  │  │   News Feed     │
│                 │  │                 │  │                 │
│  BBCA  9,500    │  │  BBCA > 10,000  │  │  CNBC ▲ Bank    │
│  BBRI  4,800    │  │  BBRI < 4,500   │  │  Kontan ▲ Tech  │
│  BMRI  6,200    │  │                 │  │  IDX ▼ Mining   │
│  TLKM  3,800    │  │  [+ Add Alert]  │  │                 │
│                 │  │                 │  │  Sentiment: 78  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | React Native (Expo) |
| Navigation | React Navigation |
| State | Redux Toolkit |
| HTTP | Axios |
| Storage | AsyncStorage |

---

## Installation

```bash
cd mobile

# Install dependencies
npm install

# Start development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios
```

---

## Project Structure

```
mobile/
├── App.tsx                    # Main app entry
├── package.json               # Dependencies
├── src/
│   ├── screens/              # 5 screens
│   │   ├── WatchlistScreen.tsx
│   │   ├── PriceAlertsScreen.tsx
│   │   ├── NewsFeedScreen.tsx
│   │   ├── FearGreedScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/           # Reusable components
│   │   ├── StockCard.tsx
│   │   └── FearGreedGauge.tsx
│   ├── services/             # API client
│   │   └── api.ts
│   ├── store/                # Redux state
│   │   ├── index.ts
│   │   └── watchlistSlice.ts
│   └── types/                # TypeScript types
│       └── index.ts
├── android/                  # Android native code
└── ios/                      # iOS native code
```

---

## API Integration

The app connects to the Niskala API server:

```typescript
// src/services/api.ts
const API_BASE_URL = 'http://YOUR_VPS_IP';

// Endpoints
GET  /api/market/quote/{symbol}
GET  /api/market/quotes
GET  /api/trading/portfolio
POST /api/trading/order
GET  /api/trading/positions
GET  /api/trading/trades
GET  /api/auth/login
```

---

## Configuration

### Environment Variables

```bash
# API URL
API_BASE_URL=http://YOUR_VPS_IP

# Optional
ENABLE_NOTIFICATIONS=true
DEFAULT_MARKET=IDX
```

### Market Selection

The app supports multiple markets. Default is IDX (Indonesia).

To change market:
1. Go to Settings
2. Select Market
3. Choose: IDX, SGX, Bursa, SET, PSE, or HOSE

### Language Selection

The app supports 7 languages:
- English
- Bahasa Indonesia
- Bahasa Melayu
- ภาษาไทย (Thai)
- Tiếng Việt (Vietnamese)
- Filipino
- 简体中文 (Chinese)

---

## Building for Production

### Android APK

```bash
# Build APK
eas build -p android --profile preview

# Or build locally
cd android
./gradlew assembleRelease
```

### iOS

```bash
# Build for iOS
eas build -p ios
```

### Expo Build (Recommended)

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build
eas build --platform all
```

---

## Push Notifications

The app uses Firebase Cloud Messaging (FCM) for push notifications:

- Price alerts
- Trade notifications
- News alerts
- Daily summary

### Setup

1. Create Firebase project
2. Add `google-services.json` (Android)
3. Add `GoogleService-Info.plist` (iOS)
4. Configure in Expo

---

## Testing

```bash
# Run tests
npm test

# Run on device
npm run android --device
npm run ios --device
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API connection failed | Check VPS IP and port |
| Build fails | Run `npm install` again |
| Push notifications not working | Check Firebase config |
| App crashes on start | Clear AsyncStorage |

---

**END OF MOBILE README**
