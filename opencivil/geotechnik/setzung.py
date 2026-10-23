"""
opencivil/geotechnik/setzung.py -- die Setzung eines Flachfundaments auf geschichtetem Baugrund.

VERANTWORTUNG:
Das :class:`Setzungsfundament` -- die Lastfläche L × B, die Pressungen in der
Sohle, die zulässige Setzung und die Schichten des Baugrunds mit ihren
M_E-Werten, als Vorgaben im Rechenwerk -- und der Nachweis :class:`Setzung`:
s ≤ s_zul.

DAS VERFAHREN (Kap. 8.2 bis 8.5):
Jede Schicht wird in gleich dicke Teilschichten von höchstens Δz_max
zerlegt; eine Schichtgrenze ist immer auch eine Grenze von Teilschichten. Je
Teilschicht::

    Δs = J̄ · q_W · Δz / M'_E + J̄ · q_E · Δz / M_E        J̄ = (J_o + J_u) / 2

Die Pressung aus Wiederbelastung q_W rechnet mit dem Modul der
Wiederbelastung M'_E, die aus Erstbelastung q_E mit dem der Erstbelastung M_E
(Kap. 8.5); beide gibt der Benutzer getrennt an. J̄ mittelt den
Einflussfaktor an Ober- und Unterkante, wie die Spalte «J_K mittel» der
Tabelle 8.4. Die Setzung ist die Summe über alle Teilschichten; unter der
untersten Schicht gilt der Baugrund als unzusammendrückbar (Bild 8.1).

DER EINFLUSSFAKTOR (Kap. 8.2):
Die Zusatzspannung unter einer gleichmässig belasteten Rechteckfläche nach
Boussinesq, Δσ'_z = J · q. Unter einer Ecke eines Rechtecks a × b in der
Tiefe z (:func:`einflussfaktor_ecke`)::

    J_E = 1/(2π) · [arctan(a b / (z R)) + a b z / R · (1/(a² + z²) + 1/(b² + z²))]
    R   = √(a² + b² + z²)

Unter einem anderen Punkt der Fläche die Summe der vier Rechtecke, die sich in
ihm treffen (:func:`einflussfaktor`). Welcher Punkt, sagt die
:class:`Steifigkeit` (Kap. 8.10): beim starren Fundament der kennzeichnende
Punkt K, 0.13 L und 0.13 B von einer Ecke (Bild 8.15) -- dort setzt sich die
schlaffe Last so stark, wie sich das starre Fundament im Mittel setzt; beim
schlaffen die Mitte, wo die Setzungsmulde am tiefsten ist.

QUELLE:
Das Kapitel 8 «Setzungsberechnung», das der Benutzer geliefert hat; der
Abschnitt steht an jeder Formel. Die Formel für J_E steht dort nicht -- das
Kapitel verweist auf Kapitel 3, das nicht vorliegt. Sie gibt die Werte J_K
der Tabelle 8.4 auf die gedruckte Stelle wieder und die Grenztiefen der
Tabelle 8.5 so genau, wie sie dort stehen (tests/test_setzung.py); nicht
nachgeschlagen (notizbuch/Notizen/TODO.md).

EINHEITEN:
Alles in SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Berechnung, Eingabebezug, Eingaben, Nachweis, NachweisUrteil, Vorgabe,
    grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN_PRO_M2, M, MM, MN_PRO_M2, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text, angabe, bedingung, fest
from opencivil.core.protokoll import (
    Abschnitt, GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte,
)
from opencivil.core.wahl import Wahl
from opencivil.core.wert import Wert, WertDef

#: Wo der kennzeichnende Punkt K liegt: 0.13 L und 0.13 B von einer Ecke (Bild 8.15).
K = 0.13

#: Die Abschnitte des gelieferten Kapitels, an den Formeln als Referenz.
KAP_PRINZIP = "Kap. 8.2"
KAP_TABELLE = "Kap. 8.3, Tabelle 8.4"
KAP_EINFLUSSTIEFE = "Kap. 8.4"
KAP_WIEDERBELASTUNG = "Kap. 8.5"
KAP_STEIFIGKEIT = "Kap. 8.10, Bild 8.15"

#: Die Einheit der M_E-Werte in den Köpfen der Tabellen.
MODUL = MN_PRO_M2.latex


class Steifigkeit(Wahl):
    """
    Ob das Fundament der Setzungsmulde folgt -- und darum, unter welchem Punkt
    gerechnet wird (Kap. 8.10).
    """

    STARR = "starr"
    SCHLAFF = "schlaff"

    @property
    def beschriftung(self) -> str:
        """Wie sie an der Maske heisst."""
        return {Steifigkeit.STARR: "starr – Punkt K",
                Steifigkeit.SCHLAFF: "schlaff – Mitte"}[self]

    @property
    def punkt(self) -> str:
        """Wie der Punkt heisst, unter dem gerechnet wird."""
        return {Steifigkeit.STARR: "Punkt K", Steifigkeit.SCHLAFF: "Mitte"}[self]

    def lage(self, L: float, B: float) -> Tuple[float, float]:
        """Wo dieser Punkt liegt, von einer Ecke aus: längs L und längs B, in m."""
        if self is Steifigkeit.STARR:
            return K * L, K * B
        return L / 2.0, B / 2.0


# ===========================================================================
# Der Einflussfaktor
# ===========================================================================


def einflussfaktor_ecke(a: float, b: float, z: float) -> float:
    """
    J_E unter einer Ecke der gleichmässig belasteten Rechteckfläche a × b, in
    der Tiefe z -- in m. In der Sohle ein Viertel: die vier Rechtecke um einen
    Punkt tragen dort zusammen die ganze Pressung.
    """
    if a <= 0.0 or b <= 0.0:
        return 0.0
    if z <= 0.0:
        return 0.25
    R = math.sqrt(a * a + b * b + z * z)
    return (math.atan(a * b / (z * R))
            + a * b * z / R * (1.0 / (a * a + z * z) + 1.0 / (b * b + z * z))) / (2.0 * math.pi)


def einflussfaktor(L: float, B: float, x: float, y: float, z: float) -> float:
    """
    J unter dem Punkt (x, y) der Fläche L × B, in der Tiefe z: die vier
    Rechtecke, die sich in ihm treffen. x längs L, y längs B, von einer Ecke
    aus; alles in m.
    """
    return sum(einflussfaktor_ecke(a, b, z) for a in (x, L - x) for b in (y, B - y))


def einflusslinie(L: float, B: float, x: float, y: float, tiefe: float,
                  schritte: int = 60) -> List[Tuple[float, float]]:
    """
    J über die Tiefe, von der Sohle bis ``tiefe`` -- für das Bild. Die
    Schritte werden zur Sohle hin dichter: dort ändert sich J am schnellsten.
    """
    tiefen = [tiefe * (i / schritte) ** 2 for i in range(schritte + 1)]
    return [(z, einflussfaktor(L, B, x, y, z)) for z in tiefen]


# ===========================================================================
# Das Fundament
# ===========================================================================


@dataclass(frozen=True)
class Schicht:
    """Eine Schicht des Baugrunds, von der Sohle an nach unten gezählt."""

    name: str
    d: Groesse
    """Die Dicke der Schicht."""

    M_E: Groesse
    """Der M_E-Wert der Erstbelastung."""

    M_E_strich: Groesse
    """Der M_E-Wert der Wiederbelastung, M'_E."""


@dataclass
class Setzungsfundament:
    """
    Ein Flachfundament auf geschichtetem Baugrund: die Eingaben als Vorgaben
    im Rechenwerk. ``B`` und ``L`` sind die Seiten der Lastfläche; die
    Schichten liegen von der Sohle an nach unten, z wird ab der Sohle gemessen.
    """

    name: str
    B: Groesse
    L: Groesse
    q_W: Groesse
    q_E: Groesse
    s_zul: Groesse
    dz: Groesse
    steifigkeit: Steifigkeit
    schichten: Sequence[Schicht]
    praefix: str

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.id = self.praefix
        self._aufbauen()

    @property
    def abschnitt(self) -> Abschnitt:
        """Ueberschrift, unter der das Fundament in der Herleitung steht."""
        return Abschnitt(f"Setzung: {self.name}", self.id, thema="Setzung")

    def id_von(self, kurzname: str) -> str:
        return self.definitionen[kurzname].id

    def ins_rechenwerk(self, werk) -> "Setzungsfundament":
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def _aufbauen(self) -> None:
        # Je Gruppe ein Kasten in der Herleitung, je Schicht einer -- wie beim Grundbruch.
        vorgaben = [
            ("Fundament", (
                ("B", "B", M, "Breite des Fundaments", 2, self.B),
                ("L", "L", M, "Länge des Fundaments", 2, self.L),
            )),
            ("Pressung in der Sohle", (
                ("q_W", "q_W", KN_PRO_M2, "Pressung aus Wiederbelastung", 1, self.q_W),
                ("q_E", "q_E", KN_PRO_M2, "Pressung aus Erstbelastung", 1, self.q_E),
            )),
            ("Nachweis", (
                ("s_zul", "s_{zul}", MM, "Zulässige Setzung", 1, self.s_zul),
                ("dz", r"\Delta z_{max}", M, "Grösste Dicke einer Teilschicht", 2, self.dz),
            )),
        ]
        for i, schicht in enumerate(self.schichten, start=1):
            vorgaben.append((f"Schicht {i}: {schicht.name}", (
                (f"d_{i}", f"d_{{{i}}}", M, f"Dicke der Schicht {i}", 2, schicht.d),
                (f"M_E_{i}", f"M_{{E,{i}}}", MN_PRO_M2,
                 f"M_E-Wert der Schicht {i}, Erstbelastung", 1, schicht.M_E),
                (f"M_E_strich_{i}", f"M'_{{E,{i}}}", MN_PRO_M2,
                 f"M_E-Wert der Schicht {i}, Wiederbelastung", 1, schicht.M_E_strich),
            )))
        for gruppe, eintraege in vorgaben:
            for kurz, symbol, einheit, beschreibung, stellen, groesse in eintraege:
                d = WertDef(id=f"{self.id}.{kurz}", symbol=symbol, einheit=einheit,
                            beschreibung=beschreibung, stellen=stellen)
                self.definitionen[kurz] = d
                self.berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=groesse,
                                                 abschnitt=self.abschnitt, gruppe=gruppe))


# ===========================================================================
# Befund
# ===========================================================================


@dataclass(frozen=True)
class Teilschicht:
    """Eine Zeile der Tabelle: Tiefen in m ab der Sohle, Setzungen in m."""

    schicht: int
    """Die Schicht, in der sie liegt -- ihr Platz in der Liste, ab null."""

    z_o: float
    z_u: float
    J_o: float
    J_u: float
    ds_W: float
    ds_E: float

    @staticmethod
    def mittel(J_o: float, J_u: float) -> float:
        """Der Einflussfaktor einer Teilschicht: an Ober- und Unterkante gemittelt (Tabelle 8.4)."""
        return (J_o + J_u) / 2.0

    @property
    def J(self) -> float:
        return self.mittel(self.J_o, self.J_u)


@dataclass(frozen=True)
class Schichtsetzung:
    """Was eine Schicht zur Setzung beiträgt -- Tiefen in m ab der Sohle, Setzungen in m."""

    name: str
    z_o: float
    z_u: float
    s_W: float
    s_E: float

    @property
    def s(self) -> float:
        return self.s_W + self.s_E


@dataclass
class Setzungsbefund:
    """Was ausser dem Erfüllungsgrad bleibt -- für die Zusammenfassung und das Bild."""

    punkt: Tuple[float, float]
    """Wo gerechnet wurde, von einer Ecke aus: längs L und längs B, in m."""

    teilschichten: List[Teilschicht]
    schichten: List[Schichtsetzung]
    J_fuss: float
    """Der Einflussfaktor am Fuss der untersten Schicht."""

    @property
    def s_W(self) -> float:
        return sum(s.s_W for s in self.schichten)

    @property
    def s_E(self) -> float:
        return sum(s.s_E for s in self.schichten)

    @property
    def s(self) -> float:
        return self.s_W + self.s_E


# ===========================================================================
# Der Nachweis
# ===========================================================================


class Setzung(Nachweis):
    """
    Die Setzung unter dem Punkt, den die Steifigkeit des Fundaments
    bestimmt, gegen die zulässige: s ≤ s_zul, der Erfüllungsgrad s_zul / s.
    """

    THEMA = "Setzung"
    ART = "s"

    def __init__(self, fundament: Setzungsfundament) -> None:
        if not fundament.schichten:
            raise ValueError("Die Setzung braucht mindestens eine Schicht.")
        self.fundament = fundament
        basis = f"{fundament.id}.nachweis.setzung"
        self.d_grad: WertDef = grad_def(f"{basis}.erfuellungsgrad", r"\alpha_{eff,s}",
                                        "Erfüllungsgrad Setzung")
        namen = ["B", "L", "q_W", "q_E", "s_zul", "dz"]
        for i in range(1, len(fundament.schichten) + 1):
            namen += [f"d_{i}", f"M_E_{i}", f"M_E_strich_{i}"]
        super().__init__(basis, ausgaben=[self.d_grad],
                         bezuege=[Eingabebezug(n, fundament.id_von(n)) for n in namen],
                         titel=f"Setzung – {fundament.name}", abschnitt=fundament.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Setzung")
        p.erklaerung(
            "Unter der Last drückt sich das Korngerüst des Bodens zusammen. Je "
            "Teilschicht zählt die Zusatzspannung, die von der Pressung in der Sohle "
            "in ihrer Tiefe noch ankommt, und der M_E-Wert ihrer Schicht: was den "
            "Boden nur wieder so stark belastet, wie er schon einmal belastet war, "
            "mit dem Modul der Wiederbelastung M'_E, was darüber hinausgeht, mit dem "
            "der Erstbelastung M_E. Unter der untersten Schicht gilt der Baugrund als "
            "unzusammendrückbar."
        )
        p.ansatz(
            r"\Delta s = \frac{\bar{J} \, q_W \, \Delta z}{M'_E}"
            r" + \frac{\bar{J} \, q_E \, \Delta z}{M_E} \qquad"
            r" \bar{J} = \frac{J_o + J_u}{2} \qquad s = \sum \Delta s",
            titel="Setzung einer Teilschicht", referenz=KAP_WIEDERBELASTUNG,
            name="Setzung einer Teilschicht")

        x, y = self._punkt(e, p)
        teilschichten = self._teilschichten(e, p, x, y)
        befund = self._schichten(e, p, teilschichten, x, y)
        return self._nachweis(e, p, befund)

    # -- Der Punkt und sein Einflussfaktor ----------------------------------

    def _punkt(self, e: Eingaben, p: Protokoll) -> Tuple[float, float]:
        """Wo gerechnet wird -- K oder die Mitte --, mit der Formel für J darunter."""
        steifigkeit = self.fundament.steifigkeit
        starr = steifigkeit is Steifigkeit.STARR
        p.titel(f"Einflussfaktor unter {'dem Punkt K' if starr else 'der Mitte'}", ebene=3)
        B, L = e["B"], e["L"]
        x_si, y_si = steifigkeit.lage(L.groesse.si, B.groesse.si)
        if starr:
            p.text("Starres Fundament: gerechnet wird im kennzeichnenden Punkt K -- dort "
                   "setzt sich die schlaffe Last so stark, wie sich das starre Fundament "
                   "im Mittel setzt.")
            zeichen, wer, referenz = "K", "des Punktes K", KAP_STEIFIGKEIT
            vorlagen = (r"0.13 \cdot @L", r"0.13 \cdot @B")
        else:
            p.text("Schlaffes Fundament: gerechnet wird unter der Mitte, wo die "
                   "Setzungsmulde am tiefsten ist.")
            zeichen, wer, referenz = "M", "der Mitte", "Kap. 8.10"
            vorlagen = (r"\frac{@L}{2}", r"\frac{@B}{2}")
        werte = Zwischenwerte(self.id)
        for achse, si, seite, vorlage in (("x", x_si, L, vorlagen[0]),
                                          ("y", y_si, B, vorlagen[1])):
            laengs = "L" if achse == "x" else "B"
            wert = werte.wert(achse, f"{achse}_{zeichen}", Groesse.aus_si(si, M), 2,
                              f"Lage des Punktes längs {laengs}")
            p.formel(wert, vorlage, {laengs: seite},
                     titel=f"Abstand {wer} von der Ecke, längs {laengs}", referenz=referenz,
                     name=f"Lage des Punktes längs {laengs}")
        p.ansatz(
            r"\begin{aligned} J &= J_E(x, y) + J_E(L - x, y) + J_E(x, B - y) + J_E(L - x, B - y)"
            r" \\ J_E(a, b) &= \frac{1}{2\pi} \left[\arctan\frac{a \, b}{z \, R}"
            r" + \frac{a \, b \, z}{R} \left(\frac{1}{a^2 + z^2} + \frac{1}{b^2 + z^2}\right)"
            r"\right] \qquad R = \sqrt{a^2 + b^2 + z^2} \end{aligned}",
            titel="Einflussfaktor nach Boussinesq in der Tiefe z: die vier Rechtecke, die "
                  "sich im Punkt treffen", referenz=KAP_PRINZIP,
            name="Einflussfaktor der Rechtecklast")
        return x_si, y_si

    # -- Die Teilschichten --------------------------------------------------

    def _teilschichten(self, e: Eingaben, p: Protokoll, x: float, y: float) -> List[Teilschicht]:
        """Jede Schicht in gleich dicke Teilschichten, je eine Zeile der Tabelle."""
        f = self.fundament
        L, B = e["L"].groesse.si, e["B"].groesse.si
        q_W, q_E = e["q_W"].groesse.si, e["q_E"].groesse.si
        dz_max = e["dz"].groesse.si
        p.titel("Teilschichten", ebene=3)
        p.text(f"Jede Schicht in gleich dicke Teilschichten von höchstens "
               f"Δz_max = {e['dz'].formatiert()} m; J an Ober- und Unterkante, gemittelt. "
               f"z ab der Sohle.")
        teile: List[Teilschicht] = []
        oben, J_o = 0.0, einflussfaktor(L, B, x, y, 0.0)
        for i in range(1, len(f.schichten) + 1):
            d = e[f"d_{i}"].groesse.si
            M_E, M_W = e[f"M_E_{i}"].groesse.si, e[f"M_E_strich_{i}"].groesse.si
            n = max(1, math.ceil(d / dz_max - 1e-9))
            for k in range(n):
                z_o, z_u = oben + d * k / n, oben + d * (k + 1) / n
                J_u = einflussfaktor(L, B, x, y, z_u)
                J = Teilschicht.mittel(J_o, J_u)
                teile.append(Teilschicht(schicht=i - 1, z_o=z_o, z_u=z_u, J_o=J_o, J_u=J_u,
                                         ds_W=J * q_W * (z_u - z_o) / M_W,
                                         ds_E=J * q_E * (z_u - z_o) / M_E))
                J_o = J_u
            oben += d
        mm = 1e3
        # Die M_E-Werte stehen je Schicht in der Tabelle danach -- hier hätten
        # sie die Tabelle breiter gemacht als die Tafel.
        p.tabelle(
            kopf=["Schicht", Mathe(r"z_o\ [\mathrm{m}]"), Mathe(r"z_u\ [\mathrm{m}]"),
                  Mathe("J_o"), Mathe("J_u"), Mathe(r"\bar{J}"),
                  Mathe(r"\Delta s_W\ [\mathrm{mm}]"), Mathe(r"\Delta s_E\ [\mathrm{mm}]")],
            zeilen=[[f.schichten[t.schicht].name, Mathe(fest(t.z_o, 2)), Mathe(fest(t.z_u, 2)),
                     Mathe(fest(t.J_o, 3)), Mathe(fest(t.J_u, 3)), Mathe(fest(t.J, 3)),
                     Mathe(fest(t.ds_W * mm, 2)), Mathe(fest(t.ds_E * mm, 2))]
                    for t in teile],
            titel="Setzung je Teilschicht", ausrichtung="lrrrrrrr")
        return teile

    def _schichten(self, e: Eingaben, p: Protokoll, teile: Sequence[Teilschicht],
                   x: float, y: float) -> Setzungsbefund:
        """Die Teilschichten je Schicht zusammengezählt -- und was am Fuss noch ankommt."""
        f = self.fundament
        schichten: List[Schichtsetzung] = []
        for i, schicht in enumerate(f.schichten):
            eigene = [t for t in teile if t.schicht == i]
            schichten.append(Schichtsetzung(
                name=schicht.name, z_o=eigene[0].z_o, z_u=eigene[-1].z_u,
                s_W=sum(t.ds_W for t in eigene), s_E=sum(t.ds_E for t in eigene)))
        befund = Setzungsbefund(punkt=(x, y), teilschichten=list(teile), schichten=schichten,
                                J_fuss=teile[-1].J_u)
        p.tabelle(
            kopf=["Schicht", Mathe(r"z_o\ [\mathrm{m}]"), Mathe(r"z_u\ [\mathrm{m}]"),
                  Mathe(rf"M'_E\ [{MODUL}]"), Mathe(rf"M_E\ [{MODUL}]"),
                  Mathe(r"s_W\ [\mathrm{mm}]"), Mathe(r"s_E\ [\mathrm{mm}]"),
                  Mathe(r"s\ [\mathrm{mm}]")],
            zeilen=[[s.name, Mathe(fest(s.z_o, 2)), Mathe(fest(s.z_u, 2)),
                     Mathe(fest(e[f"M_E_strich_{i}"].groesse.in_einheit(MN_PRO_M2), 1)),
                     Mathe(fest(e[f"M_E_{i}"].groesse.in_einheit(MN_PRO_M2), 1)),
                     Mathe(fest(s.s_W * 1e3, 2)), Mathe(fest(s.s_E * 1e3, 2)),
                     Mathe(fest(s.s * 1e3, 2))] for i, s in enumerate(schichten, start=1)],
            titel="Setzung je Schicht", ausrichtung="lrrrrrrr")
        p.text(f"Am Fuss der untersten Schicht, z = {fest(teile[-1].z_u, 2)} m unter der Sohle, "
               f"kommt noch J = {fest(befund.J_fuss, 3)} der Pressung an; darunter gilt der "
               f"Baugrund als unzusammendrückbar ({KAP_EINFLUSSTIEFE}).")
        return befund

    # -- Der Vergleich ------------------------------------------------------

    def _nachweis(self, e: Eingaben, p: Protokoll, befund: Setzungsbefund) -> Ausfuehrung:
        p.titel("Setzung gegen zulässige Setzung", ebene=3)
        werte = Zwischenwerte(self.id)
        s_W = werte.laenge("s_W", "s_W", befund.s_W, "Setzung aus Wiederbelastung", stellen=1)
        p.formel(s_W, r"\sum \Delta s_W", {}, titel="Setzung aus Wiederbelastung",
                 referenz=KAP_WIEDERBELASTUNG, name="Setzung aus Wiederbelastung")
        s_E = werte.laenge("s_E", "s_E", befund.s_E, "Setzung aus Erstbelastung", stellen=1)
        p.formel(s_E, r"\sum \Delta s_E", {}, titel="Setzung aus Erstbelastung",
                 referenz=KAP_WIEDERBELASTUNG, name="Setzung aus Erstbelastung")
        s = werte.laenge("s", "s", befund.s, "Setzung", stellen=1)
        p.formel(s, "@s_W + @s_E", {"s_W": s_W, "s_E": s_E}, titel="Setzung",
                 referenz=KAP_PRINZIP, name="Gesamtsetzung")
        s_zul = e["s_zul"]
        erfuellt = s.groesse.si <= s_zul.groesse.si
        grad = float("inf") if s.groesse.si == 0.0 else s_zul.groesse.si / s.groesse.si
        p.gleichung(bedingung(angabe(s), r"\le", angabe(s_zul), erfuellt, mit_urteil=False),
                    titel="Setzung gegen zulässige Setzung")
        grad_formel(p, self.d_grad, grad, s_zul, s, erfuellt, mit_urteil=True)
        urteil = NachweisUrteil(
            art=self.ART, ziel=self.d_grad.id, fall=self._fall, erfuellt=erfuellt,
            erfuellungsgrad=Groesse(grad, EINHEITSLOS),
            begruendung=(f"s = {s.formatiert()} mm {'≤' if erfuellt else '>'} "
                         f"s_zul = {s_zul.formatiert()} mm."),
            einwirkung=s, widerstand=s_zul)
        return Ausfuehrung({self.d_grad.id: Groesse(grad, EINHEITSLOS)}, [urteil], befund)

    @property
    def _fall(self) -> str:
        """Wie die Zeile der Zusammenfassung heisst: unter welchem Punkt gerechnet wurde."""
        return f"{self.fundament.steifigkeit.value}, {self.fundament.steifigkeit.punkt}"


# ===========================================================================
# Für die Zusammenfassung
# ===========================================================================


def angaben(fundament: Setzungsfundament, werte: Dict[str, Wert]) -> GleichungBlock:
    """
    Die Angaben über der Tabelle, aus den Werten der Lösung, wie sie gerechnet
    wurden: die Lastfläche, die Pressungen und wo gerechnet wird.
    """
    teile = [angabe(werte[fundament.id_von(n)]) for n in ("B", "L", "q_W", "q_E")
             if fundament.id_von(n) in werte]
    teile.append(als_text(f"{fundament.steifigkeit.value}, {fundament.steifigkeit.punkt}"))
    return GleichungBlock(latex=r" \qquad ".join(teile), titel="Angaben zum Fundament")


def schichttabelle(fundament: Setzungsfundament, werte: Dict[str, Wert],
                   befund: Setzungsbefund) -> TabellenBlock:
    """Die Schichten, wie man sie im Schnitt sieht: Tiefe, M_E-Werte und ihr Beitrag zur Setzung."""
    def modul(kurz: str) -> Zelle:
        wert = werte.get(fundament.id_von(kurz))
        return Mathe(fest(wert.groesse.in_einheit(MN_PRO_M2), 1)) if wert is not None else "–"

    zeilen: List[List[Zelle]] = []
    for i, s in enumerate(befund.schichten, start=1):
        zeilen.append([s.name, Mathe(f"{fest(s.z_o, 2)} – {fest(s.z_u, 2)}"),
                       modul(f"M_E_{i}"), modul(f"M_E_strich_{i}"),
                       Mathe(fest(s.s_W * 1e3, 1)), Mathe(fest(s.s_E * 1e3, 1)),
                       Mathe(fest(s.s * 1e3, 1))])
    return TabellenBlock(
        kopf=["Schicht", Mathe(r"z\ [\mathrm{m}]"), Mathe(rf"M_E\ [{MODUL}]"),
              Mathe(rf"M'_E\ [{MODUL}]"), Mathe(r"s_W\ [\mathrm{mm}]"),
              Mathe(r"s_E\ [\mathrm{mm}]"), Mathe(r"s\ [\mathrm{mm}]")],
        zeilen=zeilen, titel="Schichten", ausrichtung="lrrrrrr")
