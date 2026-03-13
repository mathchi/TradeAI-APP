import pandas as pd
import numpy as np
from db_connector import *
# pd.options.display.max_rows = 300



def calculate_ema_cross(df: pd.DataFrame, price_col: str = "CLOSE") -> pd.DataFrame:

    """
    Değer   Anlam
    1        EMA5, EMA20'yi yukari kesti → Al sinyali
    -1       EMA5, EMA20'yi asagi kesti → Sat sinyali
    0        Kesisim yok
    DAYS_SINCE_CROSS: Son kesisimden bu yana gecen gun sayisi (0 = bugun kesisim oldu)
     - 20 gun icinde kesisim olanlari filtrele (0-20 gun arasi)
     - 20 gunu gecenleri cikart (DAYS_SINCE_CROSS > 20)
     - Kesisim olmayanlari cikart (EMA_Cross == 0)
     - EMA_Cross == 1 olunca DAYS_SINCE_CROSS 0 olur, sonraki satirlarda 1, 2, 3... olarak artar
     - EMA_Cross == -1 olunca DAYS_SINCE_CROSS yine 0 olur, sonraki satirlarda 1, 2, 3... olarak artmaz (EMA20 > EMA5 (downtrend) ve DAYS_SINCE_CROSS 0 sabit kalir.)
    """

    def _process_symbol(group: pd.DataFrame) -> pd.DataFrame:
        g = group.sort_values("TIMESTAMP").reset_index(drop=True).copy()

        g["EMA5"]       = g[price_col].ewm(span=5,  adjust=False).mean()
        g["EMA20"]      = g[price_col].ewm(span=20, adjust=False).mean()
        g["EMA_Status"] = (g["EMA5"] > g["EMA20"]).astype(int)
        g["EMA_Cross"]  = g["EMA_Status"].diff().fillna(0).astype(int)

        last_cross_pos = None
        days_since = []

        for pos, row in g.iterrows():
            if row["EMA_Cross"] == 1:
                last_cross_pos = pos
            if row["EMA_Status"] == 0 or last_cross_pos is None:
                days_since.append(0)
            else:
                days_since.append(pos - last_cross_pos)

        g["DAYS_SINCE_CROSS"] = days_since
        return g

    result = df.groupby("SYMBOL", group_keys=False).apply(_process_symbol)
    return result[result["DAYS_SINCE_CROSS"].between(0, 20)]



# Veri okuma
df = fn_read_data_cloud("silver", "bist_focus_2e_indicators_converted_daily")

symbol = "FZLGY"
target_date = "2026-02-04"

# Filtreleme
df_test = df[df["SYMBOL"] == symbol].copy()  # tüm geçmiş

df_result = calculate_ema_cross(df_test, price_col="CLOSE")

# sonra istediğin tarihe filtrele
print(
    df_result[df_result["TIMESTAMP"] == target_date][
        ["SYMBOL", "TIMESTAMP", "CLOSE", "EMA5", "EMA20", "EMA_Cross", "DAYS_SINCE_CROSS"]
    ]
)
# print(df_result["EMA_Cross"].value_counts())