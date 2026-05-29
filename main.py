import os
import sys
import ctypes
import random
import time
import shutil
import json
from datetime import datetime

# =======================================================================
# CONFIGURATION & CONSTANTS (Definicje flag API Windows Kernel32)
# =======================================================================
# Modyfikacja zachowania systemu plików za pomocą masek bitowych:
# 0x01 (FILE_ATTRIBUTE_READONLY) - Blokada zapisu i modyfikacji zawartości.
# 0x02 (FILE_ATTRIBUTE_HIDDEN)   - Ukrycie obiektu w strukturze eksploratora.
FILE_ATTRIBUTE_READONLY = 0x01
FILE_ATTRIBUTE_HIDDEN = 0x02

# Rejestr zdarzeń telemetrycznych (struktura danych dla modułu Forensics)
presentation_logs = []


def log_event(phase, message):
    """🕵️ Zapisuje zdarzenie telemetryczne z dokładną sygnaturą czasową."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    presentation_logs.append({
        "timestamp": timestamp,
        "phase": phase,
        "status": message
    })


def print_progress_bar(duration, text):
    """🎬 Wizualizacja postępu procesów systemowych w konsoli."""
    print(f"{text}", end="", flush=True)
    steps = 20
    for _ in range(steps):
        time.sleep(duration / steps)
        print("█", end="", flush=True)
    print(" [GOTOWE]")


def alter_file_restriction(file_path, enable_restriction=True):
    """🔒 Manipulacja atrybutami pliku za pomocą interfejsu programistycznego systemu Windows."""
    try:
        attributes = ctypes.windll.kernel32.GetFileAttributesW(file_path)
        if attributes == -1:
            return False

        if enable_restriction:
            # Nakładanie restrykcji przy użyciu operacji bitowej OR
            new_attributes = attributes | FILE_ATTRIBUTE_READONLY | FILE_ATTRIBUTE_HIDDEN
        else:
            # Zdejmowanie restrykcji przy użyciu operacji bitowej AND NOT
            new_attributes = attributes & ~FILE_ATTRIBUTE_READONLY & ~FILE_ATTRIBUTE_HIDDEN

        return bool(ctypes.windll.kernel32.SetFileAttributesW(file_path, new_attributes))
    except:
        return False


def main():
    # =======================================================================
    # FAZA 1: INICJALIZACJA ŚRODOWISKA TESTOWEGO (Izolowane środowisko PoC)
    # =======================================================================
    demo_folder = os.path.join(os.getcwd(), "PoC_Demo_Folder")
    backup_folder = os.path.join(os.getcwd(), "Security_Backup")

    if not os.path.exists(demo_folder):
        os.makedirs(demo_folder)
        with open(os.path.join(demo_folder, "baza_danych_klientow.txt"), "w", encoding="utf-8") as f:
            f.write("ID: 1 | Klient: Jan Kowalski | Status: OPLACONE\nID: 2 | Klient: Anna Nowak | Status: NIEOPLACONE")

    # Losowanie celu (symulacja procedury skanowania struktur katalogów przez malware)
    files = [f for f in os.listdir(demo_folder) if os.path.isfile(os.path.join(demo_folder, f))]
    if not files:
        print("[-] Brak plików w folderze laboratoryjnym.")
        sys.exit(1)

    selected_file = os.path.join(demo_folder, random.choice(files))
    file_name = os.path.basename(selected_file)

    print("=======================================================")
    print("      SYMULACJA INCYDENTU BEZPIECZEŃSTWA (PoC)        ")
    print("=======================================================")
    log_event("INITIALIZATION", f"Uruchomiono pokaz. Cel: {file_name}")
    time.sleep(1.0)

    # =======================================================================
    # FAZA 2: PROAKTYWNA OBRONA (Wdrożenie polityki tworzenia kopii zapasowych)
    # =======================================================================
    # Prewencyjne zabezpieczenie integralności danych przed wystąpieniem naruszenia
    print(f"\n[*] [DEFENSE] Detekcja krytycznych danych: {file_name}")
    print_progress_bar(1.0, "[*] [DEFENSE] Tworzenie bezpiecznej kopii zapasowej: ")

    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    shutil.copy(selected_file, os.path.join(backup_folder, f"backup_{file_name}"))
    log_event("DEFENSE_BACKUP", "Utworzono punkt przywracania danych (Backup).")
    time.sleep(0.5)

    # =======================================================================
    # FAZA 3: EXPLOITACJA & NARUSZENIE (Symulacja mechanizmu Ransomware)
    # =======================================================================
    # Wywołanie procedury blokady uprawnień modyfikacji oraz eskalacja atrybutu niewidoczności
    print("\n[!] [ATTACK] Wykryto podejrzaną aktywność w tle...")
    time.sleep(1.0)
    print_progress_bar(1.5, "[!] [ATTACK] Blokowanie i ukrywanie struktury plików: ")

    if alter_file_restriction(selected_file, enable_restriction=True):
        log_event("ATTACK_TRIGGERED", "Nałożono restrykcje pliku (Read-only + Hidden).")
        print("\n" + "=" * 55)
        print("   ALERT: TWOJE DANE ZOSTAŁY ZABLOKOWANE!   ")
        print("   W celu odzyskania wpłać 1000$ na podany adres. ")
        print("=" * 55)
    else:
        print("[-] Atak zablokowany przez systemy ochronne.")
        sys.exit(1)

    print("\n[!] System został zablokowany. Wprowadź klucz deszyfrujący, aby kontynuować.")

    # =======================================================================
    # FAZA 4: INTERAKCJA & UWIERZYTELNIANIE (Autoryzacja dostępu administracyjnego)
    # =======================================================================
    correct_password = "technischools"
    attempts = 3
    authenticated = False

    while attempts > 0:
        user_input = input(f"[Wpisz hasło (Pozostało prób: {attempts})]: ")

        if user_input == correct_password:
            authenticated = True
            log_event("AUTH_SUCCESS", "Podano prawidłowe hasło administratora.")
            break
        else:
            attempts -= 1
            log_event("AUTH_FAILED", f"Błędne hasło. Pozostało prób: {attempts}")
            print("[-] Niepoprawny klucz dostępu.\n")

    if not authenticated:
        print("\n[X] Przekroczono limit prób! System pozostaje zablokowany.")
        log_event("MITIGATION_FAILED", "Mitygacja przerwana - wyczerpano limit prób.")
        sys.exit(1)

    # =======================================================================
    # FAZA 5: MITYGACJA & INCIDENT RESPONSE (Procedura odzyskiwania systemu)
    # =======================================================================
    # Autoryzowane cofnięcie wprowadzonych zmian atrybutów pliku przez administratora
    print("\n[+] [MITIGATION] Klucz poprawny! Autoryzacja administratora...")
    print_progress_bar(1.5, "[+] [MITIGATION] Cofanie zmian i przywracanie praw:   ")

    if alter_file_restriction(selected_file, enable_restriction=False):
        log_event("MITIGATION_SUCCESS", "Przywrócono domyślne atrybuty pliku.")
        print("\n[+] [SUKCES] Integralność systemu przywrócona pomyślnie.")
    else:
        print("\n[-] Błąd podczas procedury automatycznej naprawy.")

    # =======================================================================
    # FAZA 6: CYFROWA DETEKTYWISTYKA (Generowanie raportu po-incydentowego)
    # =======================================================================
    # Eksport zebranych logów telemetrycznych do formatu JSON w celu analizy powłamaniowej
    time.sleep(1.0)
    print("\n[*] [FORENSICS] Generowanie powłamaniowego raportu zdarzeń...")
    log_file_path = os.path.join(os.getcwd(), "incident_report.json")

    with open(log_file_path, "w", encoding="utf-8") as lf:
        json.dump(presentation_logs, lf, indent=4, ensure_ascii=False)

    print(f"[+] Raport śledczy zapisany jako: {os.path.basename(log_file_path)}")
    print("\n=== KONIEC PREZENTACJI (SYSTEM JEST BEZPIECZNY) ===")


if __name__ == "__main__":
    main()