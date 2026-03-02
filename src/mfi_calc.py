import pandas as pd
import numpy as np

def calculate_mfi(df: pd.DataFrame,
                  close_col: str = "Close",
                  volume_col: str = "Volume",
                  high_col: str = None,
                  low_col: str = None,
                  length: int = 14) -> pd.DataFrame:
    """
    Money Flow Index (MFI) hesaplar ve mevcut DataFrame'e yeni kolonlar ekler.
    
    Eger High ve Low kolonlari yoksa, Close'dan turetir:
    - High = Close * 1.01 (Close'un %1 ustunde)
    - Low = Close * 0.99 (Close'un %1 altinda)
    
    Parameters
    ----------
    df : pd.DataFrame
        Fiyat ve hacim verisi iceren DataFrame
    close_col : str
        Kapanis fiyat kolonu (zorunlu)
    volume_col : str
        Hacim kolonu (zorunlu)
    high_col : str, optional
        Yuksek fiyat kolonu (yoksa Close'dan turetilir)
    low_col : str, optional
        Dusuk fiyat kolonu (yoksa Close'dan turetilir)
    length : int
        MFI hesaplama periyodu (default: 14)
    
    Returns
    -------
    pd.DataFrame
        MFI kolonlari eklenmis DataFrame
    """
    
    # Kopyasini al (orijinali degistirmemek icin)
    result = df.copy()
    
    # --- High ve Low yoksa Close'dan turet ---
    if high_col is None or high_col not in result.columns:
        result["High"] = result[close_col] * 1.01  # %1 yukarida
        high_col = "High"
    
    if low_col is None or low_col not in result.columns:
        result["Low"] = result[close_col] * 0.99  # %1 asagida
        low_col = "Low"
    
    # --- 1. Typical Price hesapla ---
    result["Typical_Price"] = (result[high_col] + result[low_col] + result[close_col]) / 3
    
    # --- 2. Raw Money Flow hesapla ---
    result["Raw_Money_Flow"] = result["Typical_Price"] * result[volume_col]
    
    # --- 3. Positive ve Negative Money Flow ayir ---
    result["Price_Change"] = result["Typical_Price"].diff()
    result["Positive_MF"] = np.where(result["Price_Change"] > 0, result["Raw_Money_Flow"], 0)
    result["Negative_MF"] = np.where(result["Price_Change"] < 0, result["Raw_Money_Flow"], 0)
    
    # --- 4. Rolling sum (14 gun) ---
    result["Positive_MF_Sum"] = result["Positive_MF"].rolling(window=length, min_periods=1).sum()
    result["Negative_MF_Sum"] = result["Negative_MF"].rolling(window=length, min_periods=1).sum()
    
    # --- 5. Money Flow Ratio ve MFI ---
    result["MF_Ratio"] = result["Positive_MF_Sum"] / (result["Negative_MF_Sum"] + 1e-10)  # Sifira bolme onleme
    result["MFI"] = 100 - (100 / (1 + result["MF_Ratio"]))
    
    # --- 6. Kullanicinin istedigi output'lar ---
    result["MF_Today"] = result["Raw_Money_Flow"]
    result["MF_Yesterday"] = result["Raw_Money_Flow"].shift(1)
    
    # Son 14 gunun ortalamasi (bugun ve dun haric, geriye kalan 12 gun)
    result["MF_12Day_Avg"] = (
        result["Raw_Money_Flow"].rolling(window=length, min_periods=1).sum() - 
        result["MF_Today"] - 
        result["MF_Yesterday"]
    ) / 12
    
    # --- 7. Para akisi yonu (yukarı mı?) ---
    result["MF_Direction"] = np.where(
        result["MF_Today"] > result["MF_Yesterday"],
        "Upward",
        "Downward"
    )
    
    # Ara hesaplama kolonlarini kaldir
    result = result.drop(columns=[
        "Typical_Price", "Raw_Money_Flow", "Price_Change",
        "Positive_MF", "Negative_MF", "Positive_MF_Sum", 
        "Negative_MF_Sum", "MF_Ratio"
    ])
    
    return result