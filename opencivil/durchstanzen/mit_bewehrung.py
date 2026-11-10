"""
opencivil/durchstanzen/mit_bewehrung.py -- der Nachweis mit Durchstanzbewehrung und Stahlpilz.

VERANTWORTUNG:
Was der Durchstanznachweis tut, wenn der Beton allein nicht reicht: das
kleinste ancoPLUS suchen (:func:`.bewehrung.bemessen`) und die vier Nachweise
mit ihm schreiben (SIA 262:2025, 4.3.6.5.1) -- Bewehrung (66), (68), (69),
Verformungsvermögen (67), erste Betondruckdiagonale (70) und ausserhalb der
Bewehrung (4.3.6.5.10, Figur 26). Gerechnet wird jede Bedingung einmal, in
:mod:`.pruefung`; die Suche fragt die Prüfung, die Herleitung schreibt
dieselben Zahlen.

Der Stahl der Anker ist der der Biegebewehrung -- ancoPLUS ist aus B500B.
k_sys ist der Faktor aus dem Gutachten des Produkts anstelle der 2 in (70),
wie 4.3.6.5.9 es zulässt (:func:`.produkte.k_sys`).

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
ohne Leisten, sonst mit Leisten um ihn -- dieselben Schritte wie an der
Stütze, mit dem Pilz als gestützter Fläche (4.3.6.6.2). Seine Fläche reicht
bis an die Enden der Stege; die wirksame Höhe reicht von der Zugbewehrung bis
zur Unterkante des Pilzes, d_v = d − 20 mm (gelesen, nicht nachgeschlagen).
Den Widerstand des Pilzes selbst (4.3.6.6.1) bestätigt der Hersteller.

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.nachweis import NachweisUrteil, Vergleich
from opencivil.core.einheiten import MM2, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen import herleitung, produkte
from opencivil.durchstanzen.bewehrung import Vorschlag, bemessen
from opencivil.durchstanzen.herleitung import Index
from opencivil.durchstanzen.produkte import Stahlpilz
from opencivil.durchstanzen.pruefung import (
    Leistenpruefung, Pilzbefund, Schnittpruefung, druckdiagonale, spannung,
)
from opencivil.durchstanzen.schnitt import (
    ECKENBEREICH, Punkt, Schatten, Stueck, Stuetzenflaeche, kandidaten_stuetze, konvexe_huelle,
    nachweisschnitt, schatten_am_schnitt,
)

if TYPE_CHECKING:
    from opencivil.durchstanzen.nachweis import Durchstanzen


@dataclass(frozen=True)
class Grundlage:
    """
    Was der Nachweis ohne Bewehrung schon gerechnet hat -- als Prüfung des
    Schnitts um die Stütze und als die Werte, mit denen seine Herleitung sie
    zeigt.
    """

    innen: Schnittpruefung
    d: Wert
    d_v: Wert
    k_e: Wert
    k_r: Wert
    tau_cd: Wert
    u: Wert
    psi: Wert
    V_d: Wert
    """Die Querkraft im Schnitt um die Stütze, die Flächenlast darin abgezogen."""

    V_Rd_c: Wert
    masse: Dict[str, float]
    umriss: Tuple[Punkt, ...]


@dataclass(frozen=True)
class Ort:
    """
    Wo die Leisten ansetzen: an der Stütze oder um den Stahlpilz (4.3.6.6.2) --
    die gestützte Fläche, der Schnitt um sie und die Werte, mit denen die
    Herleitung ihn zeigt.
    """

    zusatz: str
    """Was hinter dem Namen eines Urteils steht: leer, oder «um den Stahlpilz»."""

    vorsilbe: str
    """Die Vorsilbe der Zwischenwerte, damit Stütze und Pilz nebeneinander stehen können."""

    umriss: Tuple[Punkt, ...]
    r_zu: Callable[[float], Sequence[Stueck]]
    """Der geschlossene Schnitt im Abstand r um die gestützte Fläche."""

    pruefung: Schnittpruefung
    ausnahme: bool
    """Ob der Faktor des Gutachtens erhöht ist -- Innenstütze und Wandende."""

    schatten: Tuple[Schatten, ...]
    """Die Schatten der Aussparungen am Schnitt um diese Fläche: dort liegt keine Leiste."""

    d_v: Optional[Wert] = None
    u: Optional[Wert] = None
    V_d: Optional[Wert] = None
    V_Rd_c: Optional[Wert] = None
    """Wie die Herleitung den Schnitt zeigt -- fehlt nur in der stummen Suche nach dem Pilz."""


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


# ===========================================================================
# Der Nachweis
# ===========================================================================


def nachweisen(n: "Durchstanzen", e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Grundlage
               ) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung], Optional[Pilzbefund]]:
    """
    Die Durchstanzbewehrung suchen und mit ihr nachweisen -- und wo die erste
    Druckdiagonale an einer Innenstütze bricht, einen Stahlpilz. Zurück kommen
    die Urteile, die Leisten und der Pilz, so weit es sie gibt.
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
    f = s.flaeche
    stuetze = Ort("", "", g.umriss, lambda r: f.kandidaten(g.masse, r, g.d_v.groesse.si)[0].stuecke,
                  g.innen, f.k_sys_erhoeht,
                  tuple(schatten_am_schnitt(s.aussparungen, g.innen.auswertung.kandidat.stuecke,
                                            d_v=g.innen.d_v, achse=f.achse(g.masse))),
                  g.d_v, g.u, g.V_d, g.V_Rd_c)
    leisten = _suchen(n, werte, stuetze)
    if leisten is not None:
        urteile = _leisten_schreiben(n, p, w, werte, stuetze, leisten)
        if leisten.diagonale_haelt:
            return urteile, leisten, None
    else:
        p.hinweis("Für diese Platte gibt es kein ancoPLUS: sie ist zu dünn (d < 160 mm), "
                  "keine lieferbare Höhe passt, oder keine Leiste findet Platz.")
        urteile = n.nicht_fuehrbar("Kein ancoPLUS passt in diese Platte.")
    if not f.stahlpilz:
        p.hinweis("Stahlpilze sind im Katalog nur für Innenstützen. Eine grössere Stütze, eine "
                  "dickere Platte oder ein besserer Beton.")
        return urteile, leisten, None
    gewaehlt = _pilz_suchen(n, werte)
    if gewaehlt is None:
        p.hinweis("Auch kein ZEUS-Stahlpilz reicht, der in diese Platte passt. Eine grössere "
                  "Stütze, eine dickere Platte oder ein besserer Beton.")
        return urteile, leisten, None
    return _mit_pilz(n, p, w, werte, *gewaehlt)


def _suchen(n: "Durchstanzen", werte: _Werte, ort: Ort) -> Optional[Leistenpruefung]:
    """Das kleinste ancoPLUS für diesen Ort, mit seiner Prüfung -- siehe :func:`.bewehrung.bemessen`."""
    s, g, e = n.stelle, werte.g, werte.e
    k_sys = produkte.k_sys(werte.c_v, g.d.groesse.si, ort.ausnahme)

    def pruefen(vorschlag: Vorschlag) -> Leistenpruefung:
        return Leistenpruefung(
            vorschlag, ort.pruefung,
            Schnittpruefung(vorschlag.aussen, werte.d_v_out.groesse.si, ort.pruefung.k_e,
                            e.g("V_d").si, e.g("q_d").si),
            k_r=g.k_r.groesse.si, tau_cd=g.tau_cd.groesse.si,
            sigma_sd=spannung(werte.E_s.groesse.si, g.psi.groesse.si, werte.f_ctm.groesse.si,
                              werte.f_yd.groesse.si, g.d.groesse.si, vorschlag.typ.durchmesser),
            f_yd=werte.f_yd.groesse.si, k_sys=k_sys)

    return bemessen(
        d=g.d.groesse.si, d_v=ort.pruefung.d_v, d_v_out=werte.d_v_out.groesse.si,
        h_A=werte.h_A.groesse.si, r_2_zu=ort.r_zu, umriss=ort.umriss,
        raender=s.flaeche.raender(g.masse), aussparungen=s.aussparungen, schatten=ort.schatten,
        achse=s.flaeche.achse(g.masse),
        ueberdeckung=e.g("c").si, pruefen=pruefen)


def _leisten_schreiben(n: "Durchstanzen", p: Protokoll, w: Zwischenwerte, werte: _Werte, ort: Ort,
                       pruefung: Leistenpruefung) -> List[NachweisUrteil]:
    """Die vier Nachweise mit diesen Leisten, wie die Prüfung sie gerechnet hat."""
    e, g, k = werte.e, werte.g, ort.vorsilbe
    vorschlag = pruefung.vorschlag
    typ = vorschlag.typ
    p.erklaerung(
        f"Vorgeschlagen wird ancoPLUS von AncoTech{ort.zusatz and ' ' + ort.zusatz}: "
        f"{vorschlag.name} -- Anker ⌀{typ.durchmesser * 1e3:.0f} mit h_A = "
        f"{werte.h_A.formatiert()} mm, vom Rand der gestützten Fläche "
        f"{' / '.join(f'{a * 1e3:.0f}' for a in vorschlag.abstaende)} mm. Die Abstände sind die "
        f"der Typen «D» nach dem Gutachten des Herstellers: 0.375·d zum ersten Anker, bis zum "
        f"dritten 0.60·d, danach 0.75·d; zwei Leisten stehen beim zweiten Anker höchstens "
        f"1.5·d auseinander ({produkte.QUELLE_ANCOPLUS}, nach Vorgabe, nicht nachgeschlagen).")
    if ort.schatten or len(vorschlag.gruppen) > 1:
        p.erklaerung(
            "Keine Leiste läuft über den Plattenrand oder durch eine Aussparung, auch nicht "
            "zwischen zwei Ankern; zu beiden hält sie die Überdeckung c_nom, sonst endet sie mit "
            "dem Anker davor. Im Schatten einer Aussparung zählt der Nachweisschnitt nicht "
            "(Figur 23d) -- dort liegt auch keine Leiste: Bewehrung, die diesen Teil quert, "
            "trüge nichts zur gestützten Fläche.")
    if not pruefung.reicht:
        p.hinweis("Kein ancoPLUS erfüllt alle Bedingungen; gerechnet ist der stärkste Versuch.")

    # -- Bewehrung (66), (68), (69) ---------------------------------------
    phi = w.laenge(f"{k}phi_sw", r"\varnothing_{sw}", typ.durchmesser, stellen=0)
    sigma = w.wert(f"{k}sigma_sd", r"\sigma_{sd}", Groesse.aus_si(pruefung.sigma_sd, N_PRO_MM2), 0,
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
    A_sw = w.wert(f"{k}A_sw", r"\sum A_{sw}", Groesse.aus_si(pruefung.A_sw, MM2), 0,
                  "Anrechenbare Durchstanzbewehrung")
    p.formel(A_sw, r"@n_L \cdot @n_A \cdot \frac{\pi \cdot @phi^{2}}{4}",
             {"n_L": leisten, "n_A": im_bereich, "phi": phi},
             titel="Anrechenbare Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4",
             name="Anrechenbare Durchstanzbewehrung")
    V_Rd_s = w.kraft(f"{k}V_Rd_s", r"V_{Rd,s}", pruefung.V_Rd_s, "Beitrag der Durchstanzbewehrung")
    p.formel(V_Rd_s, r"@A_sw \cdot @k_e \cdot @sigma_sd", {"A_sw": A_sw, "k_e": g.k_e, "sigma_sd": sigma},
             titel="Beitrag der Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.4, (68)",
             name="Beitrag der Durchstanzbewehrung")
    V_d_s = w.kraft(f"{k}V_d_s", r"V_{d,s}", pruefung.V_d_s)
    p.formel(V_d_s, r"@V_d - @V_Rd_c", {"V_d": ort.V_d, "V_Rd_c": ort.V_Rd_c},
             titel="Querkraft für die Durchstanzbewehrung", referenz="SIA 262:2025, 4.3.6.5.2, (66)",
             name="Querkraft für die Durchstanzbewehrung")
    v_s = Vergleich(V_d_s, V_Rd_s)
    v_s.bedingung(p, "Querkraft für die Bewehrung gegen ihren Beitrag")
    v_s.zeile(p, n.d_mit, mit_urteil=True)

    # -- Verformungsvermögen (67) ------------------------------------------
    V_halb = w.kraft(f"{k}V_d_halb", r"V_d / 2", pruefung.V_halb)
    p.formel(V_halb, r"\frac{@V_d}{2}", {"V_d": ort.V_d}, titel="Die halbe Querkraft",
             referenz="SIA 262:2025, 4.3.6.5.3, (67)", name="Halbe Querkraft für das Verformungsvermögen")
    V_Rd_v = w.kraft(f"{k}V_Rd_v", r"V_{Rd,v}", pruefung.V_Rd_v)
    p.formel(V_Rd_v, r"@A_sw \cdot @k_e \cdot @f_yd", {"A_sw": A_sw, "k_e": g.k_e, "f_yd": werte.f_yd},
             titel="Durchstanzbewehrung an der Fliessgrenze", referenz="SIA 262:2025, 4.3.6.5.3, (67)",
             name="Durchstanzbewehrung an der Fliessgrenze")
    v_v = Vergleich(V_halb, V_Rd_v)
    v_v.bedingung(p, "Verformungsvermögen: die halbe Querkraft gegen die fliessende Bewehrung")
    v_v.zeile(p, n.d_verformung, mit_urteil=True)

    # -- Betondruckdiagonale (70) ------------------------------------------
    d = g.d.groesse.si
    k_sys = w.zahl(f"{k}k_sys", r"k_{sys}", pruefung.k_sys, stellen=2)
    p.erklaerung(
        "Die Faktoren 2 und 3.5 in Gleichung (70) dürfen erhöht werden, wenn Versuche es "
        "belegen (4.3.6.5.9). Das Gutachten von ancoPLUS lässt für Innenstützen und Wandenden "
        "3·k_r zu, wenn die Köpfe auf der Druckseite höchstens d/10 tief liegen; bei d/6 gilt "
        "wieder 2·k_r, dazwischen linear. Für Rand- und Eckstützen bleibt es bei 2·k_r. Die "
        "Obergrenze bleibt 3.5.")
    p.wert(k_sys, titel=f"Faktor des Produkts: c_v = {werte.c_v * 1e3:.0f} mm, d/10 = {d * 1e2:.0f} mm, "
                        f"d/6 = {d * 1e3 / 6:.0f} mm")
    V_Rd_max = w.kraft(f"{k}V_Rd_max", r"V_{Rd,max}", pruefung.V_Rd_max,
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
    aussen = pruefung.aussen
    ix = Index("out", k)
    p.titel(f"Ausserhalb der Durchstanzbewehrung{ort.zusatz and ' ' + ort.zusatz}", ebene=3)
    p.formel(werte.d_v_out, "@d - @c_v", {"d": g.d, "c_v": e["c_v"]},
             titel="Wirksame statische Höhe bis zu den Köpfen der Anker",
             referenz="SIA 262:2025, 4.3.6.5.10, Figur 26",
             name="Wirksame statische Höhe im äusseren Nachweisschnitt")
    p.erklaerung("Der äussere Schnitt läuft im Abstand 0.5·d_v,out um die äussersten Anker.")
    u_0 = herleitung.rand(p, w, aussen.auswertung, ix=ix,
                          titel="Äusserer Nachweisschnitt, soweit er in der Platte liegt",
                          referenz="SIA 262:2025, 4.3.6.5.10, Figur 26")
    u_red = herleitung.abzuege(
        p, w, aussen.auswertung, u_0, ix=ix,
        ecken_text="Von einer Geraden zwischen zwei äussersten Ankern zählen höchstens "
                   "1.5·d_v,out von jedem Ende (Figur 26).",
        ecken_referenz="SIA 262:2025, 4.3.6.5.10, Figur 26")
    u = herleitung.wirksam(p, w, g.k_e, u_red, ix=ix,
                           titel="Wirksamer Umfang des äusseren Nachweisschnitts, mit k_e von innen")
    V_d_out = herleitung.querkraft(
        p, w, e, aussen, ix=ix,
        titel_last=f"{n.stelle.plattenart.last} innerhalb des äusseren Schnitts",
        titel="Querkraft im äusseren Nachweisschnitt")
    V_Rd_out = herleitung.widerstand(
        p, w, aussen, ix=ix, k_r=g.k_r, tau_cd=g.tau_cd, d_v=werte.d_v_out, u=u,
        titel="Durchstanzwiderstand im äusseren Nachweisschnitt",
        referenz="SIA 262:2025, 4.3.6.5.10, (58)")
    v_a = Vergleich(V_d_out, V_Rd_out)
    v_a.bedingung(p, "Querkraft gegen den Widerstand ausserhalb der Bewehrung")
    v_a.zeile(p, n.d_aussen, mit_urteil=True)

    z = f" {ort.zusatz}" if ort.zusatz else ""
    return [
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


# ===========================================================================
# Der Stahlpilz
# ===========================================================================


def _pilz_pruefen(n: "Durchstanzen", werte: _Werte, pilz: Stahlpilz) -> Pilzbefund:
    """Die gestützte Fläche des Pilzes und der Schnitt im Abstand d_v/2 um sie, geprüft ohne Leisten."""
    s, g, e = n.stelle, werte.g, werte.e
    umriss = tuple(konvexe_huelle(list(g.umriss) + list(pilz.armenden())))
    d_v = g.d.groesse.si - produkte.PILZ_UNTEN
    schnitt = nachweisschnitt(
        kandidaten_stuetze(Stuetzenflaeche(umriss), d_v / 2.0, ECKENBEREICH * d_v,
                           s.flaeche.raender(g.masse)),
        d_v=d_v, achse=s.flaeche.achse(g.masse), aussparungen=s.aussparungen)
    pruefung = Schnittpruefung(schnitt, d_v, g.k_e.groesse.si, e.g("V_d").si, e.g("q_d").si)
    return Pilzbefund(pilz, umriss, pruefung,
                      pruefung.V_Rd_c(g.k_r.groesse.si, g.tau_cd.groesse.si))


def _pilzort(n: "Durchstanzen", werte: _Werte, befund: Pilzbefund, d_v: Optional[Wert] = None,
             u: Optional[Wert] = None, V_d: Optional[Wert] = None,
             V_Rd_c: Optional[Wert] = None) -> Ort:
    """Der Pilz als Ort der Leisten: seine Fläche, der Schnitt um ihn und dessen Schatten."""
    s = n.stelle
    huelle = befund.umriss
    return Ort("um den Stahlpilz", "P_", huelle,
               lambda r: kandidaten_stuetze(Stuetzenflaeche(huelle), r, math.inf)[0].stuecke,
               befund.pruefung, True,
               tuple(schatten_am_schnitt(s.aussparungen, befund.pruefung.auswertung.kandidat.stuecke,
                                         d_v=befund.pruefung.d_v,
                                         achse=s.flaeche.achse(werte.g.masse))),
               d_v, u, V_d, V_Rd_c)


def _pilz_suchen(n: "Durchstanzen", werte: _Werte
                 ) -> Optional[Tuple[Pilzbefund, Optional[Leistenpruefung]]]:
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
    for pilz in produkte.STAHLPILZE:
        if pilz.h > hoehe + 1e-9 or pilz.s / 2.0 < weite + produkte.PILZ_UEBERSTAND - 1e-9:
            continue
        huelle = konvexe_huelle(list(g.umriss) + list(pilz.armenden()))
        rand = sum(math.dist(huelle[i - 1], huelle[i]) for i in range(len(huelle)))
        flaeche = (abs(sum(huelle[i - 1][0] * huelle[i][1] - huelle[i][0] * huelle[i - 1][1]
                           for i in range(len(huelle)))) / 2.0
                   + rand * d_v / 2.0 + math.pi * d_v ** 2 / 4.0)
        if (druckdiagonale(k_sys, k_r, tau, d_v, k_e * (rand + math.pi * d_v))
                < e.g("V_d").si - e.g("q_d").si * flaeche):
            continue
        befund = _pilz_pruefen(n, werte, pilz)
        if befund.reicht:
            return befund, None
        if befund.pruefung.V_Rd_max(k_sys, k_r, tau) < befund.pruefung.V_d_red:
            continue
        leisten = _suchen(n, werte, _pilzort(n, werte, befund))
        if leisten is not None and leisten.reicht and leisten.diagonale_haelt:
            return befund, leisten
    return None


def _mit_pilz(n: "Durchstanzen", p: Protokoll, w: Zwischenwerte, werte: _Werte,
              befund: Pilzbefund, leisten: Optional[Leistenpruefung]
              ) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung], Pilzbefund]:
    """
    Die Herleitung mit dem gewählten Pilz: der Schnitt um ihn mit denselben
    Schritten wie um die Stütze, ohne Leisten oder mit Leisten um ihn.
    """
    e, g = werte.e, werte.g
    pilz = befund.pilz
    ix = Index("P")
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
    d_v = w.laenge(ix.name("d_v"), r"d_{v,P}", befund.pruefung.d_v)
    p.formel(d_v, "@d - @c_P", {"d": g.d, "c_P": c_P},
             titel="Wirksame statische Höhe bis zur Unterkante des Pilzes",
             referenz="SIA 262:2025, 4.3.6.6.2", name="Wirksame statische Höhe um den Stahlpilz")
    a = befund.pruefung.auswertung
    u_0 = herleitung.rand(p, w, a, ix=ix, titel="Schnitt um den Stahlpilz, soweit er in der Platte liegt",
                          referenz="SIA 262:2025, 4.3.6.6.2")
    u_red = herleitung.abzuege(
        p, w, a, u_0, ix=ix,
        ecken_text="Die Enden der Stege sind Ecken der gestützten Fläche: von einer Geraden "
                   "zwischen ihnen zählt nur, was höchstens 1.5·d_v von einem Ende entfernt liegt.",
        ecken_referenz="SIA 262:2025, 4.3.6.2.3, Figur 23a")
    u = herleitung.wirksam(p, w, g.k_e, u_red, ix=ix,
                           titel="Wirksamer Umfang des Schnitts um den Stahlpilz, mit k_e von innen")
    V_d = herleitung.querkraft(
        p, w, e, befund.pruefung, ix=ix,
        titel_last=f"{n.stelle.plattenart.last} innerhalb des Schnitts um den Stahlpilz",
        titel="Querkraft im Schnitt um den Stahlpilz")
    V_Rd_c = herleitung.widerstand(
        p, w, befund.pruefung, ix=ix, k_r=g.k_r, tau_cd=g.tau_cd, d_v=d_v, u=u,
        titel="Durchstanzwiderstand um den Stahlpilz, ohne Bewehrung",
        referenz="SIA 262:2025, 4.3.6.6.2")
    v = Vergleich(V_d, V_Rd_c)
    v.bedingung(p, "Querkraft gegen den Widerstand um den Stahlpilz")
    if leisten is None:
        v.zeile(p, n.d_aussen, mit_urteil=True)
        return [n.urteil(n.d_aussen, "ausserhalb des Stahlpilzes", v,
                         f"{pilz.name}: V_d,P = {V_d.formatiert()} kN ≤ "
                         f"V_Rd,c,P = {V_Rd_c.formatiert()} kN.")], None, befund
    p.erklaerung("Um den Pilz reicht der Beton allein nicht: dazu kommen Leisten, bündig an "
                 "den Pilz, mit den vier Nachweisen der Durchstanzbewehrung.")
    ort = _pilzort(n, werte, befund, d_v, u, V_d, V_Rd_c)
    return _leisten_schreiben(n, p, w, werte, ort, leisten), leisten, befund
