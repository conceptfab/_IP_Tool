Zmiany w pliku ip_checker_gui.py
1. Modyfikacja inicjalizacji mapy w konstruktorze MainWindow
Lokalizacja: klasa MainWindow, funkcja __init__
Proponowany kod do zmiany:
python# Prawa strona - mapa
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
self.map_view.setStyleSheet("""
    QWebEngineView {
        background-color: #2b2b2b;
        border: 1px solid #3d3d3d;
        border-radius: 5px;
    }
""")
right_layout.addWidget(self.map_view)

# Dodaj prawą stronę do głównego layoutu - zwiększ stretch dla lepszego dopasowania
main_layout.addWidget(right_widget, stretch=4)  # Zwiększono z 3 do 4
2. Całkowita przebudowa funkcji update_map
Lokalizacja: klasa MainWindow, funkcja update_map
Proponowany kod do zmiany:
pythondef update_map(self, lat, lon):
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
3. Modyfikacja funkcji show_fallback_map
Lokalizacja: klasa MainWindow, funkcja show_fallback_map
Proponowany kod do zmiany:
pythondef show_fallback_map(self, lat, lon):
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
4. Dodanie inicjalizacji domyślnej mapy w konstruktorze
Lokalizacja: klasa MainWindow, funkcja __init__ (na końcu konstruktora)
Proponowany kod do dodania:
python# Na końcu konstruktora __init__, przed display_history()
self.init_default_map()

# Wyświetl wczytaną historię
self.display_history()
5. Dodanie nowej funkcji inicjalizacji domyślnej mapy
Lokalizacja: klasa MainWindow - nowa metoda
Proponowany kod do dodania:
pythondef init_default_map(self):
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
6. Usunięcie niepotrzebnych funkcji i zmiennych
Lokalizacja: klasa MainWindow
Proponowane zmiany:

Usuń funkcję get_location_info (nie jest już potrzebna)
W konstruktorze usuń linię: self.map_label = QLabel() i wszystkie związane z nią style

7. Dodanie responsywności dla różnych rozmiarów okna
Lokalizacja: klasa MainWindow, funkcja __init__
Proponowany kod do zmiany (główny splitter):
python# Główny widget i layout - zwiększ minimalny rozmiar
main_widget = QWidget()
self.setCentralWidget(main_widget)
main_layout = QHBoxLayout(main_widget)
main_layout.setSpacing(15)
main_layout.setContentsMargins(20, 20, 20, 20)

# Ustawienia proporcji - lewa strona 2, prawa strona 4
main_layout.addWidget(left_widget, stretch=2)
main_layout.addWidget(right_widget, stretch=4)
Podsumowanie zmian

Zamiana statycznej bitmapy na interaktywną mapę - używa biblioteki Leaflet.js przez QWebEngineView
Dodanie możliwości skalowania i przesuwania - pełna funkcjonalność interaktywnej mapy
Lepsze dopasowanie do rozmiaru okna - mapa automatycznie dopasowuje się do prawej kolumny
Domyślna mapa na starcie - wyświetla mapę Polski przed pierwszym sprawdzeniem IP
Ulepszony fallback - lepiej wyglądająca strona błędu w formacie HTML
Responsywny design - mapa dostosowuje się do zmiany rozmiaru okna

Te zmiany sprawią, że mapa będzie w pełni interaktywna, podobnie jak na stronach internetowych, z możliwością przybliżania, oddalania i przesuwania.