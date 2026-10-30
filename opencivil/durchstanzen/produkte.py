"""
opencivil/durchstanzen/produkte.py -- Durchstanzbewehrung und Stahlpilze, wie man sie kaufen kann.

VERANTWORTUNG:
Die Produkte, aus denen die Bemessung wählt, mit ihren Regeln -- Typen,
Durchmesser, Höhen, Abstände, der Faktor des Gutachtens -- und woher jede
Zahl stammt. Gerechnet wird hier nichts, was über ein Produkt hinausgeht:
die Anordnung um die Stütze steht in :mod:`.bewehrung`, der Nachweis in
:mod:`.nachweis`.

ANCOPLUS (AncoTech AG):
Doppelkopfanker auf einer Montageleiste, je Leiste 2 bis 9 Anker gleichen
Durchmessers. Die Typen «D…» haben ungleiche Abstände: der erste Anker
liegt 0.375·d vom Rand der Stütze, bis und mit dem dritten folgen sie sich
im Abstand 0.60·d, danach 0.75·d. So hat es das Gutachten Muttoni /
Fernández Ruiz von 2007 für die erhöhte Obergrenze 3·k_r festgelegt
(Bericht 07-A05-R1c, zu SIA 262:2003, S. 5–6). Ein neueres Gutachten zu
SIA 262:2025 war nicht lesbar; die Regeln gelten darum **nach Vorgabe,
nicht nachgeschlagen**.

ZEUS (AncoTech AG):
Stahlpilze aus Stahlprofilen, als einfaches Kreuz, Doppelkreuz oder H-Kreuz,
s × s im Grundriss, Höhe h. Aus der Preisliste 12.2018 (S. 8–9). Profile,
Armlängen und Widerstände sind nicht veröffentlicht: den Widerstand des
Pilzes selbst (SIA 262:2025, 4.3.6.6.1) bestätigt der Hersteller.

EINHEITEN:
SI-Basis, Längen in m.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

#: Woher die Regeln von ancoPLUS stammen -- so steht es in der Herleitung.
QUELLE_ANCOPLUS = ("AncoTech, Gutachten Muttoni / Fernández Ruiz 2007 (07-A05-R1c) und "
                   "Preisliste ancoPLUS")
QUELLE_ZEUS = "AncoTech, Preisliste ZEUS 12.2018"


@dataclass(frozen=True)
class Ankertyp:
    """Ein Durchmesser von ancoPLUS: Kennbuchstabe, ⌀ und die lieferbaren Höhen h_A."""

    buchstabe: str
    durchmesser: float
    h_min: float
    h_max: float

    @property
    def flaeche(self) -> float:
        """Die Querschnittsfläche eines Ankers."""
        return math.pi * self.durchmesser ** 2 / 4.0


#: Die Typen von ancoPLUS mit ihren Höhen h_A (Preisliste ancoPLUS, S. 6).
#: Bei 22, 25 und 28 mm nennt die Liste mehrere Buchstaben und für 25/28 auch
#: 26/30 mm; genommen ist der erste Buchstabe und der kleinere Durchmesser.
ANKERTYPEN: Tuple[Ankertyp, ...] = (
    Ankertyp("X", 0.010, 0.125, 0.295),
    Ankertyp("A", 0.012, 0.125, 0.315),
    Ankertyp("B", 0.014, 0.125, 0.405),
    Ankertyp("C", 0.016, 0.195, 0.405),
    Ankertyp("G", 0.020, 0.215, 0.455),
    Ankertyp("J", 0.022, 0.295, 0.455),
    Ankertyp("O", 0.025, 0.345, 0.455),
    Ankertyp("T", 0.028, 0.345, 0.455),
)

#: So viele Anker trägt eine Leiste -- nur ganze Elemente sind lieferbar.
ANKER_JE_LEISTE = range(2, 10)

#: Die Abstände der Typen «D…», in Vielfachen von d (siehe Dateikopf): vom
#: Rand der Stütze zum ersten Anker, bis zum dritten, danach.
ABSTAND_ERSTER = 0.375
ABSTAND_BIS_DRITTER = 0.60
ABSTAND_DANACH = 0.75

#: Höchstens so weit stehen zwei Leisten beim zweiten Anker auseinander,
#: in Vielfachen von d (Gutachten 2007, Regel 5).
TANGENTIAL = 1.5

#: Die Durchmesser je statischer Höhe d (Gutachten 2007, Tabelle 1): bis zu
#: diesem d höchstens dieser Durchmesser; unter 0.160 m keiner.
GROESSTER_DURCHMESSER: Tuple[Tuple[float, float], ...] = (
    (0.180, 0.014), (0.220, 0.016), (0.260, 0.018), (0.340, 0.020), (0.600, 0.025),
    (math.inf, 0.030),
)
KLEINSTES_D = 0.160

#: Der Faktor des Gutachtens anstelle der 2 in Gleichung (70), und die
#: Obergrenze anstelle der 3.5: für Innenstützen, Wandenden und einspringende
#: Ecken 3·k_r, wenn die Überdeckung der unteren Köpfe höchstens d/10 ist;
#: bei d/6 gilt wieder 2·k_r, dazwischen linear (Gutachten 2007, S. 5–7).
#: Für Rand- und Eckstützen 2.0 wie in der Norm -- die Software von 2026 nennt
#: dort 3.0, ein Gutachten dazu war nicht lesbar.
K_SYS_HOCH = 3.0
K_SYS_NORM = 2.0
GRENZE = 3.5

#: Die Höhen h_A enden auf 5 mm, in Schritten von 10 mm (Preisliste).
HOEHENSCHRITT = 0.010


def groesster_durchmesser(d: float) -> Optional[float]:
    """Der grösste Ankerdurchmesser, den das Gutachten bei dieser statischen Höhe zulässt."""
    if d < KLEINSTES_D:
        return None
    return next(phi for bis, phi in GROESSTER_DURCHMESSER if d <= bis)


def ankerhoehe(h: float, c_zug: float, c_druck: float) -> float:
    """
    Die Höhe h_A der Anker: die Plattendicke ohne beide Überdeckungen, auf
    eine lieferbare Höhe abgerundet -- auf 5 mm, in Schritten von 10 mm.
    Nach der Zulassung ETA-13/0196 und zwei Beispielen von AncoTech, nach
    Vorgabe, nicht nachgeschlagen.
    """
    frei = h - c_zug - c_druck
    return round(math.floor(round((frei - 0.005) / HOEHENSCHRITT, 9)) * HOEHENSCHRITT + 0.005, 6)


def k_sys(c_druck: float, d: float, mit_ausnahme: bool) -> float:
    """
    Der Faktor anstelle der 2 in Gleichung (70) -- siehe :data:`K_SYS_HOCH`.
    ``mit_ausnahme``: Innenstütze, Wandende oder einspringende Ecke.
    """
    if not mit_ausnahme:
        return K_SYS_NORM
    if c_druck <= d / 10.0:
        return K_SYS_HOCH
    if c_druck >= d / 6.0:
        return K_SYS_NORM
    t = (c_druck - d / 10.0) / (d / 6.0 - d / 10.0)
    return K_SYS_HOCH + t * (K_SYS_NORM - K_SYS_HOCH)


def abstaende(d: float, anzahl: int) -> Tuple[float, ...]:
    """
    Die Abstände einer Leiste vom Rand der Stütze an, auf 5 mm abgerundet --
    der erste vom Rand zum ersten Anker, dann von Anker zu Anker.
    """
    def runden(x: float) -> float:
        return round(math.floor(round(x / 0.005, 9)) * 0.005, 6)
    folge = [runden(ABSTAND_ERSTER * d)]
    for i in range(1, anzahl):
        folge.append(runden((ABSTAND_BIS_DRITTER if i < 3 else ABSTAND_DANACH) * d))
    return tuple(folge)


def typname(typ: Ankertyp, anzahl: int, h_A: float) -> str:
    """«DA3-0215»: ungleiche Abstände, Typ, Anker je Leiste, Höhe h_A in mm."""
    return f"D{typ.buchstabe}{anzahl}-{round(h_A * 1e3):04d}"


# ===========================================================================
# ZEUS
# ===========================================================================


@dataclass(frozen=True)
class Stahlpilz:
    """Ein ZEUS-Stahlpilz: Art, s × s im Grundriss, Höhe h, Abstand g der Doppelstege."""

    art: str
    s: float
    h: float
    g: float = 0.0

    @property
    def name(self) -> str:
        """«ZEUS Kreuz 650 × 650, h = 160 mm»."""
        g = f", g = {round(self.g * 1e3)} mm" if self.g else ""
        return (f"ZEUS {self.art} {round(self.s * 1e3)} × {round(self.s * 1e3)} mm, "
                f"h = {round(self.h * 1e3)} mm{g}")

    def stege(self) -> Tuple[Tuple[Tuple[float, float], Tuple[float, float]], ...]:
        """Die Stege als Strecken im Grundriss -- fürs Bild: beim Kreuz zwei, sonst vier."""
        a = self.s / 2.0
        if not self.g:
            return (((-a, 0.0), (a, 0.0)), ((0.0, -a), (0.0, a)))
        b = self.g / 2.0
        return (((-a, -b), (a, -b)), ((-a, b), (a, b)), ((-b, -a), (-b, a)), ((b, -a), (b, a)))

    def armenden(self) -> Tuple[Tuple[float, float], ...]:
        """
        Wo die Stege enden, von der Stützenachse aus: beim Kreuz die vier
        Armenden, beim Doppel- und H-Kreuz je Arm zwei im Abstand g. Sie
        umschliessen die gestützte Fläche ausserhalb des Pilzes
        (SIA 262:2025, 4.3.6.6.2).
        """
        a = self.s / 2.0
        if not self.g:
            return ((a, 0.0), (0.0, a), (-a, 0.0), (0.0, -a))
        b = self.g / 2.0
        return ((a, -b), (a, b), (b, a), (-b, a), (-a, b), (-a, -b), (-b, -a), (b, -a))


def _pilze(art: str, s_mm: float, hoehen_mm, g_mm: float = 0.0) -> Tuple[Stahlpilz, ...]:
    return tuple(Stahlpilz(art, s_mm / 1e3, h / 1e3, g_mm / 1e3) for h in hoehen_mm)


#: Die ZEUS-Pilze der Preisliste, kleinste zuerst. Die Sondertypen (Rechteck)
#: und der Doppelkreuz ohne g sind weggelassen.
STAHLPILZE: Tuple[Stahlpilz, ...] = tuple(sorted(
    _pilze("Kreuz", 470, (100, 120)) + _pilze("Kreuz", 530, (120, 140, 160, 220))
    + _pilze("Kreuz", 650, (160, 180, 200, 230, 240)) + _pilze("Kreuz", 730, (180, 200, 220, 240))
    + _pilze("Kreuz", 780, (240, 260)) + _pilze("Kreuz", 800, (350, 400))
    + _pilze("Kreuz", 850, (260, 280, 300)) + _pilze("Kreuz", 900, (350, 400))
    + _pilze("Kreuz", 1000, (380, 400, 450)) + _pilze("Kreuz", 1060, (300, 320, 350))
    + _pilze("Kreuz", 1100, (440,)) + _pilze("Kreuz", 1200, (460, 500))
    + _pilze("Kreuz", 1360, (350, 400))
    + _pilze("Doppelkreuz", 530, (100, 120, 140), 150)
    + _pilze("Doppelkreuz", 650, (120, 140, 160, 180, 200), 150)
    + _pilze("Doppelkreuz", 730, (120, 140, 160, 180, 200, 220), 150)
    + _pilze("Doppelkreuz", 850, (180, 200, 220, 240), 150)
    + _pilze("Doppelkreuz", 1060, (220, 240, 260, 280), 150)
    + _pilze("Doppelkreuz", 1360, (280,), 150) + _pilze("Doppelkreuz", 1360, (300, 320), 200)
    + _pilze("Doppelkreuz", 1360, (350, 400), 250) + _pilze("Doppelkreuz", 1360, (380,), 300)
    + _pilze("H-Kreuz", 730, (120, 140, 160, 180), 150)
    + _pilze("H-Kreuz", 850, (180, 200, 220, 240), 150)
    + _pilze("H-Kreuz", 1060, (240, 260, 280), 150) + _pilze("H-Kreuz", 1360, (280, 300), 150)
    + _pilze("H-Kreuz", 1060, (300,), 200) + _pilze("H-Kreuz", 1360, (320,), 200)
    + _pilze("H-Kreuz", 1360, (350, 400), 250),
    key=lambda p: (p.s, p.g, p.h)))

#: Unter dem Pilz bleiben 20 mm Beton, über ihm 50 mm bis zur Oberfläche --
#: die Vorgaben der AncoTech-Software (Theorie 2010, S. 11, aus dem Bild).
PILZ_UNTEN = 0.020
PILZ_OBEN = 0.050

#: So weit müssen die Stege mindestens über die Stütze hinausreichen, sonst
#: vergrössert der Pilz die gestützte Fläche kaum (nach Vorgabe, nicht
#: nachgeschlagen).
PILZ_UEBERSTAND = 0.050
