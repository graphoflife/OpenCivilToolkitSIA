"""
opencivil/durchstanzen/mit_bewehrung.py -- der Nachweis mit Durchstanzbewehrung und Stahlpilz.

VERANTWORTUNG:
Was der Durchstanznachweis rechnet, wenn der Beton allein nicht reicht:
welches ancoPLUS es braucht (:func:`.bewehrung.bemessen`), und die vier
Nachweise mit ihm, je mit Herleitung und Urteil (SIA 262:2025, 4.3.6.5.1)::

    Bewehrung        V_d − V_Rd,c ≤ V_Rd,s = ΣA_sw · k_e · σ_sd        (66), (68), (69)
    Verformung       V_d / 2 ≤ ΣA_sw · k_e · f_yd                       (67)
    Druckdiagonale   V_d ≤ min[k_sys · k_r; 3.5] · τ_cd · d_v · u        (70), 4.3.6.5.9
    ausserhalb       V_d,out ≤ k_r · τ_cd · d_v,out · u_out             4.3.6.5.10, Figur 26

Die Anker stehen senkrecht (β = 90°, sin β = 1). Der Stahl der Anker ist
der der Biegebewehrung -- ancoPLUS ist aus B500B. k_sys ist der Faktor aus
dem Gutachten des Produkts anstelle der 2 in (70), wie 4.3.6.5.9 es zulässt
(:func:`.produkte.k_sys`).

IM ÄUSSEREN SCHNITT:
d_v,out reicht von der Zugbewehrung bis zu den Köpfen der Anker auf der
Druckseite: d − c_v (Figur 26). k_e ist das des inneren Schnitts -- aus der
Näherung dasselbe; aus der Exzentrizität wäre es aussen grösser, der Wert
von innen liegt auf der sicheren Seite. Abgezogen wird die Flächenlast
innerhalb des äusseren Schnitts (4.3.6.2.6).

DER STAHLPILZ (4.3.6.6):
Bricht an einer Innenstütze die erste Betondruckdiagonale, hilft mehr
Bewehrung nicht. Dann wird der kleinste ZEUS gewählt, der zwischen die
Überdeckungen passt und mit dem die Platte ausserhalb seiner Stege hält:
ohne Leisten, sonst mit Leisten um ihn -- dieselben vier Nachweise, mit dem
Pilz als gestützter Fläche (4.3.6.6.2). Seine Fläche reicht bis an die Enden
der Stege; die wirksame Höhe reicht von der Zugbewehrung bis zur Unterkante
des Pilzes, d_v = d − 20 mm (gelesen, nicht nachgeschlagen). Den Widerstand
des Pilzes selbst (4.3.6.6.1) bestätigt der Hersteller.

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingaben, NachweisUrteil, Vergleich
from opencivil.core.einheiten import EINHEITSLOS, M2, MM2, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.bewehrung import Vorschlag, bemessen
from opencivil.durchstanzen.produkte import Stahlpilz
from opencivil.durchstanzen.schnitt import (
    ECKENBEREICH, Auswertung, Nachweisschnitt, Punkt, Stueck, Stuetzenflaeche, kandidaten_stuetze,
    konvexe_huelle, nachweisschnitt,
)
from opencivil.durchstanzen.stelle import Lage

if TYPE_CHECKING:
    from opencivil.durchstanzen.nachweis import Durchstanzen


@dataclass(frozen=True)
class Grundlage:
    """Was der Nachweis ohne Bewehrung schon gerechnet hat -- der mit Bewehrung baut darauf."""

    d: Wert
    d_v: Wert
    k_e: Wert
    k_r: Wert
    tau_cd: Wert
    u: Wert
    psi: Wert
    V_d: Wert
    """Die Querkraft im inneren Schnitt, die Flächenlast darin abgezogen."""

    V_Rd_c: Wert
    masse: Dict[str, float]
    umriss: Tuple[Punkt, ...]


@dataclass(frozen=True)
class Ort:
    """Wo die Leisten ansetzen: an der Stütze, oder um den Stahlpilz (4.3.6.6.2)."""

    zusatz: str
    """Was hinter dem Namen eines Urteils steht: leer, oder «um den Stahlpilz»."""

    kurz: str
    """Die Vorsilbe der Zwischenwerte, damit Stütze und Pilz nebeneinander stehen können."""

    umriss: Tuple[Punkt, ...]
    r_zu: Callable[[float], Sequence[Stueck]]
    """Der geschlossene Schnitt im Abstand r um die gestützte Fläche."""

    d_v: Wert
    u: Wert
    V_d: Wert
    V_Rd_c: Wert
    ausnahme: bool
    """Ob der Faktor des Gutachtens erhöht ist -- Innenstütze und Wandende."""


@dataclass(frozen=True)
class Pilzbefund:
    """Der gewählte Stahlpilz: welcher, seine gestützte Fläche und der Schnitt um sie. m."""

    pilz: Stahlpilz
    umriss: Tuple[Punkt, ...]
    schnitt: Nachweisschnitt
    d_v: float


@dataclass(frozen=True)
class Bewehrungsbefund:
    """
    Was die Bemessung vorschlägt und was es trägt -- fürs Bild und die
    Zusammenfassung. Leisten an der Stütze, ein Pilz ohne Leisten, oder ein
    Pilz mit Leisten um ihn. Der äussere Nachweis ist der um die Leisten,
    ohne Leisten der um den Pilz. N, m.
    """

    vorschlag: Optional[Vorschlag]
    pilz: Optional[Pilzbefund]
    sigma_sd: float
    V_Rd_s: float
    V_Rd_max: float
    k_sys: float
    d_v_out: float
    u_out: float
    V_d_out: float
    V_Rd_c_out: float


# ===========================================================================
# Die Regeln -- je einmal, für die Suche und für die Herleitung
# ===========================================================================


def spannung(E_s: float, psi: float, f_ctm: float, f_yd: float, d: float, phi: float) -> float:
    """σ_sd nach Gleichung (69)."""
    return min(E_s * psi / 6.0 * (1.0 + f_ctm / f_yd * d / phi), f_yd)


def widerstand(k_r: float, tau_cd: float, d_v: float, u: float) -> float:
    """V_Rd,c nach (58) -- im äusseren Schnitt mit d_v,out (4.3.6.5.10), am Pilz mit seinem d_v."""
    return k_r * tau_cd * d_v * u


def druckdiagonale(k_sys: float, k_r: float, tau_cd: float, d_v: float, u: float) -> float:
    """V_Rd,max nach (70), mit dem Faktor des Gutachtens (4.3.6.5.9)."""
    return min(k_sys * k_r, produkte.GRENZE) * tau_cd * d_v * u


@dataclass(frozen=True)
class _Werte:
    """Was jede Rechnung mit Bewehrung braucht, als Zahlen und als Werte der Herleitung."""

    e: Eingaben
    g: Grundlage
    f_yd: Wert
    E_s: Wert
    f_ctm: Wert
    c_v: float
    h_A: Wert
    d_v_out: Wert

    def sigma(self, phi: float) -> float:
        return spannung(self.E_s.groesse.si, self.g.psi.groesse.si, self.f_ctm.groesse.si,
                        self.f_yd.groesse.si, self.g.d.groesse.si, phi)

    def flaechenlast(self, flaeche: float) -> float:
        return self.e.g("q_d").si * flaeche


# ===========================================================================
# Der Nachweis
# ===========================================================================


def nachweisen(n: "Durchstanzen", e: Eingaben, p: Protokoll, w: Zwischenwerte,
               g: Grundlage) -> Tuple[List[NachweisUrteil], Optional[Bewehrungsbefund],
                                      Dict[str, Groesse]]:
    """
    Die Durchstanzbewehrung suchen und mit ihr nachweisen -- und wo die erste
    Druckdiagonale an einer Innenstütze bricht, einen Stahlpilz. Zurück kommen
    die Urteile, der Befund und die Grade, die ohne Urteil bleiben (ein Pilz,
    der ohne Leisten auskommt, braucht keine Bewehrung).
    """
    s = n.stelle
    p.titel("Durchstanzbewehrung", ebene=3)
    c_v = e.g("c_v").si
    h_frei = w.laenge("h_frei", r"h_{frei}", e.g("h").si - e.g("c").si - c_v)
    p.formel(h_frei, "@h - @c - @c_v", {"h": e["h"], "c": e["c"], "c_v": e["c_v"]},
             titel="Platz für die Anker zwischen den Überdeckungen",
             name="Platz für die Durchstanzbewehrung")
    h_A = w.laenge("h_A", "h_A", produkte.ankerhoehe(e.g("h").si, e.g("c").si, c_v))
    p.wert(h_A, titel="Höhe der Anker: auf eine lieferbare Höhe abgerundet, die auf 5 mm endet")
    werte = _Werte(e, g, e[s.stahl.eingabename("f_yd")], e[s.stahl.eingabename("E_s")],
                   e[s.beton.eingabename("f_ctm")], c_v, h_A,
                   w.laenge("d_v_out", r"d_{v,out}", g.d.groesse.si - c_v))
    stuetze = Ort("", "", g.umriss, lambda r: s.kandidaten(g.masse, r, g.d_v.groesse.si)[0].stuecke,
                  g.d_v, g.u, g.V_d, g.V_Rd_c, s.lage in (Lage.INNEN, Lage.WANDENDE))
    vorschlag = _suchen(n, werte, stuetze)
    if vorschlag is not None:
        urteile, befund, bricht = _mit_leisten(n, p, w, werte, stuetze, vorschlag)
    else:
        p.hinweis("Für diese Platte gibt es kein ancoPLUS: sie ist zu dünn (d < 160 mm), "
                  "keine lieferbare Höhe passt, oder keine Leiste findet Platz.")
        urteile, befund, bricht = n.nicht_fuehrbar("Kein ancoPLUS passt in diese Platte."), None, True
    if not bricht:
        return urteile, befund, {}
    if s.lage is not Lage.INNEN:
        p.hinweis("Stahlpilze sind im Katalog nur für Innenstützen. Eine grössere Stütze, eine "
                  "dickere Platte oder ein besserer Beton.")
        return urteile, befund, {}
    gewaehlt = _pilz_suchen(n, werte)
    if gewaehlt is None:
        p.hinweis("Auch kein ZEUS-Stahlpilz reicht, der in diese Platte passt. Eine grössere "
                  "Stütze, eine dickere Platte oder ein besserer Beton.")
        return urteile, befund, {}
    return _mit_pilz(n, p, w, werte, *gewaehlt)


def _suchen(n: "Durchstanzen", werte: _Werte, ort: Ort) -> Optional[Vorschlag]:
    """Das kleinste ancoPLUS für diesen Ort -- siehe :func:`.bewehrung.bemessen`."""
    s, g = n.stelle, werte.g
    k_e, k_r, tau = g.k_e.groesse.si, g.k_r.groesse.si, g.tau_cd.groesse.si
    V_d, V_Rd_c = ort.V_d.groesse.si, ort.V_Rd_c.groesse.si
    d_v_out = werte.d_v_out.groesse.si

    def noetig(typ: produkte.Ankertyp, A_sw: float) -> bool:
        return (A_sw * k_e * werte.sigma(typ.durchmesser) >= V_d - V_Rd_c
                and A_sw * k_e * werte.f_yd.groesse.si >= V_d / 2.0)

    def aussen_reicht(schnitt: Nachweisschnitt) -> bool:
        return (widerstand(k_r, tau, d_v_out, k_e * schnitt.u)
                >= werte.e.g("V_d").si - werte.flaechenlast(schnitt.massgebend.flaeche_ohne_aussparungen))

    return bemessen(
        d=g.d.groesse.si, d_v=ort.d_v.groesse.si, d_v_out=d_v_out, h_A=werte.h_A.groesse.si,
        r_2_zu=ort.r_zu, umriss=ort.umriss, raender=s.raender(g.masse),
        aussparungen=s.aussparungen, achse=s.achse(g.masse), ueberdeckung=werte.e.g("c").si,
        noetig=noetig, aussen_reicht=aussen_reicht)


def _mit_leisten(n: "Durchstanzen", p: Protokoll, w: Zwischenwerte, werte: _Werte, ort: Ort,
                 vorschlag: Vorschlag, pilz: Optional[Pilzbefund] = None,
                 ) -> Tuple[List[NachweisUrteil], Bewehrungsbefund, bool]:
    """
    Die vier Nachweise mit diesen Leisten, mit Herleitung. Zurück: die Urteile,
    der Befund und ob die erste Druckdiagonale bricht.
    """
    e, g, k = werte.e, werte.g, ort.kurz
    k_e, k_r, tau = g.k_e.groesse.si, g.k_r.groesse.si, g.tau_cd.groesse.si
    V_d = ort.V_d.groesse.si
    typ = vorschlag.typ
    p.erklaerung(
        f"Vorgeschlagen wird ancoPLUS von AncoTech{ort.zusatz and ' ' + ort.zusatz}: "
        f"{vorschlag.name} -- je Leiste {len(vorschlag.abstaende)} Anker ⌀{typ.durchmesser * 1e3:.0f} "
        f"mit h_A = {werte.h_A.formatiert()} mm, vom Rand der gestützten Fläche "
        f"{' / '.join(f'{a * 1e3:.0f}' for a in vorschlag.abstaende)} mm. Die Abstände sind die "
        f"der Typen «D» nach dem Gutachten des Herstellers: 0.375·d zum ersten Anker, bis zum "
        f"dritten 0.60·d, danach 0.75·d; zwei Leisten stehen beim zweiten Anker höchstens "
        f"1.5·d auseinander ({produkte.QUELLE_ANCOPLUS}, nach Vorgabe, nicht nachgeschlagen).")
    if not vorschlag.reicht:
        p.hinweis("Kein ancoPLUS erfüllt alle Bedingungen; gerechnet ist der stärkste Versuch.")

    # -- Bewehrung (66), (68), (69) ---------------------------------------
    phi = w.laenge(f"{k}phi_sw", r"\varnothing_{sw}", typ.durchmesser, stellen=0)
    sigma_si = werte.sigma(typ.durchmesser)
    sigma = w.wert(f"{k}sigma_sd", r"\sigma_{sd}", Groesse.aus_si(sigma_si, N_PRO_MM2), 0,
                   "Spannung in der Durchstanzbewehrung")
    p.formel(sigma, r"\min\left[\frac{@E_s \cdot @psi}{6} \cdot \left(1 + \frac{@f_ctm}{@f_yd} "
                    r"\cdot \frac{@d}{@phi}\right);\ @f_yd\right]",
             {"E_s": werte.E_s, "psi": g.psi, "f_ctm": werte.f_ctm, "f_yd": werte.f_yd, "d": g.d,
              "phi": phi},
             titel="Spannung in der Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4, (69)",
             name="Spannung in der Durchstanzbewehrung")
    leisten = w.zahl(f"{k}n_L", "n_L", len(vorschlag.leisten), stellen=0)
    im_bereich = w.zahl(f"{k}n_A", "n_A", vorschlag.anrechenbar, stellen=0)
    p.erklaerung(f"Angerechnet werden die Anker zwischen 0.35·d_v und d_v vom Rand der "
                 f"gestützten Fläche: {vorschlag.anrechenbar} je Leiste.")
    A_sw = w.wert(f"{k}A_sw", r"\sum A_{sw}", Groesse.aus_si(vorschlag.A_sw, MM2), 0,
                  "Anrechenbare Durchstanzbewehrung")
    p.formel(A_sw, r"@n_L \cdot @n_A \cdot \frac{\pi \cdot @phi^{2}}{4}",
             {"n_L": leisten, "n_A": im_bereich, "phi": phi},
             titel="Anrechenbare Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4",
             name="Anrechenbare Durchstanzbewehrung")
    V_Rd_s = w.kraft(f"{k}V_Rd_s", r"V_{Rd,s}", vorschlag.A_sw * k_e * sigma_si,
                     "Beitrag der Durchstanzbewehrung")
    p.formel(V_Rd_s, r"@A_sw \cdot @k_e \cdot @sigma_sd", {"A_sw": A_sw, "k_e": g.k_e, "sigma_sd": sigma},
             titel="Beitrag der Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4, (68)",
             name="Beitrag der Durchstanzbewehrung")
    V_d_s = w.kraft(f"{k}V_d_s", r"V_{d,s}", V_d - ort.V_Rd_c.groesse.si)
    p.formel(V_d_s, r"@V_d - @V_Rd_c", {"V_d": ort.V_d, "V_Rd_c": ort.V_Rd_c},
             titel="Querkraft für die Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.2, (66)",
             name="Querkraft für die Durchstanzbewehrung")
    v_s = Vergleich(V_d_s, V_Rd_s)
    v_s.bedingung(p, "Querkraft für die Bewehrung gegen ihren Beitrag")
    v_s.zeile(p, n.d_mit, mit_urteil=True)

    # -- Verformungsvermögen (67) ------------------------------------------
    V_halb = w.kraft(f"{k}V_d_halb", r"V_d / 2", V_d / 2.0)
    p.formel(V_halb, r"\frac{@V_d}{2}", {"V_d": ort.V_d}, titel="Die halbe Querkraft",
             referenz="SIA 262:2025, 4.3.6.5.3, (67)", name="Halbe Querkraft für das Verformungsvermögen")
    V_Rd_v = w.kraft(f"{k}V_Rd_v", r"V_{Rd,v}", vorschlag.A_sw * k_e * werte.f_yd.groesse.si)
    p.formel(V_Rd_v, r"@A_sw \cdot @k_e \cdot @f_yd", {"A_sw": A_sw, "k_e": g.k_e, "f_yd": werte.f_yd},
             titel="Durchstanzbewehrung an der Fliessgrenze", referenz="SIA 262:2025, 4.3.6.5.3, (67)",
             name="Durchstanzbewehrung an der Fliessgrenze")
    v_v = Vergleich(V_halb, V_Rd_v)
    v_v.bedingung(p, "Verformungsvermögen: die halbe Querkraft gegen die fliessende Bewehrung")
    v_v.zeile(p, n.d_verformung, mit_urteil=True)

    # -- Betondruckdiagonale (70) ------------------------------------------
    d = g.d.groesse.si
    k_sys_si = produkte.k_sys(werte.c_v, d, ort.ausnahme)
    k_sys = w.zahl(f"{k}k_sys", r"k_{sys}", k_sys_si, stellen=2)
    p.erklaerung(
        "Die Faktoren 2 und 3.5 in Gleichung (70) dürfen erhöht werden, wenn Versuche es "
        "belegen (4.3.6.5.9). Das Gutachten von ancoPLUS lässt für Innenstützen und Wandenden "
        "3·k_r zu, wenn die Köpfe auf der Druckseite höchstens d/10 tief liegen; bei d/6 gilt "
        "wieder 2·k_r, dazwischen linear. Für Rand- und Eckstützen bleibt es bei 2·k_r. Die "
        "Obergrenze bleibt 3.5.")
    p.wert(k_sys, titel=f"Faktor des Produkts: c_v = {werte.c_v * 1e3:.0f} mm, d/10 = {d * 1e2:.0f} mm, "
                        f"d/6 = {d * 1e3 / 6:.0f} mm")
    V_Rd_max_si = druckdiagonale(k_sys_si, k_r, tau, ort.d_v.groesse.si, ort.u.groesse.si)
    V_Rd_max = w.kraft(f"{k}V_Rd_max", r"V_{Rd,max}", V_Rd_max_si,
                       "Widerstand der ersten Betondruckdiagonale")
    p.formel(V_Rd_max, rf"\min\left[@k_sys \cdot @k_r;\ {produkte.GRENZE:g}\right] \cdot @tau_cd "
                       r"\cdot @d_v \cdot @u",
             {"k_sys": k_sys, "k_r": g.k_r, "tau_cd": g.tau_cd, "d_v": ort.d_v, "u": ort.u},
             titel="Widerstand der ersten Betondruckdiagonale an der gestützten Fläche",
             referenz="SIA 262:2025, 4.3.6.5.8, (70)", name="Widerstand der ersten Betondruckdiagonale")
    v_m = Vergleich(ort.V_d, V_Rd_max)
    v_m.bedingung(p, "Querkraft gegen die erste Betondruckdiagonale")
    v_m.zeile(p, n.d_diagonale, mit_urteil=True)
    if not v_m.erfuellt:
        p.hinweis("Die erste Betondruckdiagonale an der gestützten Fläche bricht vor der "
                  "Bewehrung: mehr Durchstanzbewehrung hilft nicht.")

    # -- Ausserhalb der Bewehrung (4.3.6.5.10) -----------------------------
    p.titel(f"Ausserhalb der Durchstanzbewehrung{ort.zusatz and ' ' + ort.zusatz}", ebene=3)
    p.formel(werte.d_v_out, "@d - @c_v", {"d": g.d, "c_v": e["c_v"]},
             titel="Wirksame statische Höhe bis zu den Köpfen der Anker",
             referenz="SIA 262:2025, 4.3.6.5.10, Figur 26",
             name="Wirksame statische Höhe im äusseren Nachweisschnitt")
    a = vorschlag.aussen.massgebend
    p.erklaerung("Der äussere Schnitt läuft im Abstand 0.5·d_v,out um die äussersten Anker. "
                 "Von einer Geraden zwischen zwei äussersten Ankern zählen höchstens "
                 "1.5·d_v,out von jedem Ende (Figur 26).")
    u_out = _umfang(p, w, g, a, f"{k}u_out", "out", "äusseren Nachweisschnitts",
                    "Äusserer Nachweisschnitt", "SIA 262:2025, 4.3.6.5.10, Figur 26")
    V_d_out = _querkraft(e, p, w, a.flaeche_ohne_aussparungen, f"{k}V_d_out", r"V_{d,out}",
                         f"{k}A_out", r"A_{out}", "äusseren Nachweisschnitt", "out")
    V_Rd_out = w.kraft(f"{k}V_Rd_c_out", r"V_{Rd,c,out}",
                       widerstand(k_r, tau, werte.d_v_out.groesse.si, u_out.groesse.si),
                       "Durchstanzwiderstand im äusseren Nachweisschnitt")
    p.formel(V_Rd_out, r"@k_r \cdot @tau_cd \cdot @d_v_out \cdot @u_out",
             {"k_r": g.k_r, "tau_cd": g.tau_cd, "d_v_out": werte.d_v_out, "u_out": u_out},
             titel="Durchstanzwiderstand im äusseren Nachweisschnitt",
             referenz="SIA 262:2025, 4.3.6.5.10, (58)",
             name="Durchstanzwiderstand im äusseren Nachweisschnitt")
    v_a = Vergleich(V_d_out, V_Rd_out)
    v_a.bedingung(p, "Querkraft gegen den Widerstand ausserhalb der Bewehrung")
    v_a.zeile(p, n.d_aussen, mit_urteil=True)

    z = f" {ort.zusatz}" if ort.zusatz else ""
    urteile = [
        n.urteil(n.d_mit, f"mit Durchstanzbewehrung{z}", v_s,
                 f"{vorschlag.name}: V_d,s = {V_d_s.formatiert()} kN "
                 f"{'≤' if v_s.erfuellt else '>'} V_Rd,s = {V_Rd_s.formatiert()} kN."),
        n.urteil(n.d_verformung, f"Verformungsvermögen{z}", v_v,
                 f"V_d/2 = {V_halb.formatiert()} kN {'≤' if v_v.erfuellt else '>'} "
                 f"ΣA_sw·k_e·f_yd = {V_Rd_v.formatiert()} kN."),
        n.urteil(n.d_diagonale, f"Betondruckdiagonale{z}", v_m,
                 f"V_d = {ort.V_d.formatiert()} kN {'≤' if v_m.erfuellt else '>'} "
                 f"V_Rd,max = {V_Rd_max.formatiert()} kN."),
        n.urteil(n.d_aussen, f"ausserhalb der Durchstanzbewehrung{z}", v_a,
                 f"V_d,out = {V_d_out.formatiert()} kN {'≤' if v_a.erfuellt else '>'} "
                 f"V_Rd,c,out = {V_Rd_out.formatiert()} kN."),
    ]
    befund = Bewehrungsbefund(
        vorschlag=vorschlag, pilz=pilz, sigma_sd=sigma_si, V_Rd_s=V_Rd_s.groesse.si,
        V_Rd_max=V_Rd_max_si, k_sys=k_sys_si, d_v_out=werte.d_v_out.groesse.si,
        u_out=u_out.groesse.si, V_d_out=V_d_out.groesse.si, V_Rd_c_out=V_Rd_out.groesse.si)
    return urteile, befund, not v_m.erfuellt


def _umfang(p: Protokoll, w: Zwischenwerte, g: Grundlage, a: Auswertung, name: str, index: str,
            genitiv: str, nominativ: str, referenz: str) -> Wert:
    """
    Ein Schnitt, wie er zählt: in der Platte, ohne was nicht zählt, mit k_e --
    für den äusseren Schnitt (``index`` «out») und den um den Pilz («P»).
    """
    symbol = f"u_{{{index}}}"
    roh = w.laenge(f"{name}_0", f"u_{{{index},0}}", a.in_der_platte, stellen=0)
    p.wert(roh, titel=f"{nominativ}, soweit er in der Platte liegt", referenz=referenz)
    red = w.laenge(f"{name}_red", f"u_{{{index},red}}", a.u, stellen=0)
    if a.an_ecken + a.hinter_aussparungen > 1e-6:
        abzug = w.laenge(f"{name}_ab", rf"\Delta {symbol}", a.an_ecken + a.hinter_aussparungen,
                         stellen=0)
        p.wert(abzug, titel="Was neben den Ecken und hinter Aussparungen nicht zählt",
               referenz="SIA 262:2025, Figur 23a, 23d und 26")
        # Die Platzhalter tragen den Index: der äussere Schnitt und der um den
        # Pilz sind in der Formelsammlung zwei Seiten, nicht eine.
        p.formel(red, f"@roh_{index} - @ab_{index}", {f"roh_{index}": roh, f"ab_{index}": abzug},
                 titel=f"{nominativ} ohne das, was nicht zählt",
                 name=f"{nominativ} ohne das, was nicht zählt")
    else:
        p.formel(red, f"@roh_{index}", {f"roh_{index}": roh},
                 titel=f"{nominativ} ohne das, was nicht zählt",
                 name=f"{nominativ} ohne das, was nicht zählt")
    wirksam = w.laenge(name, symbol, g.k_e.groesse.si * a.u, stellen=0)
    p.formel(wirksam, rf"@k_e \cdot @red_{index}", {"k_e": g.k_e, f"red_{index}": red},
             titel=f"Wirksamer Umfang des {genitiv}, mit k_e von innen",
             referenz="SIA 262:2025, 4.3.6.2.3", name=f"Wirksamer Umfang des {genitiv}")
    return wirksam


def _querkraft(e: Eingaben, p: Protokoll, w: Zwischenwerte, flaeche: float, name: str,
               symbol: str, name_A: str, symbol_A: str, wo: str, index: str) -> Wert:
    """
    V_d in einem Schnitt ausserhalb: die Flächenlast darin abgezogen
    (4.3.6.2.6). Die Platzhalter tragen den Index, wie in :func:`_umfang`.
    """
    V_d, q_d = e["V_d"], e["q_d"]
    titel = f"Querkraft im {wo}"
    if q_d.groesse.si <= 0.0:
        ergebnis = w.kraft(name, symbol, V_d.groesse.si)
        p.formel(ergebnis, f"@Vd_{index}", {f"Vd_{index}": V_d}, titel=f"{titel}: keine Flächenlast",
                 referenz="SIA 262:2025, 4.3.6.2.6", name=titel)
        return ergebnis
    A = w.wert(name_A, symbol_A, Groesse.aus_si(flaeche, M2), 3,
               "Fläche innerhalb des Schnitts, ohne Aussparungen")
    p.wert(A, titel="Fläche innerhalb des Schnitts, ohne Aussparungen")
    ergebnis = w.kraft(name, symbol, V_d.groesse.si - q_d.groesse.si * flaeche)
    p.formel(ergebnis, rf"@Vd_{index} - @qd_{index} \cdot @A_{index}",
             {f"Vd_{index}": V_d, f"qd_{index}": q_d, f"A_{index}": A},
             titel=titel, referenz="SIA 262:2025, 4.3.6.2.6", name=titel)
    return ergebnis


# ===========================================================================
# Der Stahlpilz
# ===========================================================================


def _pilzflaeche(werte: _Werte, n: "Durchstanzen", pilz: Stahlpilz
                 ) -> Tuple[Tuple[Punkt, ...], Nachweisschnitt, float]:
    """Die gestützte Fläche des Pilzes, der Schnitt im Abstand d_v/2 um sie und sein d_v."""
    s, g = n.stelle, werte.g
    umriss = tuple(konvexe_huelle(list(g.umriss) + list(pilz.armenden())))
    d_v = g.d.groesse.si - produkte.PILZ_UNTEN
    schnitt = nachweisschnitt(
        kandidaten_stuetze(Stuetzenflaeche(umriss), d_v / 2.0, ECKENBEREICH * d_v, s.raender(g.masse)),
        d_v=d_v, achse=s.achse(g.masse), aussparungen=s.aussparungen)
    return umriss, schnitt, d_v


def _pilz_suchen(n: "Durchstanzen", werte: _Werte
                 ) -> Optional[Tuple[Pilzbefund, Optional[Vorschlag]]]:
    """
    Der kleinste ZEUS, der zwischen die Überdeckungen passt, über die Stütze
    hinausreicht und mit dem die Platte ausserhalb hält -- ohne Leisten oder
    mit Leisten um ihn, die alle vier Nachweise erfüllen.

    Ein Pilz, dessen Druckdiagonale nicht einmal mit dem ganzen Umfang um ihn
    hielte -- der Hülle samt dem Bogen d_v/2 rundum, ohne Abzüge --, fällt
    weg, bevor sein Schnitt gerechnet wird: so bleibt die Suche schnell.
    """
    g, e = werte.g, werte.e
    k_e, k_r, tau, d = g.k_e.groesse.si, g.k_r.groesse.si, g.tau_cd.groesse.si, g.d.groesse.si
    hoehe = e.g("h").si - produkte.PILZ_OBEN - produkte.PILZ_UNTEN
    weite = max(max(abs(x), abs(y)) for x, y in g.umriss)
    k_sys = produkte.k_sys(werte.c_v, d, True)
    d_v = d - produkte.PILZ_UNTEN
    V_d_hoechstens = e.g("V_d").si
    for pilz in produkte.STAHLPILZE:
        if pilz.h > hoehe + 1e-9 or pilz.s / 2.0 < weite + produkte.PILZ_UEBERSTAND - 1e-9:
            continue
        huelle = konvexe_huelle(list(g.umriss) + list(pilz.armenden()))
        rand = sum(math.dist(huelle[i - 1], huelle[i]) for i in range(len(huelle)))
        u_hoechstens = k_e * (rand + math.pi * d_v)
        V_d_wenigstens = V_d_hoechstens - werte.flaechenlast(
            abs(sum(huelle[i - 1][0] * huelle[i][1] - huelle[i][0] * huelle[i - 1][1]
                    for i in range(len(huelle))) / 2.0) + rand * d_v / 2.0 + math.pi * d_v ** 2 / 4.0)
        if druckdiagonale(k_sys, k_r, tau, d_v, u_hoechstens) < V_d_wenigstens:
            continue
        umriss, schnitt, d_v = _pilzflaeche(werte, n, pilz)
        u = k_e * schnitt.u
        V_d = V_d_hoechstens - werte.flaechenlast(schnitt.massgebend.flaeche_ohne_aussparungen)
        V_Rd_c = widerstand(k_r, tau, d_v, u)
        befund = Pilzbefund(pilz, umriss, schnitt, d_v)
        if V_Rd_c >= V_d:
            return befund, None
        if druckdiagonale(k_sys, k_r, tau, d_v, u) < V_d:
            continue
        # Nur für die Suche: Werte, die in keine Herleitung kommen.
        w = Zwischenwerte("suche")
        ort = _pilzort(befund, w.laenge("d_v", "d_v", d_v), w.laenge("u", "u", u),
                       w.kraft("V_d", "V_d", V_d), w.kraft("V_Rd_c", "V_Rd_c", V_Rd_c))
        vorschlag = _suchen(n, werte, ort)
        if vorschlag is not None and vorschlag.reicht:
            return befund, vorschlag
    return None


def _pilzort(befund: Pilzbefund, d_v: Wert, u: Wert, V_d: Wert, V_Rd_c: Wert) -> Ort:
    """Der Pilz als Ort der Leisten: seine Fläche, sein d_v, der Schnitt um ihn."""
    huelle = befund.umriss
    return Ort("um den Stahlpilz", "P_", huelle,
               lambda r: kandidaten_stuetze(Stuetzenflaeche(huelle), r, math.inf)[0].stuecke,
               d_v, u, V_d, V_Rd_c, True)


def _mit_pilz(n: "Durchstanzen", p: Protokoll, w: Zwischenwerte, werte: _Werte,
              befund: Pilzbefund, vorschlag: Optional[Vorschlag]
              ) -> Tuple[List[NachweisUrteil], Bewehrungsbefund, Dict[str, Groesse]]:
    """Die Herleitung mit dem gewählten Pilz: die Platte ausserhalb, ohne oder mit Leisten."""
    e, g = werte.e, werte.g
    pilz = befund.pilz
    p.titel("Stahlpilz", ebene=3)
    p.erklaerung(
        f"Ein Stahlpilz vergrössert die gestützte Fläche. Gewählt ist der kleinste, der "
        f"zwischen die Überdeckungen passt -- unten {produkte.PILZ_UNTEN * 1e3:.0f} mm, oben "
        f"{produkte.PILZ_OBEN * 1e3:.0f} mm, die Vorgaben der Software von AncoTech -- und mit "
        f"dem die Platte ausserhalb hält: {pilz.name} ({produkte.QUELLE_ZEUS}). Seine "
        f"gestützte Fläche reicht bis an die Enden der Stege (4.3.6.6.2). Den Widerstand des "
        f"Pilzes selbst (4.3.6.6.1) bestätigt der Hersteller.")
    c_P = w.laenge("c_P", "c_P", produkte.PILZ_UNTEN, stellen=0)
    p.wert(c_P, titel="Beton unter dem Pilz")
    d_v = w.laenge("P_d_v", r"d_{v,P}", befund.d_v)
    p.formel(d_v, "@d - @c_P", {"d": g.d, "c_P": c_P},
             titel="Wirksame statische Höhe bis zur Unterkante des Pilzes",
             referenz="SIA 262:2025, 4.3.6.6.2", name="Wirksame statische Höhe um den Stahlpilz")
    a = befund.schnitt.massgebend
    u = _umfang(p, w, g, a, "P_u", "P", "Schnitts um den Stahlpilz", "Schnitt um den Stahlpilz",
                "SIA 262:2025, 4.3.6.6.2")
    V_d = _querkraft(e, p, w, a.flaeche_ohne_aussparungen, "P_V_d", r"V_{d,P}", "P_A", r"A_P",
                     "Schnitt um den Stahlpilz", "P")
    V_Rd_c = w.kraft("P_V_Rd_c", r"V_{Rd,c,P}",
                     widerstand(g.k_r.groesse.si, g.tau_cd.groesse.si, befund.d_v, u.groesse.si),
                     "Durchstanzwiderstand um den Stahlpilz")
    # Dieselbe Formel wie ohne Pilz (58): dieselbe Seite der Formelsammlung.
    p.formel(V_Rd_c, r"@k_r \cdot @tau_cd \cdot @d_v \cdot @u",
             {"k_r": g.k_r, "tau_cd": g.tau_cd, "d_v": d_v, "u": u},
             titel="Durchstanzwiderstand um den Stahlpilz, ohne Bewehrung",
             referenz="SIA 262:2025, 4.3.6.6.2", name="Durchstanzwiderstand ohne Durchstanzbewehrung")
    v = Vergleich(V_d, V_Rd_c)
    v.bedingung(p, "Querkraft gegen den Widerstand um den Stahlpilz")
    if vorschlag is None:
        v.zeile(p, n.d_aussen, mit_urteil=True)
        urteil = n.urteil(n.d_aussen, "ausserhalb des Stahlpilzes", v,
                          f"{pilz.name}: V_d,P = {V_d.formatiert()} kN ≤ "
                          f"V_Rd,c,P = {V_Rd_c.formatiert()} kN.")
        unbeschraenkt = Groesse(math.inf, EINHEITSLOS)
        bewehrungsbefund = Bewehrungsbefund(
            vorschlag=None, pilz=befund, sigma_sd=0.0, V_Rd_s=0.0, V_Rd_max=math.inf, k_sys=0.0,
            d_v_out=befund.d_v, u_out=u.groesse.si, V_d_out=V_d.groesse.si,
            V_Rd_c_out=V_Rd_c.groesse.si)
        return [urteil], bewehrungsbefund, {
            d.id: unbeschraenkt for d in (n.d_mit, n.d_verformung, n.d_diagonale)}
    p.erklaerung("Um den Pilz reicht der Beton allein nicht: dazu kommen Leisten, bündig an "
                 "den Pilz, mit den vier Nachweisen der Durchstanzbewehrung.")
    urteile, bewehrungsbefund, _ = _mit_leisten(n, p, w, werte, _pilzort(befund, d_v, u, V_d, V_Rd_c),
                                                vorschlag, befund)
    return urteile, bewehrungsbefund, {}
