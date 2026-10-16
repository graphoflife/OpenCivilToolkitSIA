"""
opencivil/geotechnik/grundbruch.py -- Grundbruch und Gleiten eines Flachfundaments.

VERANTWORTUNG:
Das :class:`Fundament` -- Boden, Abmessungen, Gelände und Grundwasser als
Vorgaben, dazu die Bemessungswerte der Scherfestigkeit -- und je
Einwirkungskombination zwei Nachweise:

* :class:`Grundbruch` -- der Grundbruchwiderstand nach der erweiterten
  Tragfähigkeitsformel (Kap. 9.2.10)::

      sigma_f = c N_c s_c d_c i_c g_c b_c
              + (gamma t + q) N_q s_q d_q i_q g_q b_q
              + 1/2 gamma b N_gamma s_gamma d_gamma i_gamma g_gamma b_gamma
      N_Rd    = sigma_f · b · L

  und für phi = 0, undrainiert (Kap. 9.2.17)::

      sigma_f = 5.1 s_u (1 + s_c + d_c - i_c - b_c - g_c) + (gamma t + q)

* :class:`Gleiten` -- der Gleitwiderstand in der Sohle,
  T_Rd = N_Ed · tan delta* (Kap. 9.2.18).

Gerechnet wird mit Bemessungswerten: phi_eff = arctan(tan phi_k / gamma_phi)
(SIA 267:2013, 5.3.2.1) und c_eff = c_k / gamma_c. Ein globaler
Sicherheitsgrad wie F_stat des Kapitels kommt nicht dazu.

QUELLE:
Die Formeln stammen aus dem Kapitel 9.2 «Tragfähigkeit», das der Benutzer
geliefert hat; der Abschnitt steht an jeder Formel. Wo der Text und seine
Tabellen auseinandergehen, steht es beim Faktor: b_gamma rechnet nach
Tabelle 9.2.18 mit tan phi, im Text steht tan alpha.

WINKEL (Bild 9.2.15):
alpha ist die Neigung der Sohle, positiv, wenn sie gegen T ansteigt -- das
Abgleiten wird schwerer; beta die Neigung des Geländes, positiv, wenn es vom
Fundament weg abfällt; delta_R die Neigung der Last gegen die Sohlnormale.
N steht normal zur Sohle, T in ihrer Richtung. Alle drei Winkel gehen in Grad
in die Faktoren ein, wie das Kapitel sie schreibt («0.007 arctan t/b»).

GRUNDWASSER (Bild 9.2.10):
t_1 ist die Tiefe des höchsten Grundwasserspiegels unter Terrain. Liegt er
über der Sohle oder auf ihr (Lage 1, 2), zählt unter ihm gamma'; liegt er um
mindestens die Tiefe H des Gleitkörpers tiefer (Lage 3), zählt gamma.
Dazwischen verlangt das Kapitel eine Stabilitätsberechnung; gerechnet wird
dann mit gamma' wie in Lage 2, auf der sicheren Seite -- eine Annahme, nicht
aus dem Kapitel (notizbuch/Notizen/TODO.md). Undrainiert zählen totale
Spannungen, das Wasser spielt dort keine Rolle.

EINHEITEN:
Alles in SI-Basis; die Winkel als Groessen in Grad.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Berechnung, Eingabebezug, Eingaben, Formel, Nachweis, NachweisUrteil,
    Vorgabe, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, GRAD, KN, KN_PRO_M3, KPA, M, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text, angabe, bedingung
from opencivil.core.protokoll import (
    Abschnitt, GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte,
)
from opencivil.core.wert import Wert, WertDef, kennung_aus

#: Der Beiwert der undrainierten Tragfähigkeitsformel, Kap. 9.2.17 -- 5.1,
#: wie das Kapitel ihn schreibt (pi + 2 = 5.14 gerundet).
N_C_UNDRAINIERT = 5.1

#: Die Abschnitte des gelieferten Kapitels, an den Formeln als Referenz.
KAP_FAKTOREN = "Kap. 9.2.6"
KAP_GRUNDWASSER = "Kap. 9.2.8"
KAP_FORMEL = "Kap. 9.2.10"
KAP_FORM = "Kap. 9.2.12"
KAP_TIEFE = "Kap. 9.2.13"
KAP_LAST = "Kap. 9.2.14"
KAP_GELAENDE = "Kap. 9.2.15"
KAP_SOHLE = "Kap. 9.2.16"
KAP_UNDRAINIERT = "Kap. 9.2.17"
KAP_GLEITEN = "Kap. 9.2.18"

#: Die Spalten der Tragfähigkeitsformel, wie die Zusammenfassung sie zeigt.
SPALTEN = (("c", "Kohäsion"), ("q", "Seitliche Auflast"), ("g", "Gewicht Gleitkörper"))


def grad(winkel: Groesse) -> float:
    """Ein Winkel in Grad -- so gehen alpha, beta und arctan(t/b) in die Faktoren ein."""
    return math.degrees(winkel.si)


# ===========================================================================
# Das Fundament
# ===========================================================================


@dataclass
class Fundament:
    """
    Ein Flachfundament auf seinem Baugrund: die Eingaben als Vorgaben im
    Rechenwerk, dazu phi_eff, c_eff und gamma'.

    ``b`` ist die Breite, die kürzere Seite, ``L`` die Länge; ein
    Streifenfundament ist ein sehr langes.
    """

    name: str
    phi_k: Groesse
    gamma_phi: Groesse
    c_k: Groesse
    gamma_c: Groesse
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

    def id_von(self, kurzname: str) -> str:
        return self.definitionen[kurzname].id

    def ins_rechenwerk(self, werk) -> "Fundament":
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int = 2, referenz: str = "") -> WertDef:
        d = WertDef(id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
                    beschreibung=beschreibung, referenz=referenz, stellen=stellen)
        self.definitionen[kurzname] = d
        return d

    def _aufbauen(self) -> None:
        abschnitt = self.abschnitt
        # Je Gruppe ein Kasten in der Herleitung -- wie die Abmessungen der Platte.
        vorgaben = (
            ("Boden", (
                ("phi_k", r"\varphi_k", GRAD, "Reibungswinkel, charakteristisch", 1, ""),
                ("gamma_phi", r"\gamma_{\varphi}", EINHEITSLOS,
                 "Partialfaktor des Reibungswinkels", 2, "SIA 267:2013, 5.3.2.2"),
                ("c_k", "c_k", KPA, "Kohäsion, charakteristisch", 1, ""),
                ("gamma_c", r"\gamma_c", EINHEITSLOS, "Partialfaktor der Kohäsion", 2, ""),
                ("gamma", r"\gamma", KN_PRO_M3, "Raumlast des Bodens", 1, ""),
                ("gamma_w", r"\gamma_w", KN_PRO_M3, "Raumlast des Wassers", 1, ""),
            )),
            ("Fundament", (
                ("b", "b", M, "Breite des Fundaments", 2, ""),
                ("L", "L", M, "Länge des Fundaments", 2, ""),
                ("t", "t", M, "Tiefe der Sohle unter Terrain", 2, ""),
                ("alpha", r"\alpha", GRAD, "Neigung der Sohle", 1, ""),
            )),
            ("Gelände und Grundwasser", (
                ("t1", "t_1", M, "Tiefe des höchsten Grundwasserspiegels unter Terrain", 2, ""),
                ("beta", r"\beta", GRAD, "Neigung des Geländes", 1, ""),
                ("q_Ed", "q_{Ed}", KPA, "Bemessungslast neben dem Fundament", 1, ""),
            )),
            ("Sohlreibung", (
                ("delta_faktor", r"k_{\delta}", EINHEITSLOS,
                 "Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ*/φ", 2, ""),
            )),
        )
        for gruppe, eintraege in vorgaben:
            for kurz, symbol, einheit, beschreibung, stellen, referenz in eintraege:
                d = self._def(kurz, symbol, einheit, beschreibung, stellen, referenz)
                self.berechnungen.append(Vorgabe(
                    id=d.id, ausgabe=d, groesse=getattr(self, kurz),
                    abschnitt=abschnitt, gruppe=gruppe))

        d_phi = self._def("phi_eff", r"\varphi_{eff}", GRAD,
                          "Reibungswinkel, Bemessungswert", 2, "SIA 267:2013, 5.3.2.1")
        d_c = self._def("c_eff", "c_{eff}", KPA, "Kohäsion, Bemessungswert", 1)
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
# Befund
# ===========================================================================


@dataclass
class Faktoren:
    """Eine Spalte der Tragfähigkeitsformel: N, s, d, g und b' -- i hängt am Fall."""

    N: float
    s: float
    d: float
    g: float
    b: float


@dataclass
class Fallergebnis:
    """Was der Grundbruch bei einer Kombination ergibt."""

    kombination: Kombination
    delta_R: float
    """Die Neigung der Last gegen die Sohlnormale, in rad."""

    i: Dict[str, Optional[float]] = field(default_factory=dict)
    """Die Lastneigungsfaktoren je Spalte -- ``None``, wo es keinen gibt."""

    sigma_f: float = 0.0
    N_Rd: float = 0.0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""


@dataclass
class Grundbruchbefund:
    """Was ausser den Erfüllungsgraden bleibt -- für die Zusammenfassung und das Bild."""

    undrainiert: bool
    spalten: Dict[str, Faktoren]
    """Je Spalte der Formel (``c``, ``q``, ``g``) ihre Faktoren; undrainiert nur ``c``."""

    L_gl: Optional[float] = None
    """Wie weit der Gleitkörper neben das Fundament reicht, in m -- drainiert."""

    H_gl: Optional[float] = None
    """Wie tief er unter die Sohle reicht, in m -- drainiert."""

    grundwasser: str = ""
    ergebnisse: List[Fallergebnis] = field(default_factory=list)


# ===========================================================================
# Grundbruch
# ===========================================================================


class Grundbruch(Nachweis):
    """
    Der Grundbruchwiderstand N_Rd je Kombination, gegen N_Ed gehalten. Die
    Faktoren, die nicht an der Last hängen, werden einmal gerechnet; die
    Lastneigung je Kombination.
    """

    THEMA = "Grundbruch"
    ART = "GB"

    def __init__(self, fundament: Fundament, kombinationen: Sequence[Kombination]) -> None:
        if not kombinationen:
            raise ValueError("Der Grundbruchnachweis braucht mindestens eine Kombination.")
        self.fundament = fundament
        self.kombinationen = list(kombinationen)
        basis = f"{fundament.id}.nachweis.grundbruch"
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,GB,{als_text(k.name)}}}",
                             f"Erfüllungsgrad Grundbruch – {k.name}")
            for k in self.kombinationen}
        bezuege = [Eingabebezug(n, fundament.id_von(n)) for n in (
            "phi_eff", "c_eff", "gamma", "gamma_auftrieb", "q_Ed", "b", "L", "t1", "t",
            "alpha", "beta")]
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()), bezuege=bezuege,
                         titel=f"Grundbruch – {fundament.name}",
                         abschnitt=fundament.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Grundbruch")
        if e.g("phi_eff").si <= 0.0:
            befund = self._undrainiert(e, p)
        else:
            befund = self._drainiert(e, p)
        ergebnis = {self.d_ausnutzung[r.kombination.name].id:
                    Groesse(r.erfuellungsgrad, EINHEITSLOS) for r in befund.ergebnisse}
        return Ausfuehrung(ergebnis, [self._urteil(r, e) for r in befund.ergebnisse], befund)

    # -- Drainiert ----------------------------------------------------------

    def _drainiert(self, e: Eingaben, p: Protokoll) -> Grundbruchbefund:
        p.erklaerung(
            "Unter der Sohle bildet sich beim Grundbruch ein Gleitkörper, der den "
            "Boden seitlich hinaus und nach oben drückt. Die erweiterte "
            "Tragfähigkeitsformel setzt seinen Widerstand aus drei Teilen zusammen: "
            "der Kohäsion, der seitlichen Auflast neben dem Fundament und dem "
            "Gewicht des Gleitkörpers -- je mit einem Tragfähigkeitsfaktor und den "
            "Korrekturen für Form, Tiefe, Lastneigung, Geländeneigung und "
            "Sohlneigung."
        )
        p.ansatz(
            r"\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q"
            r" + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma}"
            r" g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L",
            titel="Erweiterte Tragfähigkeitsformel", referenz=KAP_FORMEL,
            name="Erweiterte Tragfähigkeitsformel")
        werte = Zwischenwerte(self.id)
        phi, b, L, t = e["phi_eff"], e["b"], e["L"], e["t"]
        tan_phi = math.tan(phi.groesse.si)

        # -- Tragfähigkeitsfaktoren -------------------------------------------
        p.titel("Tragfähigkeitsfaktoren", ebene=3)
        n_q = math.exp(math.pi * tan_phi) * math.tan(math.pi / 4 + phi.groesse.si / 2) ** 2
        N_q = werte.zahl("N_q", "N_q", n_q, "Tragfähigkeitsfaktor der seitlichen Auflast",
                         stellen=2)
        p.formel(N_q, r"e^{\pi \tan @phi} \cdot \tan^{2}\left(45^\circ + \frac{@phi}{2}\right)",
                 {"phi": phi}, titel="Tragfähigkeitsfaktor der seitlichen Auflast",
                 referenz=KAP_FAKTOREN, name="Tragfähigkeitsfaktor N_q")
        N_c = werte.zahl("N_c", "N_c", (n_q - 1.0) / tan_phi,
                         "Tragfähigkeitsfaktor der Kohäsion", stellen=2)
        p.formel(N_c, r"\frac{@N_q - 1}{\tan @phi}", {"N_q": N_q, "phi": phi},
                 titel="Tragfähigkeitsfaktor der Kohäsion", referenz=KAP_FAKTOREN,
                 name="Tragfähigkeitsfaktor N_c")
        N_g = werte.zahl("N_gamma", r"N_{\gamma}", 1.8 * (n_q - 1.0) * tan_phi,
                         "Tragfähigkeitsfaktor des Gleitkörpergewichts", stellen=2)
        p.formel(N_g, r"1.8 \cdot \left(@N_q - 1\right) \cdot \tan @phi",
                 {"N_q": N_q, "phi": phi}, titel="Tragfähigkeitsfaktor des Gleitkörpergewichts",
                 referenz=KAP_FAKTOREN, name="Tragfähigkeitsfaktor N_γ")

        # -- Gleitkörper und Grundwasser ----------------------------------------
        p.titel("Gleitkörper und Grundwasser", ebene=3)
        halb = math.pi / 4 + phi.groesse.si / 2
        L_gl = werte.wert("L_gl", "L_{Gl}", Groesse.aus_si(
            b.groesse.si * math.tan(halb) * math.exp(math.pi / 2 * tan_phi), M), 2,
            "Reichweite des Gleitkörpers neben dem Fundament")
        p.formel(L_gl, r"@b \cdot \tan\left(45^\circ + \frac{@phi}{2}\right) \cdot "
                       r"e^{\frac{\pi}{2} \tan @phi}", {"b": b, "phi": phi},
                 titel="Reichweite des Gleitkörpers", referenz=KAP_FORMEL,
                 name="Reichweite des Gleitkörpers")
        H_gl = werte.wert("H_gl", "H_{Gl}", Groesse.aus_si(
            b.groesse.si * math.cos(phi.groesse.si) / (2.0 * math.cos(halb))
            * math.exp(halb * tan_phi), M), 2, "Tiefe des Gleitkörpers unter der Sohle")
        p.formel(H_gl, r"@b \cdot \frac{\cos @phi}{2 \cos\left(45^\circ + \frac{@phi}{2}\right)}"
                       r" \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{@phi}{2}\right)"
                       r" \tan @phi}", {"b": b, "phi": phi},
                 titel="Tiefe des Gleitkörpers", referenz=KAP_FORMEL,
                 name="Tiefe des Gleitkörpers")
        sigma0, gamma_G, grundwasser = self._grundwasser(e, p, werte, H_gl)

        # -- Korrekturfaktoren --------------------------------------------------
        p.titel("Form, Tiefe, Gelände und Sohle", ebene=3)
        bl = b.groesse.si / L.groesse.si
        s_c = werte.zahl("s_c", "s_c", 1.0 + bl * N_q.groesse.si / N_c.groesse.si,
                         "Formfaktor der Kohäsion", stellen=2)
        p.formel(s_c, r"1 + \frac{@b}{@L} \cdot \frac{@N_q}{@N_c}",
                 {"b": b, "L": L, "N_q": N_q, "N_c": N_c}, titel="Formfaktor der Kohäsion",
                 referenz=KAP_FORM, name="Formfaktor s_c")
        s_q = werte.zahl("s_q", "s_q", 1.0 + bl * tan_phi,
                         "Formfaktor der seitlichen Auflast", stellen=2)
        p.formel(s_q, r"1 + \frac{@b}{@L} \cdot \tan @phi", {"b": b, "L": L, "phi": phi},
                 titel="Formfaktor der seitlichen Auflast", referenz=KAP_FORM,
                 name="Formfaktor s_q")
        s_g = werte.zahl("s_gamma", r"s_{\gamma}", 1.0 - 0.4 * bl,
                         "Formfaktor des Gleitkörpergewichts", stellen=2)
        p.formel(s_g, r"1 - 0.4 \cdot \frac{@b}{@L}", {"b": b, "L": L},
                 titel="Formfaktor des Gleitkörpergewichts", referenz=KAP_FORM,
                 name="Formfaktor s_γ")

        theta = self._einbindewinkel(p, werte, t, b)
        d_c = werte.zahl("d_c", "d_c", 1.0 + 0.007 * grad(theta.groesse),
                         "Tiefenfaktor der Kohäsion", stellen=2)
        p.formel(d_c, r"1 + 0.007 \cdot @theta", {"theta": theta},
                 titel="Tiefenfaktor der Kohäsion", referenz=KAP_TIEFE, name="Tiefenfaktor d_c")
        d_q = werte.zahl("d_q", "d_q", 1.0 + 0.035 * tan_phi
                         * (1.0 - math.sin(phi.groesse.si)) ** 2 * grad(theta.groesse),
                         "Tiefenfaktor der seitlichen Auflast", stellen=2)
        p.formel(d_q, r"1 + 0.035 \cdot \tan @phi \cdot \left(1 - \sin @phi\right)^{2}"
                      r" \cdot @theta", {"phi": phi, "theta": theta},
                 titel="Tiefenfaktor der seitlichen Auflast", referenz=KAP_TIEFE,
                 name="Tiefenfaktor d_q")
        p.text("Der Tiefenfaktor des Gleitkörpergewichts ist d_γ = 1.")

        beta = e["beta"]
        g_c = werte.zahl("g_c", "g_c", 1.0 - grad(beta.groesse) / 147.0,
                         "Geländeneigungsfaktor der Kohäsion", stellen=2)
        p.formel(g_c, r"1 - \frac{@beta}{147^\circ}", {"beta": beta},
                 titel="Geländeneigungsfaktor der Kohäsion", referenz=KAP_GELAENDE,
                 name="Geländeneigungsfaktor g_c")
        g_q = werte.zahl("g_q", "g_q", _hoch5(1.0 - 0.5 * math.tan(beta.groesse.si)),
                         "Geländeneigungsfaktor der Auflast und des Gleitkörpers", stellen=2)
        p.formel(g_q, r"\left(1 - 0.5 \cdot \tan @beta\right)^{5}", {"beta": beta},
                 titel="Geländeneigungsfaktor der Auflast und des Gleitkörpers",
                 referenz=KAP_GELAENDE, name="Geländeneigungsfaktor g_q")
        p.text("Für das Gleitkörpergewicht gilt derselbe Faktor: g_γ = g_q.")

        alpha = e["alpha"]
        b_c = werte.zahl("b_c", "b_c", 1.0 - grad(alpha.groesse) / 147.0,
                         "Sohlneigungsfaktor der Kohäsion", stellen=2)
        p.formel(b_c, r"1 - \frac{@alpha}{147^\circ}", {"alpha": alpha},
                 titel="Sohlneigungsfaktor der Kohäsion", referenz=KAP_SOHLE,
                 name="Sohlneigungsfaktor b_c")
        b_q = werte.zahl("b_q", "b_q", math.exp(-0.035 * grad(alpha.groesse) * tan_phi),
                         "Sohlneigungsfaktor der seitlichen Auflast", stellen=2)
        p.formel(b_q, r"e^{-0.035 \cdot @alpha \cdot \tan @phi}", {"alpha": alpha, "phi": phi},
                 titel="Sohlneigungsfaktor der seitlichen Auflast", referenz=KAP_SOHLE,
                 name="Sohlneigungsfaktor b_q")
        b_g = werte.zahl("b_gamma", r"b_{\gamma}",
                         math.exp(-0.047 * grad(alpha.groesse) * tan_phi),
                         "Sohlneigungsfaktor des Gleitkörpergewichts", stellen=2)
        p.formel(b_g, r"e^{-0.047 \cdot @alpha \cdot \tan @phi}", {"alpha": alpha, "phi": phi},
                 titel="Sohlneigungsfaktor des Gleitkörpergewichts", referenz=KAP_SOHLE,
                 name="Sohlneigungsfaktor b_γ")
        p.annahme("b_γ mit tan φ wie in Tabelle 9.2.18 -- im Text des Kapitels steht "
                  "tan α; die Tabelle und die Formel für b_q rechnen mit tan φ.")

        spalten = {
            "c": Faktoren(N_c.groesse.si, s_c.groesse.si, d_c.groesse.si, g_c.groesse.si,
                          b_c.groesse.si),
            "q": Faktoren(n_q, s_q.groesse.si, d_q.groesse.si, g_q.groesse.si, b_q.groesse.si),
            "g": Faktoren(N_g.groesse.si, s_g.groesse.si, 1.0, g_q.groesse.si, b_g.groesse.si),
        }
        befund = Grundbruchbefund(undrainiert=False, spalten=spalten, L_gl=L_gl.groesse.si,
                                  H_gl=H_gl.groesse.si, grundwasser=grundwasser)
        z = {"N_c": N_c, "N_q": N_q, "N_g": N_g, "s_c": s_c, "s_q": s_q, "s_g": s_g,
             "d_c": d_c, "d_q": d_q, "g_c": g_c, "g_q": g_q, "b_c": b_c, "b_q": b_q,
             "b_g": b_g, "sigma0": sigma0, "gamma_G": gamma_G}
        for k in self.kombinationen:
            befund.ergebnisse.append(self._drainierter_fall(e, p, k, z))
        return befund

    def _grundwasser(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                     H_gl: Wert) -> Tuple[Wert, Wert, str]:
        """Überlagerung auf Höhe der Sohle und Raumlast im Gleitkörper, je nach Wasser."""
        t, t1, q = e["t"], e["t1"], e["q_Ed"]
        gamma, gamma_a = e["gamma"], e["gamma_auftrieb"]
        sigma0_def = ("sigma_v0", r"\sigma_{v,0}", "Überlagerung auf Höhe der Sohle")
        if t1.groesse.si <= t.groesse.si:
            lage = ("Lage 1: Grundwasser über der Sohle" if t1.groesse.si < t.groesse.si
                    else "Lage 2: Grundwasser auf Höhe der Sohle")
            sigma0 = werte.wert(sigma0_def[0], sigma0_def[1], Groesse.aus_si(
                gamma.groesse.si * t1.groesse.si
                + gamma_a.groesse.si * (t.groesse.si - t1.groesse.si) + q.groesse.si, KPA),
                1, sigma0_def[2])
            p.formel(sigma0, r"@gamma \cdot @t1 + @gamma_a \cdot \left(@t - @t1\right) + @q",
                     {"gamma": gamma, "t1": t1, "gamma_a": gamma_a, "t": t, "q": q},
                     titel=f"Überlagerung auf Höhe der Sohle, {lage}",
                     referenz=KAP_GRUNDWASSER, name="Überlagerung auf Höhe der Sohle")
            gamma_G = werte.wert("gamma_G", r"\gamma_G", gamma_a.groesse, 1,
                                 "Raumlast im Gleitkörper")
            p.formel(gamma_G, "@gamma_a", {"gamma_a": gamma_a},
                     titel="Raumlast im Gleitkörper, unter Wasser", referenz=KAP_GRUNDWASSER,
                     name="Raumlast im Gleitkörper")
            return sigma0, gamma_G, lage

        sigma0 = werte.wert(sigma0_def[0], sigma0_def[1], Groesse.aus_si(
            gamma.groesse.si * t.groesse.si + q.groesse.si, KPA), 1, sigma0_def[2])
        p.formel(sigma0, r"@gamma \cdot @t + @q", {"gamma": gamma, "t": t, "q": q},
                 titel="Überlagerung auf Höhe der Sohle, Grundwasser tiefer",
                 referenz=KAP_GRUNDWASSER, name="Überlagerung auf Höhe der Sohle")
        tief = t1.groesse.si - t.groesse.si
        T = werte.wert("T_w", "T", Groesse.aus_si(tief, M), 2,
                       "Abstand des Grundwasserspiegels unter der Sohle")
        p.formel(T, r"@t1 - @t", {"t1": t1, "t": t},
                 titel="Abstand des Grundwassers unter der Sohle", referenz=KAP_GRUNDWASSER,
                 name="Abstand des Grundwassers unter der Sohle")
        if tief >= H_gl.groesse.si:
            lage = "Lage 3: Grundwasser tiefer als der Gleitkörper"
            p.gleichung(bedingung(angabe(T), r"\ge", angabe(H_gl), True, mit_urteil=False),
                        titel=lage)
            gamma_G = werte.wert("gamma_G", r"\gamma_G", gamma.groesse, 1,
                                 "Raumlast im Gleitkörper")
            p.formel(gamma_G, "@gamma", {"gamma": gamma},
                     titel="Raumlast im Gleitkörper, über dem Wasser",
                     referenz=KAP_GRUNDWASSER, name="Raumlast im Gleitkörper")
            return sigma0, gamma_G, lage
        lage = "Grundwasser im Gleitkörper, unter der Sohle"
        p.gleichung(bedingung(angabe(T), r"\ge", angabe(H_gl), False, mit_urteil=False),
                    titel=lage)
        p.annahme("Der Grundwasserspiegel liegt im Gleitkörper (T < H). Das Kapitel "
                  "verlangt dafür eine Stabilitätsberechnung; gerechnet wird mit γ' wie in "
                  "Lage 2, auf der sicheren Seite.")
        gamma_G = werte.wert("gamma_G", r"\gamma_G", gamma_a.groesse, 1,
                             "Raumlast im Gleitkörper")
        p.formel(gamma_G, "@gamma_a", {"gamma_a": gamma_a},
                 titel="Raumlast im Gleitkörper, unter Wasser", referenz=KAP_GRUNDWASSER,
                 name="Raumlast im Gleitkörper")
        return sigma0, gamma_G, lage

    @staticmethod
    def _einbindewinkel(p: Protokoll, werte: Zwischenwerte, t: Wert, b: Wert) -> Wert:
        """arctan(t/b) in Grad -- so steht er in den Tiefenfaktoren."""
        theta = werte.wert("theta_t", r"\vartheta_t",
                           Groesse.aus_si(math.atan(t.groesse.si / b.groesse.si), GRAD), 1,
                           "Winkel der Einbindetiefe")
        p.formel(theta, r"\arctan\frac{@t}{@b}", {"t": t, "b": b},
                 titel="Winkel der Einbindetiefe, in Grad", referenz=KAP_TIEFE,
                 name="Winkel der Einbindetiefe")
        return theta

    def _drainierter_fall(self, e: Eingaben, p: Protokoll, k: Kombination,
                          z: Dict[str, Wert]) -> Fallergebnis:
        werte = Zwischenwerte(f"{self.id}.{k.kennung}")
        p.titel(f"Grundbruch – {k.name}", ebene=3)
        phi, c, b, L, alpha = e["phi_eff"], e["c_eff"], e["b"], e["L"], e["alpha"]
        tan_phi = math.tan(phi.groesse.si)
        N = werte.kraft("N_Ed", "N_{Ed}", k.N_Ed.si, "Einwirkung normal zur Sohle")
        T = werte.kraft("T_Ed", "T_{Ed}", k.T_Ed.si, "Einwirkung in der Sohle")
        erg = Fallergebnis(kombination=k, delta_R=math.atan2(k.T_Ed.si, k.N_Ed.si))

        delta = werte.wert("delta_R", r"\delta_R", Groesse.aus_si(erg.delta_R, GRAD), 1,
                           "Neigung der Last")
        p.formel(delta, r"\arctan\frac{@T}{@N}", {"T": T, "N": N}, titel="Neigung der Last",
                 referenz=KAP_LAST, name="Neigung der Last")

        nenner = N.groesse.si + b.groesse.si * L.groesse.si * c.groesse.si / tan_phi
        x = k.T_Ed.si / nenner
        roh_q = 1.0 - 0.5 * x
        i_q = werte.zahl("i_q", "i_q", _hoch5(roh_q), "Lastneigungsfaktor der seitlichen Auflast",
                         stellen=2)
        p.formel(i_q, r"\left[1 - \frac{0.5 \cdot @T}{@N + @b \cdot @L \cdot @c \cdot "
                      r"\cot @phi}\right]^{5}",
                 {"T": T, "N": N, "b": b, "L": L, "c": c, "phi": phi},
                 titel="Lastneigungsfaktor der seitlichen Auflast", referenz=KAP_LAST,
                 name="Lastneigungsfaktor i_q")
        i_c = werte.zahl("i_c", "i_c", i_q.groesse.si
                         - (1.0 - i_q.groesse.si) / (z["N_q"].groesse.si - 1.0),
                         "Lastneigungsfaktor der Kohäsion", stellen=2)
        p.formel(i_c, r"@i_q - \frac{1 - @i_q}{@N_q - 1}", {"i_q": i_q, "N_q": z["N_q"]},
                 titel="Lastneigungsfaktor der Kohäsion", referenz=KAP_LAST,
                 name="Lastneigungsfaktor i_c")
        roh_g = 1.0 - (0.7 - grad(alpha.groesse) / 450.0) * x
        i_g = werte.zahl("i_gamma", r"i_{\gamma}", _hoch5(roh_g),
                         "Lastneigungsfaktor des Gleitkörpergewichts", stellen=2)
        p.formel(i_g, r"\left[1 - \frac{\left(0.7 - \frac{@alpha}{450^\circ}\right) \cdot @T}"
                      r"{@N + @b \cdot @L \cdot @c \cdot \cot @phi}\right]^{5}",
                 {"alpha": alpha, "T": T, "N": N, "b": b, "L": L, "c": c, "phi": phi},
                 titel="Lastneigungsfaktor des Gleitkörpergewichts", referenz=KAP_LAST,
                 name="Lastneigungsfaktor i_γ")
        if roh_q < 0.0 or roh_g < 0.0:
            p.annahme("Ist die Klammer eines Lastneigungsfaktors kleiner als null, gilt null: "
                      "die Last ist so stark geneigt, dass die Auflast oder das Gewicht des "
                      "Gleitkörpers nichts mehr trägt.")
        erg.i = {"c": i_c.groesse.si, "q": i_q.groesse.si, "g": i_g.groesse.si}

        sigma_f = werte.wert("sigma_f", r"\sigma_f", Groesse.aus_si(
            c.groesse.si * _produkt(z, "N_c", "s_c", "d_c", "g_c", "b_c") * i_c.groesse.si
            + z["sigma0"].groesse.si * _produkt(z, "N_q", "s_q", "d_q", "g_q", "b_q")
            * i_q.groesse.si
            + 0.5 * z["gamma_G"].groesse.si * b.groesse.si
            * _produkt(z, "N_g", "s_g", "g_q", "b_g") * i_g.groesse.si, KPA), 1,
            "Bruchspannung in der Sohle")
        p.formel(sigma_f,
                 r"@c \cdot @N_c \cdot @s_c \cdot @d_c \cdot @i_c \cdot @g_c \cdot @b_c"
                 r" + @sigma0 \cdot @N_q \cdot @s_q \cdot @d_q \cdot @i_q \cdot @g_q \cdot @b_q"
                 r" + \tfrac{1}{2} \cdot @gamma_G \cdot @b \cdot @N_g \cdot @s_g \cdot 1"
                 r" \cdot @i_g \cdot @g_q \cdot @b_g",
                 {"c": c, "b": b, "i_c": i_c, "i_q": i_q, "i_g": i_g, **z},
                 titel="Bruchspannung in der Sohle", referenz=KAP_FORMEL,
                 name="Bruchspannung in der Sohle")
        erg.sigma_f = sigma_f.groesse.si
        return self._widerstand(p, werte, erg, sigma_f, b, L, N)

    # -- Undrainiert --------------------------------------------------------

    def _undrainiert(self, e: Eingaben, p: Protokoll) -> Grundbruchbefund:
        p.erklaerung(
            "Wird ein gesättigter Ton schnell belastet, kann das Porenwasser nicht "
            "entweichen: es gilt φ = 0, und an die Stelle der Kohäsion tritt die "
            "undrainierte Scherfestigkeit s_u. Die Korrekturen stehen dann nicht als "
            "Faktoren, sondern als Summanden in der Klammer."
        )
        p.ansatz(r"\sigma_f = 5.1 \, s_u \left(1 + s_c + d_c - i_c - b_c - g_c\right)"
                 r" + \left(\gamma t + q\right) \qquad N_{Rd} = \sigma_f \cdot b \cdot L",
                 titel="Tragfähigkeitsformel undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Tragfähigkeitsformel undrainiert")
        p.text("Mit φ = 0 ist c_eff die undrainierte Scherfestigkeit s_u.")
        werte = Zwischenwerte(self.id)
        b, L, t = e["b"], e["L"], e["t"]

        s_c = werte.zahl("s_c", "s_c", 0.2 * b.groesse.si / L.groesse.si,
                         "Formfaktor, undrainiert", stellen=2)
        p.formel(s_c, r"0.2 \cdot \frac{@b}{@L}", {"b": b, "L": L},
                 titel="Formfaktor, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Formfaktor s_c")
        if t.groesse.si < b.groesse.si:
            d_c = werte.zahl("d_c", "d_c", 0.4 * t.groesse.si / b.groesse.si,
                             "Tiefenfaktor, undrainiert", stellen=2)
            p.formel(d_c, r"0.4 \cdot \frac{@t}{@b}", {"t": t, "b": b},
                     titel="Tiefenfaktor, undrainiert, t < b", referenz=KAP_UNDRAINIERT,
                     name="Tiefenfaktor d_c")
        else:
            theta = self._einbindewinkel(p, werte, t, b)
            d_c = werte.zahl("d_c", "d_c", 0.007 * grad(theta.groesse),
                             "Tiefenfaktor, undrainiert", stellen=2)
            p.formel(d_c, r"0.007 \cdot @theta", {"theta": theta},
                     titel="Tiefenfaktor, undrainiert, t ≥ b", referenz=KAP_UNDRAINIERT,
                     name="Tiefenfaktor d_c")
        beta, alpha = e["beta"], e["alpha"]
        g_c = werte.zahl("g_c", "g_c", grad(beta.groesse) / 147.0,
                         "Geländeneigungsfaktor, undrainiert", stellen=2)
        p.formel(g_c, r"\frac{@beta}{147^\circ}", {"beta": beta},
                 titel="Geländeneigungsfaktor, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Geländeneigungsfaktor g_c")
        b_c = werte.zahl("b_c", "b_c", grad(alpha.groesse) / 147.0,
                         "Sohlneigungsfaktor, undrainiert", stellen=2)
        p.formel(b_c, r"\frac{@alpha}{147^\circ}", {"alpha": alpha},
                 titel="Sohlneigungsfaktor, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Sohlneigungsfaktor b_c")
        gamma, q = e["gamma"], e["q_Ed"]
        sigma0 = werte.wert("sigma_v0", r"\sigma_{v,0}", Groesse.aus_si(
            gamma.groesse.si * t.groesse.si + q.groesse.si, KPA), 1,
            "Überlagerung auf Höhe der Sohle")
        p.formel(sigma0, r"@gamma \cdot @t + @q", {"gamma": gamma, "t": t, "q": q},
                 titel="Überlagerung auf Höhe der Sohle, totale Spannung",
                 referenz=KAP_UNDRAINIERT, name="Überlagerung auf Höhe der Sohle")

        spalten = {"c": Faktoren(N_C_UNDRAINIERT, s_c.groesse.si, d_c.groesse.si,
                                 g_c.groesse.si, b_c.groesse.si)}
        befund = Grundbruchbefund(
            undrainiert=True, spalten=spalten,
            grundwasser="Grundwasser ohne Einfluss: undrainiert, totale Spannungen")
        for k in self.kombinationen:
            befund.ergebnisse.append(self._undrainierter_fall(
                e, p, k, s_c=s_c, d_c=d_c, g_c=g_c, b_c=b_c, sigma0=sigma0))
        return befund

    def _undrainierter_fall(self, e: Eingaben, p: Protokoll, k: Kombination,
                            **z: Wert) -> Fallergebnis:
        werte = Zwischenwerte(f"{self.id}.{k.kennung}")
        p.titel(f"Grundbruch – {k.name}", ebene=3)
        s_u, b, L = e["c_eff"], e["b"], e["L"]
        N = werte.kraft("N_Ed", "N_{Ed}", k.N_Ed.si, "Einwirkung normal zur Sohle")
        T = werte.kraft("T_Ed", "T_{Ed}", k.T_Ed.si, "Einwirkung in der Sohle")
        erg = Fallergebnis(kombination=k, delta_R=math.atan2(k.T_Ed.si, k.N_Ed.si))
        x = k.T_Ed.si / (s_u.groesse.si * b.groesse.si * L.groesse.si)
        if x > 1.0:
            # Ohne Lösung: die Wurzel des Lastneigungsfaktors wird negativ.
            erg.i = {"c": None}
            erg.begruendung = erg.hinweis = (
                "T_Ed > s_u · b · L: die Last ist zu stark geneigt, der "
                "Lastneigungsfaktor ist nicht bestimmt -- kein Grundbruchwiderstand.")
            p.text(erg.begruendung)
            return erg
        i_c = werte.zahl("i_c", "i_c", 0.5 - 0.5 * math.sqrt(1.0 - x),
                         "Lastneigungsfaktor, undrainiert", stellen=2)
        p.formel(i_c, r"0.5 - \frac{1}{2} \sqrt{1 - \frac{@T}{@s_u \cdot @b \cdot @L}}",
                 {"T": T, "s_u": s_u, "b": b, "L": L},
                 titel="Lastneigungsfaktor, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Lastneigungsfaktor i_c")
        erg.i = {"c": i_c.groesse.si}
        summe = (1.0 + z["s_c"].groesse.si + z["d_c"].groesse.si - i_c.groesse.si
                 - z["b_c"].groesse.si - z["g_c"].groesse.si)
        sigma_f = werte.wert("sigma_f", r"\sigma_f", Groesse.aus_si(
            N_C_UNDRAINIERT * s_u.groesse.si * summe + z["sigma0"].groesse.si, KPA), 1,
            "Bruchspannung in der Sohle")
        p.formel(sigma_f, r"5.1 \cdot @s_u \cdot \left(1 + @s_c + @d_c - @i_c - @b_c - @g_c\right)"
                          r" + @sigma0", {"s_u": s_u, "i_c": i_c, **z},
                 titel="Bruchspannung in der Sohle, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Bruchspannung in der Sohle")
        erg.sigma_f = sigma_f.groesse.si
        return self._widerstand(p, werte, erg, sigma_f, b, L, N)

    # -- Gemeinsam ----------------------------------------------------------

    def _widerstand(self, p: Protokoll, werte: Zwischenwerte, erg: Fallergebnis,
                    sigma_f: Wert, b: Wert, L: Wert, N: Wert) -> Fallergebnis:
        N_Rd = werte.kraft("N_Rd", "N_{Rd}", max(0.0, sigma_f.groesse.si) * b.groesse.si
                           * L.groesse.si, "Widerstand")
        p.formel(N_Rd, r"@sigma_f \cdot @b \cdot @L", {"sigma_f": sigma_f, "b": b, "L": L},
                 titel="Grundbruchwiderstand", referenz=KAP_FORMEL,
                 name="Grundbruchwiderstand")
        erg.N_Rd = N_Rd.groesse.si
        erg.erfuellt = N.groesse.si <= erg.N_Rd
        erg.erfuellungsgrad = (float("inf") if N.groesse.si == 0.0
                               else erg.N_Rd / N.groesse.si)
        erg.begruendung = (f"N_Rd = {N_Rd.formatiert()} kN "
                           f"{'≥' if erg.erfuellt else '<'} N_Ed = {N.formatiert()} kN.")
        p.gleichung(bedingung(angabe(N), r"\le", angabe(N_Rd), erg.erfuellt, mit_urteil=False),
                    titel="Einwirkung gegen Widerstand")
        grad_formel(p, self.d_ausnutzung[erg.kombination.name], erg.erfuellungsgrad, N_Rd, N,
                    erg.erfuellt, mit_urteil=True)
        return erg

    def _urteil(self, erg: Fallergebnis, e: Eingaben) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{erg.kombination.kennung}")
        einwirkung = werte.kraft("N_Ed", "N_{Ed}", erg.kombination.N_Ed.si, "Einwirkung")
        widerstand = werte.kraft("N_Rd", "N_{Rd}", erg.N_Rd, "Widerstand")
        return NachweisUrteil(
            art=self.ART, ziel=self.d_ausnutzung[erg.kombination.name].id,
            fall=erg.kombination.name, erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung, hinweis=erg.hinweis,
            einwirkung=einwirkung, widerstand=widerstand)


def gleitkoerper(b: float, phi: float, schritte: int = 24) -> List[Tuple[float, float]]:
    """
    Der Umriss des Gleitkörpers nach Prandtl, für Sohle und Gelände waagrecht
    -- so, wie die Formeln für L_Gl und H_Gl ihn messen. In m, gemessen von
    der Sohlkante auf der Seite, zu der T zeigt: x von dort weg vom
    Fundament, z nach unten; das Fundament liegt bei -b < x < 0.

    Der Zug läuft von der anderen Sohlkante über die Spitze des Keils unter
    dem Fundament (Neigung 45° + φ/2), die logarithmische Spirale um die
    Kante (r = r_0 · e^{ψ tan φ}, um 90° gedreht) und den Keil daneben
    (45° - φ/2) bis ins Gelände bei x = L_Gl. Seine tiefste Stelle liegt
    bei H_Gl. ``phi`` in rad, grösser als null.
    """
    oben = math.pi / 4 + phi / 2
    r_0 = b / 2 / math.cos(oben)
    tan_phi = math.tan(phi)
    # Die Richtung eines Strahls von der Kante aus: von +x nach unten gemessen.
    anfang = math.pi - oben
    zug: List[Tuple[float, float]] = [(-b, 0.0)]
    for i in range(schritte + 1):
        psi = math.pi / 2 * i / schritte
        r = r_0 * math.exp(psi * tan_phi)
        zug.append((r * math.cos(anfang - psi), r * math.sin(anfang - psi)))
    r_1 = r_0 * math.exp(math.pi / 2 * tan_phi)
    zug.append((2.0 * r_1 * math.cos(math.pi / 4 - phi / 2), 0.0))
    return zug


def _hoch5(klammer: float) -> float:
    """Eine Klammer hoch fünf -- unter null gilt null (siehe Herleitung)."""
    return max(0.0, klammer) ** 5


def _produkt(z: Dict[str, Wert], *namen: str) -> float:
    ergebnis = 1.0
    for n in namen:
        ergebnis *= z[n].groesse.si
    return ergebnis


# ===========================================================================
# Gleiten
# ===========================================================================


class Gleiten(Nachweis):
    """
    Der Gleitwiderstand in der Sohle je Kombination: T_Rd = N_Ed · tan delta*,
    ohne Erdwiderstand -- wie im Kapitel für eine geneigte Sohle.
    """

    THEMA = "Gleiten"
    ART = "GL"

    def __init__(self, fundament: Fundament, kombinationen: Sequence[Kombination]) -> None:
        if not kombinationen:
            raise ValueError("Der Gleitnachweis braucht mindestens eine Kombination.")
        self.fundament = fundament
        self.kombinationen = list(kombinationen)
        basis = f"{fundament.id}.nachweis.gleiten"
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,GL,{als_text(k.name)}}}",
                             f"Erfüllungsgrad Gleiten – {k.name}")
            for k in self.kombinationen}
        bezuege = [Eingabebezug(n, fundament.id_von(n)) for n in ("phi_eff", "delta_faktor")]
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()), bezuege=bezuege,
                         titel=f"Gleiten – {fundament.name}", abschnitt=fundament.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Gleiten")
        p.erklaerung(
            "Die Kraft T in der Sohle muss durch Reibung zwischen Fundament und "
            "Boden aufgenommen werden. Der Reibungswinkel δ* der Sohlfuge liegt "
            "meist zwischen 2/3 φ und φ; ein Erdwiderstand vor dem Fundament wird "
            "nicht angesetzt."
        )
        werte = Zwischenwerte(self.id)
        phi, k_delta = e["phi_eff"], e["delta_faktor"]
        delta = werte.wert("delta_stern", r"\delta^{*}", Groesse.aus_si(
            k_delta.groesse.si * phi.groesse.si, GRAD), 2, "Reibungswinkel der Sohlfuge")
        p.formel(delta, r"@k \cdot @phi", {"k": k_delta, "phi": phi},
                 titel="Reibungswinkel der Sohlfuge", referenz=KAP_GLEITEN,
                 name="Reibungswinkel der Sohlfuge")
        if phi.groesse.si <= 0.0:
            p.text("Mit φ = 0 gibt die Reibung in der Sohle keinen Widerstand; eine "
                   "Haftung zählt nach dem Kapitel nicht.")
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for k in self.kombinationen:
            zw = Zwischenwerte(f"{self.id}.{k.kennung}")
            p.titel(f"Gleiten – {k.name}", ebene=3)
            N = zw.kraft("N_Ed", "N_{Ed}", k.N_Ed.si, "Einwirkung normal zur Sohle")
            T = zw.kraft("T_Ed", "T_{Ed}", k.T_Ed.si, "Einwirkung")
            T_Rd = zw.kraft("T_Rd", "T_{Rd}", k.N_Ed.si * math.tan(delta.groesse.si),
                            "Widerstand")
            p.formel(T_Rd, r"@N \cdot \tan @delta", {"N": N, "delta": delta},
                     titel="Gleitwiderstand", referenz=KAP_GLEITEN, name="Gleitwiderstand")
            erfuellt = T.groesse.si <= T_Rd.groesse.si
            grad_wert = float("inf") if T.groesse.si == 0.0 else T_Rd.groesse.si / T.groesse.si
            p.gleichung(bedingung(angabe(T), r"\le", angabe(T_Rd), erfuellt, mit_urteil=False),
                        titel="Einwirkung gegen Widerstand")
            grad_formel(p, self.d_ausnutzung[k.name], grad_wert, T_Rd, T, erfuellt,
                        mit_urteil=True)
            ergebnis[self.d_ausnutzung[k.name].id] = Groesse(grad_wert, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art=self.ART, ziel=self.d_ausnutzung[k.name].id, fall=k.name,
                erfuellt=erfuellt, erfuellungsgrad=Groesse(grad_wert, EINHEITSLOS),
                begruendung=(f"T_Rd = {T_Rd.formatiert()} kN {'≥' if erfuellt else '<'} "
                             f"T_Ed = {T.formatiert()} kN."),
                einwirkung=T, widerstand=T_Rd))
        return Ausfuehrung(ergebnis, urteile)


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
                                if fundament.id_von(n) in werte)

    boden = zeile(("phi_eff", "c_eff", "gamma", "gamma_auftrieb"))
    masse = zeile(("b", "L", "t", "t1"))
    return GleichungBlock(latex=rf"\begin{{aligned}} & {boden} \\ & {masse} \end{{aligned}}",
                          titel="Angaben zum Fundament")


def faktortabelle(befund: Grundbruchbefund) -> TabellenBlock:
    """
    Die Faktoren der Tragfähigkeitsformel in drei Spalten -- Kohäsion,
    seitliche Auflast, Gewicht des Gleitkörpers --, wie der Benutzer sie
    tabelliert. Die Lastneigung je Kombination eine Zeile; undrainiert nur
    die Spalte der Kohäsion.
    """
    zeichen = {"c": "c", "q": "q", "g": r"\gamma"}

    def zelle(wert: Optional[float]) -> Zelle:
        return "–" if wert is None else Mathe(f"{wert:.2f}")

    def zeile(buchstabe: str, holen, fall: str = "") -> List[Zelle]:
        heraus: List[Zelle] = []
        for spalte, _ in SPALTEN:
            index = zeichen[spalte] + (rf",\ {als_text(fall)}" if fall else "")
            if spalte in befund.spalten:
                heraus += [Mathe(f"{buchstabe}_{{{index}}}"), zelle(holen(spalte))]
            else:
                heraus += ["–", "–"]
        return heraus

    mehrere = len(befund.ergebnisse) > 1
    zeilen = [
        zeile("N", lambda s: befund.spalten[s].N),
        zeile("s", lambda s: befund.spalten[s].s),
        zeile("d", lambda s: befund.spalten[s].d),
        *[zeile("i", lambda s, r=r: r.i.get(s), r.kombination.name if mehrere else "")
          for r in befund.ergebnisse],
        zeile("g", lambda s: befund.spalten[s].g),
        zeile("b'", lambda s: befund.spalten[s].b),
    ]
    kopf: List[Zelle] = []
    for _, titel in SPALTEN:
        kopf += [titel, ""]
    return TabellenBlock(kopf=kopf, zeilen=zeilen, titel="Tragfähigkeitsfaktoren",
                         ausrichtung="lrlrlr")
