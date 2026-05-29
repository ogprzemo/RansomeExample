import os
import sys
import random
import time
import shutil
import json
import stat
from datetime import datetime

# =======================================================================
# CONFIGURATION & CONSTANTS (Linux / Ubuntu 22.04)
# =======================================================================
# Linux nie wykorzystuje atrybutów FILE_ATTRIBUTE_READONLY
# ani FILE_ATTRIBUTE_HIDDEN znanych z WinAPI.
#
# Mechanizmy stosowane w Ubuntu/Linux:
#
# 1. Ukrywanie plików
#    - Plik staje się ukryty po dodaniu prefiksu "."
#    - Przykład:
#          dokument.txt -> .dokument.txt
#
# 2. Ograniczenie modyfikacji
#    - Realizowane przy użyciu systemu uprawnień POSIX.
#    - Funkcja chmod() usuwa prawo zapisu,
#      ustawiając plik w tryb "read-only".
#
# 3. Zaawansowane zabezpieczenia (opcjonalne)
#    - Linux umożliwia użycie:
#          chattr +i
#      co ustawia flagę immutable:
#          - brak możliwości edycji,
#          - brak możliwości usunięcia,
#          - brak możliwości zmiany nazwy.
#
# 4. Mechanizmy wykorzystywane w PoC
#    - os.rename()   -> ukrywanie pliku
#    - os.chmod()    -> blokowanie zapisu
#    - shutil.copy() -> tworzenie kopii zapasowej
#
# =======================================================================
# TELEMETRY & FORENSICS
# =======================================================================
# presentation_logs:
# Rejestr zdarzeń telemetrycznych wykorzystywany przez:
#   - monitoring przebiegu demonstracji,
#   - analizę incydentu,
#   - generowanie raportu JSON.
#
presentation_logs = []


def log_event(phase, message):
    """
    🕵️ Rejestracja zdarzeń telemetrycznych.

    Każde zdarzenie otrzymuje:
        - dokładny timestamp,
        - nazwę fazy,
        - opis działania.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    presentation_logs.append({
        "timestamp": timestamp,
        "phase": phase,
        "status": message
    })


def print_progress_bar(duration, text):
    """
    🎬 Wizualizacja postępu operacji systemowych.
    """

    print(text, end="", flush=True)

    steps = 20

    for _ in range(steps):
        time.sleep(duration / steps)
        print("█", end="", flush=True)

    print(" [GOTOWE]")


def alter_file_restriction(file_path, enable_restriction=True):
    """
    🔒 Symulacja blokady pliku w środowisku Linux.

    enable_restriction=True:
        - zmiana nazwy pliku na ukrytą (.plik)
        - usunięcie prawa zapisu

    enable_restriction=False:
        - przywrócenie prawa zapisu
        - usunięcie prefiksu "."
    """

    try:

        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # ===============================================================
        # NAKŁADANIE RESTRYKCJI
        # ===============================================================
        if enable_restriction:

            hidden_name = "." + filename
            hidden_path = os.path.join(directory, hidden_name)

            # Ukrycie pliku
            os.rename(file_path, hidden_path)

            # Read-only
            os.chmod(hidden_path, stat.S_IREAD)

            return hidden_path

        # ===============================================================
        # ZDEJMOWANIE RESTRYKCJI
        # ===============================================================
        else:

            # Przywrócenie zapisu
            os.chmod(
                file_path,
                stat.S_IREAD | stat.S_IWRITE
            )

            current_name = os.path.basename(file_path)

            # Odkrycie pliku
            if current_name.startswith("."):
                restored_name = current_name[1:]
                restored_path = os.path.join(
                    directory,
                    restored_name
                )

                os.rename(file_path, restored_path)

                return restored_path

            return file_path

    except Exception as e:

        print(f"[-] Linux filesystem error: {e}")
        return None


def main():
    # ===================================================================
    # FAZA 1: INICJALIZACJA ŚRODOWISKA TESTOWEGO
    # ===================================================================
    # Tworzenie izolowanego katalogu laboratoryjnego PoC.
    #
    # PoC_Demo_Folder:
    #     folder demonstracyjny zawierający przykładowe dane.
    #
    # Security_Backup:
    #     lokalizacja kopii bezpieczeństwa.
    # ===================================================================

    demo_folder = os.path.join(
        os.getcwd(),
        "PoC_Demo_Folder"
    )

    backup_folder = os.path.join(
        os.getcwd(),
        "Security_Backup"
    )

    # Tworzenie folderu laboratoryjnego
    os.makedirs(demo_folder, exist_ok=True)

    sample_file = os.path.join(
        demo_folder,
        "baza_danych_klientow.txt"
    )

    # Generowanie przykładowych danych
    if not os.path.exists(sample_file):
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(
                "ID: 1 | Klient: Jan Kowalski | Status: OPLACONE\n"
                "ID: 2 | Klient: Anna Nowak | Status: NIEOPLACONE"
            )

    # ===================================================================
    # LOSOWANIE CELU
    # ===================================================================
    # Symulacja procesu skanowania katalogów przez malware.
    # ===================================================================

    files = [
        f for f in os.listdir(demo_folder)
        if os.path.isfile(os.path.join(demo_folder, f))
    ]

    if not files:
        print("[-] Brak plików laboratoryjnych.")
        sys.exit(1)

    selected_file = os.path.join(
        demo_folder,
        random.choice(files)
    )

    file_name = os.path.basename(selected_file)

    print("=======================================================")
    print("      SYMULACJA INCYDENTU BEZPIECZEŃSTWA (LINUX)       ")
    print("=======================================================")

    log_event(
        "INITIALIZATION",
        f"Wybrano cel: {file_name}"
    )

    time.sleep(1)

    # ===================================================================
    # FAZA 2: BACKUP / OBRONA PROAKTYWNA
    # ===================================================================
    # Tworzenie kopii bezpieczeństwa przed wystąpieniem incydentu.
    # ===================================================================

    print(f"\n[*] [DEFENSE] Wykryto dane krytyczne: {file_name}")

    print_progress_bar(
        1.0,
        "[*] [DEFENSE] Tworzenie kopii bezpieczeństwa: "
    )

    os.makedirs(backup_folder, exist_ok=True)

    shutil.copy(
        selected_file,
        os.path.join(
            backup_folder,
            f"backup_{file_name}"
        )
    )

    log_event(
        "DEFENSE_BACKUP",
        "Utworzono kopię bezpieczeństwa."
    )

    # ===================================================================
    # FAZA 3: ATAK / SYMULACJA RANSOMWARE
    # ===================================================================
    # Linux:
    #     - ukrycie pliku poprzez zmianę nazwy,
    #     - blokada modyfikacji poprzez chmod().
    # ===================================================================

    print("\n[!] [ATTACK] Wykryto podejrzaną aktywność...")
    time.sleep(1)

    print_progress_bar(
        1.5,
        "[!] [ATTACK] Ukrywanie i blokowanie plików: "
    )

    modified_file = alter_file_restriction(
        selected_file,
        enable_restriction=True
    )

    if modified_file:

        log_event(
            "ATTACK_TRIGGERED",
            "Ukryto plik oraz odebrano prawa zapisu."
        )

        print("\n" + "=" * 55)
        print("   ALERT: TWOJE DANE ZOSTAŁY ZABLOKOWANE!   ")
        print("   (Symulacja edukacyjna Linux PoC)         ")
        print("=" * 55)

    else:

        print("[-] Operacja nie powiodła się.")
        sys.exit(1)

    # ===================================================================
    # FAZA 4: AUTORYZACJA
    # ===================================================================
    # Symulacja odzyskiwania dostępu administracyjnego.
    # ===================================================================

    print("\n[!] Wprowadź hasło administratora.")

    correct_password = "technischools"

    attempts = 3
    authenticated = False

    while attempts > 0:

        user_input = input(
            f"[Hasło (Pozostało prób: {attempts})]: "
        )

        if user_input == correct_password:

            authenticated = True

            log_event(
                "AUTH_SUCCESS",
                "Poprawne hasło administratora."
            )

            break

        else:

            attempts -= 1

            log_event(
                "AUTH_FAILED",
                f"Błędne hasło. Pozostało prób: {attempts}"
            )

            print("[-] Niepoprawne hasło.\n")

    if not authenticated:
        print("\n[X] Limit prób został przekroczony.")

        log_event(
            "MITIGATION_FAILED",
            "Nieudana procedura odzyskiwania."
        )

        sys.exit(1)

    # ===================================================================
    # FAZA 5: MITIGATION / ODTWARZANIE SYSTEMU
    # ===================================================================
    # Przywracanie:
    #     - praw zapisu,
    #     - widoczności pliku.
    # ===================================================================

    print("\n[+] [MITIGATION] Autoryzacja administratora...")

    print_progress_bar(
        1.5,
        "[+] [MITIGATION] Przywracanie systemu: "
    )

    restored_file = alter_file_restriction(
        modified_file,
        enable_restriction=False
    )

    if restored_file:

        log_event(
            "MITIGATION_SUCCESS",
            "Przywrócono domyślne atrybuty Linux."
        )

        print("\n[+] [SUKCES] Integralność systemu przywrócona.")

    else:

        print("\n[-] Błąd przywracania systemu.")

    # ===================================================================
    # FAZA 6: CYFROWA DETEKTYWISTYKA
    # ===================================================================
    # Eksport logów telemetrycznych do formatu JSON.
    # ===================================================================

    time.sleep(1)

    print("\n[*] [FORENSICS] Generowanie raportu incydentu...")

    log_file_path = os.path.join(
        os.getcwd(),
        "incident_report.json"
    )

    with open(log_file_path, "w", encoding="utf-8") as lf:

        json.dump(
            presentation_logs,
            lf,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[+] Raport zapisano jako: "
        f"{os.path.basename(log_file_path)}"
    )

    print("\n=== KONIEC PREZENTACJI (SYSTEM BEZPIECZNY) ===")


if __name__ == "__main__":
    main()
