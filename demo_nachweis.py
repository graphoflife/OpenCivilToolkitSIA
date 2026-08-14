"""
demo_nachweis.py -- Vollständiger Durchlauf vom Material bis zum Bericht.

Aufruf::

    python3 demo_nachweis.py

Zeigt:
  1. Querschnitt aus Material, Geometrie und Bewehrung aufbauen
  2. M-N-Nachweis für mehrere Schnittgrössenkombinationen
  3. Rückverfolgung: welche Rechenschritte waren nötig
  4. Bericht auf der Konsole und als LaTeX-Dokument
"""

from pathlib import Path

from opencivil.bericht.konsole import drucke
from opencivil.bericht.latex_dokument import formeln_sammeln, schreibe
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, MM, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.querschnitt.platte import Bewehrungslage, Plattenquerschnitt

AUSGABE = Path(__file__).parent / "ausgabe"


def main() -> None:
    # -- 1. Modell aufbauen ------------------------------------------------
    c30 = beton("C30/37")
    b500b = betonstahl("B500B")

    platte = Plattenquerschnitt(
        name="Decke über EG",
        h=Groesse(300, MM),
        b=Groesse(1000, MM),          # 1 m Breite -> alle Werte pro Laufmeter
        beton=c30,
        lagen_unten=[
            Bewehrungslage(Groesse(18, MM), b500b, abstand=Groesse(150, MM)),
            Bewehrungslage(Groesse(12, MM), b500b, abstand=Groesse(150, MM)),
        ],
        lagen_oben=[
            Bewehrungslage(Groesse(12, MM), b500b, abstand=Groesse(150, MM)),
        ],
        ueberdeckung_unten=Groesse(30, MM),
        ueberdeckung_oben=Groesse(30, MM),
    )

    kombinationen = [
        Schnittgroessen("Feld", M_Ed=Groesse(150, KNM)),
        Schnittgroessen("Feld mit Druck", M_Ed=Groesse(150, KNM), N_Ed=Groesse(-300, KN)),
        Schnittgroessen("Feld mit Zug", M_Ed=Groesse(150, KNM), N_Ed=Groesse(300, KN)),
        Schnittgroessen("Stuetze", M_Ed=Groesse(-60, KNM)),
        Schnittgroessen(
            "Feld M konstant", M_Ed=Groesse(150, KNM), N_Ed=Groesse(-300, KN),
            art=Erfuellungsart.MOMENT_KONSTANT,
        ),
        Schnittgroessen(
            "Feld kuerzester Abstand", M_Ed=Groesse(150, KNM), N_Ed=Groesse(-300, KN),
            art=Erfuellungsart.NAECHSTER_PUNKT,
        ),
        Schnittgroessen("Ueberlastfall", M_Ed=Groesse(320, KNM)),
    ]

    werk = Rechenwerk()
    platte.ins_rechenwerk(werk)
    nachweis = BiegungNormalkraft(platte, kombinationen)
    werk.registriere(nachweis)

    # -- 2. Nur die Nachweise als Ziel setzen ------------------------------
    ziele = [d.id for d in nachweis.d_ausnutzung.values()]
    loesung = werk.loese(*ziele)

    drucke(loesung, titel=f"Biegung und Normalkraft – {platte.name}")

    # -- 3. Rueckverfolgung -------------------------------------------------
    print("\n" + "=" * 100)
    print("Rückverfolgung")
    print("=" * 100)
    ziel = nachweis.d_ausnutzung["Feld"].id
    print(f"\nZiel: {ziel}")
    print("\nDafür nötige Rechenschritte:")
    for schritt in loesung.kette(ziel):
        print(f"   - {schritt}")
    print(f"\nDafür nötige Werte: {len(loesung.benoetigte_werte(ziel))}")

    print("\nEckwerte der Resistenzlinie:")
    for name, definition in nachweis.d_eckwerte.items():
        wert = loesung.wert(definition.id)
        print(f"   {name:12s} {wert.formatiert():>10s} {wert.einheit.name}")

    print(f"\nBerechnete Interaktionslinie: {len(nachweis.linie)} Punkte")

    # -- 4. Bericht ---------------------------------------------------------
    print("\n" + "=" * 100)
    print("Berichtsausgabe")
    print("=" * 100)

    formeln = formeln_sammeln(loesung)
    print(f"\n{len(formeln)} einzeln kopierbare Formeln, z.B.:")
    for eintrag in formeln[:3]:
        print(f"\n   {eintrag.titel}   [{eintrag.referenz}]")
        print(f"   {eintrag.latex.splitlines()[0][:90]}")

    ergebnis = schreibe(
        loesung,
        AUSGABE / "decke_ueber_eg",
        titel=f"Nachweis Biegung und Normalkraft – {platte.name}",
        untertitel="OpenCivilToolkit – Berechnung nach SIA 262:2025",
    )
    print(f"\n{ergebnis}")


if __name__ == "__main__":
    main()
