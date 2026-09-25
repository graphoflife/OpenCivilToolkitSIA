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
siehe :class:`Erfuellungsart` und :meth:`BiegungNormalkraft._auswerten`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, Groesse
from opencivil.core.latex import Mathe, als_text, angabe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.core.wert import kennung_aus
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
    """Beide Wege werden gerechnet, massgebend ist der kleinere Erfuellungsgrad
    -- siehe :meth:`BiegungNormalkraft._auswerten`. Der Regelfall."""

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
        return kennung_aus(self.name)


@dataclass(frozen=True)
class Normierung:
    """
    Der kuerzeste Abstand im normierten Diagramm -- alles, was die Mitschrift
    davon braucht.

    Normiert wird auf die groesste Normalkraft und das groesste Moment der
    Linie; ohne das haenge der Abstand von der Wahl der Einheiten ab. Der
    Grad ist ``rand / laenge`` -- ein Verhaeltnis von Laengen im Diagramm,
    nicht von Momenten.
    """

    N_ref: float
    M_ref: float
    laenge: float
    """Die Einwirkung als Abstand vom Ursprung."""

    abstand: float
    """Kuerzester Abstand zur Resistenzlinie."""

    rand: float
    """``laenge + abstand`` innerhalb, ``laenge - abstand`` ausserhalb, nicht
    unter null -- der Widerstand im normierten Diagramm."""


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

    normierung: Optional[Normierung] = None
    """Nur beim kuerzesten Abstand: dort ist der Grad kein Verhaeltnis von
    Momenten, sondern von Laengen im normierten Diagramm."""


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
        mit_linie: bool = True,
    ) -> None:
        # 80 Schritte je Abschnitt kosten rund 16 ms. Die Eckwerte sind schon bei
        # 40 Schritten auf fuenf Stellen auskonvergiert; die feinere Teilung
        # dient allein der Zeichnung, weil die Linie nahe dem reinen Druck
        # schnell laeuft und sonst sichtbar eckig wuerde.
        # Ohne Kombinationen bleibt der Nachweis ohne Urteil -- die Eckwerte
        # der Resistenzlinie entstehen trotzdem. Sie sind eine Eigenschaft des
        # Querschnitts, keine der Einwirkung, und andere Nachweise brauchen
        # sie: der gegen sproedes Versagen haelt M_Rd(N=0) gegen das
        # Rissmoment, ganz ohne Schnittgroessen.
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
        self.mit_linie = mit_linie
        """
        Ob die genaue Resistenzlinie mitgerechnet wird.

        Sie kostet fast die ganze Rechenzeit dieses Nachweises -- 482
        Dehnungsebenen mit je 200 Betonfasern, rund 46 ms von 48 -- und das
        Urteil faellt ohne sie: nachgewiesen wird gegen das Polygon aus der
        Handrechnung. Gebraucht wird sie allein im Diagramm.

        Die Bewehrungssuche rechnet je Lauf ein paar Dutzend Mal und sieht
        dabei kein Diagramm an. Sie baut darum ueber ``aufbauen(schnell=True)``
        ohne Linie -- dieselben Zahlen, ein Bruchteil der Zeit.
        """

        self.linie: List[Linienpunkt] = []
        self.auswertungen: List[Auswertung] = []

        self.bei_normalkraft: Dict[str, Optional[Auswertung]] = {}
        """
        Je Kombination der Momentenwiderstand bei der wirkenden Normalkraft --
        samt der Interpolation, aus der er stammt.

        Der Querkraftnachweis rechnet mit genau dieser Groesse und soll sie
        herleiten, statt eine Zahl hinzuschreiben. Er holt sie ueber
        :meth:`widerstand_bei_n`.
        """

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.mn.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: grad_def(
                f"{basis}.{k.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,{r},{als_text(k.name)}}}",
                f"Erfüllungsgrad {richtung.beschriftung} – {k.name}",
                "SIA 262:2025, 4.1.4",
            )
            for k in self.kombinationen
        }
        # Momentenwiderstand bei der tatsaechlich wirkenden Normalkraft, je
        # Kombination. Der Querkraftnachweis braucht genau diesen Wert -- bei
        # Druck liegt er deutlich ueber dem bei N = 0.
        self.d_m_rd: Dict[str, WertDef] = {
            k.name: WertDef(
                id=f"{basis}.{k.kennung}.M_Rd_bei_N_Ed",
                symbol=rf"M_{{Rd,{r}}}(N_{{Ed}})_{{{als_text(k.name)}}}",
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
            Eingabebezug("b", querschnitt.id_breite(richtung)),
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
            kurz = kennung_aus(stahl.id)
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
            # Siehe Querkraft: ohne Abschnitt landet der Nachweis unter der
            # Ueberschrift, die die Rechenreihenfolge zufaellig offen liess.
            abschnitt=querschnitt.abschnitt,
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
        # Wer sie nicht zeichnet, braucht sie nicht; siehe `mit_linie`.
        self.linie = dehnungsfaecher.aufbauen(
            h=h, b=b, lagen=lagen, beton=beton,
            schritte=self.schritte, fasern=self.fasern) if self.mit_linie else []

        # -- Die Handrechnung: das, wogegen nachgewiesen wird ----------------
        # Die Zugehoerigkeit zur unteren oder oberen Lage kommt aus dem Modell
        # (Lagen 1 und 2 liegen unten), nicht aus der Hoehenlage -- siehe
        # lagen_zusammenfassen().
        seiten = lagen_zusammenfassen([
            HandPosten(a_s=a_s, z=z, f_yd=gesetz.f_yd, E_s=gesetz.E_s, text=text,
                       index=posten_index(lage, art),
                       stahl_index=lage.stahl.symbol_index,
                       von_unten=lage.von_unten)
            for (a_s, z, gesetz, text), (lage, art, *_) in zip(lagen, self.posten)
        ])
        self.handrechnung = Handrechnung(
            h=h, b=b, f_cd=beton.f_cd, eps_c2d=beton.eps_c2d,
            unten=seiten["unten"], oben=seiten["oben"],
            richtung=self.richtung.beschriftung, basis=self.id,
            beton_index=self.querschnitt.beton.symbol_index,
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
        self.bei_normalkraft = {}
        urteile: List[NachweisUrteil] = []
        for kombination in self.kombinationen:
            auswertung = self._auswerten(kombination, eckwerte)
            self.auswertungen.append(auswertung)
            self._protokoll_kombination(p, auswertung, eckwerte)
            ergebnis[self.d_ausnutzung[kombination.name].id] = Groesse(
                auswertung.erfuellungsgrad, EINHEITSLOS
            )
            # Unabhaengig vom gewaehlten Massstab: der Momentenwiderstand bei
            # dieser Normalkraft, denn der Querkraftnachweis rechnet damit.
            bei_n = self._messen(kombination, geo.MOMENT, auswertung.innerhalb)
            self.bei_normalkraft[kombination.name] = bei_n
            ergebnis[self.d_m_rd[kombination.name].id] = Groesse.aus_si(
                abs(bei_n.rd) if bei_n else 0.0, KNM)
            urteile.append(
                NachweisUrteil(
                    name=f"M-N-Nachweis {self.richtung.value} – {kombination.name}",
                    art="M-N",
                    ziel=self.d_ausnutzung[kombination.name].id,
                    langname="Biegung und Normalkraft",
                    fall=kombination.name,
                    erfuellt=auswertung.innerhalb,
                    erfuellungsgrad=Groesse(auswertung.erfuellungsgrad, EINHEITSLOS),
                    begruendung=auswertung.begruendung,
                    einwirkung=self._als_wert(auswertung, "Ed"),
                    widerstand=self._als_wert(auswertung, "Rd"),
                )
            )
        return ergebnis, urteile

    def moment_bei(self, N_Ed: float, positiv: bool) -> Optional[float]:
        """
        Der Momentenwiderstand bei dieser Normalkraft, auf der gewaehlten Seite.

        Fuer beliebige Normalkraefte, nicht nur die der Kombinationen: die
        Querkraftkurve laesst den Benutzer ein N_Ed einstellen und braucht dann
        den passenden Widerstand. Beide Seiten des Polygons sind moeglich --
        positiv (Zug unten) und negativ (Zug oben).

        ``None``, wenn die Normalkraft ausserhalb der Resistenzlinie liegt.

        :param N_Ed: Normalkraft in N, Zug positiv.
        :return: Moment in Nm, Betrag der gewaehlten Seite.
        """
        treffer = geo.kante(self.handlinie, geo.MOMENT, N_Ed, positiv=positiv)
        return None if treffer is None else abs(treffer[0])

    def widerstand_bei_n(self, kombination: str) -> Optional[Auswertung]:
        """
        Der Momentenwiderstand bei der Normalkraft dieser Kombination.

        Liegt erst nach dem Lauf vor. Der Querkraftnachweis darf sich darauf
        verlassen: er fuehrt ``d_m_rd`` als Eingang, und damit steht die
        Reihenfolge im Graphen statt in einer Annahme.
        """
        return self.bei_normalkraft.get(kombination)

    def _als_wert(self, auswertung: Auswertung, seite: str):
        """
        Verpackt Einwirkung bzw. Widerstand als darstellbaren Wert.

        Welche Groesse verglichen wird, haengt vom Massstab ab -- bei
        'Normalkraft konstant' das Moment, bei 'Moment konstant' die Normalkraft.
        Das Urteil traegt deshalb Symbol und Einheit selbst mit sich. Beim
        kuerzesten Abstand sind es Laengen im normierten Diagramm -- sonst
        stuenden zwei Momente da, deren Quotient nicht der Grad ist.
        """
        if auswertung.normierung is not None:
            einwirkung, widerstand = self._normiert(auswertung)
            return einwirkung if seite == "Ed" else widerstand
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

    def _auswerten(
        self, kombination: Schnittgroessen, eckwerte: Mapping[str, float]
    ) -> Auswertung:
        """
        Bestimmt den Erfuellungsgrad einer Kombination.

        Gemessen wird gegen das Polygon aus der Handrechnung, nicht gegen die
        genaue Linie -- damit die Zahl im Urteil dieselbe ist, die in der
        Herleitung Schritt fuer Schritt hergeleitet wird.

        Bei ``AUTOMATISCH`` werden **beide** Wege gerechnet -- der
        Momentenwiderstand bei festgehaltener Normalkraft und der
        Normalkraftwiderstand bei festgehaltenem Moment -- und der kleinere
        Erfuellungsgrad gilt. Vorher entschied eine Schwelle am Anteil der
        Grenznormalkraft, in welcher Richtung gemessen wird; das war eine
        Faustregel, die nahe den Spitzen der Linie den groesseren der beiden
        Werte stehen lassen konnte.

        Der Vergleich erscheint **nicht** in der Mitschrift. Er ist kein
        Rechenschritt, sondern die Festlegung, in welcher Richtung gemessen
        wird; was dann gerechnet wurde, steht vollstaendig da.
        """
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        innerhalb = geo.innerhalb(N_Ed, M_Ed, self.handlinie)

        art = kombination.art
        if art is Erfuellungsart.NAECHSTER_PUNKT:
            return self._naechster(kombination, eckwerte, innerhalb)

        achsen = ((geo.MOMENT, geo.NORMALKRAFT) if art is Erfuellungsart.AUTOMATISCH
                  else (ACHSE_ZU[art],))
        gemessen = [self._messen(kombination, achse, innerhalb) for achse in achsen]
        gueltig = [g for g in gemessen if g is not None]
        if not gueltig:
            return Auswertung(
                kombination, innerhalb, 0.0, None,
                "In dieser Richtung schneidet die Resistenzlinie nicht – die "
                "Einwirkung liegt ganz ausserhalb des aufnehmbaren Bereichs.",
                massstab=(Erfuellungsart.NORMALKRAFT_KONSTANT
                          if art is Erfuellungsart.AUTOMATISCH else art))
        return min(gueltig, key=lambda g: g.erfuellungsgrad)

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
        rand = max(laenge + abstand if innerhalb else laenge - abstand, 0.0)
        grad = float("inf") if laenge == 0 else rand / laenge
        return Auswertung(
            kombination, innerhalb, grad, stelle,
            f"Kürzester Abstand zur Resistenzlinie im normierten Diagramm: "
            f"{abstand:.3f}. Nächster Punkt: N = {_in(stelle[0], geo.NORMALKRAFT)}, "
            f"M = {_in(stelle[1], geo.MOMENT)}.",
            achse=geo.MOMENT, ed=M_Ed, rd=stelle[1],
            massstab=Erfuellungsart.NAECHSTER_PUNKT,
            normierung=Normierung(N_ref, M_ref, laenge, abstand, rand))

    # -- Mitschrift ---------------------------------------------------------


    def _normiert(self, auswertung: Auswertung) -> Tuple[Wert, Wert]:
        """Einwirkung und Widerstand im normierten Diagramm -- fuer Tabelle und Herleitung."""
        n, r = auswertung.normierung, self.richtung.value
        werte = Zwischenwerte(f"{self.id}.{auswertung.schnittgroessen.kennung}")
        return (werte.zahl("E_norm", rf"\bar{{E}}_{{d,{r}}}", n.laenge, "Einwirkung"),
                werte.zahl("R_norm", rf"\bar{{R}}_{{d,{r}}}", n.rand, "Widerstand"))

    def _protokoll_kombination(self, p: Protokoll, auswertung: Auswertung,
                               eckwerte: Mapping[str, float]) -> None:
        k = auswertung.schnittgroessen
        p.titel(f"Nachweis – {k.name}", ebene=3)
        p.gleichung(
            rf"M_{{Ed}} = {k.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {k.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung",
        )
        basis = f"{self.id}.{k.kennung}"
        if auswertung.normierung is not None:
            ed, rd = self._protokoll_naechster(p, auswertung, eckwerte, basis)
        else:
            protokoll_interpolation(p, auswertung, basis=basis)
            werte, achse = Zwischenwerte(basis), auswertung.achse
            rd, ed = (werte.wert(name, f"{achse.name}_{{{name}}}",
                                 Groesse.aus_si(abs(si), achse.einheit))
                      for name, si in (("Rd", auswertung.rd), ("Ed", auswertung.ed)))
        grad_formel(p, self.d_ausnutzung[k.name], auswertung.erfuellungsgrad,
                    rd, ed, auswertung.innerhalb, mit_urteil=True)

    def _protokoll_naechster(
        self, p: Protokoll, auswertung: Auswertung, eckwerte: Mapping[str, float],
        basis: str,
    ) -> Tuple[Wert, Wert]:
        """
        Der kuerzeste Abstand, Schritt fuer Schritt -- und daraus Einwirkung und
        Widerstand im normierten Diagramm, deren Quotient der Grad ist.
        """
        n, k = auswertung.normierung, auswertung.schnittgroessen
        werte = Zwischenwerte(basis)
        eck = {name: self.d_eckwerte[name].belegen(
                   Groesse.aus_si(eckwerte[name], KN if name.startswith("N") else KNM))
               for name in ("N_Rd_zug", "N_Rd_druck", "M_Rd_max", "M_Rd_min")}
        N_ref = werte.kraft("N_ref", "N_{ref}", n.N_ref)
        M_ref = werte.moment("M_ref", "M_{ref}", n.M_ref)
        p.formel(N_ref, r"\max\left(\left|@a\right|;\ \left|@b\right|\right)",
                 {"a": eck["N_Rd_zug"], "b": eck["N_Rd_druck"]},
                 titel="Bezugsgrösse der Normalkraft")
        p.formel(M_ref, r"\max\left(\left|@a\right|;\ \left|@b\right|\right)",
                 {"a": eck["M_Rd_max"], "b": eck["M_Rd_min"]},
                 titel="Bezugsgrösse des Moments")

        einwirkung, widerstand = self._normiert(auswertung)
        N_Ed = werte.kraft("N_Ed", "N_{Ed}", k.N_Ed.si)
        M_Ed = werte.moment("M_Ed", "M_{Ed}", k.M_Ed.si)
        p.formel(einwirkung,
                 r"\sqrt{\left(\frac{@N_Ed}{@N_ref}\right)^{2} + "
                 r"\left(\frac{@M_Ed}{@M_ref}\right)^{2}}",
                 {"N_Ed": N_Ed, "M_Ed": M_Ed, "N_ref": N_ref, "M_ref": M_ref},
                 titel="Einwirkung im normierten Diagramm")

        N_P = werte.kraft("N_P", "N_P", auswertung.widerstand[0])
        M_P = werte.moment("M_P", "M_P", auswertung.widerstand[1])
        p.gleichung(rf"{angabe(N_P)} \qquad {angabe(M_P)}",
                    titel="Nächster Punkt P der Resistenzlinie")
        abstand = werte.zahl("a", "a", n.abstand)
        p.formel(abstand,
                 r"\sqrt{\left(\frac{@N_Ed - @N_P}{@N_ref}\right)^{2} + "
                 r"\left(\frac{@M_Ed - @M_P}{@M_ref}\right)^{2}}",
                 {"N_Ed": N_Ed, "M_Ed": M_Ed, "N_P": N_P, "M_P": M_P,
                  "N_ref": N_ref, "M_ref": M_ref},
                 titel="Kürzester Abstand zur Resistenzlinie")
        # Innerhalb liegt der Rand um a weiter aussen, ausserhalb um a innen.
        vorlage = "@E + @a" if auswertung.innerhalb else r"\max\left(@E - @a;\ 0\right)"
        p.formel(widerstand, vorlage, {"E": einwirkung, "a": abstand},
                 titel="Widerstand im normierten Diagramm")
        return einwirkung, widerstand


def protokoll_interpolation(
    p: Protokoll, auswertung: Auswertung, titel: str = "",
    *, basis: str,
) -> None:
    """
    Schreibt, wie der Widerstand auf dem Polygon gefunden wurde.

    Ohne diesen Schritt stuende in der Mitschrift eine Zahl, die zwar aus
    nachvollziehbaren Eckpunkten stammt, aber selbst vom Himmel faellt. Hier
    steht, zwischen welchen beiden Punkten geradlinig interpoliert wurde und
    mit welchem Anteil.

    Frei und nicht an :class:`BiegungNormalkraft` gebunden: der
    Querkraftnachweis rechnet mit dem Momentenwiderstand bei der wirkenden
    Normalkraft und muss dieselbe Interpolation zeigen. Zweimal geschrieben
    liefe sie frueher oder spaeter auseinander.

    Faellt die festgehaltene Groesse genau auf einen Eckpunkt -- der haeufige
    Fall ``N_Ed = 0``, und ebenso ``M_Ed = 0`` bei reiner Normalkraft --, wird
    nicht interpoliert. Dort stuende sonst ein Bruch mit null im Zaehler, der
    nichts erklaert und nur so aussieht, als waere etwas gerechnet worden.
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

    # Der Eckpunkt selbst, falls die Einwirkung genau auf ihm liegt. Geprueft
    # wird auch der Zielwert: bei einer Kante laengs der festgehaltenen Achse
    # traefen beide Stuetzpunkte zu, und nur einer davon ist der Widerstand.
    treffer = next(
        (q for q in (a, b)
         if _trifft(lauf.von(q), fest) and _trifft(ziel.von(q), auswertung.rd)),
        None)

    werte = Zwischenwerte(basis)

    def wert(name: str, symbol: str, si: float, achse: geo.Achse):
        return werte.wert(name, symbol, Groesse.aus_si(si, achse.einheit))

    rd = wert("Rd", f"{ziel.name}_{{Rd}}", auswertung.rd, ziel)
    if treffer is not None:
        p.formel(rd, "@P", {"P": wert("P", treffer.symbol, ziel.von(treffer), ziel)},
                 titel=titel or (f"Widerstand bei {lauf.name}_Ed = "
                                 f"{_k(fest)} {lauf.einheit.beschriftung} – "
                                 f"ein Eckpunkt liegt genau dort"))
        return

    p.formel(
        rd, r"@x_1 + \frac{@y_Ed - @y_1}{@y_2 - @y_1} \cdot \left(@x_2 - @x_1\right)",
        {"x_1": wert("x_1", f"{ziel.name}_1", ziel.von(a), ziel),
         "x_2": wert("x_2", f"{ziel.name}_2", ziel.von(b), ziel),
         "y_1": wert("y_1", f"{lauf.name}_1", lauf.von(a), lauf),
         "y_2": wert("y_2", f"{lauf.name}_2", lauf.von(b), lauf),
         "y_Ed": wert("y_Ed", f"{lauf.name}_{{Ed}}", fest, lauf)},
        titel=titel or (f"Widerstand bei festgehaltenem {lauf.name}_Ed = "
                        f"{_k(fest)} {lauf.einheit.beschriftung}"),
    )
    p.tabelle(
        kopf=["Punkt", Mathe(rf"{lauf.name}\ [{e_lauf}]"),
              Mathe(rf"{ziel.name}\ [{e_ziel}]")],
        zeilen=[
            [Mathe(q.symbol), Mathe(_k(lauf.von(q))), Mathe(_k(ziel.von(q)))]
            for q in (a, b)
        ],
        titel="Stützpunkte der Interpolation",
        ausrichtung="lrr",
    )



def _trifft(a: float, b: float) -> bool:
    """
    Ob zwei SI-Werte fuer die Mitschrift als derselbe gelten.

    Die Schranke haengt an der Groesse der Werte, nicht an einer festen Zahl:
    Momente liegen im Bereich 1e5 Nm, und dort ist ein absoluter Abstand von
    1e-9 unerreichbar streng.
    """
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def _k(si_wert: float) -> str:
    """Ein SI-Wert in Kilo-Einheiten, eine Nachkommastelle."""
    return f"{si_wert / 1e3:.1f}"


def _in(si_wert: float, achse: geo.Achse) -> str:
    """Ein SI-Wert in der Einheit seiner Achse, mit Einheitenzeichen."""
    g = Groesse.aus_si(si_wert, achse.einheit)
    return f"{g.formatiert(1)} {achse.einheit.beschriftung}"

