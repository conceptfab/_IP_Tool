import requests


def get_ip_info(ip):
    try:
        # Używamy serwisu ipinfo.io do pobrania szczegółowych informacji
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Błąd przy pobieraniu informacji o IP: {str(e)}")
        return None


def get_public_ip():
    # Lista serwisów do sprawdzania IP
    ip_services = [
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://ident.me",
    ]

    for service in ip_services:
        try:
            print(f"Próba połączenia z {service}...")
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                if service.endswith("json"):
                    return response.json()["ip"]
                else:
                    return response.text.strip()
        except Exception as e:
            print(f"Błąd przy próbie połączenia z {service}: {str(e)}")
            continue

    return "Nie udało się pobrać adresu IP z żadnego serwisu"


def print_ip_info(ip_info):
    if not ip_info:
        print("Nie udało się pobrać szczegółowych informacji o IP")
        return

    print("\nSzczegółowe informacje o Twoim IP:")
    print("-" * 50)
    print(f"Kraj: {ip_info.get('country', 'Nieznany')}")
    print(f"Region: {ip_info.get('region', 'Nieznany')}")
    print(f"Miasto: {ip_info.get('city', 'Nieznane')}")
    print(f"Kod pocztowy: {ip_info.get('postal', 'Nieznany')}")
    print(f"Strefa czasowa: {ip_info.get('timezone', 'Nieznana')}")
    print(f"ISP: {ip_info.get('org', 'Nieznany')}")
    if "loc" in ip_info:
        lat, lon = ip_info["loc"].split(",")
        print(f"Szerokość geograficzna: {lat}")
        print(f"Długość geograficzna: {lon}")
        print(f"\nLink do mapy: https://www.google.com/maps?q={lat},{lon}")
    print("-" * 50)


if __name__ == "__main__":
    print("Sprawdzanie Twojego publicznego adresu IP...")
    ip = get_public_ip()
    print("Twój publiczny adres IP to:", ip)

    if ip and ip != "Nie udało się pobrać adresu IP z żadnego serwisu":
        print("\nPobieranie szczegółowych informacji...")
        ip_info = get_ip_info(ip)
        print_ip_info(ip_info)
