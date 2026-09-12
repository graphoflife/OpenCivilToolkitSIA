"""
opencivil/nachweis/biegung_normalkraft.py -- Nachweis für Biegung mit Normalkraft.

VERANTWORTUNG:
Prueft beliebig viele Schnittgroessenkombinationen gegen die M-N-Interaktion
eines Querschnitts.

ZWEI LINIEN, EINE DAVON MASSGEBEND:
* **Resistenzlinie aus Handrechnung** -- das Polygon aus wenigen Eckpunkten in
  :mod:`opencivil.nachweis.handrechnung`. Dagegen wird nachgewiesen, und ihre
  Herleitung steht vollstaendig in der Mitschrift.
* **Praezise Resistenzlinie** -- die punktweise aus Dehnungsebenen aufgebaute
  Linie, unten beschrieben. Sie wird weiterhin gerechnet und im Diagramm
  gezeigt, aber **nicht mehr hergeleitet**: sie entsteht aus hunderten
  Faserintegrationen, die niemand mit dem Taschenrechner nachvollzieht. Wer
  sie herleiten liesse, lieferte Zeilen zum Glauben statt zum Pruefen.

Wie sie entsteht und warum die Mitschrift dafuer stillgelegt ist, steht in
:mod:`opencivil.nachweis.dehnungsfaecher`.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite (Feldmoment)
Bezugsachse fuer M ist die halbe Querschnittshoehe.

EINHEITEN:
N und M gelten fuer die betrachtete Breite ``b``. Mit ``b = 1 m`` sind es also
unmittelbar die Werte pro Laufmeter.

ERFUELLUNGSGRAD:
Ob ein Punkt drin liegt oder nicht, entscheidet immer derselbe Test (Punkt in
geschlossener Linie), angewandt auf das Polygon der Handrechnung. Nur *wie
weit* er von der Linie entfernt ist, haengt vom gewaehlten Massstab ab --
siehe :class:`Erfuellungsart` und :meth:`BiegungNormalkraft._massstab`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, MM, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.nachweis import dehnungsfaecher, linie as geo
from opencivil.nachweis.handrechnung import (
    Eckpunkt, Handrechnung, Posten as HandPosten, lagen_zusammenfassen,
)
from opencivil.querschnitt.platte import (
    Plattenquerschnitt, Richtung, posten_index,
)
from opencivil.querschnitt.werkstoffgesetz import Betongesetz


class Erfuellungsart(str, Enum):
    """Massstab, in dem der Abstand zur Resistenzlinie gemessen wird."""

    AUTOMATISCH = "automatisch"
    """Waagrecht, ausser nahe den Spitzen der Linie -- siehe
    :meth:`BiegungNormalkraft._massstab`. Der Regelfall."""

    NORMALKRAFT_KONSTANT = "N_konstant"
    """Bei festgehaltener Normalkraft waagrecht bis zur Momentengrenze.
    Der Regelfall: die Normalkraft ist meist vorgegeben, aufnehmen muss der
    Querschnitt das Moment."""

    MOMENT_KONSTANT = "M_konstant"
    """Bei festgehaltenem Moment senkrecht bis zur Normalkraftgrenze."""

    NAECHSTER_PUNKT = "naechster_Punkt"
    """Kuerzester Weg zur Linie, gemessen im auf die Groesstwerte normierten
    Diagramm (sonst waere der Abstand von der Wahl der Einheiten abhaengig)."""

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return {
            Erfuellungsart.AUTOMATISCH: "automatisch",
            Erfuellungsart.NORMALKRAFT_KONSTANT: "Normalkraft konstant",
            Erfuellungsart.MOMENT_KONSTANT: "Moment konstant",
            Erfuellungsart.NAECHSTER_PUNKT: "kürzester Abstand",
        }[self]


@dataclass(frozen=True)
class Schnittgroessen:
    """Eine zu prüfende Kombination aus Moment und Normalkraft."""

    name: str
    M_Ed: Groesse
    N_Ed: Groesse = field(default_factory=lambda: Groesse(0, KN))
    art: Erfuellungsart = Erfuellungsart.AUTOMATISCH

    @property
    def kennung(self) -> str:
        return "".join(z if z.isalnum() else "_" for z in self.name)


@dataclass
class Auswertung:
    """Ergebnis der Prüfung einer Kombination."""

    schnittgroessen: Schnittgroessen
    innerhalb: bool
    erfuellungsgrad: float
    """Widerstand/Einwirkung -- ab 1 erfuellt. Unendlich, wenn nichts einwirkt."""

    widerstand: Optional[Tuple[float, float]]
    """Der massgebende Punkt auf der Linie als (N, M) in N bzw. Nm."""

    begruendung: str = ""

    achse: geo.Achse = geo.MOMENT
    """Auf welcher Achse verglichen wird. Haengt vom Massstab ab."""

    ed: float = 0.0
    """Einwirkung in der verglichenen Groesse, in SI (N bzw. Nm)."""

    rd: float = 0.0
    """Widerstand in derselben Groesse, in SI."""

    massstab: Erfuellungsart = Erfuellungsart.NORMALKRAFT_KONSTANT
    """Welcher Massstab tatsaechlich gegriffen hat."""

    kante: Optional[Tuple["Eckpunkt", "Eckpunkt"]] = None
    """Zwischen welchen beiden Eckpunkten interpoliert wurde -- fuer die
    Mitschrift, damit dort nicht bloss das Ergebnis steht."""


#: Welche Achse ein Massstab sucht. Die einzige Stelle, an der die beiden
#: Begriffe zusammenkommen -- Erfuellungsart ist fuer die Oberflaeche da,
#: Achse fuer die Geometrie.
ACHSE_ZU: Dict[Erfuellungsart, geo.Achse] = {
    Erfuellungsart.NORMALKRAFT_KONSTANT: geo.MOMENT,
    Erfuellungsart.MOMENT_KONSTANT: geo.NORMALKRAFT,
}
MASSSTAB: Dict[str, Erfuellungsart] = {
    a.name: m for m, a in ACHSE_ZU.items()
}

#: Ab welchem Anteil der Grenznormalkraft senkrecht gemessen wird. Bewusst
#: verschieden: die Linie ist nicht symmetrisch, auf der Druckseite bleibt sie
#: laenger brauchbar waagrecht als auf der Zugseite.
SCHWELLE_ZUG = 0.25
SCHWELLE_DRUCK = 0.6


# ===========================================================================
# Nachweis
# ===========================================================================


class BiegungNormalkraft(Nachweis):
    """
    Nachweis der Biege- und Normalkrafttragfaehigkeit über die M-N-Interaktion.

    Erzeugt für jede Kombination einen Erfüllungsgrad und ein Urteil. Gemessen
    wird gegen das Polygon aus der Handrechnung (:attr:`handlinie`); die genaue
    Linie (:attr:`linie`) wird mitgerechnet und steht im Diagramm daneben.
    """

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        kombinationen: Sequence[Schnittgroessen],
        richtung: Richtung = Richtung.X,
        *,
        schritte: int = 80,
        fasern: int = 200,
    ) -> None:
        # 80 Schritte je Abschnitt kosten rund 16 ms. Die Eckwerte sind schon bei
        # 40 Schritten auf fuenf Stellen auskonvergiert; die feinere Teilung
        # dient allein der Zeichnung, weil die Linie nahe dem reinen Druck
        # schnell laeuft und sonst sichtbar eckig wuerde.
        if not kombinationen:
            raise ValueError("Der Nachweis braucht mindestens eine Kombination.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} liegt "
                f"keine Bewehrung, ein Nachweis ist dort nicht möglich."
            )
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.kombinationen = list(kombinationen)
        self.schritte = schritte
        self.fasern = fasern
        self.linie: List[Linienpunkt] = []
        self.auswertungen: List[Auswertung] = []

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.mn.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: WertDef(
                id=f"{basis}.{k.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,{r},{k.kennung}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Erfüllungsgrad {richtung.beschriftung} – {k.name}",
                referenz="SIA 262:2025, 4.1.4",
                stellen=3,
            )
            for k in self.kombinationen
        }
        # Momentenwiderstand bei der tatsaechlich wirkenden Normalkraft, je
        # Kombination. Der Querkraftnachweis braucht genau diesen Wert -- bei
        # Druck liegt er deutlich ueber dem bei N = 0.
        self.d_m_rd: Dict[str, WertDef] = {
            k.name: WertDef(
                id=f"{basis}.{k.kennung}.M_Rd_bei_N_Ed",
                symbol=rf"M_{{Rd,{r}}}(N_{{Ed}})_{{{k.kennung}}}",
                einheit=KNM,
                beschreibung=(f"Momentenwiderstand bei N_Ed "
                              f"({richtung.beschriftung}) – {k.name}"),
                referenz="SIA 262:2025, 4.1.4",
                stellen=1,
            )
            for k in self.kombinationen
        }
        self.d_eckwerte = {
            "N_Rd_zug": WertDef(f"{basis}.N_Rd_zug", f"N_{{Rd,{r}}}^{{+}}", KN,
                                f"Grösste aufnehmbare Zugkraft ({richtung.beschriftung})",
                                stellen=1),
            "N_Rd_druck": WertDef(f"{basis}.N_Rd_druck", f"N_{{Rd,{r}}}^{{-}}", KN,
                                  f"Grösste aufnehmbare Druckkraft ({richtung.beschriftung})",
                                  stellen=1),
            "M_Rd_max": WertDef(f"{basis}.M_Rd_max", f"M_{{Rd,{r}}}^{{+}}", KNM,
                                f"Grösster positiver Momentenwiderstand ({richtung.beschriftung})",
                                stellen=1),
            "M_Rd_min": WertDef(f"{basis}.M_Rd_min", f"M_{{Rd,{r}}}^{{-}}", KNM,
                                f"Grösster negativer Momentenwiderstand ({richtung.beschriftung})",
                                stellen=1),
            # Wird vom Querkraftnachweis gebraucht -- darum eine eigene Ausgabe
            # und keine im Nachweis versteckte Zwischengrösse.
            "M_Rd_N0_pos": WertDef(f"{basis}.M_Rd_N0_pos", f"M_{{Rd,{r}}}(N=0)^{{+}}", KNM,
                                   f"Momentenwiderstand bei N = 0, positiv ({richtung.beschriftung})",
                                   stellen=1),
            "M_Rd_N0_neg": WertDef(f"{basis}.M_Rd_N0_neg", f"M_{{Rd,{r}}}(N=0)^{{-}}", KNM,
                                   f"Momentenwiderstand bei N = 0, negativ ({richtung.beschriftung})",
                                   stellen=1),
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_von("b")),
            Eingabebezug("f_cd", querschnitt.beton.id_von("f_cd")),
            Eingabebezug("eps_c1d", querschnitt.beton.id_von("eps_c1d")),
            Eingabebezug("eps_c2d", querschnitt.beton.id_von("eps_c2d")),
            Eingabebezug("k_sigma", querschnitt.beton.id_von("k_sigma")),
        ]
        # Nur die Bewehrung dieser Richtung geht ein -- Querbewehrung traegt
        # nichts zum Momentenwiderstand um diese Achse bei.
        for lage, art, _, as_id, z_id in self.posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            bezuege += [
                Eingabebezug(f"a_s_{marke}", as_id),
                Eingabebezug(f"z_{marke}", z_id),
            ]
        for stahl in {l.stahl.id: l.stahl for l, _, _, _, _ in self.posten}.values():
            kurz = _kennung(stahl.id)
            for kennwert in ("E_s", "f_yd", "f_yd_druck", "eps_ud"):
                bezuege.append(
                    Eingabebezug(f"{kennwert}__{kurz}", stahl.id_von(kennwert))
                )

        super().__init__(
            basis,
            ausgaben=(list(self.d_ausnutzung.values()) + list(self.d_eckwerte.values())
                      + list(self.d_m_rd.values())),
            bezuege=bezuege,
            titel=f"M-N-Nachweis {richtung.beschriftung} – {querschnitt.name}",
            referenz="SIA 262:2025, 4.1.4",
        )

    # -- Querschnittswerte --------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        beton = Betongesetz.aus_werten({
            k: e[k] for k in ("f_cd", "eps_c1d", "eps_c2d", "k_sigma")
        })
        lagen = dehnungsfaecher.lagen_aus_eingaben(self.posten, e)

        # Die genaue Linie: nur fuer das Diagramm, ohne Mitschrift. Sie steht
        # zum Vergleich daneben -- das Urteil faellt ueber die Handrechnung.
        self.linie = dehnungsfaecher.aufbauen(
            h=h, b=b, lagen=lagen, beton=beton,
            schritte=self.schritte, fasern=self.fasern)

        # -- Die Handrechnung: das, wogegen nachgewiesen wird ----------------
        # Die Zugehoerigkeit zur unteren oder oberen Lage kommt aus dem Modell
        # (Lagen 1 und 2 liegen unten), nicht aus der Hoehenlage -- siehe
        # lagen_zusammenfassen().
        seiten = lagen_zusammenfassen([
            HandPosten(a_s=a_s, z=z, f_yd=gesetz.f_yd, E_s=gesetz.E_s, text=text,
                       index=posten_index(lage, art), von_unten=lage.von_unten)
            for (a_s, z, gesetz, text), (lage, art, *_) in zip(lagen, self.posten)
        ])
        self.handrechnung = Handrechnung(
            h=h, b=b, f_cd=beton.f_cd, eps_c2d=beton.eps_c2d,
            unten=seiten["unten"], oben=seiten["oben"],
            richtung=self.richtung.beschriftung, basis=self.id,
        )
        self.handlinie = self.handrechnung.rechnen(p)

        bei_null = geo.schnitte(self.handlinie, geo.MOMENT, 0.0)
        eckwerte = {
            "N_Rd_zug": max(pt.N for pt in self.handlinie),
            "N_Rd_druck": min(pt.N for pt in self.handlinie),
            "M_Rd_max": max(pt.M for pt in self.handlinie),
            "M_Rd_min": min(pt.M for pt in self.handlinie),
            "M_Rd_N0_pos": max([m for m in bei_null if m >= 0] or [0.0]),
            "M_Rd_N0_neg": min([m for m in bei_null if m <= 0] or [0.0]),
        }
        # Achtung: die Eckwerte liegen in SI-Basis vor (N bzw. Nm), darum
        # aus_si() -- Groesse(x, KN) wuerde x als Kilonewton lesen.
        ergebnis: Dict[str, Groesse] = {
            self.d_eckwerte[k].id: Groesse.aus_si(v, KN if k.startswith("N") else KNM)
            for k, v in eckwerte.items()
        }

        self.auswertungen = []
        urteile: List[NachweisUrteil] = []
        for kombination in self.kombinationen:
            auswertung = self._auswerten(kombination, eckwerte)
            self.auswertungen.append(auswertung)
            self._protokoll_kombination(p, auswertung)
            ergebnis[self.d_ausnutzung[kombination.name].id] = Groesse(
                min(auswertung.erfuellungsgrad, 1e9), EINHEITSLOS
            )
            # Unabhaengig vom gewaehlten Massstab: der Momentenwiderstand bei
            # dieser Normalkraft, denn der Querkraftnachweis rechnet damit.
            bei_n = self._messen(kombination, geo.MOMENT, auswertung.innerhalb)
            ergebnis[self.d_m_rd[kombination.name].id] = Groesse.aus_si(
                abs(bei_n.rd) if bei_n else 0.0, KNM)
            urteile.append(
                NachweisUrteil(
                    name=f"M-N-Nachweis {self.richtung.value} – {kombination.name}",
                    erfuellt=auswertung.innerhalb,
                    erfuellungsgrad=Groesse(auswertung.erfuellungsgrad, EINHEITSLOS),
                    begruendung=auswertung.begruendung,
                    einwirkung=self._als_wert(auswertung, "Ed"),
                    widerstand=self._als_wert(auswertung, "Rd"),
                )
            )
        return ergebnis, urteile

    def _als_wert(self, auswertung: Auswertung, seite: str):
        """
        Verpackt Einwirkung bzw. Widerstand als darstellbaren Wert.

        Welche Groesse verglichen wird, haengt vom Massstab ab -- bei
        'Normalkraft konstant' das Moment, bei 'Moment konstant' die Normalkraft.
        Das Urteil traegt deshalb Symbol und Einheit selbst mit sich.
        """
        achse = auswertung.achse
        einheit = achse.einheit
        zahl = auswertung.ed if seite == "Ed" else auswertung.rd
        r = self.richtung.value

        # Der Widerstand gilt nur unter der festgehaltenen Gegengroesse -- das
        # gehoert ins Symbol, sonst liest sich M_Rd wie ein fester Kennwert.
        symbol = f"{achse.name}_{{{seite},{r}}}"
        if seite == "Rd":
            ed = geo.Stelle(N=auswertung.schnittgroessen.N_Ed.si,
                            M=auswertung.schnittgroessen.M_Ed.si)
            fest = Groesse.aus_si(achse.gegen.von(ed), achse.gegen.einheit)
            symbol = (rf"{achse.name}_{{Rd,{r}}}({achse.gegen.name}_{{Ed}} = "
                      rf"{fest.als_latex(1)})")

        definition = WertDef(
            id=f"{self.id}.{auswertung.schnittgroessen.kennung}.{achse.name}_{seite}",
            symbol=symbol,
            einheit=einheit,
            beschreibung=("Einwirkung" if seite == "Ed" else "Widerstand"),
            stellen=1,
        )
        return definition.belegen(Groesse.aus_si(zahl, einheit))

    def _massstab(
        self, N_Ed: float, eckwerte: Mapping[str, float]
    ) -> Erfuellungsart:
        """
        Welcher Massstab bei ``AUTOMATISCH`` gilt.

        Waagrecht (Momentenwiderstand bei festgehaltener Normalkraft) ist der
        Regelfall. Nahe den beiden Spitzen der Linie taugt er aber nicht mehr:
        dort laeuft die Grenze fast waagrecht, und eine kleine Aenderung der
        Normalkraft wirft den Momentenwiderstand weit herum. Dann wird senkrecht
        gemessen -- der Normalkraftwiderstand bei festgehaltenem Moment.

        Diese Wahl erscheint **nicht** in der Mitschrift. Sie ist kein
        Rechenschritt, sondern die Festlegung, in welcher Richtung gemessen
        wird; was dann gerechnet wird, steht vollstaendig da.
        """
        if N_Ed > 0.0 and abs(N_Ed) > abs(eckwerte["N_Rd_zug"]) * SCHWELLE_ZUG:
            return Erfuellungsart.MOMENT_KONSTANT
        if N_Ed < 0.0 and abs(N_Ed) > abs(eckwerte["N_Rd_druck"]) * SCHWELLE_DRUCK:
            return Erfuellungsart.MOMENT_KONSTANT
        return Erfuellungsart.NORMALKRAFT_KONSTANT

    def _auswerten(
        self, kombination: Schnittgroessen, eckwerte: Mapping[str, float]
    ) -> Auswertung:
        """
        Bestimmt den Erfuellungsgrad einer Kombination.

        Gemessen wird gegen das Polygon aus der Handrechnung, nicht gegen die
        genaue Linie -- damit die Zahl im Urteil dieselbe ist, die in der
        Herleitung Schritt fuer Schritt hergeleitet wird.
        """
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        innerhalb = geo.innerhalb(N_Ed, M_Ed, self.handlinie)

        art = kombination.art
        if art is Erfuellungsart.AUTOMATISCH:
            art = self._massstab(N_Ed, eckwerte)

        if art is Erfuellungsart.NAECHSTER_PUNKT:
            return self._naechster(kombination, eckwerte, innerhalb)

        ergebnis = self._messen(kombination, ACHSE_ZU[art], innerhalb)
        if ergebnis is None:
            return Auswertung(
                kombination, innerhalb, 0.0, None,
                "In dieser Richtung schneidet die Resistenzlinie nicht – die "
                "Einwirkung liegt ganz ausserhalb des aufnehmbaren Bereichs.",
                massstab=art)
        return ergebnis

    def _messen(
        self, kombination: Schnittgroessen, achse: geo.Achse, innerhalb: bool
    ) -> Optional[Auswertung]:
        """
        Widerstand auf einer Achse, bei festgehaltener Gegenachse.

        Waagrecht und senkrecht sind derselbe Vorgang mit vertauschten Achsen --
        deshalb eine Methode. Die Einwirkung wird dafuer als Punkt derselben
        Ebene gelesen; damit fallen die Sonderfaelle weg.
        """
        ed = geo.Stelle(N=kombination.N_Ed.si, M=kombination.M_Ed.si)
        fest = achse.gegen.von(ed)
        gesucht = achse.von(ed)

        treffer = geo.kante(self.handlinie, achse, fest, positiv=gesucht >= 0)
        if treffer is None:
            return None
        rd, a, b = treffer

        grad = float("inf") if gesucht == 0 else abs(rd) / abs(gesucht)
        return Auswertung(
            kombination, innerhalb, grad,
            widerstand=(ed.N, rd) if achse is geo.MOMENT else (rd, ed.M),
            begruendung=(
                f"Bei festgehaltenem {achse.gegen.name}_Ed = "
                f"{_in(fest, achse.gegen)} beträgt der "
                f"{achse.widerstand} {achse.name}_Rd = "
                f"{_in(rd, achse)}."),
            achse=achse, ed=gesucht, rd=rd,
            massstab=MASSSTAB[achse.name],
            kante=(a, b))

    def _naechster(
        self, kombination: Schnittgroessen, eckwerte: Mapping[str, float],
        innerhalb: bool,
    ) -> Auswertung:
        """Kuerzester Abstand, im auf die Eckwerte normierten Diagramm."""
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        N_ref = max(abs(eckwerte["N_Rd_zug"]), abs(eckwerte["N_Rd_druck"])) or 1.0
        M_ref = max(abs(eckwerte["M_Rd_max"]), abs(eckwerte["M_Rd_min"])) or 1.0
        abstand, stelle = geo.naechster_punkt(
            N_Ed, M_Ed, self.handlinie, N_ref, M_ref)
        laenge = math.hypot(N_Ed / N_ref, M_Ed / M_ref)
        rand = laenge + abstand if innerhalb else laenge - abstand
        grad = float("inf") if laenge == 0 else max(rand, 0.0) / laenge
        return Auswertung(
            kombination, innerhalb, grad, stelle,
            f"Kürzester Abstand zur Resistenzlinie im normierten Diagramm: "
            f"{abstand:.3f}. Nächster Punkt: N = {_kn(stelle[0])} kN, "
            f"M = {_knm(stelle[1])} kNm.",
            achse=geo.MOMENT, ed=M_Ed, rd=stelle[1],
            massstab=Erfuellungsart.NAECHSTER_PUNKT)

    # -- Mitschrift ---------------------------------------------------------


    def _protokoll_kombination(self, p: Protokoll, auswertung: Auswertung) -> None:
        k = auswertung.schnittgroessen
        p.titel(f"Nachweis – {k.name}", ebene=3)
        p.gleichung(
            rf"M_{{Ed}} = {k.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {k.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung",
        )
        self._protokoll_interpolation(p, auswertung)

        zustand = r"\text{erfüllt}" if auswertung.innerhalb else r"\text{NICHT erfüllt}"
        wert = (
            r"\infty" if math.isinf(auswertung.erfuellungsgrad)
            else f"{auswertung.erfuellungsgrad:.2f}"
        )
        gross = auswertung.achse.name
        p.gleichung(
            rf"\alpha_{{eff}} = \frac{{{gross}_{{Rd}}}}{{{gross}_{{Ed}}}} "
            rf"= \frac{{{abs(auswertung.rd) / 1e3:.1f}}}{{{abs(auswertung.ed) / 1e3:.1f}}} "
            rf"= {wert} \quad \Rightarrow \quad {zustand}"
            if auswertung.ed
            else rf"\alpha_{{eff}} = \frac{{R_d}}{{E_d}} = {wert} "
                 rf"\quad \Rightarrow \quad {zustand}",
            titel="Erfüllungsgrad",
        )

    def _protokoll_interpolation(self, p: Protokoll, auswertung: Auswertung) -> None:
        """
        Schreibt, wie der Widerstand auf dem Polygon gefunden wurde.

        Ohne diesen Schritt stuende in der Mitschrift eine Zahl, die zwar aus
        nachvollziehbaren Eckpunkten stammt, aber selbst vom Himmel faellt.
        Hier steht, zwischen welchen beiden Punkten geradlinig interpoliert
        wurde und mit welchem Anteil.
        """
        if auswertung.kante is None:
            p.text(auswertung.begruendung)
            return

        a, b = auswertung.kante
        ziel = auswertung.achse          # was gesucht wird
        lauf = ziel.gegen                # was dabei festgehalten bleibt
        ed = geo.Stelle(N=auswertung.schnittgroessen.N_Ed.si,
                        M=auswertung.schnittgroessen.M_Ed.si)
        fest = lauf.von(ed)

        e_lauf = lauf.einheit.latex
        e_ziel = ziel.einheit.latex

        p.gleichung(
            rf"{ziel.name}_{{Rd}} = {ziel.name}_1 + "
            rf"\frac{{{lauf.name}_{{Ed}} - {lauf.name}_1}}"
            rf"{{{lauf.name}_2 - {lauf.name}_1}} \cdot "
            rf"\left({ziel.name}_2 - {ziel.name}_1\right)"
            "\n= "
            rf"{_k(ziel.von(a))} + "
            rf"\frac{{{_k(fest)} - {_klammer(lauf.von(a))}}}"
            rf"{{{_k(lauf.von(b))} - {_klammer(lauf.von(a))}}} \cdot "
            rf"\left({_k(ziel.von(b))} - {_klammer(ziel.von(a))}\right)"
            rf" = {_k(auswertung.rd)}\,{e_ziel}",
            titel=(f"Widerstand bei festgehaltenem {lauf.name}_Ed = "
                   f"{_k(fest)} {lauf.einheit.beschriftung}"),
        )
        p.tabelle(
            kopf=[r"\text{Punkt}", rf"{lauf.name}\ [{e_lauf}]",
                  rf"{ziel.name}\ [{e_ziel}]"],
            zeilen=[
                [q.symbol, _k(lauf.von(q)), _k(ziel.von(q))]
                for q in (a, b)
            ],
            titel="Stützpunkte der Interpolation",
            ausrichtung="lrr",
        )


def _kennung(text: str) -> str:
    return "".join(z if z.isalnum() else "_" for z in text)


def _k(si_wert: float) -> str:
    """Ein SI-Wert in Kilo-Einheiten, eine Nachkommastelle."""
    return f"{si_wert / 1e3:.1f}"


def _klammer(si_wert: float) -> str:
    """
    Wie :func:`_k`, aber negative Werte in Klammern.

    Steht ein negativer Wert hinter einem Minuszeichen, ergaebe sich sonst
    ``100.0 - -6000.0``. Mit Klammern liest es sich als das, was es ist.
    """
    text = _k(si_wert)
    return f"\\left({text}\\right)" if si_wert < 0 else text


def _in(si_wert: float, achse: geo.Achse) -> str:
    """Ein SI-Wert in der Einheit seiner Achse, mit Einheitenzeichen."""
    g = Groesse.aus_si(si_wert, achse.einheit)
    return f"{g.formatiert(1)} {achse.einheit.beschriftung}"


def _kn(si_wert: float) -> str:
    """Formatiert eine Kraft, die in SI-Basis (N) vorliegt, als Kilonewton."""
    return Groesse.aus_si(si_wert, KN).formatiert(1)


def _knm(si_wert: float) -> str:
    """Formatiert ein Moment, das in SI-Basis (Nm) vorliegt, als Kilonewtonmeter."""
    return Groesse.aus_si(si_wert, KNM).formatiert(1)
