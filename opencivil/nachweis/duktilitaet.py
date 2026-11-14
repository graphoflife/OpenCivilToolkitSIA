"""
opencivil/nachweis/duktilitaet.py -- Duktilitaetsnachweis ueber die Druckzonenhoehe.

VERANTWORTUNG:
Prueft je Bewehrungslage, ob die Druckzone schlank genug bleibt::

    0.85 * x * b * f_cd = A_s * f_yd        (Kraeftegleichgewicht, M_Ed = 0)
    x / d <= k * 435 N/mm^2 / f_yd          (k: Vorgabe 0.35, hoechstens 0.5)

Eine flache Druckzone heisst: der Stahl fliesst lange, bevor der Beton
versagt, und das Bauteil kann Schnittgroessen umlagern. Haelt die Druckzone
die Grenze ein, darf man nach SIA 262:2025, 4.1.4.2.5 umlagern, ohne das
Verformungsvermoegen nachzurechnen -- darum wird hier keine Tragfaehigkeit
nachgewiesen, sondern ein Verhaeltnis.

JE LAGE, EIN URTEIL JE LAGE:
Anders als M-N und Querkraft gilt dieser Nachweis fuer eine einzelne
Bewehrungslage. Gerechnet werden die beiden Lagen der Tragrichtung -- die
untere traegt das Feld-, die obere das Stuetzmoment. In der Zusammenfassung
steht die unguenstigere: geht die auf, gehen beide auf. Die Urteile sind
dafuer als Teile derselben Frage gestempelt (siehe
:meth:`~opencivil.core.nachweis.Nachweis.teilurteile`); gezaehlt werden
trotzdem beide, denn die Bewehrungssuche misst ihren Fortschritt an der Summe
der Rueckstaende.

Eine Lage ohne Stahl gibt die Platte gar nicht erst mit: sie wird nicht
nachgewiesen (Benutzer, 2026-10-19, :mod:`opencivil.projekt.aufbau.platte`).
Bekommt der Nachweis eine ausdruecklich mit, steht sie mit Hinweis statt
einer Zahl da.

STATISCHE HOEHE:
``d`` wird von der **gedrueckten** Randfaser aus gemessen. Bei den unteren
Lagen (1 und 2) liegt der Zug unten, gedrueckt ist oben: ``d = z``. Bei den
oberen Lagen umgekehrt: ``d = h - z``. Gerechnet wird mit dem gemeinsamen
Schwerpunkt von Grundbewehrung und Zulage -- sie gehoeren zur selben Lage.

EINHEITEN:
Alles in SI-Basis; ``x`` und ``d`` in m, Flaechen in m^2, Festigkeiten in Pa.
Das Verhaeltnis ``x/d`` ist dimensionslos und wird als Einwirkung gegen die
Grenze ``(x/d)_max`` gehalten.

DIE GRENZE:
Sie haengt am Stahl der Lage, ``k * 435 N/mm^2 / f_yd``: bei B500 ist sie
0.35, bei B700B 0.25. Bis 2026-11-14 stand sie fest auf 0.35, auch bei B700B.
Den Beiwert ``k`` gibt man je Platte an, hoechstens 0.5
(``QuerschnittEintrag.x_d_max``): darueber raet 4.1.4.2.6 ab. Weicht er von
der Vorgabe ab, sagt das die Herleitung -- ein anderer Beiwert ist eine
Annahme, die man im Bericht finden muss.

Die Ziffer setzt ausserdem einen Stahl der Duktilitaetsklasse B oder C und
Beton bis C50/60 voraus. Sonst ist das Verformungsvermoegen nachzurechnen
(4.1.4.2.6), und das kann dieser Nachweis nicht: die Lage steht als nicht
fuehrbar da, mit dem Grund (:func:`hindernis`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.nachweis import NICHT_FUEHRBAR, Ausgang, Fallausgang, Vergleich
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import angabe, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.material.basis import Baustoff
from opencivil.material.betonstahl import duktilitaetsklasse
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL
from opencivil.querschnitt.lagenaufbau import lage_aus_posten, protokoll_lage
from opencivil.nachweis.lagennachweis import Lagennachweis
from opencivil.querschnitt.platte import Bewehrungslage

REFERENZ = "SIA 262:2025, 4.1.4.2.5"

#: Der Beiwert k der Grenze -- die Vorgabe der Ziffer.
BEIWERT = 0.35

#: So weit laesst sich der Beiwert hoechstens anheben: darueber raet
#: SIA 262:2025, 4.1.4.2.6 ab.
HOECHSTENS = 0.5

#: Die Fliessgrenze, auf die sich der Beiwert bezieht, in Pa: f_yd von B500,
#: so gerundet, wie die Norm sie in die Grenze schreibt.
BEZUG_F_YD = 435e6

#: Bis zu dieser Festigkeit f_ck, in Pa, gilt die Grenze: C50/60.
HOECHSTE_FESTIGKEIT = 50e6

#: Die Seite im Notizbuch: die Bedingung der Platte und die des gezeichneten
#: Querschnitts sind dieselbe.
DUKTILITAETSBEDINGUNG = "Bedingung der Duktilität"

#: Die Bedingung -- fuer beide dieselbe, wie die Zeile ihrer Grenze
#: (:func:`protokoll_grenze`).
BEDINGUNG = r"\frac{x}{d} \le k \cdot \frac{435\,\mathrm{N/mm^2}}{f_{yd}}"


def grenze(beiwert: float, f_yd: float) -> float:
    """Die zulaessige bezogene Druckzonenhoehe ``k * 435 N/mm^2 / f_yd``; f_yd in Pa."""
    return beiwert * BEZUG_F_YD / f_yd


def hindernis(staehle: Sequence[Baustoff], f_ck: float) -> str:
    """
    Was an den Baustoffen die Bedingung ausschliesst, als Begruendung --
    leer, wenn nichts. Ein Stahl ohne Klasse, ein eigener, schliesst nichts
    aus: seine Klasse kennt nur, wer ihn angelegt hat.
    """
    if f_ck > HOECHSTE_FESTIGKEIT * (1.0 + 1e-9):
        grund = f"Beton mit f_ck = {f_ck / 1e6:g} N/mm² über C50/60"
    else:
        klasse_a = [s.name for s in staehle if duktilitaetsklasse(s.sorte) == "A"]
        if not klasse_a:
            return ""
        grund = f"{', '.join(klasse_a)}: Duktilitätsklasse A"
    return (f"{grund} → kein Nachweis über x/d. Umlagern nur mit einem Nachweis "
            f"des Verformungsvermögens (SIA 262:2025, 4.1.4.2.6).")


def protokoll_bedingung(p: Protokoll, beiwert: float) -> None:
    """Die Bedingung, was sie voraussetzt, und ein abweichender Beiwert."""
    p.ansatz(BEDINGUNG, titel="Bedingung", referenz=REFERENZ, name=DUKTILITAETSBEDINGUNG)
    p.erklaerung(
        "Die Grenze hängt an der Fliessgrenze: mit der Vorgabe k = 0.35 ist "
        "sie bei B500 0.35, bei B700B 0.25. Ohne Nachweis des "
        "Verformungsvermögens gilt sie nur mit einem Stahl der "
        "Duktilitätsklasse B oder C und mit Beton bis C50/60. "
        f"Mehr als k = {HOECHSTENS:g} lässt das Werkzeug nicht zu, darüber rät "
        "4.1.4.2.6 ab.")
    if abs(beiwert - BEIWERT) > 1e-12:
        p.text(f"Beiwert eingegeben: k = {beiwert:.2f} statt der Vorgabe {BEIWERT:.2f}.")


def protokoll_grenze(p: Protokoll, werte: Zwischenwerte, grenzwert: Wert, *,
                     beiwert: float, f_yd: Wert) -> None:
    """Die Grenze, hergeleitet -- fuer Platte und gezeichneten Querschnitt dieselbe Zeile."""
    p.formel(grenzwert, r"@k \cdot \frac{435\,\mathrm{N/mm^2}}{@f_yd}",
             {"k": werte.zahl("k", "k", beiwert, stellen=2), "f_yd": f_yd},
             titel="Grenze der bezogenen Druckzonenhöhe", referenz=REFERENZ)


@dataclass
class Lagenergebnis(Fallausgang):
    """Was der Nachweis fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    a_s: float = 0.0
    """Summe der Bewehrungsquerschnitte dieser Lage, in m^2."""

    z: float = 0.0
    """Gemeinsamer Schwerpunkt ab Oberkante, in m."""

    d: float = 0.0
    """Statische Hoehe ab der gedrueckten Randfaser, in m."""

    f_yd: float = 0.0
    """Fliessgrenze der Lage, in Pa -- die Stahlspannung im Gleichgewicht."""

    x: float = 0.0
    """Druckzonenhoehe bei M_Ed = 0, in m."""

    verhaeltnis: float = 0.0
    grenze: float = 0.0
    """(x/d)_max der Lage -- sie haengt an ihrem Stahl."""

    ausgang: Ausgang = NICHT_FUEHRBAR
    """x/d gegen (x/d)_max."""

    begruendung: str = ""


def druckzonenhoehe(*, a_s: float, f_yd: float, b: float, f_cd: float) -> float:
    """
    ``x`` aus dem Kraeftegleichgewicht bei reiner Biegung.

    ``0.85 * x * b * f_cd = A_s * f_yd``, aufgeloest nach ``x``. Alles in
    SI-Basis; Rueckgabe in m. Dieselbe Formel wie beim Eckpunkt *reine Biegung*
    der Handrechnung -- sie steht dort schon einmal, weil sie dort einen
    anderen Zweck hat, aber es ist dieselbe Gleichgewichtsbedingung.
    """
    return a_s * f_yd / (BLOCKANTEIL * b * f_cd)


class Duktilitaet(Lagennachweis):
    """
    Duktilitaetsnachweis je Bewehrungslage (:class:`~.lagennachweis.Lagennachweis`).

    Ein Nachweis fuer die ganze Platte, ein Urteil je Lage. Die Lagen einer
    Platte gehoeren zusammen und stehen darum unter einer Ueberschrift; sie auf
    zwei Nachweise zu verteilen ergaebe zwei fast leere Abschnitte.

    Ob er ueberhaupt gefuehrt wird, entscheidet ein einziger Schalter am
    Querschnitt; welche Lagen er ansieht, sagt der Aufbau, und wie tief die
    Druckzone reichen darf, der Beiwert ``beiwert`` mit dem Stahl der Lage.
    """

    THEMA = "Duktilität"
    ART = "D"
    KUERZEL = "D"
    BENENNUNG = "Duktilität"
    REFERENZ = REFERENZ

    def __init__(
        self,
        querschnitt,
        lagen: Sequence[int],
        beiwert: float = BEIWERT,
    ) -> None:
        if not 0.0 < beiwert <= HOECHSTENS:
            raise ValueError(
                f"Der Beiwert k der Grenze muss grösser als null und höchstens "
                f"{HOECHSTENS:g} sein, angegeben ist {beiwert:g}.")
        self.beiwert = beiwert
        gewaehlt = sorted(set(lagen))
        if not gewaehlt:
            raise ValueError("Der Duktilitätsnachweis braucht mindestens eine Lage.")
        unbekannt = [n for n in gewaehlt
                     if not any(l.nummer == n for l in querschnitt.lagen)]
        if unbekannt:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': die Lagen "
                f"{', '.join(str(n) for n in unbekannt)} gibt es nicht.")

        basis = f"{querschnitt.id}.nachweis.duktilitaet"
        lagen_ = [l for l in querschnitt.lagen if l.nummer in gewaehlt]
        self.d_verhaeltnis: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.x_zu_d",
                symbol=rf"\left(x/d\right)_{{{l.nummer}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Bezogene Druckzonenhöhe – {l.nummer}. Lage",
                referenz=self.REFERENZ,
                stellen=3,
            )
            for l in lagen_
        }
        super().__init__(
            querschnitt, lagen_, basis=basis,
            titel=f"Duktilitätsnachweis – {querschnitt.name}",
            bezuege=[
                Eingabebezug("h", querschnitt.id_von("h")),
                # Zwei Breiten, weil zwei Lagen verschiedene Richtungen tragen
                # koennen. x/d bliebe zwar unveraendert, wenn man A_s und b
                # beide verwechselte -- aber nur dann; hier stammt A_s aus dem
                # Lagenaufbau und kennt seine Richtung bereits.
                Eingabebezug("b", querschnitt.id_von("b")),
                Eingabebezug("b_y", querschnitt.id_von("b_y")),
                Eingabebezug("f_cd", querschnitt.beton.id_von("f_cd")),
                Eingabebezug("f_ck", querschnitt.beton.id_von("f_ck")),
            ],
            posten=("a_s", "z"), stahl=("f_yd",),
            weitere_ausgaben=list(self.d_verhaeltnis.values()))

    # -- Rechnen ------------------------------------------------------------

    def ansatz(self, e: Eingaben, p: Protokoll) -> float:
        """f_cd -- und die Herleitung des Ansatzes."""
        self._protokoll_ansatz(p, e)
        return e.g("f_cd").si

    def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: float) -> Lagenergebnis:
        erg = Lagenergebnis(lage=lage)
        erg.a_s, erg.z, erg.d = lage_aus_posten(e, self.posten_je_lage[lage.nummer])
        # Eine Lage traegt genau einen Stahl -- eine schwaechere Sorte unter
        # ihren Posten gibt es nicht. Die Breite ist die in ihrer Richtung.
        erg.f_yd = e.g(lage.stahl.eingabename("f_yd")).si
        erg.x = druckzonenhoehe(a_s=erg.a_s, f_yd=erg.f_yd, b=e.g(lage.richtung.breite).si,
                                f_cd=ansatz)
        erg.verhaeltnis = erg.x / erg.d if erg.d > 0 else float("inf")
        erg.grenze = grenze(self.beiwert, erg.f_yd)
        erg.begruendung = hindernis([lage.stahl], e.g("f_ck").si)
        if erg.begruendung:
            return erg
        erg.ausgang = v = Vergleich(
            self.d_verhaeltnis[lage.nummer].belegen(Groesse(erg.verhaeltnis, EINHEITSLOS)),
            self._grenze(lage.nummer, erg.grenze))
        erg.begruendung = (
            f"x/d = {erg.x * 1e3:.1f} mm / {erg.d * 1e3:.1f} mm = "
            f"{erg.verhaeltnis:.3f} {'≤' if v.erfuellt else '>'} {erg.grenze:.3f}.")
        return erg

    def ausgaben_der_lage(self, erg: Lagenergebnis) -> Dict[str, Groesse]:
        return {self.d_verhaeltnis[erg.lage.nummer].id: Groesse(erg.verhaeltnis, EINHEITSLOS)}

    def _grenze(self, nummer: int, zahl: float) -> Wert:
        """Die zulaessige bezogene Druckzonenhoehe -- Widerstand und Herleitung."""
        return WertDef(
            id=f"{self.id}.lage{nummer}.grenze",
            symbol=r"\left(x/d\right)_{max}",
            einheit=EINHEITSLOS, beschreibung="Grenze der bezogenen Druckzonenhöhe",
            referenz=REFERENZ, stellen=3,
        ).belegen(Groesse(zahl, EINHEITSLOS))

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel("Duktilität")
        p.erklaerung(
            "Die Druckzone muss klein bleiben, damit der Stahl lange fliesst, "
            "bevor der Beton versagt: dann lassen sich Schnittgrössen umlagern. "
            "Gerechnet wird die Druckzonenhöhe bei reiner Biegung, je Lage "
            "einzeln, mit dem Spannungsblock und ohne Druckbewehrung."
        )
        f_cd = e["f_cd"].symbol
        p.ansatz(
            rf"{BLOCKANTEIL} \cdot x \cdot b \cdot {f_cd} = A_s \cdot f_{{yd}}"
            r" \qquad \Rightarrow \qquad "
            rf"x = \frac{{A_s \cdot f_{{yd}}}}"
            rf"{{{BLOCKANTEIL} \cdot b \cdot {f_cd}}}",
            titel="Kräftegleichgewicht bei M_Ed = 0",
            referenz="SIA 262:2025, 4.1.4.2.5; 4.2.1.5, Figur 12")
        protokoll_bedingung(p, self.beiwert)
        p.erklaerung(
            "d wird von der gedrückten Randfaser aus gemessen: bei den unteren "
            "Lagen von der Oberkante, bei den oberen von der Unterkante. "
            "Grundbewehrung und Zulage einer Lage zählen mit ihrem gemeinsamen "
            "Schwerpunkt."
        )

    def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis,
                       ansatz: float) -> None:
        """
        Die Herleitung einer Lage, aus Vorlagen: jede Formel steht einmal mit
        Symbolen da, die Fassung mit Zahlen und Einheiten entsteht daraus.
        """
        nummer, breite = erg.lage.nummer, erg.lage.richtung.breite
        p.titel(f"Duktilität – {nummer}. Lage", ebene=3)
        if not erg.machbar:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.lage{nummer}")
        a_s, d = protokoll_lage(p, e, werte, self.posten_je_lage[nummer],
                                a_s=erg.a_s, z=erg.z, d=erg.d)

        f_yd = e[erg.lage.stahl.eingabename("f_yd")]
        x = werte.laenge("x", "x", erg.x)
        p.formel(
            x,
            rf"\frac{{@A_s \cdot @f_yd}}{{{BLOCKANTEIL} \cdot @b \cdot @f_cd}}",
            {"A_s": a_s, "b": e[breite], "f_cd": e["f_cd"], "f_yd": f_yd},
            titel="Druckzonenhöhe bei reiner Biegung",
            referenz="SIA 262:2025, 4.2.1.5, Figur 12",
            name="Druckzonenhöhe aus dem Kräftegleichgewicht")

        v = erg.ausgang
        protokoll_grenze(p, werte, v.widerstand, beiwert=self.beiwert, f_yd=f_yd)
        p.formel(v.einwirkung, r"\frac{@x}{@d}", {"x": x, "d": d},
                 titel="Bezogene Druckzonenhöhe",
                 nachsatz=vergleich(r"\le", angabe(v.widerstand), v.erfuellt))
        v.zeile(p, self.d_ausnutzung[nummer])
