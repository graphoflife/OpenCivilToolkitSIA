"""
opencivil/geotechnik/grundbruch.py -- der Grundbruch eines Flachfundaments.

VERANTWORTUNG:
Der Nachweis :class:`Grundbruch`: je Einwirkungskombination der
Grundbruchwiderstand nach der erweiterten Tragfähigkeitsformel (Kap.
9.2.10)::

    sigma_f = c N_c s_c d_c i_c g_c b_c
            + (gamma t + q) N_q s_q d_q i_q g_q b_q
            + 1/2 gamma b N_gamma s_gamma d_gamma i_gamma g_gamma b_gamma
    N_Rd    = sigma_f · b · L

und undrainiert, mit s_u (Kap. 9.2.17)::

    sigma_f = 5.1 s_u (1 + s_c + d_c - i_c - b_c - g_c) + (gamma t + q)

Dazu der Umriss des Gleitkörpers für das Bild (:func:`gleitkoerper`) und
die Tabelle der Faktoren für die Zusammenfassung (:func:`faktortabelle`).
Das Fundament und seine Bemessungswerte stehen in
:mod:`~opencivil.geotechnik.fundament`, N_q und N_c in
:mod:`~opencivil.geotechnik.tragfaehigkeit`.

QUELLE:
Die Formeln stammen aus Lang, Huder, Amann, Puzrin: Bodenmechanik und
Grundbau, 8. Aufl. 2007, Kap. 9.2 «Tragfähigkeit»; der Abschnitt steht an
jeder Formel, «Kap.» meint dieses Buch. Wo der Text und seine Tabellen
auseinandergehen, steht es beim Faktor: b_gamma rechnet nach Tabelle
9.2.18 mit tan phi, im Text steht tan alpha.

WINKEL (Bild 9.2.15):
delta_R ist die Neigung der Last gegen die Sohlnormale; was alpha und beta
sind, sagt :mod:`~opencivil.geotechnik.fundament`. Alle drei Winkel gehen in
Grad in die Faktoren ein, wie das Kapitel sie schreibt («0.007 arctan t/b»).

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
from typing import Dict, List, Optional, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingaben
from opencivil.core.einheiten import GRAD, KPA, M, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text, angabe, bedingung
from opencivil.core.nachweis import NICHT_FUEHRBAR, Ausgang, Fallausgang
from opencivil.core.protokoll import Protokoll, TabellenBlock, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.geotechnik.fundament import OHNE_GAMMA_R, Fundamentnachweis, Kombination
from opencivil.geotechnik.tragfaehigkeit import KAP_FAKTOREN, tragfaehigkeitsfaktoren
from opencivil.geotechnik.verhalten import Verhalten

#: Der Beiwert der undrainierten Tragfähigkeitsformel, Kap. 9.2.17 -- 5.1,
#: wie das Kapitel ihn schreibt (pi + 2 = 5.14 gerundet).
N_C_UNDRAINIERT = 5.1

#: Die Abschnitte des Buches, an den Formeln als Referenz.
KAP_GRUNDWASSER = "Kap. 9.2.8"
KAP_FORMEL = "Kap. 9.2.10"
KAP_FORM = "Kap. 9.2.12"
KAP_TIEFE = "Kap. 9.2.13"
KAP_LAST = "Kap. 9.2.14"
KAP_GELAENDE = "Kap. 9.2.15"
KAP_SOHLE = "Kap. 9.2.16"
KAP_UNDRAINIERT = "Kap. 9.2.17"

#: Die Spalten der Tragfähigkeitsformel, wie die Zusammenfassung sie zeigt.
SPALTEN = (("c", "Kohäsion"), ("q", "Seitliche Auflast"), ("g", "Gewicht Gleitkörper"))


def grad(winkel: Groesse) -> float:
    """Ein Winkel in Grad -- so gehen alpha, beta und arctan(t/b) in die Faktoren ein."""
    return math.degrees(winkel.si)


# ===========================================================================
# Befund
# ===========================================================================


@dataclass
class Spalte:
    """
    Eine Spalte der Tragfähigkeitsformel -- Kohäsion, seitliche Auflast oder
    Gewicht des Gleitkörpers: der Tragfähigkeitsfaktor N und die Faktoren s,
    d, g und b', die nicht an der Last hängen; die Lastneigung i bringt der
    Fall. Aus ihr kommen die Zahl (:meth:`produkt`) und die Formel der
    Herleitung (:meth:`vorlage`): ein Faktor, mit dem gerechnet wird, steht
    darum auch da, und keiner steht da, mit dem nicht gerechnet wird. Bis
    2026-11-19 stand die Formel in vier Formen -- d_γ = 1 als «1», als 1.0
    und in der Rechnung gar nicht.
    """

    kurz: str
    """«c», «q» oder «g» -- davor heissen die Platzhalter der Formel: ``c_N``."""

    N: Wert
    s: Wert
    d: Wert
    g: Wert
    b: Wert

    def _reihe(self, i: Wert) -> Dict[str, Wert]:
        """Die Faktoren in der Folge der Formel, N s d i g b, unter ihren Platzhaltern."""
        return {f"{self.kurz}_{n}": w for n, w in zip(
            ("N", "s", "d", "i", "g", "b"), (self.N, self.s, self.d, i, self.g, self.b))}

    def produkt(self, i: Wert) -> float:
        """N · s · d · i · g · b' -- was die Spalte in einem Fall beiträgt, ohne Vorfaktor."""
        return math.prod(w.groesse.si for w in self._reihe(i).values())

    def vorlage(self, i: Wert) -> Tuple[str, Dict[str, Wert]]:
        """Dasselbe Produkt als Vorlage der Herleitung, mit ihren Platzhaltern."""
        reihe = self._reihe(i)
        return r" \cdot ".join(f"@{n}" for n in reihe), reihe


@dataclass
class Fallergebnis(Fallausgang):
    """Was der Grundbruch bei einer Kombination ergibt."""

    kombination: Kombination
    delta_R: float
    """Die Neigung der Last gegen die Sohlnormale, in rad."""

    i: Dict[str, Optional[float]] = field(default_factory=dict)
    """Die Lastneigungsfaktoren je Spalte -- ``None``, wo es keinen gibt."""

    sigma_f: float = 0.0
    N_Rd: float = 0.0
    ausgang: Ausgang = NICHT_FUEHRBAR
    begruendung: str = ""


@dataclass
class Grundbruchbefund:
    """Was ausser den Erfüllungsgraden bleibt -- für die Zusammenfassung und das Bild."""

    undrainiert: bool
    spalten: Dict[str, Spalte]
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


class Grundbruch(Fundamentnachweis):
    """
    Der Grundbruchwiderstand N_Rd je Kombination, gegen N_Ed gehalten. Die
    Faktoren, die nicht an der Last hängen, werden einmal gerechnet; die
    Lastneigung je Kombination.
    """

    THEMA = "Grundbruch"
    ART = "GB"
    FELD = "grundbruch"
    BODEN = {Verhalten.DRAINIERT: ("phi_eff", "c_eff", "gamma", "gamma_auftrieb"),
             Verhalten.UNDRAINIERT: ("s_u_d", "gamma")}
    MASSE = ("q_Ed", "b", "L", "t1", "t", "alpha", "beta")

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Grundbruch")
        p.annahme(OHNE_GAMMA_R)
        if self.fundament.verhalten is Verhalten.UNDRAINIERT:
            befund = self._undrainiert(e, p)
        else:
            befund = self._drainiert(e, p)
        return Ausfuehrung({}, [self.urteil(self.d_ausnutzung[r.kombination.name],
                                            r.kombination.name, r.ausgang, r.begruendung)
                                for r in befund.ergebnisse], befund)

    # -- Drainiert ----------------------------------------------------------

    def _drainiert(self, e: Eingaben, p: Protokoll) -> Grundbruchbefund:
        p.erklaerung(
            "Unter der Sohle bildet sich beim Grundbruch ein Gleitkörper, der den "
            "Boden seitlich hinaus und nach oben drückt. Die erweiterte "
            "Tragfähigkeitsformel setzt seinen Widerstand aus drei Teilen zusammen: "
            "der Kohäsion, der seitlichen Auflast neben dem Fundament und dem "
            "Gewicht des Gleitkörpers – je mit einem Tragfähigkeitsfaktor und den "
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
        N_q, N_c = tragfaehigkeitsfaktoren(p, werte, phi)
        n_q = N_q.groesse.si
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
        p.annahme("Der Boden ist bis H_Gl unter der Sohle einheitlich, wie das Buch es "
                  "voraussetzt (Kap. 9.2.10). Bei Schichten erlaubt SIA 267:2013, 8.4.4.1, "
                  "vorsichtig gemittelte Werte über die Schichten, die der Bruch erfasst.")
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
        d_g = werte.zahl("d_gamma", r"d_{\gamma}", 1.0, "Tiefenfaktor des Gleitkörpergewichts",
                         stellen=2)
        p.wert(d_g, titel="Tiefenfaktor des Gleitkörpergewichts", referenz=KAP_TIEFE)

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
        p.annahme("b_γ mit tan φ wie in Tabelle 9.2.18 – im Text des Kapitels steht "
                  "tan α; die Tabelle und die Formel für b_q rechnen mit tan φ.")

        # Für das Gleitkörpergewicht gilt g_q (siehe oben), darum zweimal derselbe Wert.
        spalten = {"c": Spalte("c", N_c, s_c, d_c, g_c, b_c),
                   "q": Spalte("q", N_q, s_q, d_q, g_q, b_q),
                   "g": Spalte("g", N_g, s_g, d_g, g_q, b_g)}
        befund = Grundbruchbefund(undrainiert=False, spalten=spalten, L_gl=L_gl.groesse.si,
                                  H_gl=H_gl.groesse.si, grundwasser=grundwasser)
        for k in self.kombinationen:
            befund.ergebnisse.append(
                self._drainierter_fall(e, p, k, spalten, sigma0=sigma0, gamma_G=gamma_G))
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
                          spalten: Dict[str, Spalte], *, sigma0: Wert,
                          gamma_G: Wert) -> Fallergebnis:
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
        N_q = spalten["q"].N
        i_c = werte.zahl("i_c", "i_c", i_q.groesse.si
                         - (1.0 - i_q.groesse.si) / (N_q.groesse.si - 1.0),
                         "Lastneigungsfaktor der Kohäsion", stellen=2)
        p.formel(i_c, r"@i_q - \frac{1 - @i_q}{@N_q - 1}", {"i_q": i_q, "N_q": N_q},
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

        # Zahl und Formel aus denselben Spalten (siehe Spalte).
        kohaesion, auflast, gewicht = spalten["c"], spalten["q"], spalten["g"]
        sigma_f = werte.wert("sigma_f", r"\sigma_f", Groesse.aus_si(
            c.groesse.si * kohaesion.produkt(i_c)
            + sigma0.groesse.si * auflast.produkt(i_q)
            + 0.5 * gamma_G.groesse.si * b.groesse.si * gewicht.produkt(i_g), KPA), 1,
            "Bruchspannung in der Sohle")
        (vorlage_c, ein_c), (vorlage_q, ein_q), (vorlage_g, ein_g) = (
            kohaesion.vorlage(i_c), auflast.vorlage(i_q), gewicht.vorlage(i_g))
        p.formel(sigma_f,
                 rf"@c \cdot {vorlage_c} + @sigma0 \cdot {vorlage_q}"
                 rf" + \tfrac{{1}}{{2}} \cdot @gamma_G \cdot @b \cdot {vorlage_g}",
                 {"c": c, "sigma0": sigma0, "gamma_G": gamma_G, "b": b,
                  **ein_c, **ein_q, **ein_g},
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

        # N_c ist die feste Zahl der Formel, 5.1 -- im Ansatz und unten in sigma_f.
        N_c = werte.zahl("N_c", "N_c", N_C_UNDRAINIERT, "Tragfähigkeitsfaktor, undrainiert",
                         stellen=2)
        spalte = Spalte("c", N_c, s_c, d_c, g_c, b_c)
        befund = Grundbruchbefund(
            undrainiert=True, spalten={"c": spalte},
            grundwasser="Grundwasser ohne Einfluss: undrainiert, totale Spannungen")
        for k in self.kombinationen:
            befund.ergebnisse.append(self._undrainierter_fall(e, p, k, spalte, sigma0))
        return befund

    def _undrainierter_fall(self, e: Eingaben, p: Protokoll, k: Kombination,
                            spalte: Spalte, sigma0: Wert) -> Fallergebnis:
        werte = Zwischenwerte(f"{self.id}.{k.kennung}")
        p.titel(f"Grundbruch – {k.name}", ebene=3)
        s_u, b, L = e["s_u_d"], e["b"], e["L"]
        N = werte.kraft("N_Ed", "N_{Ed}", k.N_Ed.si, "Einwirkung normal zur Sohle")
        T = werte.kraft("T_Ed", "T_{Ed}", k.T_Ed.si, "Einwirkung in der Sohle")
        erg = Fallergebnis(kombination=k, delta_R=math.atan2(k.T_Ed.si, k.N_Ed.si))
        x = k.T_Ed.si / (s_u.groesse.si * b.groesse.si * L.groesse.si)
        if x > 1.0:
            # Ohne Lösung: die Wurzel des Lastneigungsfaktors wird negativ.
            erg.i = {"c": None}
            erg.begruendung = (
                "T_Ed > s_u · b · L: die Last ist zu stark geneigt, der "
                "Lastneigungsfaktor ist nicht bestimmt – kein Grundbruchwiderstand.")
            p.text(erg.begruendung)
            return erg
        i_c = werte.zahl("i_c", "i_c", 0.5 - 0.5 * math.sqrt(1.0 - x),
                         "Lastneigungsfaktor, undrainiert", stellen=2)
        p.formel(i_c, r"0.5 - \frac{1}{2} \sqrt{1 - \frac{@T}{@s_u \cdot @b \cdot @L}}",
                 {"T": T, "s_u": s_u, "b": b, "L": L},
                 titel="Lastneigungsfaktor, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Lastneigungsfaktor i_c")
        erg.i = {"c": i_c.groesse.si}
        # Undrainiert sind die Korrekturen Summanden, nicht Faktoren (Kap. 9.2.17).
        summe = (1.0 + spalte.s.groesse.si + spalte.d.groesse.si - i_c.groesse.si
                 - spalte.b.groesse.si - spalte.g.groesse.si)
        sigma_f = werte.wert("sigma_f", r"\sigma_f", Groesse.aus_si(
            spalte.N.groesse.si * s_u.groesse.si * summe + sigma0.groesse.si, KPA), 1,
            "Bruchspannung in der Sohle")
        p.formel(sigma_f, r"5.1 \cdot @s_u \cdot \left(1 + @s_c + @d_c - @i_c - @b_c - @g_c\right)"
                          r" + @sigma0", {"s_u": s_u, "i_c": i_c, "s_c": spalte.s, "d_c": spalte.d,
                                          "b_c": spalte.b, "g_c": spalte.g, "sigma0": sigma0},
                 titel="Bruchspannung in der Sohle, undrainiert", referenz=KAP_UNDRAINIERT,
                 name="Bruchspannung in der Sohle")
        erg.sigma_f = sigma_f.groesse.si
        return self._widerstand(p, werte, erg, sigma_f, b, L, N)

    # -- Gemeinsam ----------------------------------------------------------

    def _widerstand(self, p: Protokoll, werte: Zwischenwerte, erg: Fallergebnis,
                    sigma_f: Wert, b: Wert, L: Wert, N: Wert) -> Fallergebnis:
        # Ein negatives σ_f gibt keinen Widerstand, nicht einen negativen: die
        # Begrenzung auf null steht in der Formel (Benutzer, 2026-11-19). Das
        # Buch sagt dazu nichts -- nach Vorgabe, nicht nachgeschlagen.
        if sigma_f.groesse.si < 0.0:
            p.text("σ_f ist negativ: die Formel gibt keinen Widerstand, N_Rd ist null "
                   "(nach Vorgabe, nicht nachgeschlagen).")
        N_Rd = werte.kraft("N_Rd", "N_{Rd}", max(0.0, sigma_f.groesse.si) * b.groesse.si
                           * L.groesse.si, "Widerstand")
        p.formel(N_Rd, r"\max\left[0;\ @sigma_f\right] \cdot @b \cdot @L",
                 {"sigma_f": sigma_f, "b": b, "L": L},
                 titel="Grundbruchwiderstand", referenz="Kap. 9.2.11; SIA 267:2013, 8.5.3.5",
                 name="Grundbruchwiderstand")
        erg.N_Rd = N_Rd.groesse.si
        erg.ausgang, erg.begruendung = self.vergleichen(p, erg.kombination, N, N_Rd,
                                                        ("N_Ed", "N_Rd"))
        return erg


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



# ===========================================================================
# Für die Zusammenfassung
# ===========================================================================


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

    def faktor(name: str):
        return lambda s: getattr(befund.spalten[s], name).groesse.si

    mehrere = len(befund.ergebnisse) > 1
    zeilen = [
        zeile("N", faktor("N")),
        zeile("s", faktor("s")),
        zeile("d", faktor("d")),
        *[zeile("i", lambda s, r=r: r.i.get(s), r.kombination.name if mehrere else "")
          for r in befund.ergebnisse],
        zeile("g", faktor("g")),
        zeile("b'", faktor("b")),
    ]
    kopf: List[Zelle] = []
    for _, titel in SPALTEN:
        kopf += [titel, ""]
    return TabellenBlock(kopf=kopf, zeilen=zeilen, titel="Tragfähigkeitsfaktoren",
                         ausrichtung="lrlrlr")
