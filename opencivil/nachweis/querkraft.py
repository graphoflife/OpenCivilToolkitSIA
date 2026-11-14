"""
opencivil/nachweis/querkraft.py -- Querkraftnachweis, was beide Ansaetze teilen.

VERANTWORTUNG:
Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.

ZWEI ANSAETZE, EINER DAVON GILT:
Ob die Platte eine Querkraftbewehrung traegt, entscheidet allein, welcher der
beiden laeuft -- je einer eine Klasse in seinem Modul:

* ohne Buegel (:mod:`~opencivil.nachweis.querkraft_ohne_buegel`):
  ``V_Rd = k_d * tau_cd * d_v``, abhaengig von Moment und Normalkraft;
* mit Buegeln (:mod:`~opencivil.nachweis.querkraft_buegel`): das
  Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen.

Beides zu addieren waere ein drittes Modell -- und dieses Werkzeug rechnet
nur, was es auch herleitet. Hier steht, was beide teilen: die Faelle, die
statische Hoehe der gezogenen Bewehrung, die Ausgaben, das Urteil und die
letzte Zeile der Herleitung.

Bis 2026-10-25 steckten beide Ansaetze in einer Klasse hinter einem
``buegel is None``, und ihr Befund trug beide Haelften als «vielleicht leer».

STATISCHE HOEHE:
``d`` ist die statische Hoehe der *gezogenen* Bewehrung und haengt damit vom
Vorzeichen des Moments ab: bei positivem Moment liegt der Zug unten, bei
negativem oben. Gemessen wird bis zum Schwerpunkt aller gezogenen Posten der
Richtung -- Grundbewehrung, Zulage, auch mehrere Lagen (SIA 262:2025,
4.3.3.2.2). Bis 2026-11-14 galt der aeusserste Posten; mit einer Zulage war
``d`` damit 1 bis 3 mm zu gross.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Befundbezug, Eingabebezug, Eingaben
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, Ausgang, Fallausgang, Nachweis, NachweisUrteil, grad_def,
)
from opencivil.core.einheiten import KN, KN_PRO_M, KNM, MM, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.querschnitt.lagenaufbau import (
    Postenbezug, lage_aus_posten, protokoll_schwerpunkt, protokoll_statische_hoehe,
)
from opencivil.querschnitt.platte import Plattenquerschnitt, Richtung
from opencivil.querschnitt.zugseite import Zugseite

#: Wo die wirksame Hoehe und ihre Einlage stehen.
REFERENZ_EINLAGE = "SIA 262:2025, 4.3.3.2.9"


def zugposten(posten: Sequence[Postenbezug], moment_positiv: bool) -> List[Postenbezug]:
    """
    Die Posten der gezogenen Seite: bei positivem Moment die unteren, bei
    negativem die oberen. **Nur sie zaehlen.** Wer alle nimmt, bekommt bei
    einseitiger Bewehrung eine Zahl, die gar keine statische Hoehe ist: eine
    Platte nur mit unterer Bewehrung lieferte fuers negative Moment
    ``h - 261 = 39 mm`` -- den Abstand der Unterkante zur *unteren* Lage.
    """
    return [q for q in posten if q.lage.von_unten is moment_positiv]


def statische_hoehen(e: Eingaben, posten: Sequence[Postenbezug]) -> Dict[bool, float]:
    """
    Je Momentenrichtung (``True``: Zug unten) die statische Hoehe der
    gezogenen Bewehrung, in m ab dem gedrueckten Rand -- im Schwerpunkt ihrer
    Posten (:func:`~opencivil.querschnitt.lagenaufbau.lage_aus_posten`). Fuer
    den Nachweis und die Kennzahlen.

    Fehlt eine Richtung, liegt auf ihrer Zugseite keine Bewehrung. Dann gibt
    es kein ``d``, und ohne ``d`` keinen Querkraftwiderstand.
    """
    hoehen: Dict[bool, float] = {}
    for positiv in (True, False):
        gezogen = zugposten(posten, positiv)
        d = lage_aus_posten(e, gezogen)[2] if gezogen else None
        if d is not None:
            hoehen[positiv] = d
    return hoehen


# ===========================================================================
# Herleitung -- fuer beide Ansaetze und die Kennzahlen der Platte dieselbe
# ===========================================================================


def _hoch(kurz: str, symbol: str, zeichen: str) -> Tuple[str, str]:
    """Kurzname und Zeichen, mit ``zeichen`` hochgestellt: ``d_+`` und ``d^{+}``."""
    if not zeichen:
        return kurz, symbol
    return f"{kurz}_{zeichen}", f"{symbol}^{{{zeichen}}}"


def protokoll_hoehen(p: Protokoll, werte: Zwischenwerte, e: Eingaben,
                     gezogen: Sequence[Postenbezug], d: float, d_v: Optional[float] = None,
                     *, seite: Zugseite, zeichen: str = "") -> Tuple[Wert, Optional[Wert]]:
    """
    Die statische Hoehe der gezogenen Bewehrung und, ohne Buegel, die
    wirksame -- geschrieben, und fuer die Formeln danach. ``gezogen`` sind die
    Posten der gezogenen Seite (:func:`zugposten`), ``seite`` die gezogene.
    Liegen dort mehrere, steht zuerst ihr Schwerpunkt da. ``zeichen`` hebt die
    Groessen hoch, wo zwei Seiten nebeneinander stehen: ``d^{+}`` (die
    Kennzahlen).

    Mit Buegeln gibt es kein ``d_v``: bis 2026-10-18 schrieben die Kennzahlen
    dort ein «d_v = d (Einlage nicht massgebend)», weil sie die Hoehen ohne
    Buegel mit einer Einlage null mitbenutzten.
    """
    _, z, _ = lage_aus_posten(e, gezogen)
    tiefe = protokoll_schwerpunkt(p, e, werte, gezogen, z, _hoch("z_s", "z_s", zeichen),
                                  titel=f"Schwerpunkt der gezogenen Bewehrung, Zug {seite}")
    hoehe = werte.laenge(*_hoch("d", "d", zeichen), d)
    protokoll_statische_hoehe(p, hoehe, h=e["h"], z=tiefe, seite=seite)
    if d_v is None:
        return hoehe, None
    wirksam = werte.laenge(*_hoch("d_v", "d_v", zeichen), d_v)
    einlage = e["einlagenhoehe"]
    if einlage.groesse.si > 0.0:
        p.text(f"Einlage {einlage.formatiert()} mm {'>' if d_v < d else '≤'} d/6 = "
               f"{Groesse.aus_si(d / 6.0, MM).formatiert(1)} mm.")
    if d_v < d:
        p.formel(wirksam, "@d - @e", {"d": hoehe, "e": einlage},
                 titel="Wirksame Höhe, um die Einlage vermindert", referenz=REFERENZ_EINLAGE)
    else:
        p.formel(wirksam, "@d", {"d": hoehe}, titel="Wirksame Höhe (Einlage nicht massgebend)",
                 referenz=REFERENZ_EINLAGE, name="Wirksame Höhe ohne Abzug")
    return hoehe, wirksam


def _ohne_zugbewehrung(M_Ed: float) -> str:
    """Die Begruendung, wenn die gezogene Seite keinen Stahl hat -- fuer beide Ansaetze."""
    return f"Zugseite ({Zugseite.aus_moment(M_Ed).value}) ohne Bewehrung → kein d, V_Rd = 0."


@dataclass(frozen=True)
class Querkraftfall:
    """Eine zu pruefende Kombination fuer den Querkraftnachweis."""

    name: str
    V_Ed: Groesse
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass
class Querkraftergebnis(Fallausgang):
    """
    Was ein Fall ergibt, in beiden Ansaetzen -- ihre eigenen Zwischenwerte
    tragen :class:`~opencivil.nachweis.querkraft_ohne_buegel.ErgebnisOhneBuegel`
    und :class:`~opencivil.nachweis.querkraft_buegel.ErgebnisMitBuegeln`.
    """

    fall: Querkraftfall
    zugposten: Tuple[Postenbezug, ...] = ()
    """Die Posten der gezogenen Seite -- aus ihrem Schwerpunkt kommt ``d``; leer ohne Zugbewehrung."""

    d: float = 0.0
    v_Rd: float = 0.0
    """in N/m."""

    ausgang: Ausgang = NICHT_FUEHRBAR
    """|V_Ed| gegen v_Rd -- nicht fuehrbar, wo sich kein Widerstand bestimmen liess."""

    begruendung: str = ""


class Querkraft(Nachweis):
    """
    Der Querkraftnachweis einer Platte in einer Tragrichtung -- was beide
    Ansaetze teilen. Welcher gilt, entscheidet allein, ob die Platte Buegel
    traegt: :class:`~opencivil.nachweis.querkraft_ohne_buegel.QuerkraftOhneBuegel`
    oder :class:`~opencivil.nachweis.querkraft_buegel.QuerkraftMitBuegeln`.
    """

    THEMA = "Querkraft"
    ART = "V"

    REFERENZ: str
    """Wo der Widerstand des Ansatzes steht -- fuer Nachweis, Widerstand und Erfuellungsgrad."""

    buegel = None
    """Die Buegel der Platte -- nur der Ansatz mit Buegeln hat welche."""

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        faelle: Sequence[Querkraftfall],
        richtung: Richtung,
        mn_nachweis,
    ) -> None:
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} liegt "
                f"keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        # Ohne Fall rechnet er still, nur fuer das Bild: die M-V-Kurve und
        # der Verlauf ueber die Neigung brauchen die Beiwerte, die erst im Lauf
        # entstehen. Er hat dann keine Ausgabe und ist Ziel unter seiner ID.
        self.faelle = list(faelle)

        self.mn = mn_nachweis
        """
        Der M-N-Nachweis derselben Richtung.

        Gebraucht ohne Buegel, fuer die Herleitung von ``m_Rd(N_Ed)``: die Zahl
        kommt als Eingang aus dem Graphen, die Interpolation dahinter aber liegt
        in dessen Befund (:class:`~opencivil.nachweis.biegung_normalkraft.MNBefund`).
        Sie hier nachzubauen hiesse, dieselbe Rechnung ein zweites Mal zu
        schreiben.
        """

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.querkraft.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,V,{r},{als_text(f.name)}}}",
                f"Erfüllungsgrad Querkraft {richtung.beschriftung} – {f.name}",
                self.REFERENZ,
            )
            for f in self.faelle
        }
        self.d_v_rd: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.v_Rd",
                symbol=f"V_{{Rd,{r}}}",
                einheit=KN_PRO_M,
                beschreibung=f"Querkraftwiderstand {richtung.beschriftung} – {f.name}",
                referenz=self.REFERENZ,
                stellen=1,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
        ]
        for q in self.posten:
            bezuege += q.bezuege("a_s", "z")

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()) + list(self.d_v_rd.values()),
            bezuege=bezuege + self._ansatzbezuege(),
            befunde=self._befunde(),
            titel=f"Querkraftnachweis {richtung.beschriftung} – {querschnitt.name}",
            referenz=self.REFERENZ,
            # Der Nachweis gehoert zu seiner Platte. Ohne diese Angabe stuende
            # er unter der Ueberschrift, die zufaellig zuletzt offen war -- und
            # welche das ist, entscheidet die Abhaengigkeitsfolge.
            abschnitt=querschnitt.abschnitt,
        )
        self.still = not faelle

    @abstractmethod
    def _ansatzbezuege(self) -> List[Eingabebezug]:
        """Was der Ansatz ausser der Hoehe und den Lagen der Bewehrung liest."""

    def _befunde(self) -> List[Befundbezug]:
        """Wessen Befund der Ansatz liest -- ohne Buegel den des M-N-Nachweises."""
        return []

    def _eintragen(
        self, erg: Querkraftergebnis, ergebnis: Dict[str, Groesse],
        urteile: List[NachweisUrteil],
    ) -> None:
        """
        Ausgaben und Urteil eines Falls -- fuer beide Ansaetze dieselben.

        Was ein Querkraftnachweis herausgibt, haengt nicht davon ab, wie der
        Widerstand zustande kam. Zweimal geschrieben liefen die beiden Faelle
        frueher oder spaeter auseinander.
        """
        fall = erg.fall
        ergebnis[self.d_v_rd[fall.name].id] = Groesse.aus_si(erg.v_Rd, KN_PRO_M)
        urteile.append(self.urteil(self.d_ausnutzung[fall.name], fall.name, erg.ausgang,
                                   erg.begruendung))

    def _einwirkung(self, fall: Querkraftfall) -> Wert:
        """
        Die Querkraft als Betrag -- fuer Urteil und Erfuellungsgrad dieselbe.

        Das Vorzeichen spielt keine Rolle, verglichen wird der Betrag. Also
        steht auch der Betrag da; sonst teilte der Leser den Widerstand durch
        eine negative Zahl und bekaeme etwas anderes als den danebenstehenden
        Erfuellungsgrad. Die Betragsstriche stehen trotzdem nicht am Symbol:
        sie sagen nichts, was die Zahl daneben nicht schon zeigt.
        """
        return Zwischenwerte(f"{self.id}.{fall.kennung}").wert(
            "V_Ed", rf"V_{{Ed,{self.richtung.value}}}",
            Groesse.aus_si(abs(fall.V_Ed.si), KN_PRO_M), beschreibung="Einwirkung")

    def _widerstand(self, erg: Querkraftergebnis) -> Wert:
        """
        Der Widerstand eines Falls -- fuer Urteil und Herleitung derselbe.

        Er gilt nur unter genau dieser Einwirkung; das gehoert ins Symbol,
        sonst liest sich V_Rd wie ein Kennwert des Querschnitts.
        """
        return Zwischenwerte(f"{self.id}.{erg.fall.kennung}").wert(
            "v_Rd", self._widerstandssymbol(erg.fall),
            Groesse.aus_si(erg.v_Rd, KN_PRO_M), beschreibung="Widerstand")

    def _widerstandssymbol(self, fall: Querkraftfall) -> str:
        """``V_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)`` -- der Widerstand ist bedingt."""
        r = self.richtung.value
        return (rf"V_{{Rd,{r}}}(M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)},\ "
                rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)})")

    # -- Mitschrift, für beide Ansätze ----------------------------------------

    def _protokoll_einwirkung(self, p: Protokoll, fall: Querkraftfall) -> None:
        p.gleichung(
            rf"V_{{Ed}} = {fall.V_Ed.als_latex(1, KN_PRO_M)} \qquad "
            rf"M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

    def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None:
        """
        Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe. Der
        Widerstand steht hier kurz: seine Bedingung steht in der Zeile, die ihn
        herleitet.
        """
        name = erg.fall.name
        kurz = erg.ausgang.benannt(widerstand=self.d_v_rd[name].belegen(
            erg.ausgang.widerstand.groesse))
        kurz.zeile(p, self.d_ausnutzung[name], mit_urteil=True)
