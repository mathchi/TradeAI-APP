import pandas as pd
import numpy as np
from db_connector import *

def calculate_rsi_features(df: pd.DataFrame,
                           rsi_length: int = 14,
                           ma_length: int = 14,
                           price_col: str = "CLOSE") -> pd.DataFrame:

    def _process_symbol(group: pd.DataFrame) -> pd.DataFrame:
        g = group.sort_values("TS").reset_index(drop=True).copy()

        delta    = g[price_col].diff()
        gain     = delta.clip(lower=0)
        loss     = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/rsi_length, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/rsi_length, adjust=False).mean()
        rs       = avg_gain / avg_loss
        g["RSI"]    = 100 - (100 / (1 + rs))
        g["RSI_MA"] = g["RSI"].rolling(window=ma_length, min_periods=ma_length).mean()

        g["RSI_Status"] = (g["RSI"] > g["RSI_MA"]).astype(int)
        g["RSI_Cross"]  = g["RSI_Status"].diff().fillna(0).astype(int)

        last_cross_pos = None
        days_since = []

        for pos, row in g.iterrows():
            if row["RSI_Cross"] == 1:
                last_cross_pos = pos
            if row["RSI_Status"] == 0 or last_cross_pos is None:
                days_since.append(0)
            else:
                days_since.append(pos - last_cross_pos)

        g["RSI_Cross_Days_Ago"] = days_since
        return g

    result = df.groupby("SYMBOL", group_keys=False).apply(_process_symbol)
    return result[result["RSI_Cross_Days_Ago"].between(1, 20)]


# Veri okuma
df = fn_read_data_cloud("bronze", "bist_daily_high_filtered")

# Hesaplama
df_result = calculate_rsi_features(df)

# Kontrol
print(df_result[["SYMBOL", "TS", "CLOSE", "RSI", "RSI_MA", "RSI_Cross", "RSI_Cross_Days_Ago"]].tail(20))