"""
YFRLT CANLI VERİ LOGGER
1 saatlik canli veri akisi - DataFrame ile loglama
"""

import yfrlt
import pandas as pd
from datetime import datetime, timedelta
import time
import os

class LiveDataLogger:
    def __init__(self, tickers, duration_minutes=60):
        """
        Args:
            tickers: List of ticker symbols (örn: ['ULKER.IS', 'THYAO.IS'])
            duration_minutes: Kaç dakika veri toplanacak (varsayilan: 60)
        """
        self.tickers = tickers
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        # Her ticker için ayrı veri listesi
        self.data_buffer = {ticker: [] for ticker in tickers}
        
        # İstatistikler
        self.update_count = {ticker: 0 for ticker in tickers}
        self.price_history = {ticker: [] for ticker in tickers}
        
        # Client
        self.client = yfrlt.Client()
        
    def on_price_update(self, data):
        """Her fiyat guncellemesinde cagrilan fonksiyon"""
        ticker = data.symbol
        current_time = datetime.now()
        
        # Süre kontrolü
        if current_time >= self.end_time:
            print(f"\n⏰ {self.duration_minutes} dakika tamamlandi!")
            self.stop_and_save()
            return
        
        # Fiyat geçmişine ekle (min/max için)
        self.price_history[ticker].append(data.price)
        
        # Veri kaydı oluştur
        record = {
            'TICKER': ticker,
            'TIMESTAMP': current_time,
            'PRICE': data.price,
            'OPEN': self.price_history[ticker][0] if self.price_history[ticker] else data.price,  # İlk fiyat = açılış
            'CLOSE': data.price,  # Son fiyat = kapanış
            'MIN': min(self.price_history[ticker]) if self.price_history[ticker] else data.price,
            'MAX': max(self.price_history[ticker]) if self.price_history[ticker] else data.price,
            'UPDATE_COUNT': self.update_count[ticker] + 1,
            'ELAPSED_SECONDS': (current_time - self.start_time).total_seconds()
        }
        
        # Buffer'a ekle
        self.data_buffer[ticker].append(record)
        self.update_count[ticker] += 1
        
        # Konsola yazdır (her 10 güncellemede bir)
        if self.update_count[ticker] % 10 == 0:
            remaining = (self.end_time - current_time).total_seconds() / 60
            print(f"⏰ {current_time.strftime('%H:%M:%S')} | {ticker}: ₺{data.price:.2f} | "
                  f"Min: ₺{record['MIN']:.2f} | Max: ₺{record['MAX']:.2f} | "
                  f"Kalan: {remaining:.1f} dk | Toplam: {self.update_count[ticker]} güncelleme")
    
    def get_dataframe(self, ticker=None):
        """Buffer'i DataFrame'e çevir"""
        if ticker:
            # Belirli bir ticker için
            if ticker in self.data_buffer and self.data_buffer[ticker]:
                return pd.DataFrame(self.data_buffer[ticker])
            return pd.DataFrame()
        else:
            # Tüm ticker'lar için
            all_data = []
            for ticker_name, records in self.data_buffer.items():
                all_data.extend(records)
            return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    
    def save_to_csv(self, filename=None):
        """DataFrame'i CSV olarak kaydet"""
        df = self.get_dataframe()
        
        if df.empty:
            print("❌ Kaydedilecek veri yok!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"live_data_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        print(f"✅ Veri kaydedildi: {filename} ({len(df)} satir)")
        return filename
    
    def show_summary(self):
        """Özet istatistikler göster"""
        print("\n" + "="*80)
        print("📊 CANLI VERİ TOPLAMA OZETI")
        print("="*80)
        
        for ticker in self.tickers:
            if ticker in self.data_buffer and self.data_buffer[ticker]:
                df = self.get_dataframe(ticker)
                
                print(f"\n🔹 {ticker}")
                print(f"   Toplam Güncelleme: {len(df)}")
                print(f"   İlk Güncelleme: {df.iloc[0]['TIMESTAMP'].strftime('%H:%M:%S')}")
                print(f"   Son Güncelleme: {df.iloc[-1]['TIMESTAMP'].strftime('%H:%M:%S')}")
                print(f"   Acilis Fiyati: ₺{df.iloc[0]['OPEN']:.2f}")
                print(f"   Kapanis Fiyati: ₺{df.iloc[-1]['CLOSE']:.2f}")
                print(f"   En Dusuk: ₺{df['MIN'].min():.2f}")
                print(f"   En Yuksek: ₺{df['MAX'].max():.2f}")
                
                # Değişim hesapla
                change = df.iloc[-1]['CLOSE'] - df.iloc[0]['OPEN']
                change_pct = (change / df.iloc[0]['OPEN']) * 100
                print(f"   Degisim: ₺{change:.2f} ({change_pct:+.2f}%)")
        
        print("\n" + "="*80)
    
    def stop_and_save(self):
        """Veri toplamayi durdur ve kaydet"""
        print("\n🛑 Veri toplama durduruluyor...")
        
        # Özet göster
        self.show_summary()
        
        # CSV'ye kaydet
        filename = self.save_to_csv()
        
        # Client'ı durdur
        self.client.stop()
        
        print(f"\n✅ İşlem tamamlandi!")
        print(f"📁 Dosya: {filename}")
        
        # DataFrame'i döndür
        return self.get_dataframe()
    
    def start(self):
        """Canli veri akisini baslat"""
        print("="*80)
        print("🚀 CANLI VERİ AKISI BASLATILIYOR")
        print("="*80)
        print(f"📊 Ticker'lar: {', '.join(self.tickers)}")
        print(f"⏱️  Süre: {self.duration_minutes} dakika")
        print(f"🕐 Başlangic: {self.start_time.strftime('%H:%M:%S')}")
        print(f"🕐 Bitiş: {self.end_time.strftime('%H:%M:%S')}")
        print("="*80)
        print("\n💡 Durdurmak icin Ctrl+C tuslayin\n")
        
        try:
            # Subscribe ve başlat
            self.client.subscribe(self.tickers, self.on_price_update)
            self.client.start()
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Kullanici tarafindan durduruldu")
            self.stop_and_save()

# ============================================
# KULLANIM ÖRNEĞİ
# ============================================
def main():
    """Ana çalistirma fonksiyonu"""
    print("\n" + "🎯 " * 20)
    print("YFRLT CANLI VERİ LOGGER")
    print("🎯 " * 20)
    
    # Kullanıcıdan ticker al
    print("\n📊 Hangi ticker'lari izlemek istiyorsunuz?")
    print("Örnekler: ULKER.IS, THYAO.IS, GARAN.IS, ISCTR.IS")
    
    ticker_input = input("\nTicker'lari virgülle ayirarak girin: ").strip()
    
    if not ticker_input:
        print("❌ Ticker girilmedi. Varsayilan kullaniliyor: ULKER.IS")
        tickers = ['ULKER.IS']
    else:
        tickers = [t.strip().upper() for t in ticker_input.split(',')]
    
    # Süre seç
    print("\n⏱️  Kaç dakika veri toplanacak?")
    duration_input = input("Süre (dakika) [varsayilan: 60]: ").strip()
    
    if duration_input:
        try:
            duration = int(duration_input)
        except:
            print("❌ Geçersiz süre. Varsayilan 60 dakika kullaniliyor.")
            duration = 60
    else:
        duration = 60
    
    # Logger'ı başlat
    logger = LiveDataLogger(tickers=tickers, duration_minutes=duration)
    logger.start()

# ============================================
# HIZLI TEST (5 Dakika)
# ============================================
def quick_test():
    """5 dakikalik hizli test"""
    print("\n🧪 HIZLI TEST MODU (5 dakika)")
    print("="*80)
    
    logger = LiveDataLogger(
        tickers=['ULKER.IS'],
        duration_minutes=5
    )
    
    logger.start()

# ============================================
# VS CODE'DA ÇALIŞTIRMA
# ============================================
if __name__ == "__main__":
    import sys
    
    # Komut satırı argümanları
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # python live_stream_logger.py test
        quick_test()
    
    elif len(sys.argv) > 1:
        # python live_stream_logger.py ULKER.IS THYAO.IS --duration 30
        tickers = []
        duration = 60
        
        for arg in sys.argv[1:]:
            if arg.startswith('--duration'):
                continue
            elif sys.argv[sys.argv.index(arg)-1] == '--duration':
                duration = int(arg)
            else:
                tickers.append(arg.upper())
        
        if '--duration' in sys.argv:
            idx = sys.argv.index('--duration')
            if idx + 1 < len(sys.argv):
                duration = int(sys.argv[idx + 1])
        
        if tickers:
            logger = LiveDataLogger(tickers=tickers, duration_minutes=duration)
            logger.start()
        else:
            main()
    
    else:
        # python live_stream_logger.py
        main()