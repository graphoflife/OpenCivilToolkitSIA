"""
opencivil/nachweis/qa_schubfluss.py -- der Schubfluss in den Schnitten eines Querschnitts.

VERANTWORTUNG:
Je Schnitt (:class:`~opencivil.querschnitt.abtrennen.Schnitt`) und je
Lastfall des Schubflusses der Schubfluss ``v`` -- die Kraft je Laenge des
Bauteils, die durch den Schnitt geht -- und die Schubspannung ``τ = v/b_i``
ueber die Laenge ``b_i``, auf der er Material von Material trennt
(:class:`SchubflussQA`). Nur die Einwirkung, ohne Widerstand (Benutzer,
2026-11-27): ob eine Fuge, die Duebel oder eine Naht das tragen, ist eine
andere Frage.

DIE REGEL:
Waechst das Moment laengs des Bauteils um ``ΔM = V·Δx``, waechst die Kraft
``F′`` im abgetrennten Teil um ``ΔF′`` -- und die kommt durch den Schnitt::

    v = ΔF′ / Δx

``F′`` ist das Integral der Spannungen ueber den abgetrennten Teil, mit
den Staeben, Spanngliedern und Stuecken verschmierter Linien, die in ihm
liegen (:func:`teilquerschnitt`). Die Spannungen kommen aus zwei
Dehnungsebenen des ganzen Querschnitts, bei ``(N, M)`` und bei
``(N, M + ΔM)`` (:func:`zustaende`): gesucht vom selben Faserloeser wie in
den Spannung-Dehnung-Analysen, im gerissenen Zustand -- der Beton traegt
keinen Zug --, mit der Rechenwahl des Falls und der Nulllinie waagrecht.

Elastisch ist das ``V·S′/I``. Gerissen, ohne Normalkraft und mit festem
Hebelarm ``z`` ist es ``V/z`` mal dem Anteil des abgetrennten Teils an der
Kraft seines Gurts -- das ``β·V/z`` der EN 1992-1-1, 6.2.5 (nicht
nachgeschlagen). Diese Regel gilt auch mit Normalkraft und wo der
Hebelarm mit dem Moment wandert.

NACH VORGABE, NICHT NACHGESCHLAGEN (``notizbuch/Notizen/TODO.md``):

* ``Δx = 10 mm`` (:data:`DX`): klein genug, dass sich der Zustand kaum
  aendert, gross genug fuer die Genauigkeit der Suche.
* Die Richtung: ``ΔM`` hat das Vorzeichen von ``M`` -- das Moment waechst im
  Betrag --, ohne Moment das positive. Gibt es bei ``M + ΔM`` keine
  Gleichgewichtslage mehr, gilt der Schritt zurueck, ``M − ΔM``.
* Angegeben wird der Betrag von ``v``: in welche Richtung er laengs geht,
  haengt daran, in welche Richtung das Moment waechst.

OHNE ERGEBNIS:
Ohne Querkraft aendert sich das Moment nicht: ``v = 0``. Nimmt der
Querschnitt ``N`` und ``M`` nicht auf, gibt es kein ``v``: die Zahl ist
nicht bestimmt (NaN), die Tabelle zeigt «–», die Herleitung und der Befund
(:class:`Schubflussbefund`) sagen warum. Ein Schnitt, der nichts abtrennt,
rechnet nicht; warum, steht in der Herleitung, unter der Tabelle und an ihm
in der Zeichnung.

EINHEITEN:
SI-Basis; die Schnitte und ihre abgetrennten Teile in mm, wie gezeichnet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union

from opencivil.core.berechnung import Ausfuehrung, Eingaben, Prozedur
from opencivil.core.einheiten import KN_PRO_M, MM, N_PRO_MM2, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.querschnitt.abtrennen import Abgetrennt, Schnitt
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.bewehrungselemente import Bewehrungselement
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.interaktion import Querschnitt, Teil, linie_als_bewehrung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import Dehnungsebene, FesteNulllinie
from opencivil.spannungsanalyse.schnitt import zerlegung

#: Wie weit der zweite Zustand laengs des Bauteils vom ersten liegt, in m --
#: nach Vorgabe, nicht nachgeschlagen (siehe Dateikopf).
DX = 0.01

#: Die Nulllinie waagrecht, positives Moment zieht unten: so ist das Moment
#: der Fasern ``M_y``.
PSI = Zugseite.UNTEN.psi

#: Was in mm steht, in m.
_MM = MM.faktor

#: Woher die Regel kommt: keine Norm nennt sie (siehe Dateikopf).
VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: Warum es zu einem Fall kein ``v`` gibt, wo der Querschnitt ihn nicht aufnimmt.
KEINE_LAGE = ("Zu N und M gibt es keine Gleichgewichtslage: der Querschnitt nimmt sie "
              "nicht auf.")


@dataclass(frozen=True)
class Schubflussfall:
    """Ein Lastfall des Schubflusses in SI, mit seiner Rechenwahl am Bauteil."""

    name: str
    N: float
    V: float
    """Die Querkraft in z."""

    M: float
    """Das Moment um y, positiv zieht es unten."""

    wahl: Rechenwahl


@dataclass(frozen=True)
class Schubflusszeile:
    """
    Eine Zeile der Tabelle: ein Schnitt in einem Fall, mit den Definitionen
    seiner Werte -- ``b_i`` gehoert dem Schnitt, ``v`` und ``τ`` dem Paar.
    """

    schnitt: str
    fall: str
    b_i: WertDef
    v: WertDef
    tau: WertDef


@dataclass(frozen=True)
class Schubflussbefund:
    """
    Was ein Lauf ueber die Werte hinaus festhaelt: je Fall ohne Schubfluss
    der Grund, ein Satz -- die Tabelle zeigt dort «–», darunter steht er.
    """

    gruende: Dict[str, str]
    """Nach dem Namen des Falls."""


@dataclass(frozen=True)
class Zustaende:
    """Die beiden Ebenen eines Falls: bei ``M_0 = M`` und beim Moment daneben, ``M_1``."""

    M_0: float
    M_1: float
    ebene_0: Dehnungsebene
    ebene_1: Dehnungsebene
    zurueck: bool
    """Ob ``M_1`` der Schritt zurueck ist, ``M − ΔM``: bei ``M + ΔM`` gab es keine Ebene."""


def zustaende(ebenen: FesteNulllinie, fall: Schubflussfall) -> Union[Zustaende, str]:
    """
    Die beiden Ebenen eines Falls (siehe Dateikopf) -- oder ein Satz, warum
    es sie nicht gibt.
    """
    erste = ebenen.zu_kraeften(fall.N, fall.M)
    if erste is None:
        return KEINE_LAGE
    if erste.verfehlt:
        return fall.wahl.arten.ohne_ebene
    schritt = abs(fall.V) * DX * (1.0 if fall.M >= 0.0 else -1.0)
    for zurueck in (False, True):
        M_1 = fall.M - schritt if zurueck else fall.M + schritt
        zweite = ebenen.zu_kraeften(fall.N, M_1)
        if zweite is not None and not zweite.verfehlt:
            return Zustaende(fall.M, M_1, erste, zweite, zurueck)
    return ("Neben M gibt es keine Gleichgewichtslage mehr: der Querschnitt nimmt N und M "
            "gerade noch auf.")


def teilquerschnitt(q: Querschnitt, herkunft: Sequence[Bewehrungselement],
                    a: Abgetrennt) -> Tuple[Querschnitt, List[str]]:
    """
    Der abgetrennte Teil als Querschnitt, mit den Werkstoffen, dem Bezug und
    den Streifen des ganzen, geteilt an seinen eigenen Ecken -- so liest er
    dieselbe Ebene, und zwei Schnitte, die dieselbe Druckzone abtrennen,
    rechnen sie gleich. Dazu die Namen
    der Bewehrung in ihm. Ein Stab und ein Spannglied zaehlen mit ihrer
    Mitte, auf dem Schnitt zum Rest; eine verschmierte Linie mit ihren
    Stuecken im abgetrennten Teil, je mit der Flaeche ihrer Laenge.
    """
    teile = [Teil(punkte=tuple((y * _MM, z * _MM) for y, z in s.punkte),
                  werkstoff=q.teile[s.polygon].werkstoff, eltern=None) for s in a.stuecke]
    bewehrung = []
    namen: Dict[str, None] = {}
    linien = set()
    for b, g in zip(q.bewehrung, herkunft):
        if not g.verschmiert:
            if a.enthaelt((b.lage[0] / _MM, b.lage[1] / _MM)):
                bewehrung.append(b)
                namen[g.name] = None
            continue
        if id(g) in linien:
            continue
        linien.add(id(g))
        je_mm = g.flaeche / sum(math.dist(von, bis) for von, bis in g.strecken)
        for von, bis in g.strecken:
            for p, r in a.strecke_teilen(von, bis):
                bewehrung += linie_als_bewehrung(
                    (p[0] * _MM, p[1] * _MM), (r[0] * _MM, r[1] * _MM),
                    je_mm * math.dist(p, r) * _MM * _MM, b.werkstoff, b.verdraengt)
                namen[g.name] = None
    return (Querschnitt(werkstoffe=q.werkstoffe, teile=teile, bewehrung=bewehrung,
                        bezug=q.bezug, streifen=q.streifen, raster=q.teile), list(namen))


def kraft_im_teil(teil: Querschnitt, ebene: Dehnungsebene) -> float:
    """``F′``: was der abgetrennte Teil in dieser Ebene traegt, Zug positiv, in N."""
    return teil.richtung(PSI).fasern.kraefte(ebene.eps_m, ebene.chi).N


class SchubflussQA(Prozedur):
    """Der Schubfluss je Schnitt und Lastfall -- siehe Dateikopf."""

    THEMA = "Schubfluss"

    def __init__(self, analyse: Querschnittsanalyse, schnitte: Sequence[Schnitt],
                 faelle: Sequence[Schubflussfall]) -> None:
        self.analyse = analyse
        self.faelle = list(faelle)
        polygone = [f.punkte for f in analyse.flaechen]
        traegt = [f.stoff is not None for f in analyse.flaechen]
        self.getrennt: List[Tuple[Schnitt, Abgetrennt]] = []
        self.ohne: List[str] = []
        """Je Schnitt, der nichts abtrennt, der Satz dazu -- mit dem Grund."""

        for s in schnitte:
            a = s.abtrennen(polygone, traegt, analyse.eltern)
            if isinstance(a, str):
                self.ohne.append(s.nichts_abgetrennt(a))
            else:
                self.getrennt.append((s, a))
        basis = f"{analyse.id}.schubfluss"
        self.zeilen: List[Schubflusszeile] = []
        """Je Schnitt, der etwas abtrennt, und Fall eine Zeile -- in dieser Folge."""

        self.breiten: Dict[str, WertDef] = {}
        for s, _ in self.getrennt:
            b_i = self.breiten[s.kennung] = WertDef(
                id=f"{basis}.{s.kennung}.b_i", symbol="b_i", einheit=MM, stellen=1,
                beschreibung=f"{s.name}: Länge, auf der er Material von Material trennt")
            for f in self.faelle:
                stamm = f"{basis}.{s.kennung}.{kennung_aus(f.name)}"
                self.zeilen.append(Schubflusszeile(
                    s.name, f.name, b_i,
                    WertDef(id=f"{stamm}.v", symbol="v", einheit=KN_PRO_M, stellen=1,
                            beschreibung=f"Schubfluss im {s.name}, {f.name}",
                            referenz=VORGABE),
                    WertDef(id=f"{stamm}.tau", symbol=r"\tau", einheit=N_PRO_MM2, stellen=2,
                            beschreibung=f"Schubspannung im {s.name}, {f.name}",
                            referenz=VORGABE)))
        ausgaben = list(self.breiten.values()) + [d for z in self.zeilen for d in (z.v, z.tau)]
        super().__init__(basis, ausgaben=ausgaben, bezuege=analyse.grundbezuege(),
                         titel=f"Schubfluss – {analyse.name}", abschnitt=analyse.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Schubfluss")
        p.erklaerung(
            "Wächst das Moment längs des Bauteils, wächst auch die Kraft im Teil, den ein "
            "Schnitt abtrennt. Was sie auf einer Länge Δx gewinnt, kommt durch den Schnitt: "
            "der Schubfluss v = ΔF′/Δx, mit ΔM = V·Δx. F′ ist die Kraft im abgetrennten Teil, "
            "aus zwei Dehnungsebenen des ganzen Querschnitts – gerissen, mit waagrechter "
            "Nulllinie und der Rechenwahl des Falls. Elastisch ist das V·S′/I.")
        p.ansatz(r"v = \frac{\left|F'(M + \Delta M) - F'(M)\right|}{\Delta x}, \qquad "
                 r"\Delta M = V \cdot \Delta x, \qquad \tau = \frac{v}{b_i}",
                 titel="Schubfluss aus der Kraft im abgetrennten Teil", referenz=VORGABE,
                 name="Schubfluss im Schnitt")
        p.annahme("Δx = 10 mm, ΔM mit dem Vorzeichen von M, ohne Moment positiv; ohne "
                  "Gleichgewichtslage bei M + ΔM der Schritt zurück (nach Vorgabe, nicht "
                  "nachgeschlagen).")
        for satz in self.ohne:
            p.hinweis(satz)
        ergebnis: Dict[str, Groesse] = {}
        gruende: Dict[str, str] = {}
        if not self.getrennt:
            return Ausfuehrung(ergebnis, befund=Schubflussbefund(gruende))

        def belegen(d: WertDef, si: float) -> Wert:
            wert = d.belegen(Groesse.aus_si(si, d.einheit))
            ergebnis[d.id] = wert.groesse
            return wert

        werte = Zwischenwerte(self.id)
        breiten = {s.kennung: belegen(self.breiten[s.kennung], a.breite * _MM)
                   for s, a in self.getrennt}
        for s, _ in self.getrennt:
            p.wert(breiten[s.kennung], titel=f"{s.name}: so lang trennt er Material von Material")
        # Je Rechenwahl einmal der Querschnitt, seine Ebenen und die abgetrennten Teile.
        gerechnet: Dict[Rechenwahl, tuple] = {}
        dx = werte.laenge("dx", r"\Delta x", DX,
                          "Abstand der beiden Zustände längs des Bauteils, nach Vorgabe")
        for fall in self.faelle:
            if fall.wahl not in gerechnet:
                q, herkunft, staehle = self.analyse.querschnitt(e.si_nach_id(), fall.wahl)
                gerechnet[fall.wahl] = (
                    zerlegung(q, herkunft, staehle).in_richtung(PSI),
                    [teilquerschnitt(q, herkunft, a) for _, a in self.getrennt])
            grund = self._fall(p, werte, belegen, fall, dx, breiten, *gerechnet[fall.wahl])
            if grund is not None:
                gruende[fall.name] = grund
        return Ausfuehrung(ergebnis, befund=Schubflussbefund(gruende))

    def _fall(self, p: Protokoll, werte: Zwischenwerte, belegen, fall: Schubflussfall,
              dx: Wert, breiten: Dict[str, Wert], ebenen: FesteNulllinie,
              teile: Sequence[Tuple[Querschnitt, List[str]]]) -> Optional[str]:
        """Ein Fall in jedem Schnitt -- ohne Schubfluss der Grund, sonst nichts."""
        p.titel(f"Lastfall «{fall.name}»", ebene=3)
        k = kennung_aus(fall.name)
        zeilen = [z for z in self.zeilen if z.fall == fall.name]
        p.text(f"N = {fest(fall.N / 1e3, 1)} kN, V_z = {fest(fall.V / 1e3, 1)} kN, "
               f"M_y = {fest(fall.M / 1e3, 1)} kNm.".replace("-", "−"))
        if fall.V == 0.0:
            p.text("Ohne Querkraft ändert sich das Moment längs des Bauteils nicht: "
                   "v = 0 in jedem Schnitt.")
            for z in zeilen:
                belegen(z.v, 0.0)
                belegen(z.tau, 0.0)
            return None
        stand = zustaende(ebenen, fall)
        if isinstance(stand, str):
            p.text(f"{stand.rstrip('.')} → kein Schubfluss.")
            for z in zeilen:
                belegen(z.v, math.nan)
                belegen(z.tau, math.nan)
            return stand
        dM = werte.moment(f"{k}.dM", r"\Delta M", abs(stand.M_1 - stand.M_0),
                          "Zuwachs des Moments über Δx")
        p.formel(dM, r"@V \cdot @dx",
                 {"V": werte.kraft(f"{k}.V", "V_z", abs(fall.V), "Querkraft des Falls"),
                  "dx": dx},
                 titel="Das Moment ändert sich über Δx um", referenz=VORGABE,
                 name="Zuwachs des Moments über Δx")
        if stand.zurueck:
            p.text("Bei M + ΔM gibt es keine Gleichgewichtslage mehr: verglichen wird mit "
                   "M − ΔM.")
        p.tabelle(
            kopf=["Ebene", Mathe(r"M_y\ [\mathrm{kNm}]"), Mathe(r"\varepsilon_m\ [‰]"),
                  Mathe(r"\chi\ [\mathrm{1/km}]")],
            zeilen=[[Mathe(name), Mathe(fest(M / 1e3, 2)), Mathe(fest(ebene.eps_m * 1e3, 4)),
                     Mathe(fest(ebene.chi * 1e3, 4))]
                    for name, M, ebene in (
                        ("M", stand.M_0, stand.ebene_0),
                        (r"M - \Delta M" if stand.zurueck else r"M + \Delta M", stand.M_1,
                         stand.ebene_1))],
            titel="Die beiden Dehnungsebenen – ε_m im Schwerpunkt, χ positiv mit Zug unten",
            ausrichtung="lrrr")
        for z, (s, a), (teil, staebe) in zip(zeilen, self.getrennt, teile):
            p.text(f"{s.name} trennt ab: "
                   + ", ".join([*(self.analyse.flaechen[i].name for i in a.polygone), *staebe])
                   + f" – A′ = {fest(a.flaeche, 0)} mm².")
            F_0, F_1 = kraft_im_teil(teil, stand.ebene_0), kraft_im_teil(teil, stand.ebene_1)
            v = belegen(z.v, abs(F_1 - F_0) / DX)
            p.formel(v, r"\frac{\left|@F_1 - @F_0\right|}{@dx}",
                     {"F_1": werte.kraft(f"{s.kennung}.{k}.F_1", "F'_1", F_1, stellen=2,
                                         beschreibung="Kraft im abgetrennten Teil daneben, "
                                                      "Zug positiv"),
                      "F_0": werte.kraft(f"{s.kennung}.{k}.F_0", "F'_0", F_0, stellen=2,
                                         beschreibung="Kraft im abgetrennten Teil bei M, "
                                                      "Zug positiv"),
                      "dx": dx},
                     titel="Schubfluss – die Kraft im abgetrennten Teil bei M und daneben",
                     name="Schubfluss im Schnitt")
            p.formel(belegen(z.tau, abs(F_1 - F_0) / DX / (a.breite * _MM)), r"\frac{@v}{@b}",
                     {"v": v, "b": breiten[s.kennung]},
                     titel="Schubspannung über b_i", name="Schubspannung im Schnitt")
        return None
