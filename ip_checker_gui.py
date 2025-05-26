import json
import sys
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import requests
from urllib.parse import urlparse
import socket
import re

# Konfiguracja serwisów
CONFIG = {
    'ip_services': [
        ("https://api.ipify.org?format=json", "json"),
        ("https://ifconfig.me/ip", "text"),
        ("https://icanhazip.com", "text")
    ],
    'info_services': [
        "https://ipinfo.io/{ip}/json",
        "https://ipapi.co/{ip}/json/",
        "https://ip-api.com/json/{ip}"
    ],
    'timeout': 5,
    'max_retries': 3,
    'cache_timeout': 3600,  # 1 godzina
    'proxy': None  # Możliwe do konfiguracji
}

def validate_url(url):
    """Walidacja URL"""
    try:
        # Sprawdzenie podstawowej struktury URL
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False

        # Sprawdzenie poprawności schematu
        if result.scheme not in ['http', 'https']:
            return False

        # Sprawdzenie poprawności hosta
        if not re.match(r'^[a-zA-Z0-9.-]+$', result.netloc):
            return False

        return True
    except:
        return False

def validate_ip(ip):
    """Walidacja adresu IP"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

import json
import sys
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests
from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QSyntaxHighlighter, QTextCharFormat

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
except ImportError:
    print("Błąd krytyczny: Moduł PyQt6-WebEngine nie jest zainstalowany.")
    print("Zainstaluj go za pomocą: pip install PyQt6-WebEngine")
    sys.exit(1)

from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QProgressBar,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class IPHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip_colors = defaultdict(lambda: QColor(255, 255, 255))
        self.color_index = 0
        # Paleta kolorów z większą różnorodnością
        self.colors = [
            # Czerwone
            QColor(255, 182, 193),  # Hot Pink
            QColor(255, 160, 122),  # Light Salmon
            QColor(255, 105, 180),  # Pink
            # Zielone
            QColor(144, 238, 144),  # Light Green
            QColor(127, 255, 0),    # Spring Green
            QColor(173, 255, 47),   # Green Yellow
            # Niebieskie
            QColor(135, 206, 250),  # Light Sky Blue
            QColor(173, 216, 230),  # Light Blue
            QColor(138, 43, 226),   # Blue Violet
            # Pomarańczowe
            QColor(255, 165, 0),    # Orange
            QColor(255, 140, 0),    # Dark Orange
            QColor(255, 127, 80),   # Coral
            # Fioletowe
            QColor(218, 112, 214),  # Orchid
            QColor(186, 85, 211),   # Medium Orchid
            QColor(147, 112, 219),  # Medium Purple
            # Brązowe
            QColor(205, 133, 63),   # Peru
            QColor(210, 105, 30),   # Chocolate
            QColor(205, 92, 92),    # Indian Red
            # Szare
            QColor(211, 211, 211),  # Light Gray
            QColor(192, 192, 192),  # Silver
            QColor(169, 169, 169),  # Dark Gray
        ]

    def set_ip_color(self, ip):
        if ip not in self.ip_colors:
            self.ip_colors[ip] = self.colors[self.color_index]
            self.color_index = (self.color_index + 1) % len(self.colors)

    def highlightBlock(self, text):
        for ip, color in self.ip_colors.items():
            format = QTextCharFormat()
            format.setBackground(color)
            format.setForeground(QColor(0, 0, 0))
            index = text.find(ip)
            while index >= 0:
                self.setFormat(index, len(ip), format)
                index = text.find(ip, index + 1)


class IPCheckerThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = {}
        self.cache_timestamps = {}
        self.parent = parent

    def is_cached(self, key):
        """Sprawdza, czy dane są w cache i czy są aktualne"""
        if key not in self.cache:
            return False
        timestamp = self.cache_timestamps[key]
        return (datetime.now() - timestamp).total_seconds() < CONFIG['cache_timeout']

    def get_from_cache(self, key):
        """Pobiera dane z cache"""
        return self.cache[key]

    def add_to_cache(self, key, data):
        """Dodaje dane do cache"""
        self.cache[key] = data
        self.cache_timestamps[key] = datetime.now()

    def validate_and_fetch(self, url, timeout=CONFIG['timeout']):
        """Waliduje URL i wykonuje zapytanie"""
        if not validate_url(url):
            raise ValueError(f"Nieprawidłowy URL: {url}")

        for attempt in range(CONFIG['max_retries']):
            try:
                # Aktualizacja postępu
                self.progress.emit(int((attempt + 1) / CONFIG['max_retries'] * 33))

                response = requests.get(
                    url,
                    timeout=timeout,
                    proxies=CONFIG['proxy']
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == CONFIG['max_retries'] - 1:
                    raise
                print(f"Próba {attempt + 1} nie powiodła się: {e}")
                continue

    def validate_ip_data(self, data):
        """Walidacja danych IP"""
        if not isinstance(data, dict):
            raise ValueError("Dane nie są słownikiem")

        ip = data.get('ip')
        if not ip or not validate_ip(ip):
            raise ValueError(f"Nieprawidłowy adres IP: {ip}")

        # Sprawdzenie kluczowych pól
        required_fields = ['country', 'region', 'city', 'org', 'loc']
        for field in required_fields:
            if field in data and not isinstance(data[field], str):
                raise ValueError(f"Nieprawidłowy typ danych dla pola {field}")

        return data

    def run(self):
        try:
            ip = None
            for service, response_type in CONFIG['ip_services']:
                try:
                    if self.is_cached('ip'):
                        ip = self.get_from_cache('ip')
                        print(f"Użyto cache dla IP: {ip}")
                        break

                    response = self.validate_and_fetch(service)
                    if response_type == "json":
                        ip = response.json().get("ip")
                    else:
                        ip = response.text.strip()

                    if ip and validate_ip(ip):
                        self.add_to_cache('ip', ip)
                        print(f"Pobrano i zwalidowano IP: {ip}")
                        break
                except Exception as e:
                    print(f"Błąd pobierania IP z {service}: {e}")

            if not ip:
                self.error.emit("Nie udało się pobrać adresu IP.")
                return

            info_cache_key = f"info_{ip}"
            if self.is_cached(info_cache_key):
                data = self.get_from_cache(info_cache_key)
                self.finished.emit(data)
                return

            for service in CONFIG['info_services']:
                try:
                    service_url = service.format(ip=ip)
                    response = self.validate_and_fetch(service_url)
                    data = response.json()
                    normalized_data = self.normalize_ip_data(data, ip)

                    if "loc" in normalized_data:  # Kluczowe jest 'loc'
                        self.add_to_cache(info_cache_key, normalized_data)
                        print(f"Pobrano dane lokalizacyjne dla {ip}")
                        self.finished.emit(normalized_data)
                        return
                except Exception as e:
                    print(f"Błąd pobrania info z {service}: {e}")

            # Jeśli doszliśmy tutaj, to znaczy, że udało się pobrać IP, ale nie dane lokalizacyjne
            print(
                f"Nie udało się pobrać danych lokalizacyjnych dla IP: {ip}, ale wysyłam IP."
            )
            partial_data = self.normalize_ip_data({}, ip)
            partial_data["error_loc"] = "Nie udało się pobrać danych lokalizacyjnych."
            self.add_to_cache(info_cache_key, partial_data)
            self.finished.emit(partial_data)

        except Exception as e:
            print(f"Nieoczekiwany błąd wątku: {e}")
            self.error.emit(f"Nieoczekiwany błąd wątku: {str(e)}")

    def normalize_ip_data(self, data, ip):
        """Normalizuje dane z różnych serwisów IP"""
        normalized = {"ip": ip}
        field_mappings = {
            "country": ["country", "country_name", "countryCode"],
            "region": ["region", "region_name", "regionName"],
            "city": ["city", "city_name"],
            "postal": ["postal", "zip"],
            "timezone": ["timezone", "time_zone"],
            "org": ["org", "isp", "as"],
            "loc": ["loc"],
            "lat": ["lat", "latitude"],
            "lon": ["lon", "longitude"],
        }

        for std_f, pos_f in field_mappings.items():
            for f in pos_f:
                if f in data and data[f]:
                    normalized[std_f] = data[f]
                    break

        if "loc" not in normalized and "lat" in normalized and "lon" in normalized:
            normalized["loc"] = f"{normalized['lat']},{normalized['lon']}"

        return normalized


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprawdzacz IP")
        self.setMinimumSize(1200, 800)
        self.history = []
        self.history_file = Path("ip_history.json")
        self.load_history()
        self.checking_in_progress = False

        self.setStyleSheet(
            """
            QMainWindow { background-color: #2b2b2b; }
            QLabel { color: #ffffff; font-size: 14px; }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton:pressed { background-color: #0a3d91; }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
            QPushButton:disabled:hover {
                background-color: #555555;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
                font-family: Consolas, 'Courier New', monospace;
            }
            QSplitter::handle {
                background-color: #3d3d3d;
                width: 5px;
            }
            QSplitter::handle:hover {
                background-color: #666666;
            }
            QProgressBar {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0d47a1;
                width: 1px;
            }
            /* Celowo nie stylizujemy QWebEngineView tutaj, jego tło jest zarządzane przez HTML */
        """
        )

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Lewa strona ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # Tytuł
        title = QLabel("Sprawdzacz Adresu IP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        left_layout.addWidget(title)

        # Przycisk sprawdzenia
        self.check_button = QPushButton("Sprawdź mój adres IP")
        self.check_button.setToolTip("Sprawdza twój adres IP i informacje o lokalizacji")
        self.check_button.clicked.connect(self.check_ip)
        left_layout.addWidget(self.check_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        splitter = QSplitter(Qt.Orientation.Vertical)
        left_layout.addWidget(splitter)

        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)  # Usuń marginesy wokół QTextEdit
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(180)  # Nieco mniejszy
        results_layout.addWidget(self.result_text)

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)  # Usuń marginesy wokół QTextEdit
        history_title = QLabel("Historia sprawdzeń")
        history_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 5px 0;"
        )
        history_layout.addWidget(history_title)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        history_layout.addWidget(self.history_text)

        self.highlighter = IPHighlighter(self.history_text.document())
        splitter.addWidget(results_widget)
        splitter.addWidget(history_widget)
        splitter.setSizes([350, 250])  # Dostosowane rozmiary
        main_layout.addWidget(left_widget, stretch=1)  # Lewa strona, mniejszy stretch

        # --- Prawa strona (mapa) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Ważne: usuwamy marginesy layoutu zawierającego mapę
        right_layout.setSpacing(5)  # Mały odstęp między tytułem mapy a mapą

        map_title_label = QLabel("Mapa lokalizacji")
        map_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-bottom: 5px;"
        )
        right_layout.addWidget(map_title_label)

        self.map_view = QWebEngineView()
        settings = self.map_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False
        )
        # QWebEngineProfile.defaultProfile().setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskCache) # Można potestować
        # self.map_view.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

        # self.map_view.setMinimumSize(300, 300) # Minimum, ale powinna się rozciągnąć
        right_layout.addWidget(
            self.map_view, stretch=1
        )  # Stretch = 1, aby wypełniła dostępną przestrzeń w QVBoxLayout

        main_layout.addWidget(
            right_widget, stretch=2
        )  # Prawa strona, większy stretch, aby była szersza

        self.init_default_map()
        self.display_history()

    def load_history(self):
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Błąd wczytywania historii: {e}")
            self.history = []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Błąd zapisywania historii: {e}")

    def display_history(self):
        self.history_text.clear()
        for entry in self.history:
            self.history_text.append(
                f"[{entry['timestamp']}] {entry['ip']} - {entry.get('city', 'N/A')}, {entry.get('country', 'N/A')}\n"
            )
            self.highlighter.set_ip_color(entry["ip"])
        self.history_text.moveCursor(self.history_text.textCursor().MoveOperation.End)
        self.highlighter.rehighlight()

    def _get_map_html(self, lat=None, lon=None):
        if lat is not None and lon is not None:
            view = f"[{lat}, {lon}]"
            zoom = 13
            marker_code = f'var marker = L.marker([{lat}, {lon}]).addTo(mymap); marker.bindPopup("<b>Przybliżona lokalizacja IP</b><br>Szer: {lat}<br>Dłg: {lon}").openPopup();'
            loading_text = "Ładowanie lokalizacji na mapie..."
        else:
            view = "[50, 10]"
            zoom = 4  # Widok na Europę
            marker_code = ""
            loading_text = "Ładowanie domyślnej mapy..."

        cdn_leaflet_css = (
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"
        )
        cdn_leaflet_js = (
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"
        )

        # Wersja HTML/CSS/JS zmodyfikowana dla lepszego dopasowania i kolorowej mapy
        return f"""
        <!DOCTYPE html>
        <html><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><title>Mapa IP</title>
            <link rel="stylesheet" href="{cdn_leaflet_css}"/>
            <script src="{cdn_leaflet_js}"
                onerror="console.error('*** KRYTYCZNY BŁĄD: Nie udało się załadować pliku leaflet.js z CDN: {cdn_leaflet_js}. ***');
                         var msgDiv = document.getElementById('message');
                         if(msgDiv) msgDiv.innerHTML = '<p>🗺️ KRYTYCZNY BŁĄD ładowania biblioteki mapy (plik JS nieosiągalny).</p>';
                         var mapDiv = document.getElementById('mapid'); if(mapDiv) mapDiv.style.display = 'none'; if(msgDiv) msgDiv.style.display = 'flex';"
            ></script>
            <style>
                html, body {{
                    height: 100%; width: 100%; /* body i html zajmują 100% viewportu QWebEngineView */
                    margin: 0; padding: 0;
                    background-color: #1e1e1e; /* Tło dla obszaru mapy, jeśli coś pójdzie nie tak */
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                    overflow: hidden; /* Zapobiega paskom przewijania na body */
                }}
                #map-container {{ /* Ten div obejmuje wszystko w body */
                    height: 100%; width: 100%;
                    display: flex;
                    flex-direction: column;
                }}
                #message {{
                    display: flex; /* Domyślnie widoczny komunikat */
                    justify-content: center; align-items: center;
                    flex-grow: 1; /* Zajmuje całą przestrzeń jeśli mapa jest ukryta */
                    text-align: center; font-size: 1.1em; padding: 10px; box-sizing: border-box;
                    background-color: #2b2b2b; /* Tło dla komunikatu */
                }}
                #mapid {{
                    display: none; /* Domyślnie mapa ukryta */
                    flex-grow: 1; /* Pozwól mapie rosnąć, aby wypełnić dostępną przestrzeń */
                    width: 100%;
                    background-color: #1e1e1e; /* Tło samej mapy zanim załadują się kafelki */
                }}
                .leaflet-popup-content-wrapper {{ background: #ffffff; color: #333333; border-radius: 5px; }}
                .leaflet-popup-tip-container {{ width: 40px; height: 20px; }}
                .leaflet-popup-tip {{ background: #ffffff; border: none; box-shadow: none; }}
                .leaflet-container a {{ color: #0078A8; }} /* Lepszy kolor linków w popupie */
            </style>
        </head><body>
            <div id="map-container">
                 <div id="message"><p>{loading_text}</p></div>
                 <div id="mapid"></div>
            </div>
            <script>
                function initMap() {{
                    var messageDiv = document.getElementById('message'); var mapDiv = document.getElementById('mapid');
                    try {{
                        messageDiv.style.display = 'none'; // Ukryj komunikat
                        mapDiv.style.display = 'block';  // Pokaż mapę (powinna się rozciągnąć dzięki flex-grow)

                        var mymap = L.map('mapid').setView({view}, {zoom});

                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ // KOLOROWA MAPA
                            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                            maxZoom: 19, minZoom: 2 // Ustawienie minZoom może być przydatne
                        }}).addTo(mymap);

                        {marker_code}
                        // Kluczowe: invalidateSize po chwili, aby mapa dostosowała się do rozmiaru kontenera
                        setTimeout(function() {{
                            console.log("Wywołuję mymap.invalidateSize()");
                            mymap.invalidateSize();
                        }}, 500); // Zwiększony timeout dla pewności
                    }} catch (error) {{
                        console.error('Błąd inicjalizacji mapy Leaflet (w bloku try...catch initMap):', error);
                        if (messageDiv && mapDiv) {{
                            messageDiv.innerHTML = '<p>🗺️ Wystąpił błąd podczas inicjalizacji mapy.</p>';
                            mapDiv.style.display = 'none'; messageDiv.style.display = 'flex';
                        }}
                    }}
                }}
                function tryInitMap(attemptsLeft = 25, delay = 400) {{ // Więcej prób, krótszy delay
                    var messageDiv = document.getElementById('message'); var mapDiv = document.getElementById('mapid');
                    if (typeof L !== 'undefined' && L.map) {{
                        console.log("Leaflet (L) jest załadowany i L.map istnieje. Inicjalizuję mapę.");
                        initMap();
                    }} else if (attemptsLeft > 0) {{
                        var attemptCount = 26 - attemptsLeft;
                        console.log(`Leaflet (L) lub L.map jeszcze nie załadowane. Próba ${{attemptCount}}/25 za ${{delay}}ms.`);
                        if (messageDiv) {{
                            messageDiv.innerHTML = `<p>Ładowanie biblioteki mapy... (próba ${{attemptCount}}/25)</p>`;
                            if(messageDiv.style.display !== 'flex') messageDiv.style.display = 'flex';
                            if(mapDiv && mapDiv.style.display !== 'none') mapDiv.style.display = 'none';
                        }}
                        setTimeout(function() {{ tryInitMap(attemptsLeft - 1, delay); }}, delay);
                    }} else {{
                        console.error('Nie udało się załadować Leaflet (L) lub L.map po wielu próbach.');
                        if (messageDiv && mapDiv) {{
                             messageDiv.innerHTML = '<p>🗺️ Błąd krytyczny: Nie można załadować biblioteki mapy po wielu próbach. Sprawdź połączenie internetowe i konsolę zdalnego debugowania (http://localhost:{os.environ.get("QTWEBENGINE_REMOTE_DEBUGGING", "PORT_NIEUSTAWIONY")}).</p>';
                             if(mapDiv.style.display !== 'none') mapDiv.style.display = 'none';
                             if(messageDiv.style.display !== 'flex') messageDiv.style.display = 'flex';
                        }}
                    }}
                }}
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log("DOMContentLoaded - rozpoczynam próby ładowania mapy.");
                    var messageDiv = document.getElementById('message');
                    var mapDiv = document.getElementById('mapid');
                    if (messageDiv) messageDiv.style.display = 'flex'; // Upewnij się, że komunikat jest widoczny
                    if (mapDiv) mapDiv.style.display = 'none';    // A mapa ukryta

                    setTimeout(function() {{ tryInitMap(); }}, 200); // Krótsze opóźnienie startowe
                }});
            </script>
        </body></html>"""

    def init_default_map(self):
        html = self._get_map_html()
        self.map_view.setHtml(
            html, QUrl("about:blank")
        )  # about:blank jest OK jako baseUrl dla prostego HTML

    def update_map(self, lat, lon):
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            print(f"Aktualizuję mapę: {lat_f}, {lon_f}")
            html = self._get_map_html(lat_f, lon_f)
            self.map_view.setHtml(html, QUrl("about:blank"))
        except ValueError as e:  # Błąd konwersji na float
            print(f"Błąd konwersji współrzędnych na float: {lat}, {lon} - {e}")
            self.show_fallback_map_message(
                f"Błąd formatu współrzędnych: {lat}, {lon}. Mapa domyślna."
            )
            self.init_default_map()  # Pokaż domyślną, jeśli współrzędne są złe
        except Exception as e:  # Inne błędy
            print(f"Błąd podczas aktualizacji mapy: {e}")
            self.show_fallback_map_message(f"Nie można zaktualizować mapy. Błąd: {e}")

    def check_ip(self):
        """Metoda wywoływana po kliknięciu przycisku sprawdzenia IP"""
        if self.checking_in_progress:
            return

        self.checking_in_progress = True
        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.ip_checker = IPCheckerThread(self)
        self.ip_checker.finished.connect(self.show_results)
        self.ip_checker.error.connect(self.show_error)
        self.ip_checker.progress.connect(self.update_progress)
        self.ip_checker.start()

    def update_progress(self, value):
        """Aktualizuje wartość progress bar"""
        self.progress_bar.setValue(value)

    def show_results(self, data):
        """Metoda wyświetlająca wyniki"""
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.checking_in_progress = False
        self.result_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ip = data.get("ip", "Nieznany")
        loc_error = data.get(
            "error_loc"
        )  # Sprawdź, czy był błąd pobierania lokalizacji

        text_parts = [
            f"================================",
            f"Adres IP: {ip}",
            f"================================",
        ]
        if loc_error:
            text_parts.append(f"\n⚠️ Lokalizacja: {loc_error}")
        else:
            text_parts.extend(
                [
                    f"\n📍 Lokalizacja:",
                    f"   Kraj: {data.get('country', 'N/A')}",
                    f"   Region: {data.get('region', 'N/A')}",
                    f"   Miasto: {data.get('city', 'N/A')}",
                    f"   Kod pocztowy: {data.get('postal', 'N/A')}",
                    f"\n🕒 Strefa czasowa: {data.get('timezone', 'N/A')}",
                    f"\n🌐 Dostawca (ISP/ORG): {data.get('org', 'N/A')}",
                ]
            )

        self.result_text.setText("\n".join(text_parts))

        if "loc" in data and not loc_error:
            try:
                lat, lon = data["loc"].split(",")
                self.update_map(lat, lon)
            except ValueError:
                self.result_text.append("\n\n⚠️ Błąd formatu współrzędnych lokalizacji.")
                self.init_default_map()  # Pokaż domyślną mapę
        else:  # Jeśli nie ma 'loc' lub był błąd lokalizacji
            self.init_default_map()

        self.check_button.setEnabled(True)
        # Historia
        entry_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
        }
        for key in ["city", "country", "region", "postal", "timezone", "org", "loc"]:
            if key in data:
                entry_data[key] = data[key]
        self.history.append(entry_data)
        self.save_history()
        self.display_history()
        # self.highlighter.set_ip_color(ip); self.highlighter.rehighlight() # Już w display_history

    def show_error(self, error_msg):
        self.result_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_text.setText(f"❌ Błąd wątku: {error_msg}")
        self.check_button.setEnabled(True)
        self.init_default_map()

    def show_fallback_map_message(self, message="Mapa tymczasowo niedostępna."):
        fallback_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <style>html,body{{height:100%;margin:0;padding:0;display:flex;justify-content:center;align-items:center;background-color:#2b2b2b;color:#fff;font-family:Arial,sans-serif;text-align:center;}}
        .container{{background-color:#1e1e1e;padding:20px 30px;border-radius:8px;border:1px solid #3d3d3d;}}</style></head><body>
        <div class="container"><h3>🗺️ Informacja o mapie</h3><p>{message}</p></div></body></html>"""
        self.map_view.setHtml(fallback_html, QUrl("about:blank"))


if __name__ == "__main__":
    debug_port = "8081"
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = debug_port
    print(f"--- ZDALNE DEBUGOWANIE QWebEngineView ---")
    print(f"Otwórz w przeglądarce Chrome/Edge: http://localhost:{debug_port}")
    print(f"--- Koniec instrukcji debugowania ---\n")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
