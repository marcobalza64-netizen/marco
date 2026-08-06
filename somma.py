#!/usr/bin/env python3
"""App da terminale per sommare numeri."""

from __future__ import annotations


def formatta(n: float) -> str:
    return str(int(n)) if n == int(n) else str(n)


def leggi_numeri() -> list[float]:
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
    print("Numeri:", " + ".join(formatta(n) for n in numeri))
    print(f"Somma:  {formatta(totale)}")


if __name__ == "__main__":
    main()
