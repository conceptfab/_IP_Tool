import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests
from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class IPHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip_colors = defaultdict(lambda: QColor(255, 255, 255))  # Domyślny kolor
        self.color_index = 0
        self.colors = [
            QColor(255, 200, 200),  # Jasny czerwony
            QColor(200, 255, 200),  # Jasny zielony
            QColor(200, 200, 255),  # Jasny niebieski
            QColor(255, 255, 200),  # Jasny żółty
            QColor(255, 200, 255),  # Jasny fioletowy
            QColor(200, 255, 255),  # Jasny cyjan
        ]

    def set_ip_color(self, ip):
        if ip not in self.ip_colors:
            self.ip_colors[ip] = self.colors[self.color_index]
            self.color_index = (self.color_index + 1) % len(self.colors)

    def highlightBlock(self, text):
        for ip, color in self.ip_colors.items():
            format = QTextCharFormat()
            format.setBackground(color)
            format.setForeground(
                QColor(0, 0, 0)
            )  # Czarny tekst dla lepszej czytelności

            # Szukamy IP w tekście
            index = text.find(ip)
            while index >= 0:
                self.setFormat(index, len(ip), format)
                index = text.find(ip, index + 1)


class IPCheckerThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def run(self):
        try:
            # Pobieranie IP z większą odpornością na błędy
            ip_services = [
                ("https://api.ipify.org?format=json", "json"),
                ("https://ifconfig.me/ip", "text"),
                ("https://icanhazip.com", "text"),
                ("https://ident.me", "text"),
                ("https://api.myip.com", "json"),
            ]

            ip = None
            for service, response_type in ip_services:
                try:
                    print(f"Próba połączenia z {service}...")
                    response = requests.get(service, timeout=8)
                    if response.status_code == 200:
                        if response_type == "json":
                            data = response.json()
                            ip = data.get("ip") or data.get("query")
                        else:
                            ip = response.text.strip()

                        if ip:
                            print(f"Pobrano IP: {ip}")
                            break
                except Exception as e:
                    print(f"Błąd z {service}: {e}")
                    continue

            if not ip:
                self.error.emit("Nie udało się pobrać adresu IP z żadnego serwisu")
                return

            # Pobieranie informacji o IP z większą odpornością
            info_services = [
                f"https://ipinfo.io/{ip}/json",
                f"https://ipapi.co/{ip}/json/",
                f"https://ip-api.com/json/{ip}",
            ]

            for service in info_services:
                try:
                    print(f"Pobieranie informacji z {service}...")
                    response = requests.get(service, timeout=8)
                    if response.status_code == 200:
                        data = response.json()
                        # Normalizuj dane z różnych serwisów
                        normalized_data = self.normalize_ip_data(data, ip)
                        self.finished.emit(normalized_data)
                        return
                except Exception as e:
                    print(f"Błąd z {service}: {e}")
                    continue

            self.error.emit("Nie udało się pobrać informacji o IP")
        except Exception as e:
            self.error.emit(f"Wystąpił błąd: {str(e)}")

    def normalize_ip_data(self, data, ip):
        """Normalizuje dane z różnych serwisów IP."""
        normalized = {"ip": ip}

        # Mapowanie pól z różnych serwisów
        field_mappings = {
            "country": ["country", "country_name", "countryCode"],
            "region": ["region", "region_name", "regionName"],
            "city": ["city", "city_name"],
            "postal": ["postal", "zip"],
            "timezone": ["timezone", "time_zone"],
            "org": ["org", "isp", "as"],
            "loc": ["loc"],
        }

        for standard_field, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in data and data[field]:
                    normalized[standard_field] = data[field]
                    break

        # Specjalna obsługa dla loc (niektóre serwisy używają lat,lon oddzielnie)
        if "loc" not in normalized:
            if "lat" in data and "lon" in data:
                normalized["loc"] = f"{data['lat']},{data['lon']}"
            elif "latitude" in data and "longitude" in data:
                normalized["loc"] = f"{data['latitude']},{data['longitude']}"

        return normalized


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprawdzacz IP")
        self.setMinimumSize(1200, 800)
        self.history = []
        self.highlighter = None
        self.history_file = Path("ip_history.json")

        # Wczytaj historię
        self.load_history()

        # Ustawienie ciemnego schematu
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QSplitter::handle {
                background-color: #3d3d3d;
            }
            QLabel#mapLabel {
                background-color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
        """
        )

        # Główny widget i layout - zwiększ minimalny rozmiar
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Lewa strona - informacje i historia
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # Tytuł
        title = QLabel("Sprawdzacz Adresu IP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        left_layout.addWidget(title)

        # Przycisk sprawdzania
        self.check_button = QPushButton("Sprawdź mój adres IP")
        self.check_button.clicked.connect(self.check_ip)
        left_layout.addWidget(self.check_button)

        # Splitter dla wyników i historii
        splitter = QSplitter(Qt.Orientation.Vertical)
        left_layout.addWidget(splitter)

        # Górna część - wyniki
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        results_layout.addWidget(self.result_text)

        # Dolna część - historia
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_title = QLabel("Historia sprawdzeń")
        history_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-bottom: 10px;"
        )
        history_layout.addWidget(history_title)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        history_layout.addWidget(self.history_text)

        # Inicjalizacja highlightera
        self.highlighter = IPHighlighter(self.history_text.document())

        # Dodaj widgety do splittera
        splitter.addWidget(results_widget)
        splitter.addWidget(history_widget)
        splitter.setSizes([400, 200])

        # Dodaj lewą stronę do głównego layoutu
        main_layout.addWidget(left_widget, stretch=2)

        # Prawa strona - mapa
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # Tytuł mapy
        map_title = QLabel("Mapa lokalizacji")
        map_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-bottom: 10px;"
        )
        right_layout.addWidget(map_title)

        # Interaktywna mapa zamiast statycznego QLabel
        self.map_view = QWebEngineView()
        self.map_view.setMinimumSize(400, 400)
        self.map_view.setStyleSheet(
            """
            QWebEngineView {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
        """
        )
        right_layout.addWidget(self.map_view)

        # Dodaj prawą stronę do głównego layoutu - zwiększ stretch dla lepszego dopasowania
        main_layout.addWidget(right_widget, stretch=4)

        # Inicjalizacja domyślnej mapy
        self.init_default_map()

        # Wyświetl wczytaną historię
        self.display_history()

    def load_history(self):
        """Wczytuje historię z pliku JSON."""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Błąd wczytywania historii: {e}")
            self.history = []

    def save_history(self):
        """Zapisuje historię do pliku JSON."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Błąd zapisywania historii: {e}")

    def display_history(self):
        """Wyświetla historię w interfejsie."""
        self.history_text.clear()
        for entry in self.history:
            self.history_text.append(
                f"[{entry['timestamp']}] {entry['ip']} - "
                f"{entry['city']}, {entry['country']}\n"
            )
            # Ustaw kolor dla IP
            self.highlighter.set_ip_color(entry["ip"])

    def init_default_map(self):
        """Inicjalizuje domyślną mapę świata."""
        default_map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mapa IP</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
                crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
                integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
                crossorigin=""></script>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background-color: #2b2b2b;
                }
                #mapid {
                    height: 100vh;
                    width: 100%;
                }
            </style>
        </head>
        <body>
            <div id="mapid"></div>
            <script>
                var mymap = L.map('mapid').setView([52.2297, 21.0122], 6); // Warszawa jako domyślna
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    maxZoom: 18,
                }).addTo(mymap);
                
                setTimeout(function() {
                    mymap.invalidateSize();
                }, 100);
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(default_map_html)

    def update_map(self, lat, lon):
        """Aktualizuje mapę z nowymi współrzędnymi."""
        try:
            # Stwórz interaktywną mapę HTML z OpenStreetMap
            map_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Mapa IP</title>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
                    crossorigin=""/>
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
                    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
                    crossorigin=""></script>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #2b2b2b;
                    }}
                    #mapid {{
                        height: 100vh;
                        width: 100%;
                    }}
                    .leaflet-control-container .leaflet-routing-container-hide {{
                        display: none;
                    }}
                </style>
            </head>
            <body>
                <div id="mapid"></div>
                <script>
                    var mymap = L.map('mapid').setView([{lat}, {lon}], 13);
                    
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 18,
                    }}).addTo(mymap);
                    
                    var marker = L.marker([{lat}, {lon}]).addTo(mymap);
                    marker.bindPopup("<b>Twoja lokalizacja IP</b><br>Szerokość: {lat}<br>Długość: {lon}").openPopup();
                    
                    // Dostosuj rozmiar mapy po załadowaniu
                    setTimeout(function() {{
                        mymap.invalidateSize();
                    }}, 100);
                </script>
            </body>
            </html>
            """

            # Załaduj mapę HTML do QWebEngineView
            self.map_view.setHtml(map_html)
            print("Interaktywna mapa załadowana pomyślnie")

        except Exception as e:
            error_msg = f"Błąd podczas ładowania mapy: {str(e)}"
            print(error_msg)
            self.show_fallback_map(lat, lon)

    def check_ip(self):
        self.check_button.setEnabled(False)
        self.result_text.clear()

        self.thread = IPCheckerThread()
        self.thread.finished.connect(self.show_results)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def show_results(self, data):
        result = f"""Twój adres IP: {data.get('ip', 'Nieznany')}

Kraj: {data.get('country', 'Nieznany')}
Region: {data.get('region', 'Nieznany')}
Miasto: {data.get('city', 'Nieznane')}
Kod pocztowy: {data.get('postal', 'Nieznany')}
Strefa czasowa: {data.get('timezone', 'Nieznana')}
ISP: {data.get('org', 'Nieznany')}"""

        if "loc" in data:
            lat, lon = data["loc"].split(",")
            result += (
                f"\n\nWspółrzędne geograficzne:\nSzerokość: {lat}\n" f"Długość: {lon}"
            )
            result += f"\n\nLink do mapy:\nhttps://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
            # Aktualizuj mapę
            self.update_map(lat, lon)

        self.result_text.setText(result)
        self.check_button.setEnabled(True)

        # Dodanie do historii
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": data.get("ip", "Nieznany"),
            "city": data.get("city", "Nieznane"),
            "country": data.get("country", "Nieznany"),
            "region": data.get("region", "Nieznany"),
            "postal": data.get("postal", "Nieznany"),
            "timezone": data.get("timezone", "Nieznana"),
            "org": data.get("org", "Nieznany"),
        }
        self.history.append(history_entry)
        self.save_history()

        # Wyświetl nowy wpis w historii
        self.history_text.append(
            f"[{history_entry['timestamp']}] {history_entry['ip']} - "
            f"{history_entry['city']}, {history_entry['country']}\n"
        )

        # Ustaw kolor dla IP
        if "ip" in data:
            self.highlighter.set_ip_color(data["ip"])

    def show_error(self, error_msg):
        self.result_text.setText(f"Błąd: {error_msg}")
        self.check_button.setEnabled(True)

    def show_fallback_map(self, lat, lon):
        """Wyświetla zastępczą mapę gdy nie można pobrać interaktywnej mapy."""
        fallback_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #2b2b2b;
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    text-align: center;
                }}
                .fallback-container {{
                    background-color: #1e1e1e;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 40px;
                    max-width: 300px;
                }}
                .coordinates {{
                    font-size: 16px;
                    margin: 20px 0;
                }}
                .link {{
                    color: #0d47a1;
                    text-decoration: none;
                    font-size: 14px;
                }}
                .link:hover {{
                    text-decoration: underline;
                }}
                h3 {{
                    color: #ffffff;
                    margin-top: 0;
                }}
            </style>
        </head>
        <body>
            <div class="fallback-container">
                <h3>📍 Lokalizacja</h3>
                <div class="coordinates">
                    <strong>Szerokość:</strong> {lat}<br>
                    <strong>Długość:</strong> {lon}
                </div>
                <p>Mapa niedostępna<br>
                Sprawdź połączenie internetowe</p>
                <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}" 
                   class="link" target="_blank">
                   🗺️ Otwórz w OpenStreetMap
                </a>
            </div>
        </body>
        </html>
        """

        self.map_view.setHtml(fallback_html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
