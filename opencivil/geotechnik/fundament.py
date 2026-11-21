"""
opencivil/geotechnik/fundament.py -- ein Flachfundament auf seinem Baugrund.

VERANTWORTUNG:
Das :class:`Fundament` -- Boden, Abmessungen, Gelände und Grundwasser als
Vorgaben, dazu die Bemessungswerte der Scherfestigkeit --, die
:class:`Kombination` einer Einwirkung und was die zwei Nachweise am
Fundament gemeinsam haben (:class:`Fundamentnachweis`): den Grundbruch
(:mod:`~opencivil.geotechnik.grundbruch`) und das Gleiten
(:mod:`~opencivil.geotechnik.gleiten`). Dazu die Angaben über der Tabelle
der Zusammenfassung (:func:`angaben`).

Gerechnet wird mit Bemessungswerten: phi_eff = arctan(tan phi_k / gamma_phi)
und c_eff = c_k / gamma_c, undrainiert s_u,d = s_u,k / gamma_cu (SIA
267:2013, 5.3.2.1, 5.3.2.2). Ein globaler Sicherheitsgrad wie F_stat des
Buches kommt nicht dazu; den Widerstandsbeiwert gamma_R der Norm (8.5.2.1)
setzen beide Nachweise 1.0 (notizbuch/Notizen/TODO.md).

WINKEL (Bild 9.2.15 in Lang, Huder, Amann, Puzrin: Bodenmechanik und
Grundbau, 8. Aufl. 2007):
alpha ist die Neigung der Sohle, positiv, wenn sie gegen T ansteigt -- das
Abgleiten wird schwerer; beta die Neigung des Geländes, positiv, wenn es vom
Fundament weg abfällt. N steht normal zur Sohle, T in ihrer Richtung.

EINHEITEN:
Alles in SI-Basis; die Winkel als Groessen in Grad.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Eingabebezug, Formel
from opencivil.core.einheiten import EINHEITSLOS, GRAD, KN_PRO_M3, KPA, M, Groesse
from opencivil.core.latex import als_text, angabe
from opencivil.core.nachweis import Teilnachweis, Vergleich, grad_def
from opencivil.core.protokoll import Abschnitt, GleichungBlock, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.geotechnik.verhalten import Verhalten

#: Die dauernde Auflast neben dem Fundament, Kap. 9.2.5 des Buches.
KAP_AUFLAST = "Kap. 9.2.5"

#: Die Teilfaktoren des Bodens und seine Raumlast.
_TABELLE_1 = "SIA 267:2013, 5.3.2.2, Tabelle 1"


def _boden(verhalten: Verhalten) -> Tuple[Feld, ...]:
    """
    Je Verhalten seine Festigkeit; was nicht gilt, steht weder in der
    Herleitung noch in der Maske (Benutzer, 2026-11-19). Das Wasser zählt nur
    drainiert, über γ' -- undrainiert gelten totale Spannungen.
    """
    if verhalten is Verhalten.DRAINIERT:
        festigkeit = (
            Feld("phi_k", r"\varphi_k", GRAD, "Reibungswinkel, charakteristisch", 1,
                 beschriftung="Reibungswinkel"),
            Feld("gamma_phi", r"\gamma_{\varphi}", EINHEITSLOS,
                 "Partialfaktor des Reibungswinkels", 2, _TABELLE_1,
                 beschriftung="Partialfaktor", schritt=0.05),
            Feld("c_k", "c_k", KPA, "Kohäsion, charakteristisch", 1, beschriftung="Kohäsion",
                 hinweis="nur, wo sie dauerhaft wirkt (SIA 267:2013, 8.5.1.6)"),
            Feld("gamma_c", r"\gamma_c", EINHEITSLOS, "Partialfaktor der Kohäsion", 2, _TABELLE_1,
                 beschriftung="Partialfaktor", schritt=0.05),
        )
        wasser = (Feld("gamma_w", r"\gamma_w", KN_PRO_M3, "Raumlast des Wassers", 1,
                       beschriftung="Raumlast Wasser", schritt=0.5),)
    else:
        festigkeit = (
            Feld("s_u", "s_{u,k}", KPA, "Undrainierte Scherfestigkeit, charakteristisch", 1,
                 beschriftung="Scherfestigkeit", schritt=5),
            Feld("gamma_cu", r"\gamma_{cu}", EINHEITSLOS,
                 "Partialfaktor der undrainierten Scherfestigkeit", 2, _TABELLE_1,
                 beschriftung="Partialfaktor", schritt=0.05),
        )
        wasser = ()
    return (*festigkeit,
            Feld("gamma", r"\gamma", KN_PRO_M3, "Raumlast des Bodens, ohne Partialfaktor", 1,
                 _TABELLE_1, beschriftung="Raumlast Boden", schritt=0.5),
            *wasser)


#: Die Vorgaben des Grundbruchs, je Kasten der Herleitung und Karte der Maske
#: (:mod:`opencivil.core.vorgaben`). Die Sohlreibung hängt am Reibungswinkel:
#: undrainiert gilt sie nicht.
VORGABEN = (
    Gruppe("Boden", _boden, nach=("verhalten",)),
    Gruppe("Fundament", lambda: (
        Feld("b", "b", M, "Breite des Fundaments", 2, beschriftung="Breite", schritt=0.1,
             hinweis="die kürzere Seite"),
        Feld("L", "L", M, "Länge des Fundaments", 2, beschriftung="Länge", schritt=0.1),
        Feld("t", "t", M, "Tiefe der Sohle unter Terrain", 2, beschriftung="Tiefe der Sohle",
             schritt=0.1, hinweis="Oberkante Terrain bis Unterkante Fundament"),
        Feld("alpha", r"\alpha", GRAD, "Neigung der Sohle", 1, beschriftung="Sohlneigung",
             hinweis="positiv, wenn die Sohle in Richtung von T ansteigt"),
    )),
    Gruppe("Gelände und Grundwasser", lambda: (
        Feld("t1", "t_1", M, "Tiefe des höchsten Grundwasserspiegels unter Terrain", 2,
             "SIA 267:2013, 4.2.2.3", beschriftung="Grundwasser", schritt=0.1),
        Feld("beta", r"\beta", GRAD, "Neigung des Geländes", 1, beschriftung="Geländeneigung",
             hinweis="positiv, wenn das Gelände auf der Seite von T abfällt"),
        Feld("q_Ed", "q_{Ed}", KPA, "Dauernde Auflast neben dem Fundament", 1, KAP_AUFLAST,
             beschriftung="Auflast neben dem Fundament",
             hinweis="auf beiden Seiten mindestens über L_Gl; sie wirkt günstig"),
    )),
    Gruppe("Sohlreibung", lambda verhalten: (
        Feld("delta_faktor", r"k_{\delta}", EINHEITSLOS,
             "Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ_k/φ_k", 2,
             "SIA 267:2013, 8.4.1.1", beschriftung="Reibung der Sohle", schritt=0.05,
             hinweis="1 bei rauer Sohle mit dem Bruch im Boden, ½ bis ⅔ bei glatter mit dem "
                     "Bruch in der Fuge; δ_k höchstens 35°"),
    ) if verhalten is Verhalten.DRAINIERT else (), nach=("verhalten",)),
)

#: Was beide Widerstände annehmen -- die Norm teilt sie noch durch gamma_R.
OHNE_GAMMA_R = (
    "Grundbruch- und Gleitwiderstand ohne Widerstandsbeiwert, γ_R = 1.0. SIA 267:2013 "
    "teilt beide durch γ_R, in der Regel 1.0 bis 1.2, und lässt 1.0 bei bewährten, "
    "zuverlässigen Verfahren zu (8.5.2.1, (29), (30)); die Tragfähigkeitsformel nennt "
    "das Buch eine Näherung (Kap. 9.2.9).")


@dataclass
class Fundament(Rechenobjekt):
    """
    Ein Flachfundament auf seinem Baugrund: die Eingaben als Vorgaben im
    Rechenwerk, dazu die Bemessungswerte -- drainiert phi_eff, c_eff und
    gamma', undrainiert s_u,d.

    ``b`` ist die Breite, die kürzere Seite, ``L`` die Länge; ein
    Streifenfundament ist ein sehr langes.
    """

    WAS = "Grundbruch"

    name: str
    verhalten: Verhalten
    phi_k: Groesse
    gamma_phi: Groesse
    c_k: Groesse
    gamma_c: Groesse
    s_u: Groesse
    gamma_cu: Groesse
    gamma: Groesse
    gamma_w: Groesse
    q_Ed: Groesse
    b: Groesse
    L: Groesse
    t1: Groesse
    t: Groesse
    alpha: Groesse
    beta: Groesse
    delta_faktor: Groesse
    praefix: str

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.id = self.praefix
        self._aufbauen()

    @property
    def abschnitt(self) -> Abschnitt:
        """Ueberschrift, unter der das Fundament in der Herleitung steht."""
        return Abschnitt(f"Grundbruch: {self.name}", self.id, thema="Fundament")

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int = 2, referenz: str = "") -> WertDef:
        d = WertDef(id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
                    beschreibung=beschreibung, referenz=referenz, stellen=stellen)
        self.definitionen[kurzname] = d
        return d

    def _aufbauen(self) -> None:
        abschnitt = self.abschnitt
        drainiert = self.verhalten is Verhalten.DRAINIERT
        # Je Gruppe ein Kasten in der Herleitung -- wie die Abmessungen der Platte.
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                d, vorgabe = f.vorgabe(self.id, abschnitt, gruppe.titel, getattr(self, f.kurz))
                self.definitionen[f.kurz] = d
                self.berechnungen.append(vorgabe)

        if not drainiert:
            d_s = self._def("s_u_d", "s_{u,d}", KPA, "Undrainierte Scherfestigkeit, "
                            "Bemessungswert", 1, "SIA 267:2013, 5.3.2.1, (5)")
            self.berechnungen.append(Formel(
                id=d_s.id, ausgabe=d_s, abschnitt=abschnitt,
                eingaben={"s_u": self.id_von("s_u"), "gamma_cu": self.id_von("gamma_cu")},
                vorlage=r"\frac{@s_u}{@gamma_cu}", funktion=_s_u_d,
                name="Bemessungswert der undrainierten Scherfestigkeit"))
            return
        d_phi = self._def("phi_eff", r"\varphi_{eff}", GRAD,
                          "Reibungswinkel, Bemessungswert", 2, "SIA 267:2013, 5.3.2.1, (5)")
        d_c = self._def("c_eff", "c_{eff}", KPA, "Kohäsion, Bemessungswert", 1,
                        "SIA 267:2013, 5.3.2.1, (5)")
        d_ga = self._def("gamma_auftrieb", r"\gamma'", KN_PRO_M3,
                         "Raumlast des Bodens unter Auftrieb", 1)
        self.berechnungen += [
            Formel(
                id=d_phi.id, ausgabe=d_phi, abschnitt=abschnitt,
                eingaben={"phi_k": self.id_von("phi_k"), "gamma_phi": self.id_von("gamma_phi")},
                vorlage=r"\arctan\left(\frac{\tan @phi_k}{@gamma_phi}\right)",
                funktion=_phi_eff, name="Bemessungswert des Reibungswinkels"),
            Formel(
                id=d_c.id, ausgabe=d_c, abschnitt=abschnitt,
                eingaben={"c_k": self.id_von("c_k"), "gamma_c": self.id_von("gamma_c")},
                vorlage=r"\frac{@c_k}{@gamma_c}",
                funktion=_c_eff, name="Bemessungswert der Kohäsion"),
            Formel(
                id=d_ga.id, ausgabe=d_ga, abschnitt=abschnitt,
                eingaben={"gamma": self.id_von("gamma"), "gamma_w": self.id_von("gamma_w")},
                vorlage=r"@gamma - @gamma_w",
                funktion=_gamma_auftrieb, name="Raumlast unter Auftrieb"),
        ]


def _phi_eff(phi_k: Groesse, gamma_phi: Groesse) -> Groesse:
    return Groesse.aus_si(math.atan(math.tan(phi_k.si) / gamma_phi.si), GRAD)


def _c_eff(c_k: Groesse, gamma_c: Groesse) -> Groesse:
    return Groesse.aus_si(c_k.si / gamma_c.si, KPA)


def _s_u_d(s_u: Groesse, gamma_cu: Groesse) -> Groesse:
    return Groesse.aus_si(s_u.si / gamma_cu.si, KPA)


def _gamma_auftrieb(gamma: Groesse, gamma_w: Groesse) -> Groesse:
    return Groesse.aus_si(gamma.si - gamma_w.si, KN_PRO_M3)


@dataclass(frozen=True)
class Kombination:
    """Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung."""

    name: str
    N_Ed: Groesse
    T_Ed: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


# ===========================================================================
# Was beide Nachweise teilen
# ===========================================================================


class Fundamentnachweis(Teilnachweis):
    """
    Was Grundbruch und Gleiten gemeinsam haben: je Kombination einen
    Erfüllungsgrad, die Eingänge aus dem Fundament -- je Verhalten andere --,
    Titel und Abschnitt, und wie ein Fall ausgeht (:meth:`vergleichen`).
    Vorbild ist :class:`~opencivil.pfahl.achse.Achsnachweis`.
    """

    FELD: str = ""
    """Wie der Nachweis im Aufbau und in seinen Kennungen heisst: «grundbruch»."""

    BODEN: Dict[Verhalten, Tuple[str, ...]] = {}
    """Was er je Verhalten vom Boden liest -- drainiert anderes als undrainiert."""

    MASSE: Tuple[str, ...] = ()
    """Was er sonst vom Fundament liest, unter jedem Verhalten."""

    def __init__(self, fundament: Fundament, kombinationen: Sequence[Kombination]) -> None:
        if not kombinationen:
            raise ValueError(f"Der Nachweis «{self.THEMA}» braucht mindestens eine Kombination.")
        self.fundament = fundament
        self.kombinationen = list(kombinationen)
        basis = f"{fundament.id}.nachweis.{self.FELD}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{self.ART},{als_text(k.name)}}}",
                             f"Erfüllungsgrad {self.THEMA} – {k.name}")
            for k in self.kombinationen}
        bezuege = [Eingabebezug(n, fundament.id_von(n))
                   for n in (*self.BODEN[fundament.verhalten], *self.MASSE)]
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()), bezuege=bezuege,
                         titel=f"{self.THEMA} – {fundament.name}",
                         abschnitt=fundament.abschnitt)

    def vergleichen(self, p: Protokoll, k: Kombination, E: Wert, R: Wert,
                    namen: Tuple[str, str]) -> Tuple[Vergleich, str]:
        """
        Die Einwirkung ``E`` einer Kombination gegen den Widerstand ``R``, in
        die Herleitung geschrieben, und der Satz für die Nachweistabelle --
        «N_Rd = 812.3 kN ≥ N_Ed = 600.0 kN.»; ``namen`` sind die von E und R.
        """
        v = Vergleich(E, R)
        v.bedingung(p, "Einwirkung gegen Widerstand")
        v.zeile(p, self.d_ausnutzung[k.name])
        return v, (f"{namen[1]} = {R.formatiert()} kN {'≥' if v.erfuellt else '<'} "
                   f"{namen[0]} = {E.formatiert()} kN.")


# ===========================================================================
# Für die Zusammenfassung
# ===========================================================================


def angaben(fundament: Fundament, werte: Dict[str, Wert]) -> GleichungBlock:
    """
    Die Angaben über der Tabelle, aus den Werten der Lösung, wie sie
    gerechnet wurden: in der ersten Zeile der Boden mit seinen
    Bemessungswerten, in der zweiten die Masse und das Grundwasser. In einer
    Zeile wären es acht Angaben -- breiter als die Spalte.
    """
    def zeile(namen: Sequence[str]) -> str:
        return r" \qquad ".join(angabe(werte[fundament.id_von(n)]) for n in namen
                                if n in fundament.definitionen
                                and fundament.id_von(n) in werte)

    boden = zeile(("phi_eff", "c_eff", "s_u_d", "gamma", "gamma_auftrieb"))
    masse = zeile(("b", "L", "t", "t1"))
    return GleichungBlock(latex=rf"\begin{{aligned}} & {boden} \\ & {masse} \end{{aligned}}",
                          titel="Angaben zum Fundament")
