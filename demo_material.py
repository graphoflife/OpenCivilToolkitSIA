"""
demo_material.py -- Vorfuehrung des Backends ohne jede Oberflaeche.

Aufruf::

    python3 demo_material.py

Zeigt der Reihe nach:
  1. Rueckwaertsaufloesung: ein Ziel waehlen, nur das Noetige rechnen
  2. Rueckverfolgung: welche Berechnungen waren dafuer erforderlich
  3. Ueberschreiben eines berechneten Kennwerts
  4. Fehlende Eingaben statt stiller Falschwerte
"""

from opencivil.bericht.konsole import drucke
from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl


def trenner(text: str) -> None:
    print("\n\n" + "#" * 100)
    print("#  " + text)
    print("#" * 100)


def main() -> None:
    # -----------------------------------------------------------------
    trenner("1. Ein Ziel wählen -- gerechnet wird nur, was dafür nötig ist")

    werk = Rechenwerk()
    c30 = beton("C30/37").ins_rechenwerk(werk)

    loesung = werk.loese(c30.id_von("f_cd"))
    drucke(loesung, titel=f"Bemessungswert der Druckfestigkeit -- Beton {c30.name}")

    print("\nBenötigte Rechenschritte (genau diese sind zu aktivieren):")
    for schritt in loesung.kette(c30.id_von("f_cd")):
        print(f"   - {schritt}")

    print("\nNicht angefasst wurden u.a.:")
    alle = set(werk.moegliche_ziele())
    ungenutzt = sorted(alle - set(loesung.werte))
    for wid in ungenutzt:
        print(f"   - {wid}")

    # -----------------------------------------------------------------
    trenner("2. Das ganze Material durchrechnen")

    loesung = werk.loese_alles()
    drucke(loesung, titel=f"Sämtliche Kennwerte -- Beton {c30.name}")

    # -----------------------------------------------------------------
    trenner("3. Einen berechneten Kennwert von Hand überschreiben")

    werk.setze(c30.id_von("f_cd"), Groesse(15.0, N_PRO_MM2))
    loesung = werk.loese(c30.id_von("k_sigma"))
    drucke(loesung, titel="k_sigma mit überschriebenem f_cd")
    print(
        "\nBeachte: eta_fc wird nicht mehr gerechnet -- der Zweig ist durch die\n"
        "Überschreibung abgeschnitten. Ausgeführt wurden nur:"
    )
    for schritt in loesung.reihenfolge:
        print(f"   - {schritt}")
    werk.loesche(c30.id_von("f_cd"))

    # -----------------------------------------------------------------
    trenner("4. Fehlende Eingaben werden benannt, nicht stillschweigend erfunden")

    leer = Rechenwerk()
    stahl = betonstahl("B500B")
    # Absichtlich nur die abgeleiteten Kennwerte anmelden, nicht die Vorgaben:
    leer.definiere(*stahl.definitionen.values())
    leer.registriere(
        *[b for b in stahl.berechnungen if b.id.endswith((".f_yd", ".eps_yd"))]
    )
    drucke(leer.loese(stahl.id_von("eps_yd")), titel="Fliessdehnung ohne Eingaben")

    # -----------------------------------------------------------------
    trenner("5. Betonstahl vollständig")

    werk2 = Rechenwerk()
    b500b = betonstahl("B500B").ins_rechenwerk(werk2)
    drucke(werk2.loese_alles(), titel=f"Sämtliche Kennwerte -- Betonstahl {b500b.name}")


if __name__ == "__main__":
    main()
