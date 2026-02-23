import pandas as pd
import numpy as np

# Test verisi oluştur
np.random.seed(42)

dates = pd.date_range(start="2024-01-01", periods=120)

test_df = pd.DataFrame({
    "Date": dates,
    "Close": np.cumsum(np.random.randn(120)) + 100,
    "Ticker": "TEST"
})

test_df = test_df.sort_values("Date")





# RSI + SMA + Cross hesaplayan fonksiyon

def calculate_rsi_features(prev_table: pd.DataFrame,
                           rsi_length: int = 14,
                           ma_length: int = 14,
                           price_col: str = "Close") -> pd.DataFrame:
    """
    RSI(14) + RSI SMA(14) + cross bilgileri hesaplar.
    Close kolonunun var olduğu varsayılır.
    """

    df = prev_table.copy()

    # --- 0. Zorunlu kontroller ---
    required_cols = ["Date", "Ticker", price_col]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # --- 1. Temizlik ---
    df = df.sort_values(["Ticker", "Date"])
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    # --- 2. RSI hesapla (Wilder) ---
    delta = df.groupby("Ticker")[price_col].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.groupby(df["Ticker"]).transform(
        lambda x: x.ewm(alpha=1/rsi_length, adjust=False).mean()
    )
    avg_loss = loss.groupby(df["Ticker"]).transform(
        lambda x: x.ewm(alpha=1/rsi_length, adjust=False).mean()
    )

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # --- 3. RSI based MA (SMA) ---
    df["RSI_MA"] = (
        df.groupby("Ticker")["RSI"]
        .transform(lambda x: x.rolling(window=ma_length, min_periods=ma_length).mean())
    )

    # --- 4. Cross yakala ---
    cross = (
        (df["RSI"] > df["RSI_MA"]) &
        (df["RSI"].shift(1) <= df["RSI_MA"].shift(1))
    )
    df["RSI_Cross"] = cross

    # --- 5. Son cross'tan bu yana gün ---
    df["Cross_Index"] = np.where(df["RSI_Cross"], df.index, np.nan)
    df["Cross_Index"] = df.groupby("Ticker")["Cross_Index"].ffill()
    df["RSI_Cross_Days_Ago"] = (df.index - df["Cross_Index"]).fillna(-1).astype(int)

    # --- 6. Senin ana göstergen ---
    df["RSI_Above_SMA"] = (df["RSI"] > df["RSI_MA"]).astype(int)

    df = df.drop(columns=["Cross_Index"])

    return df




# Output test
result = calculate_rsi_features(test_df)

print(result.tail(10))