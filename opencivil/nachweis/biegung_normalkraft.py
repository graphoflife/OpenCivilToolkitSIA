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

Die Mitschrift dafuer ist erhalten, aber stillgelegt -- siehe den Block
"STILLGELEGT" weiter unten.

WIE DIE PRAEZISE RESISTENZLINIE ENTSTEHT:
Alle zulaessigen Dehnungsebenen bilden einen Faecher. Welche Grenze ihn
begrenzt, wechselt unterwegs dreimal -- entsprechend wird er in drei
Abschnitten je Momentenvorzeichen abgefahren:

    1a  Drehung um die unterste Lage bei eps_ud; die Oberkante geht von Zug
        bis auf -eps_c2d. Massgebend ist der Stahl.
    1b  Drehung um die Oberkante bei -eps_c2d; die Unterkante geht bis auf
        null. Massgebend ist die gedrueckte Randfaser.
    1c  Drehung um den Punkt C; die Unterkante geht bis auf -eps_c1d.
        Der Querschnitt ist ganz gedrueckt, massgebend ist eps_c1d.
    2a/2b/2c  dasselbe spiegelbildlich mit Zug oben     (M < 0)

Der Punkt C liegt bei z_C = h * (1 - eps_c1d / eps_c2d) ab dem gedrueckten Rand
und traegt die Dehnung -eps_c1d. Er ist noetig, weil beim vollstaendig
gedrueckten Querschnitt nicht mehr die Randfaser massgebend ist: reiner Druck
endet bei gleichmaessig -eps_c1d, nicht bei -eps_c2d. Ohne diesen Abschnitt
liefe die Linie an beiden Enden ueber die wahre Grenze hinaus und schnitte sich
selbst -- womit Punkt-in-Linie-Test und Schnittsuche und damit jedes Urteil
unbrauchbar waeren.

Anfang (gleichmaessiger Zug bei eps_ud) und Ende (gleichmaessiger Druck bei
eps_c1d) sind beiden Faechern gemeinsam, sodass sich eine geschlossene Linie
ergibt. Deckungsgleiche Punkte -- solange alles fliesst, aendern N und M sich
nicht -- werden anschliessend zusammengefasst.

Zu jeder Dehnungsebene werden N und M durch Integration ueber den Querschnitt
bestimmt: der Beton als Faserintegration nach der Parabel-Rechteck-Beziehung,
die Bewehrung lagenweise nach der bilinearen Beziehung. Die von der Bewehrung
verdraengte Betonflaeche wird abgezogen.

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
from opencivil.nachweis import linie as geo
from opencivil.nachweis.handrechnung import (
    Eckpunkt, Handrechnung, lagen_zusammenfassen,
)
from opencivil.querschnitt.platte import Plattenquerschnitt, Richtung
from opencivil.querschnitt.werkstoffgesetz import (
    Betongesetz, Dehnungsebene, Stahlgesetz,
)


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


@dataclass(frozen=True)
class Linienpunkt:
    """Ein Punkt der Resistenzlinie samt der Dehnungsebene, die ihn erzeugt."""

    N: float
    """Normalkraft in N (Zug positiv)."""

    M: float
    """Moment in Nm (Zug unten positiv)."""

    eps_oben: float
    eps_unten: float
    abschnitt: str = ""


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

    groesse: str = "M"
    """Welche Grösse verglichen wird -- 'M' oder 'N'. Haengt vom Massstab ab."""

    ed: float = 0.0
    """Einwirkung in der verglichenen Groesse, in SI (N bzw. Nm)."""

    rd: float = 0.0
    """Widerstand in derselben Groesse, in SI."""

    massstab: Erfuellungsart = Erfuellungsart.NORMALKRAFT_KONSTANT
    """Welcher Massstab tatsaechlich gegriffen hat."""

    kante: Optional[Tuple["Eckpunkt", "Eckpunkt"]] = None
    """Zwischen welchen beiden Eckpunkten interpoliert wurde -- fuer die
    Mitschrift, damit dort nicht bloss das Ergebnis steht."""


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

    def _lagen(self, e: Eingaben) -> List[Tuple[float, float, Stahlgesetz, str]]:
        """Je Bewehrungsposten dieser Richtung: (Fläche m^2, z m, Gesetz, Text)."""
        gesetze: Dict[str, Stahlgesetz] = {}
        for stahl in {l.stahl.id: l.stahl for l, _, _, _, _ in self.posten}.values():
            kurz = _kennung(stahl.id)
            gesetze[stahl.id] = Stahlgesetz.aus_werten({
                kennwert: e[f"{kennwert}__{kurz}"]
                for kennwert in ("E_s", "f_yd", "f_yd_druck", "eps_ud")
            })

        lagen = []
        for lage, art, _, _, _ in self.posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            lagen.append((
                e.g(f"a_s_{marke}").si,
                e.g(f"z_{marke}").si,
                gesetze[lage.stahl.id],
                f"{lage.nummer}. Lage {art.beschriftung}",
            ))
        return lagen

    def _schnittgroessen(
        self, ebene: Dehnungsebene, beton: Betongesetz, lagen, h: float, b: float
    ) -> Tuple[float, float]:
        """Integriert N und M zu einer Dehnungsebene. Rueckgabe in N und Nm."""
        N = 0.0
        M = 0.0
        dz = h / self.fasern
        flaeche = b * dz
        for k in range(self.fasern):
            z = (k + 0.5) * dz
            kraft = beton.spannung(ebene.bei(z)) * flaeche
            N += kraft
            M += kraft * (z - h / 2.0)

        for a_s, z, stahl, _ in lagen:
            # Die vom Stahl verdraengte Betonflaeche wieder abziehen.
            eps = ebene.bei(z)
            kraft = (stahl.spannung(eps) - beton.spannung(eps)) * a_s
            N += kraft
            M += kraft * (z - h / 2.0)
        return N, M

    def _faecher(
        self, h: float, lagen, beton: Betongesetz
    ) -> List[Tuple[str, Dehnungsebene]]:
        """
        Baut die Folge der Dehnungsebenen -- die eigentliche Prozedur.

        Beide Faecher laufen von gleichmaessigem Zug bis zu gleichmaessigem
        Druck; zusammengesetzt ergeben sie die geschlossene Resistenzlinie.
        """
        eps_c1d, eps_c2d = beton.eps_c1d, beton.eps_c2d
        beton_grenze = -eps_c2d
        z_unten = max(z for _, z, _, _ in lagen)
        z_oben = min(z for _, z, _, _ in lagen)
        eps_ud_unten = min(s.eps_ud for _, z, s, _ in lagen if z == z_unten)
        eps_ud_oben = min(s.eps_ud for _, z, s, _ in lagen if z == z_oben)

        ebenen: List[Tuple[str, Dehnungsebene]] = []

        def strecke(
            marke: str,
            eps_fest: float, z_fest: float,
            eps_von: float, eps_bis: float, z_lauf: float,
            ab: int = 0,
        ) -> Dehnungsebene:
            for i in range(ab, self.schritte + 1):
                anteil = i / self.schritte
                eps_lauf = eps_von + (eps_bis - eps_von) * anteil
                ebenen.append((
                    marke,
                    Dehnungsebene.durch_zwei_punkte(eps_fest, z_fest, eps_lauf, z_lauf, h),
                ))
            return ebenen[-1][1]

        # Drehpunkt C: sobald die Nulllinie den Querschnitt verlassen hat, ist
        # nicht mehr die Randfaser massgebend. Fuer den vollstaendig gedrueckten
        # Querschnitt gilt die Stauchung eps_c1d, und alle Ebenen dieses
        # Abschnitts laufen durch den Punkt
        #     z_C = h * (1 - eps_c1d / eps_c2d)   ab dem gedrueckten Rand
        # mit der Dehnung -eps_c1d. Der reine Druck endet folglich bei
        # gleichmaessig -eps_c1d, nicht bei -eps_c2d.
        #
        # Ohne diesen dritten Abschnitt lief die Linie an beiden Enden ueber die
        # wahre Grenze hinaus und schnitt sich selbst.
        anteil_c = 1.0 - eps_c1d / eps_c2d
        z_c_oben = h * anteil_c          # von der Oberkante, wenn oben gedrueckt
        z_c_unten = h * (1.0 - anteil_c)  # von der Oberkante, wenn unten gedrueckt

        # Faecher 1 -- Zug unten, positives Moment
        ende_1a = strecke("1a", eps_ud_unten, z_unten, eps_ud_unten, beton_grenze, 0.0)
        strecke("1b", beton_grenze, 0.0, ende_1a.eps_unten, 0.0, h, ab=1)
        strecke("1c", -eps_c1d, z_c_oben, 0.0, -eps_c1d, h, ab=1)

        # Faecher 2 -- Zug oben, negatives Moment; rueckwaerts angehaengt, damit
        # eine geschlossene Linie entsteht.
        merker = len(ebenen)
        ende_2a = strecke("2a", eps_ud_oben, z_oben, eps_ud_oben, beton_grenze, h)
        strecke("2b", beton_grenze, h, ende_2a.eps_oben, 0.0, 0.0, ab=1)
        strecke("2c", -eps_c1d, z_c_unten, 0.0, -eps_c1d, 0.0, ab=1)
        rueck = ebenen[merker:]
        del ebenen[merker:]
        ebenen.extend(reversed(rueck))
        return ebenen

    # -- Nachweis -----------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        beton = Betongesetz.aus_werten({
            k: e[k] for k in ("f_cd", "eps_c1d", "eps_c2d", "k_sigma")
        })
        lagen = self._lagen(e)

        # -- Die genaue Linie: nur fuer das Diagramm, ohne Mitschrift --------
        # Sie entsteht aus hunderten Faserintegrationen und liesse sich von Hand
        # nicht nachrechnen. Sie herzuleiten hiesse, dem Leser Zeilen vorzusetzen,
        # die er nur glauben kann. Sie steht im Diagramm zum Vergleich -- das
        # Urteil faellt ueber die Handrechnung darunter.
        ebenen = self._faecher(h, lagen, beton)
        self.linie = geo.ohne_wiederholungen([
            Linienpunkt(
                *self._schnittgroessen(ebene, beton, lagen, h, b),
                eps_oben=ebene.eps_oben,
                eps_unten=ebene.eps_unten,
                abschnitt=marke,
            )
            for marke, ebene in ebenen
        ])

        # -- Die Handrechnung: das, wogegen nachgewiesen wird ----------------
        # Die Zugehoerigkeit zur unteren oder oberen Lage kommt aus dem Modell
        # (Lagen 1 und 2 liegen unten), nicht aus der Hoehenlage -- siehe
        # lagen_zusammenfassen().
        seiten = lagen_zusammenfassen([
            (a_s, z, gesetz.f_yd, gesetz.E_s, text, posten[0].von_unten)
            for (a_s, z, gesetz, text), posten in zip(lagen, self.posten)
        ])
        self.handrechnung = Handrechnung(
            h=h, b=b, f_cd=beton.f_cd, eps_c2d=beton.eps_c2d,
            unten=seiten["unten"], oben=seiten["oben"],
            richtung=self.richtung.beschriftung, basis=self.id,
        )
        self.handlinie = self.handrechnung.rechnen(p)

        bei_null = geo.schnitte_bei_N(self.handlinie, 0.0)
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
            bei_n = self._bei_n_konstant(kombination, auswertung.innerhalb)
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
        ist_moment = auswertung.groesse == "M"
        einheit = KNM if ist_moment else KN
        zahl = auswertung.ed if seite == "Ed" else auswertung.rd
        r = self.richtung.value

        # Der Widerstand gilt nur unter der festgehaltenen Gegengroesse -- das
        # gehoert ins Symbol, sonst liest sich M_Rd wie ein fester Kennwert.
        symbol = f"{auswertung.groesse}_{{{seite},{r}}}"
        if seite == "Rd":
            if ist_moment:
                fest = Groesse.aus_si(auswertung.schnittgroessen.N_Ed.si, KN)
                symbol = rf"M_{{Rd,{r}}}(N_{{Ed}} = {fest.formatiert(1)}\,\mathrm{{kN}})"
            else:
                fest = Groesse.aus_si(auswertung.schnittgroessen.M_Ed.si, KNM)
                symbol = rf"N_{{Rd,{r}}}(M_{{Ed}} = {fest.formatiert(1)}\,\mathrm{{kNm}})"

        definition = WertDef(
            id=f"{self.id}.{auswertung.schnittgroessen.kennung}.{auswertung.groesse}_{seite}",
            symbol=symbol,
            einheit=einheit,
            beschreibung=("Einwirkung" if seite == "Ed" else "Widerstand"),
            stellen=1,
        )
        return definition.belegen(Groesse.aus_si(zahl, einheit))

    #: Ab welchem Anteil der Grenznormalkraft senkrecht gemessen wird.
    #: Bewusst verschieden: die Linie ist nicht symmetrisch, auf der Druckseite
    #: bleibt sie laenger brauchbar waagrecht als auf der Zugseite.
    SCHWELLE_ZUG = 0.25
    SCHWELLE_DRUCK = 0.6

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
        if N_Ed > 0.0 and abs(N_Ed) > abs(eckwerte["N_Rd_zug"]) * self.SCHWELLE_ZUG:
            return Erfuellungsart.MOMENT_KONSTANT
        if N_Ed < 0.0 and abs(N_Ed) > abs(eckwerte["N_Rd_druck"]) * self.SCHWELLE_DRUCK:
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
        if art is Erfuellungsart.MOMENT_KONSTANT:
            ergebnis = self._bei_m_konstant(kombination, innerhalb)
        else:
            ergebnis = self._bei_n_konstant(kombination, innerhalb)

        if ergebnis is None:
            return Auswertung(
                kombination, innerhalb, 0.0, None,
                "In dieser Richtung schneidet die Resistenzlinie nicht – die "
                "Einwirkung liegt ganz ausserhalb des aufnehmbaren Bereichs.",
                massstab=art)
        return ergebnis

    def _bei_n_konstant(
        self, kombination: Schnittgroessen, innerhalb: bool
    ) -> Optional[Auswertung]:
        """Bei festgehaltener Normalkraft waagrecht bis zur Momentengrenze."""
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        kante = geo.kante_bei_N(self.handlinie, N_Ed, positiv=M_Ed >= 0)
        if kante is None:
            return None
        M_Rd, a, b = kante
        grad = float("inf") if M_Ed == 0 else abs(M_Rd) / abs(M_Ed)
        return Auswertung(
            kombination, innerhalb, grad, (N_Ed, M_Rd),
            f"Bei festgehaltenem N_Ed = {_kn(N_Ed)} kN beträgt der "
            f"Momentenwiderstand M_Rd = {_knm(M_Rd)} kNm.",
            groesse="M", ed=M_Ed, rd=M_Rd,
            massstab=Erfuellungsart.NORMALKRAFT_KONSTANT,
            kante=(a, b))

    def _bei_m_konstant(
        self, kombination: Schnittgroessen, innerhalb: bool
    ) -> Optional[Auswertung]:
        """Bei festgehaltenem Moment senkrecht bis zur Normalkraftgrenze."""
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        kante = geo.kante_bei_M(self.handlinie, M_Ed, positiv=N_Ed >= 0)
        if kante is None:
            return None
        N_Rd, a, b = kante
        grad = float("inf") if N_Ed == 0 else abs(N_Rd) / abs(N_Ed)
        return Auswertung(
            kombination, innerhalb, grad, (N_Rd, M_Ed),
            f"Bei festgehaltenem M_Ed = {_knm(M_Ed)} kNm beträgt der "
            f"Normalkraftwiderstand N_Rd = {_kn(N_Rd)} kN.",
            groesse="N", ed=N_Ed, rd=N_Rd,
            massstab=Erfuellungsart.MOMENT_KONSTANT,
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
            groesse="M", ed=M_Ed, rd=stelle[1],
            massstab=Erfuellungsart.NAECHSTER_PUNKT)

    # -- Mitschrift ---------------------------------------------------------

    # =======================================================================
    # STILLGELEGT -- die Herleitung der genauen Linie
    #
    # Die folgenden drei Methoden schreiben den Dehnungsebenen-Ansatz, die
    # Stuetzstellen des Faechers und die Eckwerte der genauen Linie. Sie werden
    # derzeit von niemandem aufgerufen: die genaue Linie dient nur noch dem
    # Vergleich im Diagramm, hergeleitet wird die Handrechnung.
    #
    # Sie bleiben vollstaendig stehen, weil der Inhalt spaeter wieder gebraucht
    # wird. Wer sie reaktiviert, ruft sie in pruefe() auf -- gerechnet wird die
    # genaue Linie ohnehin weiter, es fehlt allein die Mitschrift.
    # =======================================================================

    def _protokoll_ansatz(self, p: Protokoll, beton: Betongesetz, lagen, e: Eingaben) -> None:
        p.titel("Ansatz")
        p.text(
            "Der Querschnitt bleibt eben (Bernoulli). Zu jeder zulässigen "
            "Dehnungsebene werden Normalkraft und Moment durch Integration über "
            "die Querschnittshöhe bestimmt. Zug ist positiv, das Moment bezieht "
            "sich auf die halbe Querschnittshöhe."
        )
        p.gleichung(beton.latex(), titel="Beton – Parabel-Rechteck-Beziehung",
                    referenz="SIA 262:2025, 4.2.1.6")
        p.gleichung(lagen[0][2].latex(), titel="Betonstahl – bilineare Beziehung",
                    referenz="SIA 262:2025, 4.2.2.4")
        p.gleichung(
            r"N = \int_A \sigma\,\mathrm{d}A \qquad "
            r"M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A",
            titel="Schnittgrössen aus der Spannungsverteilung",
        )
        p.text(
            f"Der Beton wird in {self.fasern} Fasern über die Höhe integriert, "
            f"die Bewehrung lagenweise. Die von der Bewehrung verdrängte "
            f"Betonfläche wird abgezogen."
        )
        p.tabelle(
            kopf=[r"\text{Lage}", r"a_s\ [\mathrm{mm}^2]", r"z\ [\mathrm{mm}]",
                  r"f_{yd}\ [\mathrm{N/mm^2}]"],
            zeilen=[
                [als_text(beschriftung),
                 f"{a_s * 1e6:.0f}", f"{z * 1e3:.1f}", f"{stahl.f_yd / 1e6:.0f}"]
                for a_s, z, stahl, beschriftung in lagen
            ],
            titel="Berücksichtigte Bewehrungslagen",
            ausrichtung="lrrr",
        )

    def _protokoll_linie(self, p: Protokoll) -> None:
        p.titel("Aufbau der Resistenzlinie")
        p.text(
            f"Der Dehnungsfächer wird in vier Abschnitten mit je "
            f"{self.schritte} Schritten abgefahren; das ergibt "
            f"{len(self.linie)} Punkte. Ausgewiesen ist jeder Abschnittsanfang "
            f"und jedes Abschnittsende."
        )
        zeilen = []
        vorher = None
        for i, punkt in enumerate(self.linie):
            grenze = (
                vorher is None
                or punkt.abschnitt != vorher
                or i == len(self.linie) - 1
                or self.linie[i + 1].abschnitt != punkt.abschnitt
            )
            if grenze:
                zeilen.append([
                    punkt.abschnitt,
                    f"{punkt.eps_oben * 1000:.2f}",
                    f"{punkt.eps_unten * 1000:.2f}",
                    f"{punkt.N / 1e3:.1f}",
                    f"{punkt.M / 1e3:.1f}",
                ])
            vorher = punkt.abschnitt
        p.tabelle(
            kopf=[r"\text{Abschn.}", r"\varepsilon_{oben}\ [\text{‰}]",
                  r"\varepsilon_{unten}\ [\text{‰}]",
                  r"N\ [\mathrm{kN}]", r"M\ [\mathrm{kNm}]"],
            zeilen=zeilen,
            titel="Stützstellen des Dehnungsfächers",
            ausrichtung="lrrrr",
        )

    def _protokoll_eckwerte(self, p: Protokoll, ergebnis: Mapping[str, Groesse]) -> None:
        """Eckwerte der genauen Linie. Stillgelegt, siehe Block oben."""
        p.tabelle(
            kopf=[r"\text{Eckwert}", r"\text{Symbol}", r"\text{Wert}"],
            zeilen=[
                [als_text(beschreibung), symbol,
                 ergebnis[self.d_eckwerte[schluessel].id].als_latex(1)]
                for schluessel, symbol, beschreibung in (
                    ("N_Rd_zug", "N_{Rd}^{+}", "grösste Zugkraft"),
                    ("N_Rd_druck", "N_{Rd}^{-}", "grösste Druckkraft"),
                    ("M_Rd_max", "M_{Rd}^{+}", "grösstes Moment"),
                    ("M_Rd_min", "M_{Rd}^{-}", "kleinstes Moment"),
                )
            ],
            titel="Eckwerte der Resistenzlinie",
            ausrichtung="lcr",
        )

    # ================= Ende des stillgelegten Blocks =======================

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
        gross = auswertung.groesse
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
        ist_moment = auswertung.groesse == "M"
        # Waagrecht wird ueber N interpoliert, senkrecht ueber M.
        lauf_a, lauf_b = (a.N, b.N) if ist_moment else (a.M, b.M)
        ziel_a, ziel_b = (a.M, b.M) if ist_moment else (a.N, b.N)
        stelle = auswertung.schnittgroessen.N_Ed.si if ist_moment \
            else auswertung.schnittgroessen.M_Ed.si

        lauf, ziel = ("N", "M") if ist_moment else ("M", "N")
        e_lauf = r"\mathrm{kN}" if ist_moment else r"\mathrm{kNm}"
        e_ziel = r"\mathrm{kNm}" if ist_moment else r"\mathrm{kN}"

        p.text(
            f"Der Bemessungspunkt liegt zwischen den Eckpunkten "
            f"«{a.name}» und «{b.name}». Dazwischen verläuft die Linie "
            f"geradlinig, der Widerstand folgt also durch lineare Interpolation."
        )
        p.gleichung(
            rf"{ziel}_{{Rd}} = {ziel}_1 + \frac{{{lauf}_{{Ed}} - {lauf}_1}}"
            rf"{{{lauf}_2 - {lauf}_1}} \cdot \left({ziel}_2 - {ziel}_1\right)"
            "\n= "
            rf"{ziel_a / 1e3:.1f} + \frac{{{stelle / 1e3:.1f} - {lauf_a / 1e3:.1f}}}"
            rf"{{{lauf_b / 1e3:.1f} - {lauf_a / 1e3:.1f}}} \cdot "
            rf"\left({ziel_b / 1e3:.1f} - {ziel_a / 1e3:.1f}\right)"
            rf" = {auswertung.rd / 1e3:.1f}\,{e_ziel}",
            titel=(f"Widerstand bei festgehaltenem {lauf}_Ed = "
                   f"{stelle / 1e3:.1f} {'kN' if ist_moment else 'kNm'}"),
        )
        p.tabelle(
            kopf=[r"\text{Punkt}", rf"{lauf}\ [{e_lauf}]", rf"{ziel}\ [{e_ziel}]"],
            zeilen=[
                [als_text(a.name), f"{lauf_a / 1e3:.1f}", f"{ziel_a / 1e3:.1f}"],
                [als_text(b.name), f"{lauf_b / 1e3:.1f}", f"{ziel_b / 1e3:.1f}"],
            ],
            titel="Stützpunkte der Interpolation",
            ausrichtung="lrr",
        )


def _kennung(text: str) -> str:
    return "".join(z if z.isalnum() else "_" for z in text)


def _kn(si_wert: float) -> str:
    """Formatiert eine Kraft, die in SI-Basis (N) vorliegt, als Kilonewton."""
    return Groesse.aus_si(si_wert, KN).formatiert(1)


def _knm(si_wert: float) -> str:
    """Formatiert ein Moment, das in SI-Basis (Nm) vorliegt, als Kilonewtonmeter."""
    return Groesse.aus_si(si_wert, KNM).formatiert(1)
