#!/usr/bin/env python3
"""App per sommare numeri da terminale."""


def leggi_numeri() -> list[float]:
    """Chiede numeri all'utente fino a quando digita 'fine' o lascia vuoto."""
    numeri: list[float] = []
    print("Inserisci i numeri da sommare.")
    print("Scrivi 'fine' (o lascia vuoto) per calcolare la somma.\n")

    while True:
        valore = input(f"Numero {len(numeri) + 1}: ").strip().replace(",", ".")
        if valore == "" or valore.lower() == "fine":
            break
        try:
            numeri.append(float(valore))
        except ValueError:
            print("  Valore non valido. Inserisci un numero, oppure 'fine'.")

    return numeri


def main() -> None:
    print("=== Somma Numeri ===\n")
    numeri = leggi_numeri()

    if not numeri:
        print("\nNessun numero inserito.")
        return

    totale = sum(numeri)
    print("\n--- Risultato ---")
    print("Numeri:", " + ".join(str(n) if n % 1 else str(int(n)) for n in numeri))
    if totale % 1:
        print(f"Somma:  {totale}")
    else:
        print(f"Somma:  {int(totale)}")


if __name__ == "__main__":
    main()
