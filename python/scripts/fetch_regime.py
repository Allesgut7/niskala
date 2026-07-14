#!/usr/bin/env python3
"""Fetch AI market regime: intraday real-time + daily HMM + forecast"""

import json
import os
import sys
import warnings
import random
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

INTRADAY_SYMBOLS = ["^JKSE", "^GSPC"]

STATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "regime_trainer", "models", "intraday_state.json"
)
ACC_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "regime_trainer", "models", "regime_accuracy.json"
)


def get_market_status():
    try:
        from python.markets.market_registry import MarketRegistry
        registry = MarketRegistry()
        idx = registry.get_market("IDX")
        th = idx.trading_hours
        is_open = th.is_open()
        jakarta_tz = ZoneInfo("Asia/Jakarta")
        now = datetime.now(jakarta_tz)
        if is_open:
            return "OPEN", True
        elif now.weekday() >= 5:
            return "CLOSED_WEEKEND", False
        else:
            return "CLOSED_HOURS", False
    except Exception:
        return "UNKNOWN", False


def load_state():
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"consecutive_divergence": 0, "override_active": False, "override_regime": ""}


def save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def compute_override(intraday_bias, intraday_strength, daily_regime, state, is_market_open):
    today = str(date.today())

    if state.get("last_date") != today:
        state["consecutive_divergence"] = 0
        state["override_active"] = False
        state["last_date"] = today

    if intraday_bias is None or daily_regime is None:
        state["consecutive_divergence"] = 0
        state["override_active"] = False
        save_state(state)
        return None, state

    diverging = (
        (intraday_bias == "BULL" and intraday_strength >= 60
         and daily_regime in ("BEAR", "NEUTRAL"))
        or (intraday_bias == "BEAR" and intraday_strength >= 60
            and daily_regime in ("BULL", "STRONG BULL"))
    )

    if diverging and is_market_open:
        state["consecutive_divergence"] = state.get("consecutive_divergence", 0) + 1
    else:
        state["consecutive_divergence"] = 0

    result = None
    if state["consecutive_divergence"] >= 3 and diverging and is_market_open:
        state["override_active"] = True
        state["override_regime"] = intraday_bias
        result = {
            "active": True,
            "regime": intraday_bias,
            "consecutive_hours": state["consecutive_divergence"],
        }
    else:
        state["override_active"] = False
        state["override_regime"] = ""

    save_state(state)
    return result, state


def load_accuracy():
    try:
        if os.path.exists(ACC_PATH):
            with open(ACC_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"history": [], "stats": {"7d": 0, "30d": 0, "total": 0}}


def update_accuracy(daily_regime, close_to_close_pct, state):
    acc = load_accuracy()
    from datetime import date
    today = str(date.today())

    last_eval = state.get("last_eval_date")
    last_pred = state.get("last_prediction_regime")

    if last_eval and last_pred and last_eval != today and close_to_close_pct is not None:
        predicted_up = last_pred in ("BULL", "STRONG BULL")
        actual_up = close_to_close_pct > 0
        correct = predicted_up == actual_up

        already_logged = any(h["date"] == last_eval for h in acc["history"])
        if not already_logged:
            acc["history"].append({
                "date": last_eval,
                "predicted": last_pred,
                "return_pct": round(close_to_close_pct, 2),
                "correct": correct,
            })

    if len(acc["history"]) > 365:
        acc["history"] = acc["history"][-365:]

    total = len(acc["history"])
    correct_total = sum(1 for h in acc["history"] if h["correct"])
    acc["stats"]["total"] = round(correct_total / total * 100, 1) if total > 0 else 0

    cutoff_30 = str(date.today() - timedelta(days=30))
    cutoff_7 = str(date.today() - timedelta(days=7))

    recent_30 = [h for h in acc["history"] if h["date"] >= cutoff_30]
    recent_7 = [h for h in acc["history"] if h["date"] >= cutoff_7]

    acc["stats"]["30d"] = round(sum(1 for h in recent_30 if h["correct"]) / len(recent_30) * 100, 1) if recent_30 else 0
    acc["stats"]["7d"] = round(sum(1 for h in recent_7 if h["correct"]) / len(recent_7) * 100, 1) if recent_7 else 0

    try:
        os.makedirs(os.path.dirname(ACC_PATH), exist_ok=True)
        import tempfile
        tmp = ACC_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(acc, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ACC_PATH)
    except Exception:
        pass

    state["last_eval_date"] = state.get("last_date", today)
    state["last_prediction_regime"] = daily_regime

    return acc["stats"]


def compute_intraday(df, is_market_open=True):
    try:
        close = df["Close"].values
        volume = df["Volume"].values
        high = df["High"].values
        low = df["Low"].values
        today_open = df["Open"].iloc[0]

        intra_return = (close[-1] - today_open) / today_open

        delta = np.diff(close)
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses) if len(losses) > 0 else 0
        intra_rsi = 50.0
        if avg_loss > 0:
            rs = avg_gain / avg_loss
            intra_rsi = 100.0 - (100.0 / (1.0 + rs))

        typical_price = (high + low + close) / 3
        vwap = np.sum(typical_price * volume) / max(np.sum(volume), 1)
        vwap_dist = (close[-1] - vwap) / vwap if vwap > 0 else 0.0

        mom_3h = (close[-1] / close[-4] - 1) if len(close) >= 4 else 0.0

        rsi_3h_ago = 50.0
        if len(close) >= 17:
            delta2 = np.diff(close[:-3])
            g2 = np.where(delta2 > 0, delta2, 0)
            l2 = np.where(delta2 < 0, -delta2, 0)
            ag2 = np.mean(g2[-14:])
            al2 = np.mean(l2[-14:])
            if al2 > 0:
                rsi_3h_ago = 100.0 - (100.0 / (1.0 + ag2 / al2))
        rsi_trend = intra_rsi - rsi_3h_ago

        score = 50
        if intra_rsi > 65:
            score += 20
        elif intra_rsi > 55:
            score += 12
        elif intra_rsi > 50:
            score += 5
        elif intra_rsi < 35:
            score -= 20
        elif intra_rsi < 45:
            score -= 12
        elif intra_rsi < 48:
            score -= 5
        if vwap_dist > 0.002:
            score += 15
        elif vwap_dist > 0.001:
            score += 8
        elif vwap_dist < -0.002:
            score -= 15
        elif vwap_dist < -0.001:
            score -= 8
        if intra_return > 0.005:
            score += 15
        elif intra_return > 0.002:
            score += 8
        elif intra_return < -0.005:
            score -= 15
        elif intra_return < -0.002:
            score -= 8
        if mom_3h > 0.003:
            score += 10
        elif mom_3h > 0.001:
            score += 5
        elif mom_3h < -0.003:
            score -= 10
        elif mom_3h < -0.001:
            score -= 5
        if intra_rsi > 60 and intra_return > 0 and mom_3h > 0:
            score += 5
        elif intra_rsi < 40 and intra_return < 0 and mom_3h < 0:
            score -= 5

        bias = "BULL" if score > 60 else "BEAR" if score < 40 else "NEUTRAL"

        max_strength = 50 if not is_market_open else 100
        strength = min(abs(score - 50) * 2.2, max_strength)

        return {
            "bias": bias,
            "strength": int(strength),
            "rsi": round(intra_rsi, 1),
            "vwap_distance": round(vwap_dist * 100, 2),
            "intra_return": round(intra_return * 100, 2),
            "momentum_3h": round(mom_3h * 100, 2),
            "rsi_trend": round(rsi_trend, 1),
        }
    except Exception:
        return None


def compute_intraday_forecast(df, is_market_open=True):
    try:
        close = df["Close"].values
        intra = compute_intraday(df, is_market_open)
        if intra is None:
            return None

        rsi = intra["rsi"]
        rsi_trend = intra.get("rsi_trend", 0)
        mom = intra["momentum_3h"]
        bias = intra["bias"]

        hours = []
        h_bias = bias
        if bias == "BULL" and rsi_trend > 0:
            conf = min(55 + rsi * 0.4, 90)
        elif bias == "BEAR" and rsi_trend < 0:
            conf = min(55 + (100 - rsi) * 0.4, 90)
        elif bias == "BULL":
            conf = 55
        elif bias == "BEAR":
            conf = 55
        else:
            h_bias = "NEUTRAL"
            conf = 50

        hours.append({
            "hour": 1,
            "bias": h_bias,
            "confidence": round(min(conf, 95), 0),
        })

        return hours
    except Exception:
        return None


def main():
    market_status = "UNKNOWN"
    is_market_open = False
    intraday = None
    intra_forecast = None

    try:
        from python.ai.regime_detector import RegimeDetector, SYMBOLS
        from python.data_sources.yfinance_client import YFinanceClient
        from python.markets.market_registry import MarketRegistry
        import numpy as np
        import pandas as pd

        MODEL_PATH = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "regime_trainer", "models", "regime_hmm.pkl"
        )
        SCALER_PATH = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "regime_trainer", "models", "regime_scaler.pkl"
        )
        FEATURES_PATH = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "regime_trainer", "models", "regime_features.json"
        )

        market_status, is_market_open = get_market_status()

        client = YFinanceClient()
        detector = RegimeDetector()

        intraday_df = None
        for sym in INTRADAY_SYMBOLS:
            df = client.get_history(sym, period="5d", interval="1h")
            if df is not None and not df.empty:
                intraday_df = df[["Open", "High", "Low", "Close", "Volume"]]
                break

        intraday = compute_intraday(intraday_df, is_market_open) if intraday_df is not None and len(intraday_df) >= 14 else None
        intra_forecast = compute_intraday_forecast(intraday_df, is_market_open) if intraday_df is not None and len(intraday_df) >= 14 else None

        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            detector.load(MODEL_PATH, SCALER_PATH, FEATURES_PATH)

            df_dict = {}
            for name, symbol in SYMBOLS.items():
                df = client.get_history(symbol, period="1y")
                if not df.empty:
                    df_dict[name] = df[["Open", "High", "Low", "Close", "Volume"]].copy()
                    df_dict[name].columns = pd.MultiIndex.from_product([[name], df_dict[name].columns])

            features = detector.extract_features(df_dict)

            if len(features) > 0:
                result = detector.analyze(features)
                if result:
                    daily_regime = result["regime"]
                    daily_conf = result["confidence"]

                    divergence = False
                    if intraday:
                        divergence = (
                            (intraday["bias"] == "BULL" and daily_regime in ("BEAR", "NEUTRAL"))
                            or (intraday["bias"] == "BEAR" and daily_regime in ("BULL", "STRONG BULL"))
                        )

                    state = load_state()
                    override, state = compute_override(
                        intraday["bias"] if intraday else None,
                        intraday["strength"] if intraday else 0,
                        daily_regime, state, is_market_open
                    )

                    close_to_close = features["ihsg_return"].iloc[-1] if "ihsg_return" in features.columns else None
                    acc_stats = update_accuracy(daily_regime, close_to_close, state)

                    analysis_parts = []
                    if market_status == "OPEN" and intraday:
                        ib = intraday["bias"]
                        st = intraday["strength"]
                        rsi = intraday["rsi"]

                        if ib == "BULL":
                            if st >= 70:
                                analysis_parts.append(random.choice([
                                    "Buyer mendominasi, momentum pasar sangat kuat hari ini.",
                                    "Pasar tampak perkasa, tekanan beli solid dan berkelanjutan.",
                                    "Sentimen positif, IHSG melaju percaya diri di zona hijau.",
                                ]))
                            elif st >= 50:
                                analysis_parts.append(random.choice([
                                    "Hari ini buyer mendominasi, momentum pasar cukup positif.",
                                    "Pasar bergerak bullish, tekanan beli masih terjaga.",
                                    "Sentimen positif, pasar dalam mode risk-on hari ini.",
                                ]))
                            else:
                                analysis_parts.append(random.choice([
                                    "Pasar cenderung bullish meski pergerakannya terbatas.",
                                    "Bullish tipis, buyer belum sepenuhnya percaya diri.",
                                    "Ada tekanan beli tapi belum cukup kuat untuk breakout.",
                                ]))
                        elif ib == "BEAR":
                            if st >= 70:
                                analysis_parts.append(random.choice([
                                    "Seller menguasai pasar, tekanan jual cukup deras.",
                                    "Pasar tertekan signifikan, jumlah seller sangat dominan.",
                                    "Sentimen negatif, IHSG bergerak di zona merah dengan tekanan tinggi.",
                                ]))
                            elif st >= 50:
                                analysis_parts.append(random.choice([
                                    "Pasar sedang tertekan, seller lebih dominan.",
                                    "Tekanan jual masih berlangsung, pasar dalam mode risk-off.",
                                    "Sentimen negatif, IHSG cenderung melemah hari ini.",
                                ]))
                            else:
                                analysis_parts.append(random.choice([
                                    "Pasar cenderung bearish meski tekanan jual terbatas.",
                                    "Bearish tipis, seller belum sepenuhnya agresif.",
                                    "Ada tekanan jual tapi belum cukup kuat untuk breakdown.",
                                ]))
                        else:
                            analysis_parts.append(random.choice([
                                "Pasar bergerak sideways, buyer dan seller seimbang.",
                                "Pasar flat, belum ada arah yang jelas hari ini.",
                                "Buyer dan seller saling berimbang, pasar wait and see.",
                            ]))

                        if rsi >= 65:
                            analysis_parts.append(random.choice([
                                "RSI sudah di level tinggi, waspadai potensi koreksi teknikal.",
                                "RSI overbought — bisa jadi sinyal jenuh beli.",
                                "Momentum mulai ekstrem, koreksi mungkin terjadi.",
                            ]))
                        elif rsi <= 35:
                            analysis_parts.append(random.choice([
                                "RSI di level rendah, potensi rebound teknikal cukup besar.",
                                "RSI oversold — bisa jadi sinyal jenuh jual.",
                                "Momentum sudah lemah, peluang reversal terbuka.",
                            ]))
                        elif rsi >= 55:
                            analysis_parts.append(random.choice([
                                "RSI masih di zona aman, momentum positif terjaga.",
                                "Momentum cukup sehat, pasar masih nyaman untuk hold.",
                            ]))
                        elif rsi <= 45:
                            analysis_parts.append(random.choice([
                                "RSI mulai melemah, momentum negatif perlahan terbentuk.",
                                "Momentum mulai memudar, waspadai pelemahan lanjutan.",
                            ]))

                        if override:
                            analysis_parts.append(random.choice([
                                f"Pasar sudah berbalik arah menjadi {override['regime'].lower()}. Tren baru mulai terbentuk.",
                                f"Terjadi pembalikan tren — dari bearish kini bergerak {override['regime'].lower()}.",
                            ]))
                        elif divergence:
                            opposite = "bearish" if ib == "BULL" else "bullish"
                            analysis_parts.append(random.choice([
                                f"Menarik: intraday {ib.lower()} tapi HMM masih {opposite}. Bisa jadi early signal reversal.",
                                f"Ada perbedaan arah antara pergerakan hari ini dan tren harian. Potensi pembalikan.",
                            ]))

                    elif not is_market_open and intraday:
                        ib = intraday["bias"]
                        st = intraday["strength"]

                        if market_status == "CLOSED_WEEKEND":
                            analysis_parts.append(
                                "Market tutup (weekend). Data dari sesi terakhir."
                            )
                        elif market_status == "CLOSED_HOURS":
                            analysis_parts.append(
                                "Market sedang tutup (09:00-16:00 WIB). Data dari sesi terakhir."
                            )
                        else:
                            analysis_parts.append(
                                "Market sedang tutup. Data dari sesi terakhir."
                            )

                        if ib == "BULL":
                            analysis_parts.append(
                                f"Intraday sesi terakhir menunjukkan bias bullish (strength {st}%)."
                            )
                        elif ib == "BEAR":
                            analysis_parts.append(
                                f"Intraday sesi terakhir menunjukkan bias bearish (strength {st}%)."
                            )
                        else:
                            analysis_parts.append(
                                "Intraday sesi terakhir sideways."
                            )
                    else:
                        analysis_parts.append(random.choice([
                            f"Regime harian: {daily_regime}.",
                            f"HMM mendeteksi {daily_regime.lower()} untuk hari ini.",
                        ]))

                    analysis_parts.append(random.choice([
                        f"Besok diperkirakan masih {result['next_regime'].lower()} ({result['next_confidence']}%).",
                        f"Untuk besok, probabilitas {result['next_regime'].lower()} sebesar {result['next_confidence']}%.",
                        f"Dalam 1-2 hari ke depan masih berpotensi {result['next_regime'].lower()}.",
                    ]))
                    accuracy = {
                        "7d": acc_stats.get("7d", 0),
                        "30d": acc_stats.get("30d", 0),
                        "total": acc_stats.get("total", 0),
                    }

                    display_regime = daily_regime
                    display_conf = daily_conf
                    if override:
                        display_regime = override["regime"] + " (override)"
                        display_conf = min(daily_conf, 60)

                    output = {
                        "intraday": intraday,
                        "intraday_forecast": intra_forecast,
                        "regime": daily_regime,
                        "confidence": daily_conf,
                        "override": override,
                        "display_regime": display_regime,
                        "display_confidence": display_conf,
                        "divergence": divergence,
                        "market_status": market_status,
                        "analysis": " ".join(analysis_parts),
                        "accuracy": accuracy,
                        "forecast": {
                            "next_regime": result["next_regime"],
                            "next_confidence": result["next_confidence"],
                            "transition_prob": result["transition_prob"],
                            "steps": result["forecast_steps"],
                        },
                    }
                    print(json.dumps(output))
                    sys.exit(0)

    except Exception as e:
        error_msg = str(e)

    try:
        client = YFinanceClient()
        data = client.get_index("^JKSE")
        change_pct = data.get("changePct", 0)
        regime = "BULL" if change_pct > 0 else "BEAR"
        confidence = min(90, max(50, 70 + abs(change_pct) * 2))
        output = {
            "regime": regime,
            "confidence": int(confidence),
            "market_status": market_status,
            "analysis": f"IHSG change: {change_pct:.2f}%. Market regime: {regime}. (Fallback)",
        }
        if intraday:
            output["intraday"] = intraday
        if intra_forecast:
            output["intraday_forecast"] = intra_forecast
        print(json.dumps(output))
    except Exception:
        print(json.dumps({
            "regime": "NEUTRAL",
            "confidence": 50,
            "market_status": "UNKNOWN",
            "analysis": "Insufficient data",
        }))


if __name__ == "__main__":
    main()
