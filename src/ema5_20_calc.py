import pandas as pd
import numpy as np


# Test verisi oluştur
dates = pd.date_range(start="2024-01-01", periods=50)

prices_df = pd.DataFrame({
    "Date": dates,
    "Close": np.linspace(100, 120, 50) + np.random.randn(50),
    "Ticker": "TEST"
})
# prices_df.head(50)



# EMA5, EMA20 ve cross hesaplayan fonksiyon

def calculate_ema_cross(source_df: pd.DataFrame,
                        ticker: str,
                        prev_table: pd.DataFrame,
                        price_col: str = "Close") -> pd.DataFrame:
    """
    EMA5, EMA20 ve EMA cross hesaplar.

    Parameters
    ----------
    source_df : pd.DataFrame
        Ham fiyat datasi (ticker dahil)
    ticker : str
        Hesap yapilacak sembol
    prev_table : pd.DataFrame
        Onceki fonksiyondan gelen tablo (merge edilecek ana tablo)
    price_col : str
        EMA'nin hesaplanacagi fiyat kolonu

    Returns
    -------
    pd.DataFrame
        EMA kolonlari eklenmis son tablo
    """

    # --- 1. Ticker filtrele ---
    df = source_df[source_df["Ticker"] == ticker].copy()

    # --- 2. EMA hesapla ---
    df["EMA5"] = df[price_col].ewm(span=5, adjust=False).mean()
    df["EMA20"] = df[price_col].ewm(span=20, adjust=False).mean()

    # --- 3. Cross yakala ---
    df["EMA_Cross"] = (
        (df["EMA5"] > df["EMA20"]) &
        (df["EMA5"].shift(1) <= df["EMA20"].shift(1))
    )

    df["EMA_Cross"] = df["EMA_Cross"].map({True: "is", False: "is not"})

    # --- 4. Durum flag (senin ana kuralın) ---
    df["EMA_Status"] = (df["EMA5"] > df["EMA20"]).astype(int)

    # --- 5. Ana tabloya merge ---
    result = prev_table.merge(
        df[["Date", "Ticker", "EMA5", "EMA20", "EMA_Cross", "EMA_Status"]],
        on=["Date", "Ticker"],
        how="left"
    )
    
    return result



# output test 

test_df = calculate_ema_cross(
    source_df=prices_df,
    ticker="TEST",
    prev_table=prices_df  # geçici hack
)

print(test_df.tail())