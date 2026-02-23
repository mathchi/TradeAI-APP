# live_stream_ohlc.py

import yfrlt
import pandas as pd
from datetime import datetime, timedelta
import threading
import time

# =========================
# USER INPUT
# =========================
TICKERS = ["ULKER.IS"]  # <- BURAYI DEĞİŞTİR
RUN_MINUTES = 60    # 1 saat

# =========================
# GLOBAL STORAGE
# =========================
tick_buffer = {}
ohlc_rows = []
lock = threading.Lock()
start_time = datetime.utcnow()

# =========================
# HELPER — minute bucket
# =========================
def get_minute_bucket(ts):
    return ts.replace(second=0, microsecond=0)

# =========================
# PRICE UPDATE HANDLER
# =========================
def on_price_update(data):
    global tick_buffer, ohlc_rows

    ts = datetime.utcnow()
    minute_bucket = get_minute_bucket(ts)

    with lock:
        symbol = data.symbol
        price = float(data.price)

        if symbol not in tick_buffer:
            tick_buffer[symbol] = {}

        if minute_bucket not in tick_buffer[symbol]:
            tick_buffer[symbol][minute_bucket] = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume_ticks": 1,
                "timestamp": minute_bucket,
                "symbol": symbol,
            }
        else:
            bar = tick_buffer[symbol][minute_bucket]
            bar["high"] = max(bar["high"], price)
            bar["low"] = min(bar["low"], price)
            bar["close"] = price
            bar["volume_ticks"] += 1

# =========================
# FLUSHER — dataframe log
# =========================
def flush_loop():
    global tick_buffer, ohlc_rows

    while True:
        time.sleep(60)

        with lock:
            for symbol in list(tick_buffer.keys()):
                finished_minutes = sorted(tick_buffer[symbol].keys())[:-1]

                for minute in finished_minutes:
                    ohlc_rows.append(tick_buffer[symbol][minute])
                    del tick_buffer[symbol][minute]

        # dataframe oluştur
        if ohlc_rows:
            df = pd.DataFrame(ohlc_rows)
            df = df.sort_values("timestamp")

            print("\n=== SON BARLAR ===")
            print(df.tail())

            df.to_csv("live_ohlc_log.csv", index=False)

        # stop condition
        if datetime.utcnow() - start_time > timedelta(minutes=RUN_MINUTES):
            print("\n⏹ Süre doldu — program kapanıyor.")
            break

# =========================
# MAIN
# =========================
def main():
    client = yfrlt.Client()

    flush_thread = threading.Thread(target=flush_loop, daemon=True)
    flush_thread.start()

    print("🚀 Stream başlatıldı...")
    print("Tickers:", TICKERS)

    client.subscribe(TICKERS, on_price_update)
    client.start()

if __name__ == "__main__":
    main()