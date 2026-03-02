import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# FONKSIYON TANIMI
# ============================================================================

def calculate_ema_cross(df: pd.DataFrame,
                        price_col: str = "Close") -> pd.DataFrame:
    """
    EMA5, EMA20 ve EMA cross hesaplar.

    Parameters
    ----------
    df : pd.DataFrame
        Fiyat datasi
    price_col : str
        EMA'nin hesaplanacagi fiyat kolonu

    Returns
    -------
    pd.DataFrame
        EMA kolonlari eklenmis DataFrame
    """

    # Kopyasini al (orijinali degistirmemek icin)
    result = df.copy()

    # --- 1. EMA hesapla ---
    result["EMA5"] = result[price_col].ewm(span=5, adjust=False).mean()
    result["EMA20"] = result[price_col].ewm(span=20, adjust=False).mean()

    # --- 2. Cross yakala ---
    result["EMA_Cross"] = (
        (result["EMA5"] > result["EMA20"]) &
        (result["EMA5"].shift(1) <= result["EMA20"].shift(1))
    )

    result["EMA_Cross"] = result["EMA_Cross"].map({True: "is", False: "is not"})

    # --- 3. Durum flag ---
    result["EMA_Status"] = (result["EMA5"] > result["EMA20"]).astype(int)
    
    return result


# ============================================================================
# FONKSIYONU CALISTIR VE DF'E YAZ
# ============================================================================

# Test verisi olustur
Dates = pd.date_range(start="2024-01-01", periods=50)

prices_df = pd.DataFrame({
    "Date": Dates,
    "Close": np.linspace(100, 120, 50) + np.random.randn(50),
    "Ticker": "TEST"
})

# EMA hesapla ve df'e yaz
df = calculate_ema_cross(prices_df)

print("✅ EMA hesaplandi ve df'e yazildi")
print(f"Toplam satir: {len(df)}")
print(f"Yeni kolonlar: EMA5, EMA20, EMA_Cross, EMA_Status")
print("\nSon 10 satir:")
df[["Date", "Close", "EMA5", "EMA20", "EMA_Cross", "EMA_Status"]].tail(10)





### Visualization: EMA Chart ###

plt.plot(df['Date'], df['Close'], 
         label='Close Price', linewidth=1.5, color='#1f77b4')

plt.plot(df['Date'], df['EMA5'], 
         label='EMA5', linewidth=2.5, color='#ff7f0e')

plt.plot(df['Date'], df['EMA20'], 
         label='EMA20', linewidth=2.5, color='#2ca02c')

plt.title('EMA5 ve EMA20 Karsilastirmasi - TEST', 
          fontsize=14, fontweight='bold')
plt.xlabel('Tarih', fontsize=11)
plt.ylabel('Değer', fontsize=11)
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("✅ Grafik olusturuldu!")
import matplotlib.pyplot as plt

# EMA görselleştirmesi
plt.figure(figsize=(14, 6))

plt.plot(df['Date'], df['value'], 
         label='Gerçek Değer', marker='o', linewidth=1.5, 
         markersize=3, alpha=0.7, color='#1f77b4')

plt.plot(df['Date'], df['EMA5'], 
         label='EMA5', linewidth=2.5, color='#ff7f0e')

plt.plot(df['Date'], df['EMA20'], 
         label='EMA20', linewidth=2.5, color='#2ca02c')

plt.title('EMA5 ve EMA20 Karsilastirmasi - TICKER', 
          fontsize=14, fontweight='bold')
plt.xlabel('Tarih', fontsize=11)
plt.ylabel('Değer', fontsize=11)
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("✅ Grafik olusturuldu!")