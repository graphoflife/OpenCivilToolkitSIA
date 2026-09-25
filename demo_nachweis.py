"""
demo_nachweis.py -- eine Platte nachweisen, ganz ohne Oberfläche.

Aufruf::

    python3 demo_nachweis.py

Zeigt:
  1. Baustoffe, Platte, Bewehrung und Einwirkungen in ein paar Zeilen
  2. Die Zusammenfassung der Nachweise -- dieselbe wie in der Oberfläche
  3. Rückverfolgung: welche Rechenschritte hinter einem Erfüllungsgrad stehen
  4. Der vollständige Bericht und das LaTeX-Dokument

Gebaut wird über dieselbe Beschreibung, die auch die Oberfläche speichert --
``projekt.speichern(...)`` schreibt eine Datei, die sich dort öffnen lässt.
"""

from pathlib import Path

from opencivil import Projekt

AUSGABE = Path(__file__).parent / "ausgabe"


def trenner(text: str) -> None:
    print("\n" + "=" * 100)
    print(text)
    print("=" * 100 + "\n")


def main(ausgabe: Path = AUSGABE) -> None:
    # -- 1. Beschreiben -----------------------------------------------------
    projekt = Projekt("Decke über EG")
    projekt.beton("C30/37")
    projekt.stahl("B500B")

    # Masse in mm. x liegt innen (2. und 3. Lage), y aussen -- je zwei
    # Durchmesser, unten und oben.
    decke = projekt.platte(
        "Decke über EG", h=300,
        x=[18, 12], x_zulage=[12, 0], y=[12, 12], teilung=150,
        rissanforderung="erhoeht",
    )
    decke.einwirkung("Feld", M_Ed=150)
    decke.einwirkung("Feld mit Druck", M_Ed=150, N_Ed=-300)
    decke.einwirkung("Feld mit Zug", M_Ed=150, N_Ed=300)
    decke.einwirkung("Stütze", M_Ed=-60, V_Ed=80)
    decke.quasistaendig.lastfall("Dauerlast", M_Ed=80)

    # Was die Fassade nicht abdeckt, setzt man am Eintrag selbst.
    decke.duktilitaet = True
    decke.haeufig.aus_tragsicherheit = True

    # -- 2. Rechnen und zusammenfassen --------------------------------------
    ergebnis = projekt.rechnen()
    trenner("Zusammenfassung")
    print(ergebnis.zusammenfassung())

    # -- 3. Rückverfolgung --------------------------------------------------
    trenner("Rückverfolgung")
    urteil = ergebnis.urteile_von("Decke über EG")[0]
    ziel = next(z for z in ergebnis.loesung.werte
                if z.endswith(".erfuellungsgrad") and ".mn." in z)
    print(f"{urteil.name}: Erfüllungsgrad {urteil.gradtext()}")
    print(f"\nZiel {ziel} braucht diese Rechenschritte:")
    for schritt in ergebnis.loesung.kette(ziel):
        print(f"   - {schritt}")

    wert = ergebnis.wert(ziel)
    print(f"\n{wert.beschreibung}: {wert.formatiert()} ({wert.referenz})")

    # -- 4. Bericht ---------------------------------------------------------
    trenner("Bericht")
    bericht = ergebnis.bericht()
    print(f"{len(bericht.splitlines())} Zeilen Bericht mit Herleitung, "
          f"der Anfang:\n")
    print("\n".join(bericht.splitlines()[:12]))

    ausgabe.mkdir(parents=True, exist_ok=True)
    print(f"\n{ergebnis.latex(ausgabe / 'decke_ueber_eg')}")
    print(f"Projektdatei: {projekt.speichern(ausgabe / 'decke_ueber_eg.json')}")


if __name__ == "__main__":
    main()
