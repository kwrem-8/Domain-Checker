# domain-checker

Birden fazla domaini aynı anda kontrol et — hangisi müsait, hangisi dolu.

## Özellikler

- Her satıra bir domain gir, toplu kontrol et
- Uzantısız domain girersen .com .net .io gibi uzantıları otomatik ekler
- 10 paralel bağlantı ile hızlı kontrol
- Gerçek zamanlı sonuçlar, kontrol edildikçe güncellenir
- Müsait / Dolu / Hata sayısı özeti
- Ekstra bağımlılık yok — sadece Python standart kütüphanesi

## Çalıştırma

```bash
python domain_checker.py
```

## .exe olarak derleme

```bash
build.bat
```

`dist/domain-checker.exe` oluşur.

## Nasıl çalışır

DNS sorgusu (socket.gethostbyname) gönderir. Yanıt gelirse domain dolu,
NXDOMAIN hatası alırsa müsait olarak işaretlenir. Kayıt olup olmadığını
gösterir — alan adının satışta olup olmadığını değil.

## Lisans

MIT
