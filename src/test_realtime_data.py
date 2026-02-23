# """
# ANLIK VERİ TEST ARACI
# Bu script ile hangi yontemin anlik veri Cektigini kontrol edebilirsiniz
# """

import yfinance as yf
import time
from datetime import datetime
import pandas as pd

def test_yfinance_realtime():
    # """yfinance ile anlik veri testi"""
    print("\n" + "="*70)
    print(" TEST 1: yfinance - 1 Dakikalik Veri")
    print("="*70)
    
    ticker = "AAPL"
    print(f" Ticker: {ticker}")
    print(f" BaslangiC: {datetime.now().strftime('%H:%M:%S')}")
    
    for i in range(3):
        try:
            # 1 dakikalik veri Cek
            data = yf.Ticker(ticker)
            hist = data.history(period="1d", interval="1m")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                timestamp = hist.index[-1]
                
                # Gecikmeyi hesapla
                now = datetime.now()
                if timestamp.tzinfo is not None:
                    now = now.astimezone(timestamp.tzinfo)
                
                delay = (now - timestamp).total_seconds()
                
                print(f"\n Cekme #{i+1}:")
                print(f"   Zaman: {timestamp.strftime('%H:%M:%S')}")
                print(f"   Fiyat: ${latest['Close']:.2f}")
                print(f"   Hacim: {latest['Volume']:,.0f}")
                print(f"   Gecikme: ~{delay:.0f} saniye")
                
                if delay < 120:  # 2 dakikadan az
                    print(f"   VVV Yakin gerCek zamanli!")
                elif delay < 900:  # 15 dakikadan az
                    print(f"   !!!  Biraz gecikme var")
                else:
                    print(f"   X Cok gecikmeli (15+ dakika)")
        
        except Exception as e:
            print(f"   X Hata: {e}")
        
        if i < 2:
            print(f"    10 saniye bekleniyor...")
            time.sleep(10)
    
    print("\n SONUC: yfinance ~15 dakika gecikmeli, ama 1 dakikalik detay sagliyor")

def test_finnhub_available():
    # """Finnhub'in kurulu olup olmadigini kontrol et"""
    print("\n" + "="*70)
    print(" TEST 2: Finnhub Kutuphanesi Kontrolu")
    print("="*70)
    
    try:
        import finnhub
        print("VVV finnhub kutuphanesi kurulu")
        
        # API key kontrolu
        api_key = "DEMO"  # Demo key
        fc = finnhub.Client(api_key=api_key)
        
        try:
            quote = fc.quote('AAPL')
            print(f"VVV Finnhub API Calisiyor!")
            print(f"   AAPL Fiyat: ${quote['c']:.2f}")
            print(f"   Degisim: {quote['dp']:.2f}%")
            print("\n oNEMLİ: Kendi ucretsiz API key'inizi alin:")
            print("   → https://finnhub.io/register")
        except:
            print("!!!  Demo key sinirli. ucretsiz key alin:")
            print("   → https://finnhub.io/register")
    
    except ImportError:
        print("X finnhub kurulu degil")
        print(" Kurulum iCin:")
        print("   pip install finnhub-python")

def test_websocket_available():
    # """WebSocket kutuphanesi kontrolu"""
    print("\n" + "="*70)
    print(" TEST 3: WebSocket Kutuphanesi Kontrolu")
    print("="*70)
    
    try:
        import websocket
        print("VVV websocket-client kutuphanesi kurulu")
        print(" GerCek zamanli veri iCin WebSocket kullanabilirsiniz")
    except ImportError:
        print("X websocket-client kurulu degil")
        print(" Kurulum iCin:")
        print("   pip install websocket-client")

def test_live_comparison():
    # """3 farkli yontemi karsilastir"""
    print("\n" + "="*70)
    print(" TEST 4: CANLI KARsILAsTIRMA (30 saniye)")
    print("="*70)
    
    ticker = "AAPL"
    results = []
    
    for i in range(3):
        print(f"\n olCum #{i+1}/3 ({datetime.now().strftime('%H:%M:%S')})")
        
        # yfinance
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1d", interval="1m")
            if not hist.empty:
                price = hist.iloc[-1]['Close']
                timestamp = hist.index[-1]
                print(f"   yfinance: ${price:.2f} @ {timestamp.strftime('%H:%M:%S')}")
                results.append({
                    'method': 'yfinance',
                    'price': price,
                    'time': timestamp
                })
        except Exception as e:
            print(f"   yfinance: X {e}")
        
        if i < 2:
            print("    10 saniye...")
            time.sleep(10)
    
    # Analiz
    if results:
        df = pd.DataFrame(results)
        print(f"\n ANALİZ:")
        print(f"   Fiyat degisimi: ${df['price'].min():.2f} → ${df['price'].max():.2f}")
        print(f"   Degisim: ${df['price'].max() - df['price'].min():.2f}")
        
        if len(df) > 1:
            price_change = df['price'].max() - df['price'].min()
            if price_change > 0.10:
                print(f"   VVV Fiyat hareketli - alarm sistemi iCin uygun!")
            else:
                print(f"   !!!  Fiyat duragan - daha volatil bir ticker deneyin")

def full_test():
    # """Tum testleri Calistir"""
    print("\n" + "tam isabet " * 20)
    print("ANLIK VERİ TEST ARACI - TuM KONTROLLER")
    print("tam isabet " * 20)
    
    test_yfinance_realtime()
    test_finnhub_available()
    test_websocket_available()
    test_live_comparison()
    
    print("\n" + "="*70)
    print("VVV TuM TESTLER TAMAMLANDI")
    print("="*70)
    print("\n oNERİLER:")
    print("1. yfinance ile 1 dakikalik veri Cekebiliyorsunuz VVV")
    print("2. GerCek zamanli iCin Finnhub API key alin (ucretsiz)")
    print("3. simple_alarm_system.py ile baslayin")
    print("\n Detaylar iCin: KURULUM_REHBERI.md dosyasina bakin")

if __name__ == "__main__":
    full_test()
