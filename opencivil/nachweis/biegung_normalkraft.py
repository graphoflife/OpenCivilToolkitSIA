"""
opencivil/nachweis/biegung_normalkraft.py -- Nachweis für Biegung mit Normalkraft.

VERANTWORTUNG:
Prueft beliebig viele Schnittgroessenkombinationen gegen die M-N-Interaktion
eines Querschnitts.

ZWEI LINIEN, EINE DAVON MASSGEBEND:
Welche massgebend ist, waehlt das Kapitel (:class:`Rechenwahl`):

* **Handrechnung Block 0.85·x** -- das Polygon aus wenigen Eckpunkten in
  :mod:`opencivil.nachweis.handrechnung`. Seine Herleitung steht
  vollstaendig in der Mitschrift.
* **Block 0.85·x genau** oder **Parabel** -- der Rand des Dehnungsfaechers,
  mit der gedrueckten Bewehrung. Den Widerstand bei der Einwirkung sucht er
  genau; in die Mitschrift kommt die Probe dieses Bruchzustands, nicht die
  Suche.

Beide stehen hinter derselben Schnittstelle
(:mod:`opencivil.nachweis.resistenzlinie`). Die andere Linie steht zum
Vergleich im Diagramm: die Parabel neben der Handrechnung, sonst die
Handrechnung.

Mit charakteristischen Werten heissen die Widerstaende ``N_Rk`` und
``M_Rk``; die Kennungen der Werte bleiben dieselben.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite (Feldmoment)
Bezugsachse fuer M ist die halbe Querschnittshoehe.

EINHEITEN:
N und M gelten fuer die betrachtete Breite ``b``. Mit ``b = 1 m`` sind es also
unmittelbar die Werte pro Laufmeter.

ERFUELLUNGSGRAD:
Ob ein Punkt drin liegt oder nicht, entscheidet die massgebende Linie
(:meth:`Widerstandslinie.innerhalb`). Nur *wie weit* er von ihr entfernt ist,
haengt vom gewaehlten Massstab ab -- siehe :class:`Erfuellungsart` und
:meth:`BiegungNormalkraft._auswerten`.
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
from opencivil.core.latex import als_text, angabe
from opencivil.core.protokoll import Protokoll, StillesProtokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.core.wert import kennung_aus
from opencivil.nachweis import dehnungsfaecher, linie as geo
from opencivil.nachweis.dehnungsfaecher import Linienpunkt
from opencivil.nachweis.handrechnung import (
    Eckpunkt, Handrechnung, Posten as HandPosten, lagen_zusammenfassen,
)
from opencivil.nachweis.querschnittsloeser import Werkstoffsatz
from opencivil.nachweis.rechenwahl import (
    RECHENARTEN, Rechenart, Rechenwahl, betongesetz, protokoll_rechenwahl,
)
from opencivil.nachweis.resistenzlinie import (
    Ebenenlinie, Handlinie, Treffer, Widerstandslinie,
)
from opencivil.querschnitt.platte import (
    Plattenquerschnitt, Richtung, posten_index,
)


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

    treffer: Optional[Treffer] = None
    """Wo auf der Linie der Widerstand liegt -- zwischen welchen Stuetzpunkten,
    bei der Ebenenlinie auch auf welcher Ebene. Fuer die Mitschrift, damit
    dort nicht bloss das Ergebnis steht."""

    linie: Optional[Widerstandslinie] = None
    """Die Linie, die ihn geliefert hat -- sie schreibt, wie."""

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
    wird gegen die Linie der Wahl (:attr:`massgebend`); die andere
    (:attr:`vergleich`) steht im Diagramm daneben.
    """

    THEMA = "Biegung und Normalkraft"

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        kombinationen: Sequence[Schnittgroessen],
        richtung: Richtung = Richtung.X,
        *,
        wahl: Rechenwahl = Rechenwahl(),
        schritte: int = dehnungsfaecher.SCHRITTE,
        fasern: int = dehnungsfaecher.FASERN,
        mit_vergleich: bool = True,
    ) -> None:
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
        if wahl.art not in RECHENARTEN:
            raise ValueError(
                f"Eine Resistenzlinie gibt es mit "
                f"{', '.join(a.beschriftung for a in RECHENARTEN)} – "
                f"nicht mit «{wahl.art.beschriftung}».")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.kombinationen = list(kombinationen)
        self.wahl = wahl
        self.schritte = schritte
        self.fasern = fasern
        self.mit_vergleich = mit_vergleich
        """
        Ob die Vergleichslinie mitgerechnet wird.

        Neben der Handrechnung ist das die Parabel, und die kostet fast die
        ganze Rechenzeit dieses Nachweises -- 482 Dehnungsebenen mit je 200
        Betonfasern. Gebraucht wird sie allein im Diagramm. Die
        Bewehrungssuche rechnet je Lauf ein paar Dutzend Mal und sieht dabei
        kein Diagramm an; sie baut darum ueber ``aufbauen(schnell=True)`` ohne
        Vergleich -- dieselben Zahlen, ein Bruchteil der Zeit.
        """

        self.massgebend: Optional[Widerstandslinie] = None
        """Die Linie der Wahl -- gegen sie faellt das Urteil. Nach dem Lauf."""

        self.vergleich: Optional[Widerstandslinie] = None
        """Die andere Linie, fuer das Diagramm -- ohne Mitschrift."""

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
        idx = wahl.index
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
                symbol=rf"M_{{{idx},{r}}}(N_{{Ed}})_{{{als_text(k.name)}}}",
                einheit=KNM,
                beschreibung=(f"Momentenwiderstand bei N_Ed "
                              f"({richtung.beschriftung}) – {k.name}"),
                referenz="SIA 262:2025, 4.1.4",
                stellen=1,
            )
            for k in self.kombinationen
        }
        self.d_eckwerte = {
            "N_Rd_zug": WertDef(f"{basis}.N_Rd_zug", f"N_{{{idx},{r}}}^{{+}}", KN,
                                f"Grösste aufnehmbare Zugkraft ({richtung.beschriftung})",
                                stellen=1),
            "N_Rd_druck": WertDef(f"{basis}.N_Rd_druck", f"N_{{{idx},{r}}}^{{-}}", KN,
                                  f"Grösste aufnehmbare Druckkraft ({richtung.beschriftung})",
                                  stellen=1),
            "M_Rd_max": WertDef(f"{basis}.M_Rd_max", f"M_{{{idx},{r}}}^{{+}}", KNM,
                                f"Grösster positiver Momentenwiderstand ({richtung.beschriftung})",
                                stellen=1),
            "M_Rd_min": WertDef(f"{basis}.M_Rd_min", f"M_{{{idx},{r}}}^{{-}}", KNM,
                                f"Grösster negativer Momentenwiderstand ({richtung.beschriftung})",
                                stellen=1),
            # Wird vom Querkraftnachweis gebraucht -- darum eine eigene Ausgabe
            # und keine im Nachweis versteckte Zwischengrösse.
            "M_Rd_N0_pos": WertDef(f"{basis}.M_Rd_N0_pos", f"M_{{{idx},{r}}}(N=0)^{{+}}", KNM,
                                   f"Momentenwiderstand bei N = 0, positiv ({richtung.beschriftung})",
                                   stellen=1),
            "M_Rd_N0_neg": WertDef(f"{basis}.M_Rd_N0_neg", f"M_{{{idx},{r}}}(N=0)^{{-}}", KNM,
                                   f"Momentenwiderstand bei N = 0, negativ ({richtung.beschriftung})",
                                   stellen=1),
        }

        super().__init__(
            basis,
            ausgaben=(list(self.d_ausnutzung.values()) + list(self.d_eckwerte.values())
                      + list(self.d_m_rd.values())),
            bezuege=linienbezuege(querschnitt, self.posten, richtung, wahl.satz),
            titel=f"M-N-Nachweis {richtung.beschriftung} – {querschnitt.name}",
            referenz="SIA 262:2025, 4.1.4",
            # Siehe Querkraft: ohne Abschnitt landet der Nachweis unter der
            # Ueberschrift, die die Rechenreihenfolge zufaellig offen liess.
            abschnitt=querschnitt.abschnitt,
        )

    # -- Querschnittswerte --------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        wahl = self.wahl
        self.massgebend = self._linie(wahl, e, p)
        # Die andere Linie steht zum Vergleich im Diagramm, ohne Mitschrift:
        # neben der Handrechnung die Parabel, sonst die Handrechnung.
        self.vergleich = None
        if self.mit_vergleich:
            art = (Rechenart.PARABEL if wahl.art is Rechenart.HANDRECHNUNG
                   else Rechenart.HANDRECHNUNG)
            self.vergleich = self._linie(
                Rechenwahl(kriechzahl=wahl.kriechzahl, satz=wahl.satz, art=art),
                e, StillesProtokoll())

        eckwerte = self.massgebend.eckwerte()
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
                    art="M-N",
                    ziel=self.d_ausnutzung[kombination.name].id,
                    fall=kombination.name,
                    erfuellt=auswertung.innerhalb,
                    erfuellungsgrad=Groesse(auswertung.erfuellungsgrad, EINHEITSLOS),
                    begruendung=auswertung.begruendung,
                    einwirkung=self._als_wert(auswertung, "Ed"),
                    widerstand=self._als_wert(auswertung, "Rd"),
                )
            )
        return ergebnis, urteile

    def _linie(self, wahl: Rechenwahl, e: Eingaben, p: Protokoll) -> Widerstandslinie:
        """Die Resistenzlinie einer Wahl -- und ihre Herleitung in ``p``."""
        return resistenzlinie(wahl, e, p, querschnitt=self.querschnitt, posten=self.posten,
                              richtung=self.richtung, basis=self.id,
                              schritte=self.schritte, fasern=self.fasern)

    @property
    def handlinie(self) -> List[Eckpunkt]:
        """Die Eckpunkte der Handrechnung, ob massgebend oder Vergleich -- sonst leer."""
        return next((l.punkte for l in (self.massgebend, self.vergleich)
                     if isinstance(l, Handlinie)), [])

    @property
    def linie(self) -> List[Linienpunkt]:
        """Die Punkte der Linie aus Dehnungsebenen, ob massgebend oder Vergleich."""
        return next((l.punkte for l in (self.massgebend, self.vergleich)
                     if isinstance(l, Ebenenlinie)), [])

    def moment_bei(self, N_Ed: float, positiv: bool) -> Optional[float]:
        """
        Der Momentenwiderstand bei dieser Normalkraft, auf der gewaehlten Seite.

        Fuer beliebige Normalkraefte, nicht nur die der Kombinationen: die
        Querkraftkurve laesst den Benutzer ein N_Ed einstellen und braucht dann
        den passenden Widerstand. Beide Seiten der Linie sind moeglich --
        positiv (Zug unten) und negativ (Zug oben).

        ``None``, wenn die Normalkraft ausserhalb der Resistenzlinie liegt.

        :param N_Ed: Normalkraft in N, Zug positiv.
        :return: Moment in Nm, Betrag der gewaehlten Seite.
        """
        return self.massgebend.moment_bei(N_Ed, positiv)

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
            symbol = (rf"{achse.name}_{{{self.wahl.index},{r}}}({achse.gegen.name}_{{Ed}} = "
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

        Gemessen wird gegen die massgebende Linie -- damit die Zahl im Urteil
        dieselbe ist, die in der Herleitung steht.

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
        innerhalb = self.massgebend.innerhalb(N_Ed, M_Ed)

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
                "Kein Schnitt mit der Resistenzlinie → Einwirkung ausserhalb.",
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

        treffer = self.massgebend.kante(achse, fest, positiv=gesucht >= 0)
        if treffer is None:
            return None
        rd = treffer.wert

        grad = float("inf") if gesucht == 0 else abs(rd) / abs(gesucht)
        return Auswertung(
            kombination, innerhalb, grad,
            widerstand=(ed.N, rd) if achse is geo.MOMENT else (rd, ed.M),
            begruendung=(f"{achse.name}_{self.wahl.index} = {_in(rd, achse)} bei "
                         f"{achse.gegen.name}_Ed = {_in(fest, achse.gegen)}."),
            achse=achse, ed=gesucht, rd=rd,
            massstab=MASSSTAB[achse.name],
            treffer=treffer, linie=self.massgebend)

    def _naechster(
        self, kombination: Schnittgroessen, eckwerte: Mapping[str, float],
        innerhalb: bool,
    ) -> Auswertung:
        """
        Kuerzester Abstand, im auf die Eckwerte normierten Diagramm -- zum
        Polygon der massgebenden Linie. Bei der Linie aus Dehnungsebenen ist
        das ihr gezeichneter Rand: der naechste Punkt ist eine Frage der
        Geometrie, nicht eines Bruchzustands.
        """
        N_Ed, M_Ed = kombination.N_Ed.si, kombination.M_Ed.si
        N_ref = max(abs(eckwerte["N_Rd_zug"]), abs(eckwerte["N_Rd_druck"])) or 1.0
        M_ref = max(abs(eckwerte["M_Rd_max"]), abs(eckwerte["M_Rd_min"])) or 1.0
        abstand, stelle = geo.naechster_punkt(
            N_Ed, M_Ed, self.massgebend.punkte, N_ref, M_ref)
        laenge = math.hypot(N_Ed / N_ref, M_Ed / M_ref)
        rand = max(laenge + abstand if innerhalb else laenge - abstand, 0.0)
        grad = float("inf") if laenge == 0 else rand / laenge
        return Auswertung(
            kombination, innerhalb, grad, stelle,
            f"Kürzester Abstand (normiert) a = {abstand:.3f}; nächster Punkt "
            f"N = {_in(stelle[0], geo.NORMALKRAFT)}, M = {_in(stelle[1], geo.MOMENT)}.",
            achse=geo.MOMENT, ed=M_Ed, rd=stelle[1],
            massstab=Erfuellungsart.NAECHSTER_PUNKT,
            normierung=Normierung(N_ref, M_ref, laenge, abstand, rand))

    # -- Mitschrift ---------------------------------------------------------


    def _normiert(self, auswertung: Auswertung) -> Tuple[Wert, Wert]:
        """Einwirkung und Widerstand im normierten Diagramm -- fuer Tabelle und Herleitung."""
        n, r = auswertung.normierung, self.richtung.value
        werte = Zwischenwerte(f"{self.id}.{auswertung.schnittgroessen.kennung}")
        return (werte.zahl("E_norm", rf"\bar{{E}}_{{d,{r}}}", n.laenge, "Einwirkung"),
                werte.zahl("R_norm", rf"\bar{{R}}_{{{self.wahl.satz.kuerzel},{r}}}", n.rand,
                           "Widerstand"))

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
            protokoll_widerstand(p, auswertung, basis=basis)
            werte, achse = Zwischenwerte(basis), auswertung.achse
            rd, ed = (werte.wert(name, f"{achse.name}_{{{zeichen}}}",
                                 Groesse.aus_si(abs(si), achse.einheit))
                      for name, zeichen, si in (("Rd", self.wahl.index, auswertung.rd),
                                                ("Ed", "Ed", auswertung.ed)))
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


def linienbezuege(querschnitt: Plattenquerschnitt, posten, richtung: Richtung,
                  satz: Werkstoffsatz) -> List[Eingabebezug]:
    """
    Was eine Resistenzlinie dieser Richtung braucht -- unter den Namen, die
    :func:`resistenzlinie` liest: die Festigkeiten des Wertesatzes, ``f_cd``
    und ``f_yd`` oder ``f_ck`` und ``f_yk``, ``E_cm`` fuer die Parabel, die
    Bewehrung dieser Richtung und je Stahlsorte ihre Kennwerte.
    """
    bezuege = [
        Eingabebezug("h", querschnitt.id_von("h")),
        Eingabebezug("b", querschnitt.id_breite(richtung)),
        Eingabebezug(satz.beton, querschnitt.beton.id_von(satz.beton)),
        Eingabebezug("eps_c1d", querschnitt.beton.id_von("eps_c1d")),
        Eingabebezug("eps_c2d", querschnitt.beton.id_von("eps_c2d")),
        Eingabebezug("E_cm", querschnitt.beton.id_von("E_cm")),
    ]
    # Nur die Bewehrung dieser Richtung geht ein -- Querbewehrung traegt
    # nichts zum Momentenwiderstand um diese Achse bei.
    for lage, art, _, as_id, z_id in posten:
        marke = f"{lage.nummer}{art.kuerzel}"
        bezuege += [
            Eingabebezug(f"a_s_{marke}", as_id),
            Eingabebezug(f"z_{marke}", z_id),
        ]
    for stahl in {l.stahl.id: l.stahl for l, _, _, _, _ in posten}.values():
        kurz = kennung_aus(stahl.id)
        for kennwert in ("E_s", satz.stahl, satz.stahl_druck, "eps_ud"):
            bezuege.append(Eingabebezug(f"{kennwert}__{kurz}", stahl.id_von(kennwert)))
    return bezuege


def resistenzlinie(
    wahl: Rechenwahl, e: Eingaben, p: Protokoll, *, querschnitt: Plattenquerschnitt,
    posten, richtung: Richtung, basis: str,
    schritte: int = dehnungsfaecher.SCHRITTE, fasern: int = dehnungsfaecher.FASERN,
    vorsatz: str = "", ebene: int = 2, wahltitel: str = "Rechenwahl",
) -> Widerstandslinie:
    """
    Die Resistenzlinie einer Wahl aus den Eingaben von :func:`linienbezuege`
    -- und ihre Herleitung in ``p``: unter ihrem Titel zuerst, womit sie
    rechnet, dann wie sie entsteht. Die Tragsicherheit baut so ihre Linie,
    das Knicken seine, wenn es anders waehlt.
    """
    hand = wahl.art is Rechenart.HANDRECHNUNG
    p.titel(f"{vorsatz}Resistenzlinie aus {'Handrechnung' if hand else 'Dehnungsebenen'} – "
            f"{richtung.beschriftung}", ebene=ebene)
    phi = protokoll_rechenwahl(p, wahl, basis, titel=wahltitel)
    satz = wahl.satz
    h, b = e.g("h").si, e.g("b").si
    f_c = abs(e.g(satz.beton).si)
    eps_c1d, eps_c2d = abs(e.g("eps_c1d").si), abs(e.g("eps_c2d").si)
    lagen = dehnungsfaecher.lagen_aus_eingaben(posten, e, satz)

    if hand:
        # Die Zugehoerigkeit zur unteren oder oberen Lage kommt aus dem
        # Modell (Lagen 1 und 2 liegen unten), nicht aus der Hoehenlage --
        # siehe lagen_zusammenfassen().
        seiten = lagen_zusammenfassen([
            HandPosten(a_s=a_s, z=z, f_yd=gesetz.f_yd, E_s=gesetz.E_s, text=text,
                       index=posten_index(lage, art),
                       stahl_index=lage.stahl.symbol_index,
                       von_unten=lage.von_unten, satz=satz)
            for (a_s, z, gesetz, text), (lage, art, *_) in zip(lagen, posten)
        ])
        handrechnung = Handrechnung(
            h=h, b=b, f_cd=f_c, eps_c2d=eps_c2d,
            unten=seiten["unten"], oben=seiten["oben"], basis=basis,
            beton_index=querschnitt.beton.symbol_index, satz=satz,
        )
        return Handlinie(wahl, handrechnung.rechnen(p))

    linie = Ebenenlinie(
        wahl, h=h, b=b, lagen=lagen, eps_c1d=eps_c1d, eps_c2d=eps_c2d,
        beton=betongesetz(wahl, f_c=f_c, E_cm=e.g("E_cm").si,
                          eps_c1d=eps_c1d, eps_c2d=eps_c2d),
        schritte=schritte, fasern=fasern)
    linie.protokoll_ansatz(p, f_c=e[satz.beton], E_cm=e["E_cm"], phi=phi, basis=basis)
    return linie


def gleiche_linie(a: Rechenwahl, b: Rechenwahl) -> bool:
    """
    Ob zwei Wahlen dieselbe Resistenzlinie ergeben -- die Kriechzahl zaehlt
    nur, wo sie wirkt.
    """
    return (a.art is b.art and a.satz is b.satz
            and (a.kriechzahl == b.kriechzahl or not a.art.mit_kriechzahl))


def protokoll_widerstand(
    p: Protokoll, auswertung: Auswertung, titel: str = "",
    *, basis: str,
) -> None:
    """
    Schreibt, wie der Widerstand auf der Linie gefunden wurde -- die Linie,
    die ihn geliefert hat, weiss wie: das Polygon zeigt seine Interpolation,
    die Linie aus Dehnungsebenen die Probe ihres Bruchzustands.

    Frei und nicht an :class:`BiegungNormalkraft` gebunden: der
    Querkraftnachweis rechnet mit dem Momentenwiderstand bei der wirkenden
    Normalkraft und muss dieselbe Herleitung zeigen. Zweimal geschrieben
    liefe sie frueher oder spaeter auseinander.
    """
    if auswertung.treffer is None or auswertung.linie is None:
        p.text(auswertung.begruendung)
        return
    ed = geo.Stelle(N=auswertung.schnittgroessen.N_Ed.si,
                    M=auswertung.schnittgroessen.M_Ed.si)
    auswertung.linie.protokoll_treffer(
        p, auswertung.treffer, achse=auswertung.achse,
        fest=auswertung.achse.gegen.von(ed), basis=basis, titel=titel)


def _in(si_wert: float, achse: geo.Achse) -> str:
    """Ein SI-Wert in der Einheit seiner Achse, mit Einheitenzeichen."""
    g = Groesse.aus_si(si_wert, achse.einheit)
    return f"{g.formatiert(1)} {achse.einheit.beschriftung}"

