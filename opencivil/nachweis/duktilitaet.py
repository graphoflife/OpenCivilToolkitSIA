"""
opencivil/nachweis/duktilitaet.py -- Duktilitaetsnachweis ueber die Druckzonenhoehe.

VERANTWORTUNG:
Prueft je Bewehrungslage, ob die Druckzone schlank genug bleibt::

    0.85 * x * b * f_cd = A_s * f_sd        (Kraeftegleichgewicht, M_Ed = 0)
    x / d <= 0.35

Eine flache Druckzone heisst: der Stahl fliesst lange, bevor der Beton
versagt. Der Querschnitt kuendigt sein Versagen an, statt ploetzlich zu
brechen -- darum wird hier keine Tragfaehigkeit nachgewiesen, sondern ein
Verhaeltnis.

JE LAGE, EIN URTEIL JE LAGE:
Anders als M-N und Querkraft gilt dieser Nachweis fuer eine einzelne
Bewehrungslage. Gerechnet werden die beiden Lagen der Tragrichtung -- die
untere traegt das Feld-, die obere das Stuetzmoment. In der Zusammenfassung
steht die unguenstigere: geht die auf, gehen beide auf. Die Urteile sind
dafuer als Teile derselben Frage gestempelt (siehe
:meth:`~opencivil.core.berechnung.Nachweis.teilurteile`); gezaehlt werden
trotzdem beide, denn die Bewehrungssuche misst ihren Fortschritt an der Summe
der Rueckstaende.

Eine unbewehrte Lage ist kein Fehler der Beschreibung: sie bekommt ein Urteil
mit Hinweis statt einer Zahl -- und ist damit die unguenstigere, steht also
auch in der Tabelle.

STATISCHE HOEHE:
``d`` wird von der **gedrueckten** Randfaser aus gemessen. Bei den unteren
Lagen (1 und 2) liegt der Zug unten, gedrueckt ist oben: ``d = z``. Bei den
oberen Lagen umgekehrt: ``d = h - z``. Gerechnet wird mit dem gemeinsamen
Schwerpunkt von Grundbewehrung und Zulage -- sie gehoeren zur selben Lage.

EINHEITEN:
Alles in SI-Basis; ``x`` und ``d`` in m, Flaechen in m^2, Festigkeiten in Pa.
Das Verhaeltnis ``x/d`` ist dimensionslos und wird als Einwirkung gegen die
Grenze 0.35 gehalten.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_als_text,
)
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.material.basis import mit_index
from opencivil.nachweis.handrechnung import BLOCKANTEIL
from opencivil.querschnitt.platte import (
    Bewehrungslage, Richtung, posten_index)

#: Groesste zulaessige bezogene Druckzonenhoehe.
GRENZE = 0.35


@dataclass
class Lagenergebnis:
    """Was der Nachweis fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    a_s: float = 0.0
    """Summe der Bewehrungsquerschnitte dieser Lage, in m^2."""

    z: float = 0.0
    """Gemeinsamer Schwerpunkt ab Oberkante, in m."""

    d: float = 0.0
    """Statische Hoehe ab der gedrueckten Randfaser, in m."""

    f_sd: float = 0.0
    """Stahlspannung im Gleichgewicht -- die fliessende Bewehrung, in Pa."""

    x: float = 0.0
    """Druckzonenhoehe bei M_Ed = 0, in m."""

    verhaeltnis: float = 0.0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""

    @property
    def machbar(self) -> bool:
        return self.a_s > 0.0


def druckzonenhoehe(*, a_s: float, f_sd: float, b: float, f_cd: float) -> float:
    """
    ``x`` aus dem Kraeftegleichgewicht bei reiner Biegung.

    ``0.85 * x * b * f_cd = A_s * f_sd``, aufgeloest nach ``x``. Alles in
    SI-Basis; Rueckgabe in m. Dieselbe Formel wie beim Eckpunkt *reine Biegung*
    der Handrechnung -- sie steht dort schon einmal, weil sie dort einen
    anderen Zweck hat, aber es ist dieselbe Gleichgewichtsbedingung.
    """
    return a_s * f_sd / (BLOCKANTEIL * b * f_cd)


class Duktilitaet(Nachweis):
    """
    Duktilitaetsnachweis je Bewehrungslage.

    Ein Nachweis fuer die ganze Platte, ein Urteil je Lage. Die Lagen einer
    Platte gehoeren zusammen und stehen darum unter einer Ueberschrift; sie auf
    zwei Nachweise zu verteilen ergaebe zwei fast leere Abschnitte.

    Ob er ueberhaupt gefuehrt wird, entscheidet ein einziger Schalter am
    Querschnitt; welche Lagen er ansieht, sagt der Aufbau.
    """

    def __init__(
        self,
        querschnitt,
        lagen: Sequence[int],
    ) -> None:
        gewaehlt = sorted(set(lagen))
        if not gewaehlt:
            raise ValueError("Der Duktilitätsnachweis braucht mindestens eine Lage.")
        unbekannt = [n for n in gewaehlt
                     if not any(l.nummer == n for l in querschnitt.lagen)]
        if unbekannt:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': die Lagen "
                f"{', '.join(str(n) for n in unbekannt)} gibt es nicht.")

        self.querschnitt = querschnitt
        self.lagen = [l for l in querschnitt.lagen if l.nummer in gewaehlt]
        self.ergebnisse: List[Lagenergebnis] = []

        # Je Lage ihre Posten -- Grundbewehrung und Zulage, soweit vorhanden.
        self.posten_je_lage: Dict[int, List[Tuple]] = {
            l.nummer: [eintrag for eintrag in querschnitt.posten_ids
                       if eintrag[0].nummer == l.nummer]
            for l in self.lagen
        }

        basis = f"{querschnitt.id}.nachweis.duktilitaet"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,D,{l.nummer}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Erfüllungsgrad Duktilität – {l.nummer}. Lage",
                referenz="SIA 262:2025, 4.1.4.2.5",
                stellen=2,
            )
            for l in self.lagen
        }
        self.d_verhaeltnis: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.x_zu_d",
                symbol=rf"\left(x/d\right)_{{{l.nummer}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Bezogene Druckzonenhöhe – {l.nummer}. Lage",
                referenz="SIA 262:2025, 4.1.4.2.5",
                stellen=3,
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            # Zwei Breiten, weil zwei Lagen verschiedene Richtungen tragen
            # koennen. x/d bliebe zwar unveraendert, wenn man A_s und b beide
            # verwechselte -- aber nur dann; hier stammt A_s aus dem
            # Lagenaufbau und kennt seine Richtung bereits.
            Eingabebezug("b", querschnitt.id_von("b")),
            Eingabebezug("b_y", querschnitt.id_von("b_y")),
            Eingabebezug("f_cd", querschnitt.beton.id_von("f_cd")),
        ]
        for nummer, eintraege in self.posten_je_lage.items():
            for lage, art, _, as_id, z_id in eintraege:
                marke = f"{nummer}{art.kuerzel}"
                bezuege += [
                    Eingabebezug(f"a_s_{marke}", as_id),
                    Eingabebezug(f"z_{marke}", z_id),
                ]
        for stahl in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            bezuege.append(
                Eingabebezug(f"f_yd__{kennung_aus(stahl.id)}", stahl.id_von("f_yd")))

        self.s_f_cd = mit_index("f_{cd}", querschnitt.beton.symbol_index)

        super().__init__(
            basis,
            ausgaben=(list(self.d_ausnutzung.values())
                      + list(self.d_verhaeltnis.values())),
            bezuege=bezuege,
            titel=f"Duktilitätsnachweis – {querschnitt.name}",
            referenz="SIA 262:2025, 4.1.4.2.5",
            # Wie bei den anderen Nachweisen: ohne Abschnitt stuende er unter
            # der Ueberschrift, die die Rechenreihenfolge zufaellig offen liess.
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        f_cd = e.g("f_cd").si

        self._protokoll_ansatz(p)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for lage in self.lagen:
            # Die Breite in der Richtung der Lage.
            breite = "b" if lage.richtung is Richtung.X else "b_y"
            erg = self._eine_lage(e, lage, h=h, b=e.g(breite).si, f_cd=f_cd)
            self.ergebnisse.append(erg)
            self._protokoll_lage(p, e, erg, breite)

            ergebnis[self.d_ausnutzung[lage.nummer].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            ergebnis[self.d_verhaeltnis[lage.nummer].id] = Groesse(
                erg.verhaeltnis, EINHEITSLOS)
            urteile.append(self._urteil(erg))

        self._protokoll_massgebend(p, urteile)
        return ergebnis, self.teilurteile(urteile)

    def _eine_lage(
        self, e: Eingaben, lage: Bewehrungslage, *,
        h: float, b: float, f_cd: float,
    ) -> Lagenergebnis:
        erg = Lagenergebnis(lage=lage)
        eintraege = self.posten_je_lage[lage.nummer]

        flaechen = [(e.g(f"a_s_{lage.nummer}{art.kuerzel}").si,
                     e.g(f"z_{lage.nummer}{art.kuerzel}").si)
                    for _, art, _, _, _ in eintraege]
        erg.a_s = sum(a for a, _ in flaechen)
        if erg.a_s <= 0.0:
            erg.begruendung = erg.hinweis = (
                f"Nachweis nicht machbar, weil die {lage.nummer}. Lage nicht "
                f"definiert ist. Ohne Bewehrung gibt es keine Druckzone, "
                f"deren Höhe sich begrenzen liesse.")
            return erg

        # Grundbewehrung und Zulage liegen auf leicht verschiedenen Hoehen --
        # sie gehoeren aber zur selben Lage, also zaehlt ihr gemeinsamer
        # Schwerpunkt. Die schwaechere Stahlsorte gaebe es hier nicht: eine
        # Lage traegt genau einen Stahl.
        erg.z = sum(a * z for a, z in flaechen) / erg.a_s
        # Gemessen ab der gedrueckten Randfaser: unten bewehrt heisst oben
        # gedrueckt. Wer hier z stehen liesse, bekaeme bei den oberen Lagen
        # eine Zahl, die keine statische Hoehe ist.
        erg.d = erg.z if lage.von_unten else h - erg.z

        erg.f_sd = e.g(f"f_yd__{kennung_aus(lage.stahl.id)}").si
        erg.x = druckzonenhoehe(a_s=erg.a_s, f_sd=erg.f_sd, b=b, f_cd=f_cd)
        erg.verhaeltnis = erg.x / erg.d if erg.d > 0 else float("inf")
        erg.erfuellt = erg.verhaeltnis <= GRENZE
        erg.erfuellungsgrad = (
            float("inf") if erg.verhaeltnis == 0 else GRENZE / erg.verhaeltnis)
        erg.begruendung = (
            f"x = {erg.x * 1e3:.1f} mm bei d = {erg.d * 1e3:.1f} mm, "
            f"also x/d = {erg.verhaeltnis:.3f} "
            f"{'≤' if erg.erfuellt else '>'} {GRENZE:.2f}.")
        return erg

    def _urteil(self, erg: Lagenergebnis) -> NachweisUrteil:
        nummer = erg.lage.nummer
        einwirkung = WertDef(
            id=self.d_verhaeltnis[nummer].id,
            symbol=rf"\left(x/d\right)_{{{nummer}}}",
            einheit=EINHEITSLOS, beschreibung="Einwirkung", stellen=3,
        ).belegen(Groesse(erg.verhaeltnis, EINHEITSLOS))
        return NachweisUrteil(
            name=f"Duktilität – {nummer}. Lage",
            art="D",
            langname="Duktilität",
            fall=f"{nummer}. Lage",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            # Ohne Bewehrung gibt es kein Verhaeltnis -- dann steht dort ein
            # Strich und daneben der Hinweis, warum.
            einwirkung=einwirkung if erg.machbar else None,
            widerstand=self._grenze(nummer) if erg.machbar else None,
        )

    def _grenze(self, nummer: int) -> Wert:
        """Die zulaessige bezogene Druckzonenhoehe -- Widerstand und Herleitung."""
        return WertDef(
            id=f"{self.id}.lage{nummer}.grenze",
            symbol=r"\left(x/d\right)_{max}",
            einheit=EINHEITSLOS, beschreibung="Widerstand", stellen=2,
        ).belegen(Groesse(GRENZE, EINHEITSLOS))


    def _protokoll_massgebend(self, p: Protokoll,
                              urteile: Sequence[NachweisUrteil]) -> None:
        """
        Welche Lage den Nachweis entscheidet.

        In der Zusammenfassung steht nur eine Zeile -- die schlechtere der
        beiden Lagen. Ohne diesen Satz stuende in der Herleitung beides
        nebeneinander und man muesste die Zahlen selbst vergleichen, um zu
        wissen, welche davon in der Tabelle gelandet ist.
        """
        massgebend = self.massgebend(urteile)
        if len(urteile) < 2 or not massgebend:
            return
        p.text(f"Massgebend ist die {massgebend[0].fall} mit dem kleineren "
               f"Erfüllungsgrad; sie steht in der Zusammenfassung.")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll) -> None:
        p.titel("Duktilität")
        p.text(
            "Die Druckzone muss schlank bleiben, damit der Stahl lange fliesst, "
            "bevor der Beton versagt: der Querschnitt kündigt sein Versagen an. "
            "Gerechnet wird die Druckzonenhöhe bei reiner Biegung, je Lage "
            "einzeln."
        )
        p.gleichung(
            rf"{BLOCKANTEIL} \cdot x \cdot b \cdot {self.s_f_cd} = A_s \cdot f_{{sd}}"
            r" \qquad \Rightarrow \qquad "
            rf"x = \frac{{A_s \cdot f_{{sd}}}}"
            rf"{{{BLOCKANTEIL} \cdot b \cdot {self.s_f_cd}}}",
            titel="Kräftegleichgewicht bei M_Ed = 0",
            referenz="SIA 262:2025, 4.1.4.2.5")
        p.gleichung(
            rf"\frac{{x}}{{d}} \le {GRENZE:.2f}",
            titel="Bedingung")
        p.text(
            "d wird von der gedrückten Randfaser aus gemessen: bei den unteren "
            "Lagen von der Oberkante, bei den oberen von der Unterkante. "
            "Grundbewehrung und Zulage einer Lage zählen mit ihrem gemeinsamen "
            "Schwerpunkt."
        )

    def _protokoll_lage(
        self, p: Protokoll, e: Eingaben, erg: Lagenergebnis, breite: str,
    ) -> None:
        """
        Die Herleitung einer Lage, aus Vorlagen: jede Formel steht einmal mit
        Symbolen da, die Fassung mit Zahlen und Einheiten entsteht daraus.
        """
        nummer = erg.lage.nummer
        p.titel(f"Duktilität – {nummer}. Lage", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        index = self._index(erg)
        werte = Zwischenwerte(f"{self.id}.lage{nummer}")
        s_a_s = f"A_{{s,{index}}}" if index else "A_s"
        s_d = f"d_{{{index}}}" if index else "d"
        s_z = f"z_{{{index}}}" if index else "z"
        # Je Posten Querschnitt und Hoehe ab Oberkante -- dieselben Werte wie
        # in der Tabelle der Platte.
        posten = [(e[f"a_s_{nummer}{art.kuerzel}"], e[f"z_{nummer}{art.kuerzel}"])
                  for _, art, *_ in self.posten_je_lage[nummer]]

        a_s = werte.flaeche("A_s", s_a_s, erg.a_s)
        # Unten bewehrt ist die Hoehe ab Oberkante schon die statische Hoehe.
        z = werte.laenge("z", s_d if erg.lage.von_unten else s_z, erg.z)
        if len(posten) > 1:
            # Grundbewehrung und Zulage liegen auf leicht verschiedenen Hoehen
            # -- ohne diese beiden Zeilen fiele der Schwerpunkt vom Himmel.
            eingaben: Dict[str, Wert] = {}
            for i, (flaeche, hoehe) in enumerate(posten):
                eingaben[f"a{i}"], eingaben[f"z{i}"] = flaeche, hoehe
            summe = " + ".join(f"@a{i}" for i in range(len(posten)))
            momente = " + ".join(rf"@a{i} \cdot @z{i}" for i in range(len(posten)))
            p.formel(a_s, summe, eingaben, titel="Bewehrung der Lage")
            p.formel(z, rf"\frac{{{momente}}}{{{summe}}}", eingaben,
                     titel="Gemeinsamer Schwerpunkt der Lage")
        if erg.lage.von_unten:
            d = z
        else:
            d = werte.laenge("d", s_d, erg.d)
            p.formel(d, "@h - @z", {"h": e["h"], "z": z},
                     titel="Statische Höhe ab der gedrückten Randfaser (unten)")

        x = werte.laenge("x", "x", erg.x)
        p.formel(
            x,
            rf"\frac{{@A_s \cdot @f_sd}}{{{BLOCKANTEIL} \cdot @b \cdot @f_cd}}",
            {"A_s": a_s, "b": e[breite], "f_cd": e["f_cd"],
             "f_sd": werte.spannung(
                 "f_sd", mit_index("f_{sd}", erg.lage.stahl.symbol_index), erg.f_sd)},
            titel="Druckzonenhöhe bei reiner Biegung")

        verhaeltnis = self.d_verhaeltnis[nummer].belegen(
            Groesse(erg.verhaeltnis, EINHEITSLOS))
        grenze = self._grenze(nummer)
        p.formel(verhaeltnis, r"\frac{@x}{@d}", {"x": x, "d": d},
                 titel="Bezogene Druckzonenhöhe")
        p.gleichung(
            bedingung(rf"{verhaeltnis.symbol} = {verhaeltnis.zahl_latex()}",
                      r"\le" if erg.erfuellt else ">",
                      rf"{grenze.symbol} = {grenze.zahl_latex()}", erg.erfuellt),
            titel="Bedingung")
        p.formel(
            self.d_ausnutzung[nummer].belegen(Groesse(erg.erfuellungsgrad, EINHEITSLOS)),
            r"\frac{@grenze}{@verhaeltnis}",
            {"grenze": grenze, "verhaeltnis": verhaeltnis},
            titel="Erfüllungsgrad",
            ergebnis_latex=grad_als_text(erg.erfuellungsgrad, erg.erfuellt, latex=True))

    def _index(self, erg: Lagenergebnis) -> str:
        """
        Der Symbolindex der Lage -- ``1,x`` statt ``1,x,g``.

        Gerechnet wird mit der ganzen Lage, nicht mit einem Posten. Ein
        Postenindex am Symbol behauptete etwas anderes.
        """
        eintraege = self.posten_je_lage[erg.lage.nummer]
        if not eintraege:
            return ""
        lage, art, *_ = eintraege[0]
        if len(eintraege) == 1:
            return posten_index(lage, art)
        return f"{lage.nummer},{lage.richtung.value}"

