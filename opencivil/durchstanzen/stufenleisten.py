"""
opencivil/durchstanzen/stufenleisten.py -- Leisten an der Stufe eines Bereichs zur Stütze hin.

VERANTWORTUNG:
Hält der Schnitt an der Stufe eines Bereichs zur Stütze hin nicht (Figur
24a, :mod:`.stufen`), schlägt das Werkzeug dort eigene Leisten vor -- einen
Satz je Stufe, neben dem an der Stütze --, mit denselben vier Nachweisen wie
an der Stütze (4.3.6.5.1, :func:`.mit_bewehrung.am_ort`) und je Bereich
eigenen Graden (:func:`grade`). Der Schnitt an der Stufe hat dann kein
eigenes Urteil mehr: wie an der Stütze bleibt sein Grad ohne Bewehrung ein
Wert der Herleitung.

WIE DIE LEISTEN STEHEN (nach Vorgabe, nicht nachgeschlagen -- die Norm regelt
Leisten an einer Stufe nicht im Einzelnen):

- Der Bereich ist ihre gestützte Fläche, mit seiner konvexen Hülle wie der
  Schnitt an der Stufe (Figur 22c). Die Leisten setzen an ihr an wie an
  einer Stütze oder einem Stahlpilz und laufen nach aussen.
- Sie sind so hoch, wie die Platte jenseits der Stufe dick ist, bleiben in
  dem Bereich, der dort liegt, und ausserhalb aller übrigen, je c_nom von
  der Stufe (:class:`.mit_bewehrung.Platz`).
- Es gelten d, d_v, k_e, u, k_r und die Querkraft des Schnitts an der Stufe;
  ψ ist das der Stütze, wie für V_Rd,c an der Stufe.
- k_sys gilt wie an der Stütze: ein Kopf über einer Innenstütze trägt wie
  eine grosse Innenstütze.

WO NICHT:
Auf der Gegenseite (Figur 24c) liegt der Schnitt innerhalb des Bereichs,
und der Schnitt durch verschiedene Dicken (:mod:`.weg`) hat keine Stufe, an
der eine Leiste ansetzen könnte: dort schlägt das Werkzeug keine eigenen
vor (:func:`moeglich`).

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Optional, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.nachweis import NachweisUrteil, grad_def
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef
from opencivil.durchstanzen.bereiche import Plattenbereich, Seite
from opencivil.durchstanzen.mit_bewehrung import Grundlage, Ort, Platz, am_ort
from opencivil.durchstanzen.pruefung import Leistenpruefung
from opencivil.durchstanzen.schnitt import Stuetzenflaeche, kandidaten_stuetze, schatten_am_schnitt
from opencivil.durchstanzen.stufen import Stufe, Stufenwerte

if TYPE_CHECKING:
    from opencivil.durchstanzen.nachweis import Durchstanzen, Stuetzenschnitt, Widerstand

#: Was die Herleitung zu ψ und d in (69) an einer Stufe sagt.
ZU_69 = ("In (69) gilt dasselbe ψ wie für V_Rd,c an der Stufe: die Drehung der Platte um die "
         "Stütze; d ist das an der Stufe – nach Vorgabe, nicht nachgeschlagen.")


def moeglich(bereich: Plattenbereich) -> bool:
    """Ob an der Stufe dieses Bereichs Leisten stehen können: nur zur Stütze hin (Dateikopf)."""
    return bereich.seite is Seite.STUETZE


def grade(basis: str, bereich: Plattenbereich) -> Tuple[WertDef, ...]:
    """
    Die vier Grade mit Leisten an der Stufe von ``bereich``, in der Reihe von
    :data:`.mit_bewehrung.FAELLE`.
    """
    n, wo = bereich.name, f"an der Stufe von {bereich.titel}"
    return tuple(
        grad_def(f"{basis}.stufe.{n}.{schluessel}.erfuellungsgrad", rf"\alpha_{{eff,DS,{z},{n}}}",
                 f"Erfüllungsgrad {was} {wo}", f"SIA 262:2025, {ziffer}; 4.3.6.2.7")
        for schluessel, z, was, ziffer in (
            ("mit", "s", "der Durchstanzbewehrung", "4.3.6.5.2"),
            ("verformung", "v", "Verformungsvermögen", "4.3.6.5.3"),
            ("diagonale", "max", "erste Betondruckdiagonale", "4.3.6.5.8"),
            ("aussen", "out", "ausserhalb der Durchstanzbewehrung", "4.3.6.5.10")))


def nachweisen(n: "Durchstanzen", e: Eingaben, p: Protokoll, w: Zwischenwerte,
               g: "Stuetzenschnitt", r: "Widerstand", st: Stufe, sw: Stufenwerte
               ) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung]]:
    """
    Die Leisten an der Stufe ``st``, deren Schnitt ohne sie nicht hält: ihre
    vier Urteile und die Leisten -- oder, wo keine passt, die Urteile offen
    mit dem Grund. ``sw`` sind die Werte des Schnitts an der Stufe.
    """
    s, f, b = n.stelle, n.stelle.flaeche, st.bereich
    system = s.system.regeln
    p.titel(f"Durchstanzbewehrung an der Stufe von {b.titel}", ebene=3)
    p.erklaerung(
        f"An der Stufe von {b.titel} reicht der Beton allein nicht: dazu kommen "
        f"{system.LEISTEN} ausserhalb des Bereichs. Der Bereich ist ihre gestützte Fläche; sie "
        f"setzen an seiner Stufe an wie an einer Stütze und sind so hoch, wie die Platte "
        f"jenseits dick ist. Es gelten die Werte des Schnitts an der Stufe – nach Vorgabe, nicht "
        f"nachgeschlagen.")
    huelle = b.huelle
    ort = Ort(st.wo, f"{b.name}_", huelle,
              lambda abstand: kandidaten_stuetze(Stuetzenflaeche(huelle), abstand,
                                                 math.inf)[0].stuecke,
              st.pruefung, f.k_sys_erhoeht,
              tuple(schatten_am_schnitt(s.aussparungen, st.pruefung.auswertung.kandidat.stuecke,
                                        d_v=st.d, achse=f.achse(g.masse))),
              n.d_stufenleisten[b.name], ZU_69,
              d_v=sw.d_v, k_e=sw.k_e, u=sw.u, V_d=sw.V, V_Rd_c=sw.V_Rd_c)
    grundlage = Grundlage(innen=st.pruefung, d=sw.d, d_v=sw.d_v, k_e=sw.k_e, k_r=sw.k_r,
                          tau_cd=r.tau_cd, u=sw.u, psi=r.psi, V_d=sw.V, V_Rd_c=sw.V_Rd_c,
                          masse=g.masse, umriss=huelle)
    return am_ort(n, e, p, w, grundlage, _platz(e, g, st), ort)


def _platz(e: Eingaben, g: "Stuetzenschnitt", st: Stufe) -> Platz:
    """
    Wo die Leisten an der Stufe liegen dürfen: in dem, was jenseits liegt, so
    hoch, wie es dick ist, und ausserhalb aller Bereiche, die den Bereich der
    Stufe weder enthalten noch in ihm liegen.
    """
    dicken, b, jenseits = g.dicken, st.bereich, st.jenseits
    fremd = tuple(x for x in dicken.bereiche
                  if x != b and x not in dicken.vorfahren(b) and b not in dicken.vorfahren(x))
    if jenseits is None:
        return Platz(e["h"], (), fremd)
    return Platz(g.bereiche.dicken[jenseits.name], (jenseits,), fremd, dicken.aussen(jenseits))
