Zmiany w pliku ip_checker_gui.py
1. Funkcja update_map - naprawa błędów sieci i zarządzania plikami
Lokalizacja: klasa MainWindow, funkcja update_map
Proponowany kod do zmiany:
pythondef update_map(self, lat, lon):
    """Aktualizuje mapę z nowymi współrzędnymi."""
    temp_path = Path("temp_map.png")  # Zdefiniuj na początku
    
    try:
        # Lista alternatywnych serwisów map statycznych
        map_services = [
            f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-s+red({lon},{lat})/{lon},{lat},14,0/400x400?access_token=YOUR_TOKEN",
            f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=14&size=400x400&markers=color:red|{lat},{lon}&key=YOUR_API_KEY",
            f"https://tile.openstreetmap.org/{14}/{int((float(lon) + 180) * 2**14 / 360)}/{int((1 - math.log(math.tan(math.radians(float(lat))) + 1 / math.cos(math.radians(float(lat)))) / math.pi) / 2 * 2**14)}.png"
        ]
        
        # Spróbuj z prostym obrazem zastępczym jako fallback
        fallback_map_html = f"""
        <html>
        <body style="margin:0; padding:0; background:#2b2b2b;">
            <div style="width:400px; height:400px; background:#1e1e1e; border:1px solid #3d3d3d; 
                        display:flex; flex-direction:column; justify-content:center; align-items:center; 
                        color:#ffffff; font-family:Arial;">
                <h3>Lokalizacja</h3>
                <p>Szerokość: {lat}</p>
                <p>Długość: {lon}</p>
                <p style="font-size:12px; color:#aaa;">Mapa niedostępna</p>
                <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}" 
                   style="color:#0d47a1; text-decoration:none;">
                   Otwórz w OpenStreetMap
                </a>
            </div>
        </body>
        </html>
        """
        
        # Spróbuj pobrać mapę z OpenStreetMap Tile Server (alternatywne podejście)
        zoom = 14
        x = int((float(lon) + 180.0) / 360.0 * (1 << zoom))
        y = int((1.0 - math.asinh(math.tan(math.radians(float(lat)))) / math.pi) / 2.0 * (1 << zoom))
        
        tile_url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
        
        print(f"Próba pobrania kafelka mapy z URL: {tile_url}")
        response = requests.get(
            tile_url, 
            headers={"User-Agent": "IP_Checker/1.0"}, 
            timeout=10
        )

        if response.status_code == 200:
            # Zapisz obraz tymczasowo
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Wyświetl obraz
            pixmap = QPixmap(str(temp_path))
            if not pixmap.isNull():
                # Przeskaluj obraz do 400x400
                scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
                self.map_label.setPixmap(scaled_pixmap)
                print("Mapa załadowana pomyślnie")
            else:
                self.show_fallback_map(lat, lon)
        else:
            print(f"Nie udało się pobrać kafelka mapy (HTTP {response.status_code})")
            self.show_fallback_map(lat, lon)

        # Pobierz informacje o lokalizacji
        self.get_location_info(lat, lon)
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Błąd sieci: {str(e)}"
        print(error_msg)
        self.show_fallback_map(lat, lon)
    except Exception as e:
        error_msg = f"Błąd podczas ładowania mapy: {str(e)}"
        print(error_msg)
        self.show_fallback_map(lat, lon)
    finally:
        # Spróbuj usunąć tymczasowy plik
        try:
            if temp_path.exists():
                temp_path.unlink()
                print("Tymczasowy plik mapy usunięty")
        except Exception as e:
            print(f"Nie udało się usunąć tymczasowego pliku: {e}")
2. Dodanie funkcji pomocniczych
Lokalizacja: klasa MainWindow - nowe metody
Proponowany kod do dodania:
pythondef show_fallback_map(self, lat, lon):
    """Wyświetla zastępczą mapę gdy nie można pobrać obrazu."""
    fallback_text = f"""Lokalizacja:
    
Szerokość: {lat}
Długość: {lon}

Mapa niedostępna
Sprawdź połączenie internetowe

Otwórz w przeglądarce:
https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"""
    
    self.map_label.setText(fallback_text)
    self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.map_label.setStyleSheet("""
        QLabel {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            padding: 20px;
            font-size: 12px;
        }
    """)

def get_location_info(self, lat, lon):
    """Pobiera dodatkowe informacje o lokalizacji."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        response = requests.get(
            url, 
            headers={"User-Agent": "IP_Checker/1.0"}, 
            timeout=5
        )
        if response.status_code == 200:
            location_data = response.json()
            display_name = location_data.get("display_name", "Nieznana lokalizacja")
            print(f"Szczegółowa lokalizacja: {display_name}")
        else:
            print(f"Nie udało się pobrać szczegółów lokalizacji (HTTP {response.status_code})")
    except Exception as e:
        print(f"Błąd przy pobieraniu informacji o lokalizacji: {e}")
3. Dodanie importu dla math
Lokalizacja: początek pliku ip_checker_gui.py
Proponowany kod do dodania:
pythonimport math  # Dodaj ten import na górze pliku
4. Ulepszenie obsługi błędów w wątku
Lokalizacja: klasa IPCheckerThread, funkcja run
Proponowany kod do zmiany:
pythondef run(self):
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
        "loc": ["loc"]
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
Podsumowanie zmian

Naprawa zarządzania plikami tymczasowymi - zdefiniowanie temp_path na początku funkcji
Dodanie alternatywnych źródeł map - użycie kafelków OpenStreetMap zamiast niefunkcjonującego serwisu
Lepsza obsługa błędów sieci - dodanie fallback'u gdy mapa nie może być załadowana
Zwiększenie odporności - dodanie większej liczby serwisów IP i normalizacja danych
Dodanie brakującego importu math - potrzebnego do obliczeń współrzędnych kafelków

Te zmiany powinny rozwiązać problemy z pobieraniem map i uczynić aplikację bardziej odporną na błędy sieci.