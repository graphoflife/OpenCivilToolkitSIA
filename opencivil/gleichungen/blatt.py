"""
opencivil/gleichungen/blatt.py -- ein Blatt Gleichungen als Berechnung.

VERANTWORTUNG:
Rechnet die Zeilen eines Blatts der Reihe nach und schreibt jede in die
Herleitung -- unter «Analytische Gleichungen – Name», wie jede andere
Berechnung unter ihrer Ueberschrift. Projektwerte kommen als Eingaben aus dem
Rechenwerk; das Blatt laeuft darum nach dem, was es liest.

JEDE ZEILE FUER SICH:
Ein Fehler bleibt bei seiner Zeile -- und bei den Zeilen, die das dort
Definierte brauchen. Er bricht weder das Blatt ab noch den Lauf der Platten.
Eine Neudefinition gilt ab ihrer Zeile, wie beim Lesen von oben nach unten.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

from opencivil.core.berechnung import Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import einsetzen_symbolisch
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.wert import Wert, WertDef
from opencivil.gleichungen.ausdruck import (
    AusdruckFehler, Name, anzeigeeinheit, einheit_aus_text, lesen, namen,
    rechnen, setzen, stellen,
)

if TYPE_CHECKING:
    # Nur fuer die Typangaben: das Paket projekt baut beim Laden das Rechenwerk
    # und braucht dafuer dieses Modul.
    from opencivil.projekt.gleichungen import (
        GleichungsblattEintrag, GleichungszeileEintrag,
    )


@dataclass
class Zeilenergebnis:
    """Was die Oberflaeche neben einer Zeile zeigt."""

    ergebnis: str = ""
    """Das Ergebnis als LaTeX, ``21\\,\\mathrm{m}^{2}`` -- aus dem Kern gesetzt."""

    fehler: str = ""
    name: str = ""
    """Was die Zeile definiert, als LaTeX -- leer bei Auswertung und Text."""


class Gleichungsblatt(Prozedur):
    """
    Ein Blatt aus :class:`GleichungsblattEintrag`, im Rechenwerk.

    Ohne Thema: seine Formeln sind die des Benutzers und stehen schon als
    Liste da -- die Formelsammlung sammelt die des Werkzeugs.
    """

    def __init__(self, eintrag: GleichungsblattEintrag) -> None:
        self.eintrag = eintrag
        basis = f"gleichungen.{eintrag.kennung}"
        # Ein Ziel braucht jede Berechnung; ein Blatt hat keines, das jemand
        # anderes liest. Also die Zahl der aufgegangenen Zeilen.
        self.d_zeilen = WertDef(id=f"{basis}.zeilen", symbol="n", einheit=EINHEITSLOS,
                                beschreibung=f"Zeilen ohne Fehler – {eintrag.name}",
                                stellen=0)
        titel = f"Analytische Gleichungen – {eintrag.name}"
        super().__init__(
            basis, ausgaben=[self.d_zeilen],
            # Optional: ein Projektwert, den es nicht mehr gibt, ist ein
            # Fehler seiner Zeile und kein Grund, das Blatt nicht zu rechnen.
            bezuege=[Eingabebezug(f"p{i}", z.wert_id, optional=True)
                     for i, z in enumerate(eintrag.zeilen)
                     if z.art == "projektwert" and z.wert_id],
            titel=titel, abschnitt=Abschnitt(titel, basis))
        self.ergebnisse: List[Zeilenergebnis] = []

    def rechne(self, e: Eingaben, p: Protokoll):
        werte: Dict[str, Wert] = {}
        fehlerhaft: Dict[str, int] = {}
        self.ergebnisse = []
        for nummer, zeile in enumerate(self.eintrag.zeilen, start=1):
            erg = Zeilenergebnis()
            try:
                if zeile.art == "text":
                    if zeile.text.strip():
                        p.text(zeile.text.strip())
                elif zeile.art == "projektwert":
                    # Leer ist sie still wie eine leere Formelzeile: frisch
                    # angefuegt, der Wert noch nicht gewaehlt.
                    if zeile.wert_id or zeile.name.strip():
                        self._projektwert(nummer, zeile, e, p, werte, erg)
                elif zeile.latex.strip():
                    self._formel(nummer, zeile, p, werte, fehlerhaft, erg)
            except AusdruckFehler as fehler:
                erg.fehler = str(fehler)
                p.warnung(f"Zeile {nummer}: {fehler}")
                # Was hier definiert werden sollte, gibt es ab jetzt nicht --
                # auch nicht in einer frueheren Fassung. Sonst rechnete die
                # naechste Zeile still mit dem alten Wert weiter.
                if erg.name:
                    werte.pop(erg.name, None)
                    fehlerhaft[erg.name] = nummer
            self.ergebnisse.append(erg)
        return {self.d_zeilen.id: Groesse(sum(not r.fehler for r in self.ergebnisse))}

    # -- Zeilen -------------------------------------------------------------

    def _wert(self, nummer: int, symbol: str, groesse: Groesse, einheit,
              beschreibung: str = "", stellen_: int = None) -> Wert:
        return WertDef(
            id=f"{self.id}.z{nummer}", symbol=symbol, einheit=einheit,
            beschreibung=beschreibung,
            stellen=stellen(groesse, einheit) if stellen_ is None else stellen_,
        ).belegen(groesse.als(einheit))

    def _formel(self, nummer: int, zeile: GleichungszeileEintrag, p: Protokoll,
                werte: Dict[str, Wert], fehlerhaft: Dict[str, int],
                erg: Zeilenergebnis) -> None:
        gelesen = lesen(zeile.latex)
        if gelesen.name is not None:
            erg.name = gelesen.name.latex
        gebraucht = namen(gelesen.ausdruck)
        for name in gebraucht:
            if name not in werte:
                if name in fehlerhaft:
                    raise AusdruckFehler(f"{name}: Fehler in Zeile {fehlerhaft[name]}.")
                raise AusdruckFehler(f"{name} ist nicht definiert.")

        groesse = rechnen(gelesen.ausdruck, {n: w.groesse for n, w in werte.items()})
        einheit = anzeigeeinheit(groesse, einheit_aus_text(zeile.einheit))
        platzhalter = {name: f"v{i}" for i, name in enumerate(gebraucht)}
        vorlage = setzen(gelesen.ausdruck, platzhalter)
        eingaben = {platzhalter[name]: werte[name] for name in gebraucht}
        # Ohne Namen steht die Formel selbst links: «a · b = 3 m · 7 m = 21 m²».
        symbol = (gelesen.name.latex if gelesen.name is not None
                  else einsetzen_symbolisch(vorlage, eingaben))
        wert = self._wert(nummer, symbol, groesse, einheit)
        p.formel(wert, vorlage, eingaben, titel="")
        erg.ergebnis = wert.zahl_latex()
        if gelesen.name is not None:
            werte[gelesen.name.latex] = wert

    def _projektwert(self, nummer: int, zeile: GleichungszeileEintrag, e: Eingaben,
                     p: Protokoll, werte: Dict[str, Wert], erg: Zeilenergebnis) -> None:
        # Den Namen zuerst: fehlt dann der Wert, verweisen die Zeilen, die ihn
        # brauchen, auf diese hier.
        gelesen = lesen(zeile.name) if zeile.name.strip() else None
        if gelesen is not None and gelesen.name is None and isinstance(gelesen.ausdruck, Name):
            erg.name = gelesen.ausdruck.latex
        lokal = f"p{nummer - 1}"
        if not zeile.wert_id:
            raise AusdruckFehler("Wert wählen.")
        if not erg.name:
            raise AusdruckFehler("Name fehlt: Buchstabe mit Index, etwa f_{cd}.")
        if not e.hat(lokal):
            raise AusdruckFehler("Projektwert nicht verfügbar.")
        quelle = e[lokal]
        wert = self._wert(nummer, erg.name, quelle.groesse, quelle.einheit,
                          quelle.beschreibung, quelle.stellen)
        p.wert(wert, titel=quelle.beschreibung)
        erg.ergebnis = wert.zahl_latex()
        werte[erg.name] = wert
