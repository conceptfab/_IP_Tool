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
        <!-- Użyj CDN z timeoutem i fallbackiem -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
            integrity="sha512-h9FcoyWjHcOcmEVkxOfTLIlnOeRDg2/RPEeCaFPv/OMT8w5qDNKkKNHVZi6YQIyzs6zp8CK8sJqwFCN2uP9/Q=="
            crossorigin="anonymous" referrerpolicy="no-referrer" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"
            integrity="sha512-BwHfrr4c9kmRkLw6iXFdzcdWV/PGkVgiIyIWLRWbaXzj9CdLI+9oq0OkOaSmaqeQ5w9Mv7FqYPdDfOEF4nf1sQ=="
            crossorigin="anonymous" referrerpolicy="no-referrer"></script>
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
                    setTimeout(initMap, 500);
                });
            } else {
                setTimeout(initMap, 500);
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
            <!-- Użyj CDN z większą niezawodnością -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
                integrity="sha512-h9FcoyWjHcOcmEVkxOfTLIlnOeRDg2/RPEeCaFPv/OMT8w5qDNKkKNHVZi6YQIyzs6zp8CK8sJqwFCN2uP9/Q=="
                crossorigin="anonymous" referrerpolicy="no-referrer" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"
                integrity="sha512-BwHfrr4c9kmRkLw6iXFdzcdWV/PGkVgiIyIWLRWbaXzj9CdLI+9oq0OkOaSmaqeQ5w9Mv7FqYPdDfOEF4nf1sQ=="
                crossorigin="anonymous" referrerpolicy="no-referrer"></script>
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
            <div id="loading" class="loading">Ładowanie lokalizacji...</div>
            <div id="mapid" style="display:none;"></div>
            
            <script>
                function initLocationMap() {{
                    if (typeof L === 'undefined') {{
                        console.error('Leaflet nie załadował się poprawnie');
                        document.getElementById('loading').innerHTML = '<div style="text-align:center;"><h3>🗺️ Mapa niedostępna</h3><p>Sprawdź połączenie internetowe</p></div>';
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
                        document.getElementById('loading').innerHTML = '<div style="text-align:center; color: #ffffff;"><h3>🗺️ Błąd mapy</h3><p>Nie można załadować lokalizacji</p></div>';
                    }}
                }}
                
                // Inicjalizuj mapę po załadowaniu
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout(initLocationMap, 300);
                    }});
                }} else {{
                    setTimeout(initLocationMap, 300);
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
3. Dodanie funkcji sprawdzania połączenia internetowego
Lokalizacja: klasa MainWindow - nowa metoda
Proponowany kod do dodania:
pythondef check_internet_connection(self):
    """Sprawdza dostępność połączenia internetowego."""
    try:
        response = requests.get('https://www.google.com', timeout=3)
        return response.status_code == 200
    except:
        return False
4. Modyfikacja funkcji show_fallback_map z lepszą diagnostyką
Lokalizacja: klasa MainWindow, funkcja show_fallback_map
Proponowany kod do zmiany:
pythondef show_fallback_map(self, lat, lon):
    """Wyświetla zastępczą mapę gdy nie można pobrać interaktywnej mapy."""
    internet_status = "✅ Połączenie OK" if self.check_internet_connection() else "❌ Brak połączenia"
    
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
                max-width: 350px;
            }}
            .coordinates {{
                font-size: 16px;
                margin: 20px 0;
                background-color: #2b2b2b;
                padding: 15px;
                border-radius: 5px;
            }}
            .link {{
                color: #0d47a1;
                text-decoration: none;
                font-size: 14px;
                background-color: #2b2b2b;
                padding: 10px 15px;
                border-radius: 5px;
                display: inline-block;
                margin-top: 15px;
            }}
            .link:hover {{
                background-color: #1565c0;
                color: #ffffff;
            }}
            h3 {{
                color: #ffffff;
                margin-top: 0;
            }}
            .status {{
                font-size: 12px;
                margin-top: 20px;
                opacity: 0.8;
            }}
        </style>
    </head>
    <body>
        <div class="fallback-container">
            <h3>📍 Lokalizacja IP</h3>
            <div class="coordinates">
                <strong>Szerokość:</strong> {lat}<br>
                <strong>Długość:</strong> {lon}
            </div>
            <p>Interaktywna mapa niedostępna<br>
            Możliwe przyczyny:<br>
            • Słabe połączenie internetowe<br>
            • Blokada JavaScript<br>
            • Problem z CDN</p>
            <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}" 
               class="link" target="_blank">
               🗺️ Otwórz w przeglądarce
            </a>
            <div class="status">Status: {internet_status}</div>
        </div>
    </body>
    </html>
    """
    
    self.map_view.setHtml(fallback_html)
5. Dodanie import requests na początku pliku (jeśli brakuje)
Lokalizacja: początek pliku ip_checker_gui.py
Sprawdź czy jest już zaimportowane, jeśli nie - dodaj:
pythonimport requests  # Dodaj jeśli nie ma
Podsumowanie głównych zmian:

Zmiana CDN - przejście z unpkg.com na cdnjs.cloudflare.com (bardziej niezawodne)
Dodanie diagnostyki - sprawdzanie czy Leaflet się załadował przed inicjalizacją
Lepsze error handling - wyświetlanie stosownych komunikatów o błędach
Dodanie opóźnień - danie czasu na załadowanie bibliotek przed inicjalizacją
Status połączenia - sprawdzanie dostępności internetu w fallback
Lepszy UX - wyświetlanie komunikatu "Ładowanie..." podczas inicjalizacji

Te zmiany powinny rozwiązać problem z L is not defined i uczynić mapę bardziej niezawodną.