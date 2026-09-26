"""
opencivil/nachweis/dehnungsfaecher.py -- Die praezise M-N-Resistenzlinie.

VERANTWORTUNG:
Baut die Interaktionslinie eines Querschnitts punktweise aus Dehnungsebenen auf.
Das Ergebnis ist eine Zeichnung, kein Nachweis: nachgewiesen wird gegen das
Polygon aus :mod:`opencivil.nachweis.handrechnung`, das sich von Hand
nachrechnen laesst. Diese Linie steht im Diagramm daneben und zeigt, was die
Vereinfachung kostet.

WARUM EIGENSTAENDIG:
Sie sass frueher in der Nachweisklasse. Seit das Urteil ueber die Handrechnung
faellt, ist sie dort ein Fremdkoerper -- 300 Zeilen Faserintegration in einer
Klasse, die vergleichen und aufschreiben soll. Getrennt ist beides leichter zu
lesen, und der Nachweis haengt nur noch an einer Funktion.

WIE DIE LINIE ENTSTEHT:
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
selbst -- womit Punkt-in-Linie-Test und Schnittsuche unbrauchbar waeren.

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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import kennung_aus
from opencivil.nachweis import linie as geo
from opencivil.querschnitt.werkstoffgesetz import (
    Betongesetz, Dehnungsebene, Stahlgesetz,
)

#: Schritte je Faecherabschnitt. 80 kosten rund 16 ms. Die Eckwerte sind schon
#: bei 40 auf fuenf Stellen auskonvergiert; die feinere Teilung dient allein
#: der Zeichnung, weil die Linie nahe dem reinen Druck schnell laeuft und sonst
#: sichtbar eckig wuerde.
SCHRITTE = 80

#: Fasern ueber die Hoehe fuer die Betonintegration.
FASERN = 200


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

def lagen_aus_eingaben(posten, e: Eingaben) -> List[Tuple[float, float, Stahlgesetz, str]]:
    """Je Bewehrungsposten dieser Richtung: (Fläche m^2, z m, Gesetz, Text)."""
    gesetze: Dict[str, Stahlgesetz] = {}
    for stahl in {l.stahl.id: l.stahl for l, _, _, _, _ in posten}.values():
        kurz = kennung_aus(stahl.id)
        gesetze[stahl.id] = Stahlgesetz.aus_werten({
            kennwert: e[f"{kennwert}__{kurz}"]
            for kennwert in ("E_s", "f_yd", "f_yd_druck", "eps_ud")
        })

    lagen = []
    for lage, art, _, _, _ in posten:
        marke = f"{lage.nummer}{art.kuerzel}"
        lagen.append((
            e.g(f"a_s_{marke}").si,
            e.g(f"z_{marke}").si,
            gesetze[lage.stahl.id],
            f"{lage.nummer}. Lage {art.beschriftung}",
        ))
    return lagen

def schnittgroessen(
    ebene: Dehnungsebene, beton: Betongesetz, lagen,
    h: float, b: float, fasern: int,
) -> Tuple[float, float]:
    """Integriert N und M zu einer Dehnungsebene. Rueckgabe in N und Nm."""
    N = 0.0
    M = 0.0
    dz = h / fasern
    flaeche = b * dz
    for k in range(fasern):
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

def faecher(
    h: float, lagen, beton: Betongesetz, schritte: int,
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
        for i in range(ab, schritte + 1):
            anteil = i / schritte
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




def aufbauen(
    *, h: float, b: float, lagen, beton: Betongesetz,
    schritte: int = SCHRITTE, fasern: int = FASERN,
) -> List[Linienpunkt]:
    """
    Die vollstaendige, geschlossene Resistenzlinie.

    Der einzige Einstieg, den der Nachweis braucht -- alles Uebrige hier ist
    Innenleben.
    """
    return geo.ohne_wiederholungen([
        Linienpunkt(
            *schnittgroessen(ebene, beton, lagen, h, b, fasern),
            eps_oben=ebene.eps_oben,
            eps_unten=ebene.eps_unten,
            abschnitt=marke,
        )
        for marke, ebene in faecher(h, lagen, beton, schritte)
    ])



# ===========================================================================
# STILLGELEGT -- die Mitschrift der praezisen Linie
#
# Die folgenden Funktionen schreiben den Dehnungsebenen-Ansatz, die
# Stuetzstellen des Faechers und die Eckwerte. Sie werden derzeit von niemandem
# aufgerufen: hergeleitet wird die Handrechnung, diese Linie dient nur dem
# Vergleich im Diagramm.
#
# Sie bleiben vollstaendig stehen, weil der Inhalt spaeter wieder gebraucht
# wird. Wer sie reaktiviert, ruft sie aus BiegungNormalkraft.pruefe() auf --
# gerechnet wird die Linie ohnehin weiter, es fehlt allein die Mitschrift.
# ===========================================================================


def protokoll_ansatz(p: Protokoll, beton: Betongesetz, lagen, fasern: int = FASERN) -> None:
    p.titel("Ansatz")
    p.erklaerung(
        "Der Querschnitt bleibt eben (Bernoulli). Zu jeder zulässigen "
        "Dehnungsebene werden Normalkraft und Moment durch Integration über "
        "die Querschnittshöhe bestimmt. Zug ist positiv, das Moment bezieht "
        "sich auf die halbe Querschnittshöhe."
    )
    p.ansatz(beton.latex(), titel="Beton – Parabel-Rechteck-Beziehung",
             referenz="SIA 262:2025, 4.2.1.6")
    p.ansatz(lagen[0][2].latex(), titel="Betonstahl – bilineare Beziehung",
             referenz="SIA 262:2025, 4.2.2.4")
    p.ansatz(
        r"N = \int_A \sigma\,\mathrm{d}A \qquad "
        r"M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A",
        titel="Schnittgrössen aus der Spannungsverteilung",
    )
    p.erklaerung(
        f"Der Beton wird in {fasern} Fasern über die Höhe integriert, "
        f"die Bewehrung lagenweise. Die von der Bewehrung verdrängte "
        f"Betonfläche wird abgezogen."
    )
    p.tabelle(
        kopf=["Lage", Mathe(r"a_s\ [\mathrm{mm}^2]"), Mathe(r"z\ [\mathrm{mm}]"),
              Mathe(r"f_{yd}\ [\mathrm{N/mm^2}]")],
        zeilen=[
            [beschriftung,
             Mathe(f"{a_s * 1e6:.0f}"), Mathe(f"{z * 1e3:.1f}"),
             Mathe(f"{stahl.f_yd / 1e6:.0f}")]
            for a_s, z, stahl, beschriftung in lagen
        ],
        titel="Berücksichtigte Bewehrungslagen",
        ausrichtung="lrrr",
    )

def protokoll_linie(p: Protokoll, linie: Sequence[Linienpunkt],
                schritte: int = SCHRITTE) -> None:
    p.titel("Aufbau der Resistenzlinie")
    p.erklaerung(
        f"Der Dehnungsfächer wird in vier Abschnitten mit je "
        f"{schritte} Schritten abgefahren; das ergibt "
        f"{len(linie)} Punkte. Ausgewiesen ist jeder Abschnittsanfang "
        f"und jedes Abschnittsende."
    )
    zeilen = []
    vorher = None
    for i, punkt in enumerate(linie):
        grenze = (
            vorher is None
            or punkt.abschnitt != vorher
            or i == len(linie) - 1
            or linie[i + 1].abschnitt != punkt.abschnitt
        )
        if grenze:
            zeilen.append([
                punkt.abschnitt,
                Mathe(f"{punkt.eps_oben * 1000:.2f}"),
                Mathe(f"{punkt.eps_unten * 1000:.2f}"),
                Mathe(f"{punkt.N / 1e3:.1f}"),
                Mathe(f"{punkt.M / 1e3:.1f}"),
            ])
        vorher = punkt.abschnitt
    p.tabelle(
        kopf=["Abschn.", Mathe(r"\varepsilon_{oben}\ [\text{‰}]"),
              Mathe(r"\varepsilon_{unten}\ [\text{‰}]"),
              Mathe(r"N\ [\mathrm{kN}]"), Mathe(r"M\ [\mathrm{kNm}]")],
        zeilen=zeilen,
        titel="Stützstellen des Dehnungsfächers",
        ausrichtung="lrrrr",
    )

def protokoll_eckwerte(p: Protokoll, eckwerte: Mapping[str, str]) -> None:
    """Eckwerte der genauen Linie, je Kennung als fertige Zeichenkette."""
    p.tabelle(
        kopf=["Eckwert", "Symbol", "Wert"],
        zeilen=[
            [beschreibung, Mathe(symbol),
             Mathe(eckwerte[schluessel])]
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
