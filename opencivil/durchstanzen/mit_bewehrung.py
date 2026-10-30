"""
opencivil/durchstanzen/mit_bewehrung.py -- der Nachweis mit Durchstanzbewehrung (SIA 262:2025, 4.3.6.5).

VERANTWORTUNG:
Was der Durchstanznachweis rechnet, wenn der Beton allein nicht reicht:
welches ancoPLUS es braucht (:func:`.bewehrung.bemessen`), und die vier
Nachweise mit ihm, je mit Herleitung und Urteil (4.3.6.5.1)::

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

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from opencivil.core.berechnung import Eingaben, NachweisUrteil, Vergleich
from opencivil.core.einheiten import M2, MM2, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.bewehrung import Vorschlag, bemessen
from opencivil.durchstanzen.schnitt import Nachweisschnitt, Punkt
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
class Bewehrungsbefund:
    """Die vorgeschlagene Durchstanzbewehrung und was sie trägt -- fürs Bild und die Zusammenfassung. N, m."""

    vorschlag: Vorschlag
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


def widerstand_aussen(k_r: float, tau_cd: float, d_v_out: float, u_out: float) -> float:
    """V_Rd,c im äusseren Schnitt: (58) mit d_v,out (4.3.6.5.10)."""
    return k_r * tau_cd * d_v_out * u_out


# ===========================================================================
# Der Nachweis
# ===========================================================================


def nachweisen(n: "Durchstanzen", e: Eingaben, p: Protokoll, w: Zwischenwerte,
               g: Grundlage) -> Tuple[List[NachweisUrteil], Optional[Bewehrungsbefund]]:
    """
    Die Durchstanzbewehrung suchen und mit ihr nachweisen. Zurück kommen die
    vier Urteile und der Befund -- ohne Befund, wo es kein ancoPLUS gibt;
    dann bleibt es bei einem Hinweis, und die Urteile sagen «nicht führbar».
    """
    s = n.stelle
    p.titel("Durchstanzbewehrung", ebene=3)
    f_yd, E_s = e[s.stahl.eingabename("f_yd")], e[s.stahl.eingabename("E_s")]
    f_ctm = e[s.beton.eingabename("f_ctm")]
    d, d_v, k_e, k_r, tau = (g.d.groesse.si, g.d_v.groesse.si, g.k_e.groesse.si,
                             g.k_r.groesse.si, g.tau_cd.groesse.si)
    V_d = g.V_d.groesse.si
    c_v = e.g("c_v").si
    h_frei = w.laenge("h_frei", r"h_{frei}", e.g("h").si - e.g("c").si - c_v)
    p.formel(h_frei, "@h - @c - @c_v", {"h": e["h"], "c": e["c"], "c_v": e["c_v"]},
             titel="Platz für die Anker zwischen den Überdeckungen",
             name="Platz für die Durchstanzbewehrung")
    h_A = w.laenge("h_A", "h_A", produkte.ankerhoehe(e.g("h").si, e.g("c").si, c_v))
    p.wert(h_A, titel="Höhe der Anker: auf eine lieferbare Höhe abgerundet, die auf 5 mm endet")
    d_v_out = w.laenge("d_v_out", r"d_{v,out}", d - c_v)

    def noetig(typ: produkte.Ankertyp, A_sw: float) -> bool:
        sigma = spannung(E_s.groesse.si, g.psi.groesse.si, f_ctm.groesse.si, f_yd.groesse.si, d,
                         typ.durchmesser)
        return (A_sw * k_e * sigma >= V_d - g.V_Rd_c.groesse.si
                and A_sw * k_e * f_yd.groesse.si >= V_d / 2.0)

    def flaechenlast(schnitt: Nachweisschnitt) -> float:
        return e.g("q_d").si * schnitt.massgebend.flaeche_ohne_aussparungen

    def aussen_reicht(schnitt: Nachweisschnitt) -> bool:
        return (widerstand_aussen(k_r, tau, d_v_out.groesse.si, k_e * schnitt.u)
                >= e.g("V_d").si - flaechenlast(schnitt))

    vorschlag = bemessen(
        d=d, d_v=d_v, d_v_out=d_v_out.groesse.si, h_A=h_A.groesse.si,
        r_2_zu=lambda r: s.kandidaten(g.masse, r, d_v)[0].stuecke, umriss=g.umriss,
        raender=s.raender(g.masse), aussparungen=s.aussparungen, achse=s.achse(g.masse),
        ueberdeckung=e.g("c").si, noetig=noetig, aussen_reicht=aussen_reicht)
    if vorschlag is None:
        p.hinweis("Für diese Platte gibt es kein ancoPLUS: sie ist zu dünn (d < 160 mm), "
                  "keine lieferbare Höhe passt, oder keine Leiste findet Platz. Eine "
                  "dickere Platte oder eine grössere Stütze.")
        return n.nicht_fuehrbar("Kein ancoPLUS passt in diese Platte."), None

    typ = vorschlag.typ
    p.erklaerung(
        f"Der Beton allein reicht nicht. Vorgeschlagen wird ancoPLUS von AncoTech: "
        f"{vorschlag.name} -- je Leiste {len(vorschlag.abstaende)} Anker ⌀{typ.durchmesser * 1e3:.0f} "
        f"mit h_A = {h_A.formatiert()} mm, vom Rand der Stütze "
        f"{' / '.join(f'{a * 1e3:.0f}' for a in vorschlag.abstaende)} mm. Die Abstände sind die "
        f"der Typen «D» nach dem Gutachten des Herstellers: 0.375·d zum ersten Anker, bis zum "
        f"dritten 0.60·d, danach 0.75·d; zwei Leisten stehen beim zweiten Anker höchstens "
        f"1.5·d auseinander ({produkte.QUELLE_ANCOPLUS}, nach Vorgabe, nicht nachgeschlagen).")
    if not vorschlag.reicht:
        p.hinweis("Kein ancoPLUS erfüllt alle Bedingungen; gerechnet ist der stärkste Versuch.")

    # -- Bewehrung (66), (68), (69) ---------------------------------------
    phi = w.laenge("phi_sw", r"\varnothing_{sw}", typ.durchmesser, stellen=0)
    sigma_si = spannung(E_s.groesse.si, g.psi.groesse.si, f_ctm.groesse.si, f_yd.groesse.si, d,
                        typ.durchmesser)
    sigma = w.wert("sigma_sd", r"\sigma_{sd}", Groesse.aus_si(sigma_si, N_PRO_MM2), 0,
                   "Spannung in der Durchstanzbewehrung")
    p.formel(sigma, r"\min\left[\frac{@E_s \cdot @psi}{6} \cdot \left(1 + \frac{@f_ctm}{@f_yd} "
                    r"\cdot \frac{@d}{@phi}\right);\ @f_yd\right]",
             {"E_s": E_s, "psi": g.psi, "f_ctm": f_ctm, "f_yd": f_yd, "d": g.d, "phi": phi},
             titel="Spannung in der Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4, (69)",
             name="Spannung in der Durchstanzbewehrung")
    leisten = w.zahl("n_L", "n_L", len(vorschlag.leisten), stellen=0)
    im_bereich = w.zahl("n_A", "n_A", vorschlag.anrechenbar, stellen=0)
    p.erklaerung(f"Angerechnet werden die Anker zwischen 0.35·d_v und d_v vom Rand der "
                 f"gestützten Fläche: {vorschlag.anrechenbar} je Leiste.")
    A_sw = w.wert("A_sw", r"\sum A_{sw}", Groesse.aus_si(vorschlag.A_sw, MM2), 0,
                  "Anrechenbare Durchstanzbewehrung")
    p.formel(A_sw, r"@n_L \cdot @n_A \cdot \frac{\pi \cdot @phi^{2}}{4}",
             {"n_L": leisten, "n_A": im_bereich, "phi": phi},
             titel="Anrechenbare Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4",
             name="Anrechenbare Durchstanzbewehrung")
    V_Rd_s = w.kraft("V_Rd_s", r"V_{Rd,s}", vorschlag.A_sw * k_e * sigma_si,
                     "Beitrag der Durchstanzbewehrung")
    p.formel(V_Rd_s, r"@A_sw \cdot @k_e \cdot @sigma_sd", {"A_sw": A_sw, "k_e": g.k_e, "sigma_sd": sigma},
             titel="Beitrag der Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4, (68)",
             name="Beitrag der Durchstanzbewehrung")
    V_d_s = w.kraft("V_d_s", r"V_{d,s}", V_d - g.V_Rd_c.groesse.si)
    p.formel(V_d_s, r"@V_d - @V_Rd_c", {"V_d": g.V_d, "V_Rd_c": g.V_Rd_c},
             titel="Querkraft für die Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.2, (66)",
             name="Querkraft für die Durchstanzbewehrung")
    v_s = Vergleich(V_d_s, V_Rd_s)
    v_s.bedingung(p, "Querkraft für die Bewehrung gegen ihren Beitrag")
    v_s.zeile(p, n.d_mit, mit_urteil=True)

    # -- Verformungsvermögen (67) ------------------------------------------
    V_halb = w.kraft("V_d_halb", r"V_d / 2", V_d / 2.0)
    p.formel(V_halb, r"\frac{@V_d}{2}", {"V_d": g.V_d}, titel="Die halbe Querkraft",
             referenz="SIA 262:2025, 4.3.6.5.3, (67)", name="Halbe Querkraft für das Verformungsvermögen")
    V_Rd_v = w.kraft("V_Rd_v", r"V_{Rd,v}", vorschlag.A_sw * k_e * f_yd.groesse.si)
    p.formel(V_Rd_v, r"@A_sw \cdot @k_e \cdot @f_yd", {"A_sw": A_sw, "k_e": g.k_e, "f_yd": f_yd},
             titel="Durchstanzbewehrung an der Fliessgrenze", referenz="SIA 262:2025, 4.3.6.5.3, (67)",
             name="Durchstanzbewehrung an der Fliessgrenze")
    v_v = Vergleich(V_halb, V_Rd_v)
    v_v.bedingung(p, "Verformungsvermögen: die halbe Querkraft gegen die fliessende Bewehrung")
    v_v.zeile(p, n.d_verformung, mit_urteil=True)

    # -- Betondruckdiagonale (70) ------------------------------------------
    ausnahme = s.lage in (Lage.INNEN, Lage.WANDENDE)
    k_sys_si = produkte.k_sys(c_v, d, ausnahme)
    k_sys = w.zahl("k_sys", r"k_{sys}", k_sys_si, stellen=2)
    p.erklaerung(
        "Die Faktoren 2 und 3.5 in Gleichung (70) dürfen erhöht werden, wenn Versuche es "
        "belegen (4.3.6.5.9). Das Gutachten von ancoPLUS lässt für Innenstützen und Wandenden "
        "3·k_r zu, wenn die Köpfe auf der Druckseite höchstens d/10 tief liegen; bei d/6 gilt "
        "wieder 2·k_r, dazwischen linear. Für Rand- und Eckstützen bleibt es bei 2·k_r. Die "
        "Obergrenze bleibt 3.5.")
    p.wert(k_sys, titel=f"Faktor des Produkts: c_v = {c_v * 1e3:.0f} mm, d/10 = {d * 1e2:.0f} mm, "
                        f"d/6 = {d * 1e3 / 6:.0f} mm")
    V_Rd_max_si = min(k_sys_si * k_r, produkte.GRENZE) * tau * d_v * g.u.groesse.si
    V_Rd_max = w.kraft("V_Rd_max", r"V_{Rd,max}", V_Rd_max_si,
                       "Widerstand der ersten Betondruckdiagonale")
    p.formel(V_Rd_max, rf"\min\left[@k_sys \cdot @k_r;\ {produkte.GRENZE:g}\right] \cdot @tau_cd "
                       r"\cdot @d_v \cdot @u",
             {"k_sys": k_sys, "k_r": g.k_r, "tau_cd": g.tau_cd, "d_v": g.d_v, "u": g.u},
             titel="Widerstand der ersten Betondruckdiagonale an der gestützten Fläche",
             referenz="SIA 262:2025, 4.3.6.5.8, (70)", name="Widerstand der ersten Betondruckdiagonale")
    v_m = Vergleich(g.V_d, V_Rd_max)
    v_m.bedingung(p, "Querkraft gegen die erste Betondruckdiagonale")
    v_m.zeile(p, n.d_diagonale, mit_urteil=True)
    if not v_m.erfuellt:
        p.hinweis("Die Betondruckdiagonale an der Stütze bricht vor der Bewehrung: mehr "
                  "Durchstanzbewehrung hilft nicht. Eine grössere Stütze, eine dickere Platte, "
                  "ein besserer Beton -- oder ein Stahlpilz.")

    # -- Ausserhalb der Bewehrung (4.3.6.5.10) -----------------------------
    p.titel("Ausserhalb der Durchstanzbewehrung", ebene=3)
    p.formel(d_v_out, "@d - @c_v", {"d": g.d, "c_v": e["c_v"]},
             titel="Wirksame statische Höhe bis zu den Köpfen der Anker",
             referenz="SIA 262:2025, 4.3.6.5.10, Figur 26",
             name="Wirksame statische Höhe im äusseren Nachweisschnitt")
    a = vorschlag.aussen.massgebend
    p.erklaerung("Der äussere Schnitt läuft im Abstand 0.5·d_v,out um die äussersten Anker. "
                 "Von einer Geraden zwischen zwei äussersten Ankern zählen höchstens "
                 "1.5·d_v,out von jedem Ende (Figur 26).")
    u_out_0 = w.laenge("u_out_0", r"u_{out,0}", a.in_der_platte, stellen=0)
    p.wert(u_out_0, titel="Äusserer Nachweisschnitt, soweit er in der Platte liegt",
           referenz="SIA 262:2025, 4.3.6.5.10, Figur 26")
    u_out_red = w.laenge("u_out_red", r"u_{out,red}", a.u, stellen=0)
    if a.an_ecken + a.hinter_aussparungen > 1e-6:
        abzug = w.laenge("du_out", r"\Delta u_{out}", a.an_ecken + a.hinter_aussparungen, stellen=0)
        p.wert(abzug, titel="Was zwischen den Ankern und hinter Aussparungen nicht zählt",
               referenz="SIA 262:2025, Figur 23d und 26")
        p.formel(u_out_red, r"@u_out_0 - @du_out", {"u_out_0": u_out_0, "du_out": abzug},
                 titel="Äusserer Nachweisschnitt ohne das, was nicht zählt",
                 name="Äusserer Nachweisschnitt ohne das, was nicht zählt")
    else:
        p.formel(u_out_red, "@u_out_0", {"u_out_0": u_out_0},
                 titel="Äusserer Nachweisschnitt ohne das, was nicht zählt",
                 name="Äusserer Nachweisschnitt ohne das, was nicht zählt")
    u_out = w.laenge("u_out", r"u_{out}", k_e * a.u, stellen=0)
    p.formel(u_out, r"@k_e \cdot @u_out_red", {"k_e": g.k_e, "u_out_red": u_out_red},
             titel="Wirksamer Umfang des äusseren Nachweisschnitts, mit k_e von innen",
             referenz="SIA 262:2025, 4.3.6.2.3", name="Wirksamer Umfang des äusseren Nachweisschnitts")
    V_d_out = _querkraft_aussen(e, p, w, a.flaeche_ohne_aussparungen)
    V_Rd_out = w.kraft("V_Rd_c_out", r"V_{Rd,c,out}",
                       widerstand_aussen(k_r, tau, d_v_out.groesse.si, u_out.groesse.si),
                       "Durchstanzwiderstand im äusseren Nachweisschnitt")
    p.formel(V_Rd_out, r"@k_r \cdot @tau_cd \cdot @d_v_out \cdot @u_out",
             {"k_r": g.k_r, "tau_cd": g.tau_cd, "d_v_out": d_v_out, "u_out": u_out},
             titel="Durchstanzwiderstand im äusseren Nachweisschnitt",
             referenz="SIA 262:2025, 4.3.6.5.10, (58)",
             name="Durchstanzwiderstand im äusseren Nachweisschnitt")
    v_a = Vergleich(V_d_out, V_Rd_out)
    v_a.bedingung(p, "Querkraft gegen den Widerstand ausserhalb der Bewehrung")
    v_a.zeile(p, n.d_aussen, mit_urteil=True)

    urteile = [
        n.urteil(n.d_mit, "mit Durchstanzbewehrung", v_s,
                 f"{vorschlag.name}: V_d,s = {V_d_s.formatiert()} kN "
                 f"{'≤' if v_s.erfuellt else '>'} V_Rd,s = {V_Rd_s.formatiert()} kN."),
        n.urteil(n.d_verformung, "Verformungsvermögen", v_v,
                 f"V_d/2 = {V_halb.formatiert()} kN {'≤' if v_v.erfuellt else '>'} "
                 f"ΣA_sw·k_e·f_yd = {V_Rd_v.formatiert()} kN."),
        n.urteil(n.d_diagonale, "Betondruckdiagonale", v_m,
                 f"V_d = {g.V_d.formatiert()} kN {'≤' if v_m.erfuellt else '>'} "
                 f"V_Rd,max = {V_Rd_max.formatiert()} kN."),
        n.urteil(n.d_aussen, "ausserhalb der Durchstanzbewehrung", v_a,
                 f"V_d,out = {V_d_out.formatiert()} kN {'≤' if v_a.erfuellt else '>'} "
                 f"V_Rd,c,out = {V_Rd_out.formatiert()} kN."),
    ]
    befund = Bewehrungsbefund(
        vorschlag=vorschlag, sigma_sd=sigma_si, V_Rd_s=V_Rd_s.groesse.si,
        V_Rd_max=V_Rd_max_si, k_sys=k_sys_si, d_v_out=d_v_out.groesse.si,
        u_out=u_out.groesse.si, V_d_out=V_d_out.groesse.si, V_Rd_c_out=V_Rd_out.groesse.si)
    return urteile, befund


def _querkraft_aussen(e: Eingaben, p: Protokoll, w: Zwischenwerte, flaeche: float) -> Wert:
    """V_d im äusseren Schnitt: die Flächenlast darin abgezogen (4.3.6.2.6)."""
    V_d, q_d = e["V_d"], e["q_d"]
    if q_d.groesse.si <= 0.0:
        ergebnis = w.kraft("V_d_out", r"V_{d,out}", V_d.groesse.si)
        p.formel(ergebnis, "@V_d", {"V_d": V_d}, titel="Keine Flächenlast im äusseren Schnitt",
                 referenz="SIA 262:2025, 4.3.6.2.6", name="Querkraft im äusseren Nachweisschnitt")
        return ergebnis
    A = w.wert("A_out", r"A_{out}", Groesse.aus_si(flaeche, M2), 3,
               "Fläche innerhalb des äusseren Schnitts, ohne Aussparungen")
    p.wert(A, titel="Fläche innerhalb des äusseren Nachweisschnitts, ohne Aussparungen")
    ergebnis = w.kraft("V_d_out", r"V_{d,out}", V_d.groesse.si - q_d.groesse.si * flaeche)
    p.formel(ergebnis, r"@V_d - @q_d \cdot @A_out", {"V_d": V_d, "q_d": q_d, "A_out": A},
             titel="Querkraft im äusseren Nachweisschnitt", referenz="SIA 262:2025, 4.3.6.2.6",
             name="Querkraft im äusseren Nachweisschnitt")
    return ergebnis
