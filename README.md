# AI Münazara Uygulaması - Mimari Dökümantasyonu

Bu döküman, AI Münazara uygulamasının detaylı mimari yapısını, sınıf hiyerarşisini ve modüller arasındaki etkileşimleri tanımlar.

## Temel Veri Yapıları (`core/models.py`)

### Agent Sınıfı
```python
class Agent:
    """
    Münazarada yer alan bir ajanı temsil eder.
    
    Her ajan, bir isim, API anahtarı, model bilgisi ve sistem promptuna sahiptir.
    Moderatör rolü opsiyonel olarak belirtilebilir.
    
    Attributes:
        name (str): Ajanın adı
        api_key (str): OpenRouter API anahtarı
        model (str): Kullanılacak dil modeli (ör: "openai/gpt-4", "anthropic/claude-3")
        system_prompt (str): Ajanın rolünü ve davranışını belirleyen sistem promptu
        is_moderator (bool): Ajanın moderatör olup olmadığını belirtir
        token_usage (dict): Ajanın kullandığı toplam token sayısı (prompt ve completion)
        cost (float): Ajanın API çağrılarının toplam maliyeti
    """
```

### Message Sınıfı
```python
class Message:
    """
    Münazara sırasında bir ajan tarafından gönderilen mesajı temsil eder.
    
    Her mesaj, gönderen ajan, içerik, zaman damgası ve token kullanımı bilgilerine sahiptir.
    
    Attributes:
        agent (Agent): Mesajı gönderen ajan
        content (str): Mesajın içeriği
        timestamp (datetime): Mesajın gönderilme zamanı
        prompt_tokens (int): API çağrısı için kullanılan prompt token sayısı
        completion_tokens (int): API yanıtının token sayısı
        cost (float): Bu mesaj için harcanan tahmini maliyet
    """
```

### Debate Sınıfı
```python
class Debate:
    """
    Bir münazara oturumunu temsil eder.
    
    Münazara, bir konu, katılımcı ajanlar listesi ve turlardan oluşur.
    Ayrıca token kullanımı ve maliyet takibi yapar.
    
    Attributes:
        topic (str): Münazara konusu
        agents (list): Katılımcı ajanların listesi
        moderator (Agent): Moderatör rolündeki ajan
        turns (list): Tamamlanan turların listesi
        current_turn (Turn): Şu anki aktif tur
        total_prompt_tokens (int): Toplam kullanılan prompt token sayısı
        total_completion_tokens (int): Toplam kullanılan completion token sayısı
        total_cost (float): Münazaranın toplam maliyeti
        start_time (datetime): Münazaranın başlangıç zamanı
        end_time (datetime): Münazaranın bitiş zamanı (tamamlandıysa)
    """
```

### Turn Sınıfı
```python
class Turn:
    """
    Münazarada bir turu temsil eder.
    
    Bir tur, tüm ajanların sırayla konuşması ve moderatörün özet yapmasından oluşur.
    
    Attributes:
        turn_number (int): Tur numarası
        messages (list): Turdaki mesajların listesi
        summary (Message): Moderatörün tur sonu özeti
        is_last_turn (bool): Bu turun son tur olup olmadığını belirtir
        prompt_tokens (int): Bu turda kullanılan prompt token sayısı
        completion_tokens (int): Bu turda kullanılan completion token sayısı
        cost (float): Bu turun toplam maliyeti
    """
```

## Ajan Yönetimi (`core/agent_manager.py`)

### AgentManager Sınıfı
```python
class AgentManager:
    """
    Ajanların oluşturulması, yapılandırılması ve yönetimi için merkezi sınıf.
    
    Bu sınıf, JSON dosyalarından ajan yapılandırmalarını yükler, yeni ajanlar oluşturur
    ve mevcut ajanları yönetir.
    
    Methods:
        load_agents_from_file(file_path): JSON dosyasından ajan yapılandırmalarını yükler
        create_agent(name, api_key, model, system_prompt, is_moderator): Yeni bir ajan oluşturur
        add_agent(agent): Mevcut bir ajanı yöneticiye ekler
        remove_agent(agent_id): Bir ajanı yöneticiden kaldırır
        get_agent_by_id(agent_id): ID'ye göre bir ajan döndürür
        get_moderator(): Moderatör rolündeki ajanı döndürür
        save_agents_to_file(file_path): Ajan yapılandırmalarını JSON dosyasına kaydeder
    """
```

## API İletişimi (`core/api_client.py`)

### APIClient Sınıfı
```python
class APIClient:
    """
    OpenRouter API ile iletişim kurmak için kullanılan sınıf.
    
    Bu sınıf, asenkron API çağrıları yapar, token kullanımını takip eder
    ve hata yönetimini sağlar.
    
    Methods:
        async_request(agent, prompt, conversation_history): Asenkron API isteği yapar
        format_messages(system_prompt, prompt, conversation_history): API mesajlarını formatlar
        parse_response(response): API yanıtını ayrıştırır
        extract_token_usage(response): API yanıtından token kullanımını çıkarır
        calculate_cost(model, prompt_tokens, completion_tokens): Maliyet hesaplaması yapar
    """
```

### APIThread Sınıfı
```python
class APIThread(QThread):
    """
    API isteklerini asenkron olarak çalıştırmak için QThread temelli sınıf.
    
    Bu sınıf, API çağrılarını UI thread'ini bloke etmeden yapar
    ve sonuçları Qt sinyal mekanizması aracılığıyla iletir.
    
    Signals:
        response_ready(str, dict): API yanıtı hazır olduğunda tetiklenir
        error_occurred(str): Bir hata oluştuğunda tetiklenir
        request_started(): İstek başladığında tetiklenir
        request_finished(): İstek tamamlandığında tetiklenir
    """
```

## Münazara Yönetimi (`core/debate_manager.py`)

### DebateManager Sınıfı
```python
class DebateManager:
    """
    Münazara akışını yöneten merkezi sınıf.
    
    Bu sınıf, turları yönetir, moderatör akışını kontrol eder,
    ajanların sırayla konuşmasını sağlar ve münazara durumunu izler.
    
    Signals:
        new_message(Message): Yeni bir mesaj oluştuğunda tetiklenir
        turn_ended(Turn): Bir tur tamamlandığında tetiklenir
        turn_started(int): Yeni bir tur başladığında tetiklenir
        debate_ended(Debate): Münazara tamamlandığında tetiklenir
        token_usage_updated(int, int, float): Token kullanımı güncellendiğinde tetiklenir
    
    Methods:
        start_debate(topic, agents): Yeni bir münazara başlatır
        end_debate(): Mevcut münazarayı sonlandırır
        pause_debate(): Münazarayı duraklatır
        resume_debate(): Duraklatılmış münazarayı sürdürür
        next_turn(): Bir sonraki tura geçer
        start_turn(): Yeni bir tur başlatır
        end_turn(): Mevcut turu sonlandırır
        moderator_turn(): Moderatörün konuşması için çağrılır
        agent_turn(agent): Bir ajanın konuşması için çağrılır
        prepare_prompt_for_agent(agent): Bir ajan için prompt hazırlar
        optimize_conversation_history(): Konuşma geçmişini optimize eder
        save_debate_to_file(file_path): Münazarayı dosyaya kaydeder
        load_debate_from_file(file_path): Dosyadan münazara yükler
    """
```

## Konfigürasyon Yönetimi (`utils/config.py`)

### Config Sınıfı
```python
class Config:
    """
    Uygulama ayarlarını yöneten sınıf.
    
    Bu sınıf, ayarları JSON dosyasından yükler, değişiklikleri kaydeder
    ve güvenli bir şekilde API anahtarlarını yönetir.
    
    Methods:
        load_from_file(file_path): Ayarları dosyadan yükler
        save_to_file(file_path): Ayarları dosyaya kaydeder
        get(key, default=None): Bir ayarı döndürür
        set(key, value): Bir ayarı değiştirir
        get_secure(key): Güvenli bir değeri döndürür (API anahtarları için)
        set_secure(key, value): Güvenli bir değeri ayarlar
    """
```

## Loglama ve İzleme (`utils/logger.py`)

### Logger Sınıfı
```python
class Logger:
    """
    Uygulama loglamasını yöneten sınıf.
    
    Bu sınıf, workspace logger ile entegre çalışır, modül geçişlerini izler
    ve hata takibi sağlar.
    
    Methods:
        debug(message): Debug seviyesinde log mesajı
        info(message): Info seviyesinde log mesajı
        warning(message): Warning seviyesinde log mesajı
        error(message): Error seviyesinde log mesajı
        critical(message): Critical seviyesinde log mesajı
        log_module_transition(from_module, to_module): Modül geçişlerini loglar
        log_api_call(agent, model, prompt_tokens, completion_tokens): API çağrılarını loglar
    """
```

### CostTracker Sınıfı
```python
class CostTracker:
    """
    Token kullanımı ve maliyet takibi yapan sınıf.
    
    Bu sınıf, API çağrılarında kullanılan token miktarını ve maliyeti takip eder,
    istatistikler oluşturur ve bu verileri görselleştirmek için arayüz sağlar.
    
    Methods:
        add_usage(prompt_tokens, completion_tokens, model): Yeni token kullanımı ekler
        calculate_cost(model, prompt_tokens, completion_tokens): Maliyet hesaplaması yapar
        get_total_usage(): Toplam token kullanımını döndürür
        get_total_cost(): Toplam maliyeti döndürür
        get_usage_by_model(): Modele göre kullanım istatistiklerini döndürür
        reset(): İstatistikleri sıfırlar
    """
```

## Kullanıcı Arayüzü (`ui/`)

### MainWindow Sınıfı (`ui/main_window.py`)
```python
class MainWindow(QMainWindow):
    """
    Uygulamanın ana penceresi.
    
    Bu sınıf, tüm UI panellerini içerir ve bunları düzenler.
    """
```

### AgentPanel Sınıfı (`ui/agent_panel.py`)
```python
class AgentPanel(QWidget):
    """
    Ajanların yapılandırmasını yönetmek için kullanılan panel.
    
    Bu panel, ajanların listesini gösterir, yeni ajan ekleme, düzenleme ve silme işlevlerini sağlar.
    """
```

### DebatePanel Sınıfı (`ui/debate_panel.py`)
```python
class DebatePanel(QWidget):
    """
    Münazara akışını gösteren panel.
    
    Bu panel, mesajları ajan renkleriyle gösterir, moderatör özetlerini vurgular
    ve token/maliyet bilgilerini her mesajın yanında gösterir.
    """
```

### ControlPanel Sınıfı (`ui/control_panel.py`)
```python
class ControlPanel(QWidget):
    """
    Kullanıcı kontrollerini içeren panel.
    
    Bu panel, başlat/durdur/duraklat gibi butonları, konu giriş alanını,
    kayıt/yükleme seçeneklerini ve temayı değiştirme düğmelerini içerir.
    """
```

## Modüller Arası Etkileşimler

1. **UI → Core**
   - `MainWindow` → `DebateManager`: Münazara başlat/bitir/duraklat
   - `AgentPanel` → `AgentManager`: Ajan ekle/düzenle/sil
   - `ControlPanel` → `DebateManager`: Kontroller (başlat/durdur)

2. **Core → UI (Sinyaller)**
   - `DebateManager` → `DebatePanel`: Yeni mesaj, tur başlangıç/bitiş
   - `DebateManager` → `ControlPanel`: Münazara durumu değişikliği

3. **Core → Core**
   - `DebateManager` → `APIClient`: API istekleri
   - `AgentManager` → `DebateManager`: Ajan yapılandırması

4. **Utils Entegrasyonu**
   - Tüm sınıflar → `Logger`: Loglama için
   - `APIClient` → `CostTracker`: Token kullanımı ve maliyet takibi

## Asenkron İşlem Akışı

1. **Kullanıcı münazara başlatır** (`ControlPanel` → `MainWindow` → `DebateManager`)
2. **Moderatör açılış konuşması yapar** (`DebateManager` → `APIThread` → `APIClient`)
3. **Ajanlar sırayla konuşur** (Her ajan için asenkron çağrı)
4. **Moderatör tur özeti yapar** (Asenkron çağrı)
5. **Tüm konuşmalar tamamlandığında** (`QThread` → `DebateManager` → `DebatePanel`)

## Token Optimizasyonu Detayları

1. **Hafıza Yönetimi**
   - Her turdan sonra, tam geçmiş yerine moderatör özeti kullanılır
   - Bu, token kullanımını önemli ölçüde azaltır

2. **Prompt Mühendisliği**
   - Her ajanın promptu, rolüne uygun olarak optimize edilir
   - Moderatör promptu özetleme ve yönlendirme üzerine odaklanır

3. **Mesaj Filtresi**
   - Uzun münazaralarda, sadece son N mesaj gönderilir
   - Önceki mesajlar özetlenerek token kullanımı azaltılır

## Hata Yönetimi ve Dayanıklılık

1. **API Hataları**
   - Bağlantı sorunları için yeniden deneme mekanizması
   - Rate limit aşımı durumunda bekleme ve tekrar deneme

2. **Kullanıcı Geri Bildirimi**
   - Hata durumunda kullanıcıya Türkçe açıklamalar
   - İşlem durumu hakkında sürekli bilgilendirme

3. **Veri Kaybını Önleme**
   - Otomatik kayıt mekanizması
   - Beklenmeyen kapanmalarda son durumu koruma

## Gelecekteki Mimari Genişletmeler

1. **Vektör Veritabanı Entegrasyonu**
   - Münazara içeriğinin vektörleştirilmesi ve aranabilir hale getirilmesi

2. **Gelişmiş Analitik**
   - Ajanların performansını değerlendirme mekanizması
   - Argüman kalitesini ölçme ve puanlama

3. **Dil Model Değişimi**
   - Çalışma zamanında farklı dil modellerine geçiş imkanı
   - Model performans karşılaştırma aracı

## LLM API Servis Sağlayıcıları

Münazara uygulaması için OpenRouter dışında kullanabileceğiniz alternatif API servis sağlayıcıları ve entegrasyon stratejileri:

### Önerilen API Servisleri

1. **Together AI**
   ```python
   class TogetherAIClient(APIClient):
       """
       Together AI API ile iletişim kurmak için kullanılan özel istemci.
       
       200'den fazla açık kaynak modele erişim sağlar.
       """
       
       BASE_URL = "https://api.together.xyz/v1"
       
       def format_messages(self, system_prompt, prompt, conversation_history):
           """Together AI formatında mesajları biçimlendir"""
           # Together AI için özel formatlama
       
       def extract_token_usage(self, response):
           """Together AI yanıtından token kullanımını çıkar"""
           # Together AI token bilgisi çıkarımı
   ```

2. **Anthropic**
   ```python
   class AnthropicClient(APIClient):
       """
       Anthropic (Claude) API ile iletişim kurmak için kullanılan özel istemci.
       
       Claude 3 modelleri argüman oluşturma konusunda yüksek kaliteli sonuçlar verir.
       """
       
       BASE_URL = "https://api.anthropic.com/v1/messages"
       
       def format_messages(self, system_prompt, prompt, conversation_history):
           """Anthropic formatında mesajları biçimlendir"""
           # Claude XML formatını kullan
       
       def extract_token_usage(self, response):
           """Anthropic yanıtından token kullanımını çıkar"""
           # Anthropic token bilgisi çıkarımı
   ```

3. **Groq**
   ```python
   class GroqClient(APIClient):
       """
       Groq API ile iletişim kurmak için kullanılan özel istemci.
       
       LPU teknolojisi sayesinde ultra-hızlı yanıt süreleri sağlar.
       """
       
       BASE_URL = "https://api.groq.com/openai/v1"
       
       def format_messages(self, system_prompt, prompt, conversation_history):
           """Groq formatında mesajları biçimlendir"""
           # Groq OpenAI uyumlu format kullanır
       
       def extract_token_usage(self, response):
           """Groq yanıtından token kullanımını çıkar"""
           # Groq token bilgisi çıkarımı
   ```

### API İstemci Fabrikası

```python
class APIClientFactory:
    """
    Belirtilen sağlayıcı tipine göre uygun API istemcisi oluşturan fabrika sınıfı.
    
    Bu fabrika, farklı API istemcileri arasında sorunsuz geçiş yapılmasını sağlar.
    
    Methods:
        create_client(provider_type, api_key): Belirtilen sağlayıcı için bir API istemcisi oluşturur
        get_available_providers(): Kullanılabilir tüm API sağlayıcılarını döndürür
    """
    
    @staticmethod
    def create_client(provider_type, api_key):
        """Belirtilen sağlayıcı için bir API istemcisi oluşturur"""
        if provider_type == "openrouter":
            return APIClient(api_key)
        elif provider_type == "together":
            return TogetherAIClient(api_key)
        elif provider_type == "anthropic":
            return AnthropicClient(api_key)
        elif provider_type == "groq":
            return GroqClient(api_key)
        # ... diğer sağlayıcılar için ...
        else:
            raise ValueError(f"Desteklenmeyen sağlayıcı tipi: {provider_type}")
```

### Çoklu API Sağlayıcı Yönetimi

```python
class MultiProviderAPIManager:
    """
    Birden çok API sağlayıcısını yöneten sınıf.
    
    Bu sınıf, farklı API sağlayıcıları arasında otomatik geçiş,
    yük dengeleme ve hata durumunda alternatif sağlayıcıya geçiş yapabilir.
    
    Methods:
        add_provider(provider_type, api_key, priority): Yeni bir API sağlayıcısı ekler
        remove_provider(provider_id): Bir API sağlayıcısını kaldırır
        send_request(agent, prompt, conversation_history): En uygun sağlayıcıyı kullanarak istek gönderir
        get_best_provider_for_agent(agent): Bir ajan için en uygun sağlayıcıyı belirler
    """
    
    def send_request(self, agent, prompt, conversation_history):
        """Mevcut duruma göre en uygun sağlayıcıyı seçerek istek gönderir"""
        # İstek başarısız olursa alternatif sağlayıcıları dene
        # Rate limit aşılırsa farklı sağlayıcıya geç
        # Maliyet optimizasyonu yap
```

### API Önbelleği ve Optimizasyon

```python
class APICacheManager:
    """
    API yanıtlarını önbelleğe alan ve optimize eden sınıf.
    
    Bu sınıf, tekrarlanan istekleri önbelleğe alarak API çağrı sayısını
    ve token kullanımını optimize eder.
    
    Methods:
        cache_response(key, response): Bir API yanıtını önbelleğe alır
        get_cached_response(key): Önbellekteki bir yanıtı döndürür
        generate_cache_key(agent, prompt, conversation_history): Önbellek anahtarı oluşturur
    """
```

Bu API entegrasyon stratejisi, münazara uygulamanızın esnekliğini ve dayanıklılığını önemli ölçüde artıracaktır. Farklı API sağlayıcıları arasında sorunsuz geçiş yapma, optimum maliyetle en iyi performansı elde etme ve hata durumlarında bile kesintisiz hizmet sunma olanağı sağlar.
# AI Münazara Uygulama Yol Haritası ve Akış Diyagramı

## Proje Genel Bakış

Bu proje, PySide6 kullanarak modern bir arayüz ile OpenRouter API üzerinden 5 ajanın (biri moderatör) münazara yapabildiği bir ortam sağlar. Ajanlar OpenRouter API üzerinden farklı dil modelleriyle entegre edilir, ve sistem, münazaraların akışını, moderatörün koordinasyonunu ve tur bazlı değerlendirmeleri yönetir.

## Proje Amaçları

1. **Modern Arayüz**: PySide6 ile kullanıcı dostu, tema desteği olan bir UI
2. **Ajan Yapılandırması**: Maksimum 5 ajanın OpenRouter API üzerinden konfigürasyonu
3. **Moderatör Rolü**: Ajanlardan birinin moderatör olarak atanması ve münazara akışını koordine etmesi
4. **Sıralı Tartışma**: Ajanların sırayla konuştuğu bir tartışma ortamı
5. **Tur Sistemi**: Her ajanın sırayla konuşması bir tur olarak kabul edilir
6. **Son Tur Bilgisi**: Son turda ajanlara bilgi verilerek kapanış yapmaları sağlanır
7. **Maliyet ve Token Takibi**: API kullanımının şeffaf bir şekilde izlenmesi

## Klasör Yapısı

```
ai_debate_app/
├── main.py                      # Ana uygulama başlangıç noktası
├── README.md                    # Proje dökümantasyonu
├── requirements.txt             # Gerekli Python paketleri
├── ui/                          # Kullanıcı arayüzü bileşenleri
│   ├── __init__.py
│   ├── main_window.py           # Ana pencere
│   ├── agent_panel.py           # Ajan yönetim paneli
│   ├── debate_panel.py          # Münazara akış paneli
│   └── control_panel.py         # Kontrol paneli (başlat/durdur vb.)
├── core/                        # Çekirdek işlevsellik
│   ├── __init__.py
│   ├── models.py                # Temel veri yapıları (Ajan, Mesaj, Münazara, Tur)
│   ├── agent_manager.py         # Ajan yapılandırması ve yönetimi
│   ├── debate_manager.py        # Münazara akışını yöneten sınıf
│   └── api_client.py            # OpenRouter API ile iletişim
├── utils/                       # Yardımcı araçlar
│   ├── __init__.py
│   ├── config.py                # Konfigürasyon yönetimi
│   ├── logger.py                # Gelişmiş loglama sistemi
│   └── cost_tracker.py          # Token kullanımı ve maliyet takibi
└── data/                        # Veri dosyaları
    ├── agents/                  # Ajan yapılandırma dosyaları (JSON)
    └── debates/                 # Kaydedilmiş münazara oturumları
```

## Proje Aşamaları

### Aşama 1: Temel Atma ve Yapılandırma

**Hedef**: Projenin temel iskeletini ve yapılarını oluşturmak

1. **Görevler**:
   - `core/models.py`: Ajan, Mesaj, Münazara, Tur sınıflarını oluştur (Token/maliyet alanları dahil)
   - `utils/config.py`: JSON tabanlı yapılandırma yönetimini oluştur
   - `utils/logger.py`: Workspace logger ile entegre loglama mekanizmasını kur
   - Proje klasör yapısını oluştur

2. **Teknik Detaylar**:
   - Her sınıf ve metot için detaylı docstring ekle
   - Token ve maliyet takibi için gerekli alanları veri yapılarına dahil et

3. **Çıktı**: Temel veri yapıları ve yapılandırma sistemi hazır

### Aşama 2: Çekirdek Mantık Geliştirme

**Hedef**: Uygulamanın ana işlevlerini oluşturmak

1. **Görevler**:
   - `core/api_client.py`: OpenRouter API entegrasyonu (token takibi dahil)
   - `core/agent_manager.py`: Ajanların yapılandırılması ve yönetimi
   - Asenkron API çağrıları için QThread mekanizması

2. **Teknik Detaylar**:
   - API çağrıları asenkron olarak (QThread) yapılacak
   - Her API çağrısı için token kullanımı ve maliyet takibi
   - Kapsamlı hata yönetimi ve Türkçe hata mesajları

3. **Çıktı**: API iletişimi ve ajan yönetimi çalışır durumda

### Aşama 3: Münazara Akışı ve Moderasyon

**Hedef**: Münazara mantığını ve moderatör rolünü oluşturmak

1. **Görevler**:
   - `core/debate_manager.py`: Münazara akışını yönetecek sınıfı oluştur
   - Tur yönetimi: Her ajanın sırayla konuşması
   - Moderatör işlevleri: Tur sonunda özet yapma, yeni turu başlatma

2. **Teknik Detaylar**:
   - Sıralı (sequential) ama asenkron (non-blocking UI) yaklaşım 
   - Moderatör özetlerinin bir sonraki tura aktarılması
   - Token optimizasyonu: Geçmiş mesajları modele gönderirken özetleme

3. **Çıktı**: Temel münazara akışı ve moderatör işlevleri çalışır durumda

### Aşama 4: Kullanıcı Arayüzü Geliştirme

**Hedef**: Kullanıcı etkileşim arayüzünü oluşturmak

1. **Görevler**:
   - `ui/main_window.py`: Ana pencere düzenini oluştur
   - `ui/agent_panel.py`: Ajan yapılandırma panelini tasarla
   - `ui/debate_panel.py`: Münazara akış panelini oluştur
   - `ui/control_panel.py`: Kontrol butonlarını ekle

2. **Teknik Detaylar**:
   - PySide6 sinyal-slot mekanizmasıyla UI ve çekirdek mantık arasında iletişim
   - Renk kodlaması ile her ajanın mesajlarını belirgin şekilde ayırt etme
   - Tema desteği (açık/koyu mod)
   - Kullanıcı dostu hata mesajları

3. **Çıktı**: Temel kullanıcı arayüzü çalışır durumda

### Aşama 5: Entegrasyon ve İyileştirmeler

**Hedef**: Tüm bileşenleri entegre etmek ve projeyi geliştirmek

1. **Görevler**:
   - Token ve maliyet takibi verilerinin UI'da gösterilmesi
   - Münazaraları kaydetme/yükleme işlevselliği
   - Ajanlar arası etkileşimi geliştirme (peer review mekanizması)
   - Kullanıcı deneyimini iyileştirme (durum göstergeleri, ilerleme bildirimleri)

2. **Teknik Detaylar**:
   - JSON formatında münazara kayıtları
   - API çağrılarından token/maliyet verilerini çekme ve görselleştirme
   - Her mesajın yanında kullanılan token sayısı ve maliyeti gösterme

3. **Çıktı**: Tam entegre edilmiş, gelişmiş özelliklere sahip uygulama

### Aşama 6: Test, Dokümantasyon ve Son Dokunuşlar

**Hedef**: Projeyi tamamlamak ve yayına hazır hale getirmek

1. **Görevler**:
   - Kapsamlı testler (fonksiyonel, UI, hata durumları)
   - Kod içi dokümantasyon ve README güncelleme
   - Son hata düzeltmeleri ve performans iyileştirmeleri

2. **Teknik Detaylar**:
   - Tüm kod içi yorumların ve docstring'lerin Türkçe olarak yazılması
   - Kullanıcı kılavuzunun hazırlanması
   - Hata loglama mekanizmasının son kontrolü

3. **Çıktı**: Test edilmiş, belgelenmiş ve yayına hazır uygulama

## Münazara Akış Diyagramı

Aşağıdaki diyagram, münazara sırasındaki temel iş akışını göstermektedir:

```
+---------------------+
|   Başlangıç         |
| (Kullanıcı konuyu   |
|    belirler)        |
+---------------------+
          |
          v
+---------------------+
|  Moderatör Açılış   |
|  (Konuyu tanıtır ve |
|   sırayla söz verir)|
+---------------------+
          |
          v
+---------------------+       +---------------------+
|   Ajan 1 Konuşur    |------>|   Ajan 2 Konuşur    |
+---------------------+       +---------------------+
                                       |
                                       v
+---------------------+       +---------------------+
|   Ajan N Konuşur    |<------|   Ajan 3 Konuşur    |
+---------------------+       +---------------------+
          |
          v
+---------------------+       +---------------------+
|  Moderatör Özet     |------>|   Yeni Tur?         |
|  (Tur özetlenir)    |       |                     |
+---------------------+       +---------------------+
                                       |
                                       v
          +------------------------+   |   +---------------------+
          |   Son Tur Başlatılır   |<--+-->|   Normal Tur        |
          |(Ajanlara bildirilir)   |   |   |   Başlatılır        |
          +------------------------+   |   +---------------------+
                      |               [Evet]       |
                      v                            v
          +------------------------+        (Döngüye geri dön)
          |   Kapanış Argümanları  |
          |   (Ajanlar son         |
          |    sözlerini söyler)   |
          +------------------------+
                      |
                      v
          +------------------------+
          |   Moderatör Final Özet |
          |   (Münazara sonlandırılır)|
          +------------------------+
```

## Modüller Arası Etkileşim Diyagramı

Aşağıdaki diyagram, sistem bileşenleri arasındaki temel etkileşimleri göstermektedir:

```
+---------------------+           +---------------------+
|   Kullanıcı Arayüzü |<--------->|   Ajan Yönetimi     |
|   (UI)              |           |   (agent_manager.py)|
| - Ajan Paneli       |           | - Ajan oluşturma    |
| - Münazara Paneli   |           | - Moderatör rolü    |
| - Kontrol Paneli    |           +---------------------+
+---------------------+                     ^
          ^                                 |
          |                                 v
          v                     +---------------------+
+---------------------+         |   Münazara Yönetimi |
|   Config Yönetimi   |<------->|   (debate_manager.py)|
|   (config.py)       |         | - Tur yönetimi      |
+---------------------+         | - Moderatör aksiyonları|
                                +---------------------+
                                        ^
                                        |
                                        v
          +------------------------+   +---------------------+
          |   Loglama/İzleme       |<->|   API İstemcisi    |
          |   (logger.py,          |   |   (api_client.py)  |
          |    cost_tracker.py)    |   | - OpenRouter çağrıları|
          +------------------------+   | - Token takibi     |
                                       +---------------------+
```

## Her Tur İçin Token Optimizasyonu Mekanizması

```
1. Başlangıç: Kullanıcı münazara konusunu girer
2. Her tur için:
   a. Moderatör turu başlatır
   b. Her ajan sırayla konuşur
   c. Tüm ajanlar konuştuğunda, moderatör tur özetini yapar
   d. Özet bir sonraki turun başında tüm ajanlara iletilir
   e. Eski mesajlar yerine özet kullanılarak token kullanımı optimize edilir
3. Son tur: 
   a. Ajanlara "son tur" bilgisi verilir
   b. Kapanış argümanları sunulur
   c. Moderatör final özet yapar
```

## Ajan Etkileşimi Mekanizması

```
1. Her ajan argümanını sunar
2. Her ajanın promptuna "Önceki konuşmacılar şunları söyledi: [...]" bilgisi eklenir
3. Moderatör her turun sonunda bir özet hazırlar:
   "Ajan 1 şu argümanları sundu: [...]"
   "Ajan 2 bu argümanlara karşı çıktı: [...]"
4. Ajanlar bu özeti kullanarak karşı argümanlar oluşturur
5. Son turda ajanlara "Bu son tur, kapanış argümanlarını sun" bilgisi verilir
```

## Token/Maliyet Takibi Sistemi

```
1. Her API çağrısı için (api_client.py):
   a. Prompt token sayısını ölç
   b. Tamamlama token sayısını ölç
   c. OpenRouter yanıtından maliyet bilgisini çek

2. Her mesaj için (models.py):
   a. Token kullanımını kaydet
   b. Tahmini maliyeti hesapla

3. Her tur için (debate_manager.py):
   a. Toplam token kullanımını hesapla
   b. Toplam maliyeti hesapla

4. Görselleştirme (ui):
   a. Her mesajın yanında token sayısı ve maliyeti göster
   b. Tur bazında toplam maliyeti göster
   c. Münazara genelinde toplam maliyeti göster
```

## Geliştirici Notları

- Tüm sınıflar ve metotlar için detaylı Türkçe docstring yazılacak
- Workspace logger sistemine entegrasyon için her sınıfa uygun log çağrıları eklenecek
- Kullanıcıya her adımda onay alınacak şekilde UI tasarlanacak
- Hata yönetimi için try-except blokları ve Türkçe hata mesajları kullanılacak
- API anahtarlarının güvenli saklanması için uygun yöntemler (örn: keyring) kullanılacak
- Tüm modüller arası iletişim, temiz sinyal-slot mekanizmasıyla sağlanacak

## Gelecek Geliştirmeler

- Dil model seçimine göre maliyet hesaplayıcı
- Münazara içeriğinin PDF olarak dışa aktarılması
- Sohbet geçmişlerinin vektör veritabanında saklanması ve aranabilmesi
- Ajan kişiliklerinin özelleştirilebilmesi için kütüphane
- Canlı transkript ve özet oluşturucu

## Çoklu API Sağlayıcı Entegrasyonu Planı

### Faz 1: Genişletilmiş API Desteği (0-2 Hafta)

1. **API İstemci Soyutlama Katmanı**
   - Mevcut `api_client.py` modülünü tüm sağlayıcılar için soyut temel sınıf olacak şekilde yeniden düzenle
   - Her sağlayıcı için özel istemci sınıfları oluştur:
     - `openrouter_client.py`: Mevcut OpenRouter entegrasyonu
     - `together_client.py`: Together AI entegrasyonu
     - `anthropic_client.py`: Anthropic (Claude) entegrasyonu
     - `groq_client.py`: Groq entegrasyonu
     - `perplexity_client.py`: Perplexity AI entegrasyonu
     - `fireworks_client.py`: Fireworks AI entegrasyonu

2. **API İstemci Fabrikası**
   - `api_client_factory.py`: Farklı sağlayıcı istemcilerini oluşturmak için fabrika sınıfı
   - Yapılandırma dosyasından sağlayıcı seçimi yapabilme
   - UI'dan sağlayıcı değiştirme mekanizması

3. **Dokümantasyon ve Testler**
   - Her API sağlayıcısı için kullanım dökümantasyonu
   - Birim testleri ve entegrasyon testleri

### Faz 2: Gelişmiş API Yönetimi (2-4 Hafta)

1. **Çoklu Sağlayıcı Yönetimi**
   - `multi_provider_manager.py`: Birden çok API sağlayıcısını aynı anda yönetebilen modül
   - Hata durumlarında otomatik failover (alternatif sağlayıcıya geçiş)
   - Sağlayıcılar arasında yük dengeleme

2. **Sağlayıcı Seçim Stratejileri**
   - Maliyet optimizasyonu: En düşük maliyetli sağlayıcıyı seçme
   - Performans optimizasyonu: En hızlı sağlayıcıyı seçme
   - Kalite optimizasyonu: En iyi kalitede yanıt veren sağlayıcıyı seçme
   - Karma strateji: Maliyet, hız ve kalite dengesini otomatik olarak optimize etme

3. **Sağlayıcı Performans Analizi**
   - Her sağlayıcı için yanıt hızı, kalite ve maliyet metriklerini toplama
   - Performans raporları oluşturma
   - Otomatik sağlayıcı önerisi algoritması

### Faz 3: UI ve Kullanıcı Deneyimi Entegrasyonu (4-6 Hafta)

1. **Genişletilmiş Ajan Yapılandırma Paneli**
   - Sağlayıcı seçim arayüzü
   - Model seçenekleri (her sağlayıcı için kullanılabilir modeller)
   - Her sağlayıcı için özel parametre ayarları

2. **Münazara Ayarları**
   - Her ajan için özel sağlayıcı ve model atama
   - Moderatör için ayrı sağlayıcı/model seçimi
   - Otomatik veya manuel sağlayıcı seçimi ayarları

3. **Sağlayıcı Performans Görselleştirmeleri**
   - Sağlayıcı performansı için grafik ve tablolar
   - Maliyet karşılaştırma araçları
   - Kullanım istatistikleri

## Münazara "Self-Play" Gelişim Stratejisi

### Kavramsal Çerçeve

"Self-play" yaklaşımı, münazara modellerinin kendi kendileriyle etkileşime girerek yeteneklerini geliştirmesini sağlar. Bu yaklaşım, aşağıdaki adımları içerir:

1. **Argüman Üretme**: Model, bir konu hakkında bir argüman üretir
2. **Karşı Argüman Üretme**: Aynı model, kendi argümanına karşı bir argüman oluşturur
3. **Değerlendirme**: Üçüncü bir model, hangi argümanın daha ikna edici olduğunu değerlendirir
4. **Öğrenme**: Modeller, başarılı stratejileri tekrarlayarak gelişir

### Uygulama Planı

1. **Argüman Kütüphanesi**
   - `argument_library.py`: Başarılı argümanları saklayan ve kategorize eden modül
   - JSON formatında argüman veritabanı
   - Argüman şablonları ve yapıları

2. **Argüman Değerlendirme Sistemi**
   - `argument_evaluator.py`: Argümanları değerlendiren modül
   - Mantıksal tutarlılık, kanıt kullanımı, ikna ediciliği değerlendirme
   - Puanlama sistemi

3. **Gelişim Döngüsü**
   - `debate_trainer.py`: Self-play sürecini yöneten modül
   - Çevrimdışı eğitim modu
   - Gerçek zamanlı öğrenme

### Entegrasyon

Self-play sistemi, mevcut münazara uygulamasına aşağıdaki şekilde entegre edilecektir:

1. **Ajan Promptlarına Şablon Enjeksiyonu**
   - Başarılı argüman şablonlarını ajan promptlarına ekleme
   - Şablon seçimi için akıllı algoritma

2. **Münazara Sonrası Analiz**
   - Münazara tamamlandıktan sonra argümanları değerlendirme
   - Başarılı argümanları kütüphaneye ekleme

3. **Sürekli İyileştirme**
   - Kullanıcı uygulamayı kullandıkça münazara kalitesi artacak
   - Özel konulara ve alanlara özel argüman kütüphaneleri

## Self-Play İş Diyagramı

```
+------------------+       +------------------+       +------------------+
|  Münazara        |------>|  Argüman         |------>|  Kütüphane       |
|  Tamamlandı      |       |  Değerlendirme   |       |  Güncelleme      |
+------------------+       +------------------+       +------------------+
                                    |
                                    v
+------------------+       +------------------+       +------------------+
|  Yeni Şablonlar  |<------|  Analiz &        |<------|  Argüman         |
|  Oluşturuldu     |       |  Sınıflandırma   |       |  Ayıklama        |
+------------------+       +------------------+       +------------------+
        |
        v
+------------------+       +------------------+
|  Ajan Promptları |------>|  Geliştirilmiş   |
|  Güncellendi     |       |  Münazara        |
+------------------+       +------------------+
```

## Alternatif API Servis Sağlayıcılarının Karşılaştırması

| Sağlayıcı       | Güçlü Yönleri                               | Zayıf Yönleri                             | İdeal Kullanım                           |
|-----------------|---------------------------------------------|-------------------------------------------|------------------------------------------|
| OpenRouter      | Çok sayıda modele erişim, tek API           | Doğrudan erişime göre ekstra maliyet      | Çeşitlilik gerektiren durumlar          |
| Together AI     | 200+ açık kaynak model, hız                 | Bazı özel modellere erişim yok            | Açık kaynak model kullanımı             |
| Anthropic       | Claude 3 kalitesi, argüman üretme           | Sınırlı model seçeneği, maliyet           | Moderatör, kaliteli argüman üretimi     |
| Groq            | Ultra düşük latency, yüksek hız             | Sınırlı model seçeneği                    | Gerçek zamanlı münazaralar              |
| Perplexity      | Bilgi yoğun tartışmalar                     | Görece yeni API                           | Faktüel doğruluk gerektiren tartışmalar |
| Fireworks AI    | Hızlı yanıt, multimodal                     | Maliyet                                   | Görsel içerikli münazaralar             |
| DeepInfra       | Uygun fiyatlı, kurumsal                     | API özellikleri sınırlı olabilir          | Büyük ölçekli deploymentlar            |
| Lepton AI       | Python entegrasyonu, makul fiyat            | Daha az popüler                           | Hızlı prototipleme                      |
| Hyperbolic      | Ekonomik çözüm                              | Sınırlı özellikler                        | Düşük bütçeli projeler                  |

## Uygulama İnşa Süreci

1. **Temelleri Hazırla**
   - `APIClientFactory` ve temel soyut `APIClient` sınıfını oluştur
   - Her sağlayıcı için temel istemci sınıfını oluştur

2. **İlk Sağlayıcıları Entegre Et**
   - Together AI ve Anthropic entegrasyonunu öncelikle tamamla
   - Bu sağlayıcılarla temel münazara işlevselliğini test et

3. **Çoklu Sağlayıcı Sistemini Oluştur**
   - `MultiProviderAPIManager` sınıfını geliştir
   - Yük dengeleme ve failover mekanizmalarını oluştur

4. **UI Entegrasyonu**
   - Ajan yapılandırma paneline sağlayıcı seçimi ekle
   - Münazara ayarlarına sağlayıcı stratejileri ekle

5. **Argüman Geliştirme Sistemini Entegre Et**
   - Self-play sistemini kurup test et
   - Argüman kütüphanesini oluştur ve entegre et

6. **Test ve Optimizasyon**
   - Her sağlayıcıyı kapsamlı şekilde test et
   - Performans, maliyet ve kalite metriklerini topla
   - Sistem optimizasyonu yap

Bu yol haritası, münazara uygulamanızı daha esnek, güçlü ve etkili hale getirecektir. Çoklu API sağlayıcı desteği ve self-play ile sürekli gelişen argüman yapıları, uygulamanızın kalitesini önemli ölçüde artıracaktır.

