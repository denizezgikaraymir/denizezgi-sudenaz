# Socket Programming Assignment - Python Implementation

Bu proje, atanan ödevin temel bir uygulamasıdır: Client1 (gönderici), Server (aracı & veriyi bozucu), Client2 (alıcı & hata denetleyici).

Özellikler
- Kontrol yöntemleri: parity (byte başına), 2D parity, CRC16-CCITT, Hamming(7,4) (nibble bazlı), IP checksum
- Sunucu çeşitli hata enjektasyon modları sunar

Çalıştırma (terminal)
1. Server'ı başlatın (örnek port 9000, injection=bitflip):
   python server.py 9000 bitflip

2. Client2 (alıcı) başlatın (aynı host/port):
   python client2.py 127.0.0.1 9000

3. Client1 (gönderici) başlatın, metin ve yöntem seçin:
   python client1.py 127.0.0.1 9000

Proje akışı
- Client2 server'a bağlanır ve "CLIENT2" olarak kaydolur.
- Client1 bağlanır, "CLIENT1" yazar ve paketi gönderir: `DATA|METHOD|CONTROL`
- Server gelen paketi okur, seçilen hata enjeksiyonunu uygular ve Client2'ye iletir.
- Client2 gelen paketi alır, aynı yöntemi kullanarak kontrol bits/özet hesaplar ve gelen ile karşılaştırır; sonucu ekrana yazar.

Notlar / Geliştirme
- 2D parity, row/col paritelerini basit string formatında geri döner. 
- Hamming burada 7,4 için nibble başına parity hesaplar (tam Hamming kodlama/decoding değil; kontrol bitleri üretilir).
- CRC16-CCITT kullanıldı (poly 0x1021, init 0xFFFF).
  


