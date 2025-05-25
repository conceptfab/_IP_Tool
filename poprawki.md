Zmiany w pliku ip_checker_gui.py
1. Modyfikacja funkcji init_default_map
Lokalizacja: klasa MainWindow, funkcja init_default_map
Proponowany kod do zmiany:
pythondef init_default_map(self):
    """Inicjalizuje domyślną mapę świata."""
    default_map_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mapa IP</title>
        <!-- Użyj CDN bez integrity checks dla lepszej kompatybilności -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
            crossorigin="" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #2b2b2b;
                font-family: Arial, sans-serif;
            }
            #mapid {
                height: 100vh;
                width: 100%;
            }
            .loading {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #ffffff;
                background-color: #2b2b2b;
            }
            .error-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #ffffff;
                background-color: #2b2b2b;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div id="loading" class="loading">Ładowanie mapy...</div>
        <div id="mapid" style="display:none;"></div>
        <div id="error" class="error-container" style="display:none;">
            <div>
                <h3>🗺️ Mapa niedostępna</h3>
                <p>Sprawdź połączenie internetowe<br>lub spróbuj ponownie później</p>
            </div>
        </div>
        
        <script>
            // Sprawdź czy Leaflet się załadował
            function initMap() {
                if (typeof L === 'undefined') {
                    console.error('Leaflet nie załadował się poprawnie');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'flex';
                    return;
                }
                
                try {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mapid').style.display = 'block';
                    
                    var mymap = L.map('mapid').setView([52.2297, 21.0122], 6); // Warszawa jako domyślna
                    
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 18,
                    }).addTo(mymap);
                    
                    // Dostosuj rozmiar mapy po załadowaniu
                    setTimeout(function() {
                        mymap.invalidateSize();
                    }, 200);
                    
                } catch (error) {
                    console.error('Błąd inicjalizacji mapy:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'flex';
                }
            }
            
            // Spróbuj załadować mapę po załadowaniu strony
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(initMap, 1000);
                });
            } else {
                setTimeout(initMap, 1000);
            }
        </script>
    </body>
    </html>
    """
    self.map_view.setHtml(default_map_html)
2. Modyfikacja funkcji update_map
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
            <!-- Użyj unpkg.com bez integrity checks -->
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                crossorigin="" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
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
                .loading {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    color: #ffffff;
                    background-color: #2b2b2b;
                }}
                .error-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    color: #ffffff;
                    background-color: #2b2b2b;
                    text-align: center;
                }}
                .leaflet-popup-content {{
                    color: #000000;
                }}
            </style>
        </head>
        <body>
            <div id="loading" class="loading">Ładowanie lokalizacji...</div>
            <div id="mapid" style="display:none;"></div>
            <div id="error" class="error-container" style="display:none;">
                <div>
                    <h3>🗺️ Błąd ładowania mapy</h3>
                    <p>Nie można załadować interaktywnej mapy</p>
                </div>
            </div>
            
            <script>
                function initLocationMap() {{
                    if (typeof L === 'undefined') {{
                        console.error('Leaflet nie załadował się poprawnie');
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('error').style.display = 'flex';
                        return;
                    }}
                    
                    try {{
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('mapid').style.display = 'block';
                        
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
                        }}, 200);
                        
                    }} catch (error) {{
                        console.error('Błąd ładowania mapy:', error);
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('error').style.display = 'flex';
                    }}
                }}
                
                // Inicjalizuj mapę po załadowaniu - zwiększony timeout
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout(initLocationMap, 1000);
                    }});
                }} else {{
                    setTimeout(initLocationMap, 1000);
                }}
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
3. Alternatywne rozwiązanie - lokalne pliki Leaflet
Lokalizacja: można dodać jako nową metodę w klasie MainWindow
Proponowany kod do dodania:
pythondef get_leaflet_local_html(self, lat=None, lon=None):
    """Zwraca HTML z lokalnie hostowanymi plikami Leaflet lub alternatywnym CDN."""
    coords = f"[{lat}, {lon}]" if lat and lon else "[52.2297, 21.0122]"
    zoom = 13 if lat and lon else 6
    marker_code = f"""
        var marker = L.marker([{lat}, {lon}]).addTo(mymap);
        marker.bindPopup("<b>Twoja lokalizacja IP</b><br>Szerokość: {lat}<br>Długość: {lon}").openPopup();
    """ if lat and lon else ""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mapa IP</title>
        <!-- Fallback do innego CDN jeśli pierwszy nie działa -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
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
            .loading {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #ffffff;
                background-color: #2b2b2b;
            }}
            .leaflet-popup-content {{
                color: #000000;
            }}
        </style>
    </head>
    <body>
        <div id="loading" class="loading">Ładowanie mapy...</div>
        <div id="mapid" style="display:none;"></div>
        
        <script>
            setTimeout(function() {{
                if (typeof L !== 'undefined') {{
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mapid').style.display = 'block';
                    
                    var mymap = L.map('mapid').setView({coords}, {zoom});
                    
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '&copy; OpenStreetMap contributors',
                        maxZoom: 18,
                    }}).addTo(mymap);
                    
                    {marker_code}
                    
                    setTimeout(function() {{
                        mymap.invalidateSize();
                    }}, 300);
                }} else {{
                    document.getElementById('loading').innerHTML = 
                        '<div style="text-align:center;"><h3>🗺️ Błąd ładowania</h3><p>Biblioteka mapy niedostępna</p></div>';
                }}
            }}, 1500);
        </script>
    </body>
    </html>
    """
Podsumowanie głównych zmian:

Usunięcie integrity checks - usunięte atrybuty integrity i sha512 które powodowały blokowanie zasobów
Zmiana CDN - powrót do unpkg.com który jest bardziej niezawodny dla Leaflet
Zwiększone timeouty - z 300-500ms na 1000ms dla lepszego ładowania
Lepsze error handling - dodanie kontenerów błędów w obu funkcjach
Alternatywne CDN - dodanie opcji użycia jsdelivr.net jako backup

Te zmiany powinny rozwiązać problem z integrity hashes i umożliwić poprawne ładowanie biblioteki Leaflet.