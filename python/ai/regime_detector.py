"""HMM-based Market Regime Detector with forecasting"""

import json
import os
import warnings
import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


SYMBOLS = {
    "ihsg": "^JKSE",
    "sp500": "^GSPC",
    "nikkei": "^N225",
    "hangseng": "^HSI",
    "kospi": "^KS11",
    "sti": "^STI",
    "usdidr": "USDIDR=X",
}

REGIME_LABELS = {
    0: "STRONG BULL",
    1: "BULL",
    2: "NEUTRAL",
    3: "BEAR",
    4: "CRASH",
}


class RegimeDetector:
    def __init__(self, model_path=None, scaler_path=None, features_path=None):
        self.model = None
        self.scaler = None
        self.state_labels = {}
        self.feature_names = []
        self._fitted = False

        if model_path and scaler_path:
            self.load(model_path, scaler_path, features_path)

    def load(self, model_path, scaler_path, features_path=None):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self._fitted = True

        if features_path and os.path.exists(features_path):
            with open(features_path) as f:
                meta = json.load(f)
            self.state_labels = {int(k): v for k, v in meta.get("state_labels", {}).items()}
            self.feature_names = meta.get("feature_names", meta.get("train_columns", []))

        if not self.state_labels:
            self._label_states()

    def _label_states(self):
        means = self.model.means_
        return_col = None
        for i, name in enumerate(self.feature_names):
            if name == "ihsg_return":
                return_col = i
                break
        if return_col is None:
            for i, name in enumerate(self.feature_names):
                if "return" in name:
                    return_col = i
                    break
        if return_col is None:
            return_col = 0
        state_returns = means[:, return_col]
        sorted_idx = np.argsort(state_returns)[::-1]
        for new_order, orig_state in enumerate(sorted_idx):
            label = REGIME_LABELS.get(new_order, f"STATE_{new_order}")
            self.state_labels[orig_state] = label

    def extract_features(self, df_dict):
        name_order = list(SYMBOLS.keys())
        features_list = []
        for name in name_order:
            if name not in df_dict:
                continue
            df = df_dict[name].copy()
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            feats = pd.DataFrame(index=df.index)

            ret = df["Close"].pct_change()
            feats["return"] = ret
            feats["vol_5d"] = ret.rolling(5).std()

            high_low = df["High"] - df["Low"]
            feats["hl_range"] = high_low / df["Close"].replace(0, np.nan)

            if name == "ihsg":
                delta = df["Close"].diff()
                gain = delta.where(delta > 0, 0.0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
                rs = gain / loss.replace(0, np.nan)
                feats["rsi"] = 100 - (100 / (1 + rs))

                ema12 = df["Close"].ewm(span=12).mean()
                ema26 = df["Close"].ewm(span=26).mean()
                feats["macd_hist"] = (ema12 - ema26) - (ema12 - ema26).ewm(span=9).mean()

                sma20 = df["Close"].rolling(20).mean()
                feats["sma20_dist"] = (df["Close"] - sma20) / sma20.replace(0, np.nan)

            feats.columns = [f"{name}_{c}" for c in feats.columns]
            features_list.append(feats)

        if not features_list:
            return pd.DataFrame()
        combined = pd.concat(features_list, axis=1).dropna()
        return combined

    def _align_features(self, features_df):
        if not self.feature_names:
            return features_df.values
        out = pd.DataFrame(index=features_df.index)
        for col in self.feature_names:
            out[col] = features_df[col] if col in features_df.columns else 0.0
        return out.values

    def predict_current(self, features_df):
        if not self._fitted:
            return None, 0.0, ""

        X = self._align_features(features_df)
        X_scaled = self.scaler.transform(X)

        states = self.model.predict(X_scaled)
        current_state = states[-1]

        state_probs = self.model.predict_proba(X_scaled)
        current_probs = state_probs[-1]
        confidence = float(current_probs[current_state] * 100)

        regime_label = self.state_labels.get(current_state, f"STATE_{current_state}")

        return regime_label, confidence, current_state

    def predict_next(self, current_state):
        if not self._fitted:
            return None, 0.0, 0.0

        trans = self.model.transmat_
        next_probs = trans[current_state]
        next_state = int(np.argmax(next_probs))
        transition_prob = float(next_probs[next_state])

        next_label = self.state_labels.get(next_state, f"STATE_{next_state}")

        return next_label, transition_prob * 100, next_state

    def predict_n_steps(self, current_state, steps=5):
        if not self._fitted:
            return []

        trans = self.model.transmat_
        current_prob_vec = np.zeros(self.model.n_components)
        current_prob_vec[current_state] = 1.0

        result = []
        for step in range(1, steps + 1):
            step_probs = current_prob_vec @ np.linalg.matrix_power(trans, step)
            most_likely = int(np.argmax(step_probs))
            prob = float(step_probs[most_likely])
            label = self.state_labels.get(most_likely, f"STATE_{most_likely}")
            result.append({
                "step": step,
                "regime": label,
                "probability": round(prob * 100, 1),
            })

        return result

    def get_transition_matrix(self):
        if not self._fitted:
            return {}

        trans = self.model.transmat_
        matrix = {}
        for i in range(trans.shape[0]):
            src = self.state_labels.get(i, f"STATE_{i}")
            matrix[src] = {}
            for j in range(trans.shape[1]):
                dst = self.state_labels.get(j, f"STATE_{j}")
                matrix[src][dst] = round(float(trans[i, j]), 3)
        return matrix

    def analyze(self, features_df):
        regime_label, confidence, current_state = self.predict_current(features_df)
        if regime_label is None:
            return None

        next_label, next_prob, next_state = self.predict_next(current_state)
        forecast = self.predict_n_steps(current_state, steps=5)
        trans_matrix = self.get_transition_matrix()

        return {
            "regime": regime_label,
            "confidence": round(confidence),
            "next_regime": next_label,
            "next_confidence": round(next_prob),
            "transition_prob": round(next_prob / 100, 3),
            "forecast_steps": forecast,
            "transition_matrix": trans_matrix,
        }
