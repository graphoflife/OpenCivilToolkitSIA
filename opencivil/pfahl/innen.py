"""
opencivil/pfahl/innen.py -- der innere Widerstand eines Pfahls: sein Querschnitt.

VERANTWORTUNG:
Der Nachweis :class:`InnererWiderstand`: je Kombination die Normalkraft am
Kopf gegen den Bemessungswert des inneren Widerstands, auf Druck oder auf
Zug (SIA 267:2013, 9.5.2.4)::

    R_i,d = η_i · R_mat,d     (50)    η_i ≤ 0.8 in der Regel (51), bis 0.9 mit
                                      Prüfung der Integrität (9.5.2.4.9)

R_mat,d ist der Widerstand des Querschnitts nach SIA 262, gleichmässig
gestaucht oder gedehnt -- der Bruchzustand derselben Interaktion, mit der
die Querschnittsanalyse rechnet
(:meth:`~opencivil.querschnitt.interaktion.Querschnitt.reine_normalkraft`),
mit denselben Werkstoffen (:func:`~opencivil.querschnitt.analyse.werkstoff`).
Ganz gedrückt endet der Beton dort bei −ε_c1d, und der Stahl mit ihm.

DER QUERSCHNITT (:func:`querschnitt`):
* Bohrpfahl -- ein Kreis aus Beton mit dem Durchmesser D, darin n Längsstäbe
  auf dem Kreis, den Überdeckung und Wendel frei lassen.
* Mikropfahl -- nur das Tragglied aus Stahl, um die Abrostung aussen
  verkleinert: ein Rohr oder ein Vollstab.
Kreise sind Vielecke derselben Fläche (:func:`kreis`).

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* Der Mörtel im Rohr des Mikropfahls zählt nicht, obwohl 9.5.2.4.8 den vom
  Stahl umschlossenen Beton zuliesse: nach SIA 262 gerechnet, endete mit ihm
  das Ganze bei −ε_c1d, und das Rohr flösse nicht mehr.
* Das Tragglied rechnet als Stahl der Liste nach SIA 262, mit dessen γ_s;
  SIA 263 liegt nicht vor.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import MM
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.pfahl.achse import Achsnachweis
from opencivil.pfahl.pfahl import ETA_I_REGEL, Kombination, Pfahl, Tragglied
from opencivil.querschnitt.analyse import KENNWERTE, gesetz_protokollieren, werkstoff
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl
from opencivil.querschnitt.interaktion import Bewehrung, Querschnitt, Teil, Werkstoff
from opencivil.querschnitt.vorlagen import KREISECKEN, kreispunkte

#: Womit der Querschnitt rechnet: Bemessungswerte, der Beton als Parabel.
WAHL = Rechenwahl(art=Rechenart.PARABEL)

Punkt = Tuple[float, float]


def kreis(durchmesser: float) -> Tuple[Punkt, ...]:
    """
    Ein Kreis um den Ursprung als Vieleck derselben Fläche, in m: die Ecken
    liegen etwas ausserhalb des Kreises, damit A = π · d²/4 genau bleibt.
    """
    m = KREISECKEN
    r = durchmesser / 2.0 * math.sqrt(2.0 * math.pi / (m * math.sin(2.0 * math.pi / m)))
    # In mm gebaut: kreispunkte rundet auf Tausendstel.
    return tuple((y * MM.faktor, z * MM.faktor)
                 for y, z in kreispunkte((0.0, 0.0), r / MM.faktor))


@dataclass(frozen=True)
class Masse:
    """Was der Querschnitt aus den Eingaben braucht, in m -- je Pfahlart ein Teil davon."""

    D: float = 0.0
    """Bohrpfahl: Durchmesser des Betons."""

    r_s: float = 0.0
    """Bohrpfahl: Radius des Kreises, auf dem die Längsstäbe liegen."""

    n: int = 0
    phi_l: float = 0.0
    d_aussen: float = 0.0
    """Mikropfahl: Aussendurchmesser des Tragglieds nach der Abrostung."""

    d_innen: float = 0.0
    """Mikropfahl: Innendurchmesser des Rohrs -- null beim Vollstab."""


def querschnitt(masse: Masse, werkstoffe: Sequence[Werkstoff]) -> Querschnitt:
    """
    Der Querschnitt der Interaktion, um die Achse des Pfahls: mit Beton als
    erstem Werkstoff und Stahl als zweitem der Bohrpfahl, sonst nur Stahl.
    """
    if len(werkstoffe) == 2:
        bewehrung = [Bewehrung(lage=(masse.r_s * math.cos(2.0 * math.pi * k / masse.n),
                                     masse.r_s * math.sin(2.0 * math.pi * k / masse.n)),
                               flaeche=math.pi * masse.phi_l ** 2 / 4.0, werkstoff=1,
                               verdraengt=0)
                     for k in range(masse.n)]
        return Querschnitt(werkstoffe=werkstoffe,
                           teile=[Teil(kreis(masse.D), werkstoff=0, eltern=None)],
                           bewehrung=bewehrung, bezug=(0.0, 0.0))
    teile = [Teil(kreis(masse.d_aussen), werkstoff=0, eltern=None)]
    if masse.d_innen > 0.0:
        teile.append(Teil(kreis(masse.d_innen), werkstoff=None, eltern=0))
    return Querschnitt(werkstoffe=werkstoffe, teile=teile, bewehrung=[], bezug=(0.0, 0.0))


def biegewiderstand(q: Querschnitt, N: float, eta_i: float, staebe: int = 0) -> float:
    """
    Das Moment, das der Pfahl bei der Normalkraft N trägt, Druck positiv:
    η_i · M_R(N / η_i) -- die Fläche der Widerstände um η_i verkleinert, wie
    (50) den Widerstand. Von ``staebe`` Stäben gilt die Lage, die dem Moment
    weniger nützt: ein Stab im gezogenen Rand oder zwei beidseits davon.
    Null, wo N allein schon mehr ist, als der Querschnitt trägt.
    """
    momente = []
    for drehung in ((0.0, math.pi / staebe) if staebe else (0.0,)):
        punkt = q.bei_normalkraft(-math.pi / 2.0 + drehung, -N / eta_i)
        if punkt is None:
            return 0.0
        momente.append(punkt.moment)
    return eta_i * min(momente)


@dataclass
class Innenbefund:
    """Was ausser den Erfüllungsgraden bleibt -- für Zusammenfassung und Bild, in SI."""

    masse: Masse
    A_s: float
    R_mat: float
    R_mat_zug: float
    R_id: float
    R_id_zug: float


class InnererWiderstand(Achsnachweis):
    """Siehe Dateikopf."""

    THEMA = "Innerer Pfahlwiderstand"
    ART = "R_i"
    INDEX = "i"
    TITEL = "Innerer Widerstand"
    WORT = "innerer Widerstand"

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination]) -> None:
        namen = pfahl.kurznamen("Querschnitt") + (["D"] if pfahl.bohrpfahl else [])
        super().__init__(pfahl, kombinationen, basis=f"{pfahl.id}.nachweis.innen",
                         bezuege=[Eingabebezug(n, pfahl.id_von(n)) for n in namen]
                         + [s.bezug(k) for s in pfahl.stoffe for k in KENNWERTE[s.art]])

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        f = self.pfahl
        p.titel("Innerer Widerstand")
        p.erklaerung(
            "Der Pfahl selbst muss die Kraft tragen, die er an den Boden abgibt. Sein "
            "Querschnitt trägt sie nach SIA 262: ganz gestaucht oder ganz gedehnt, "
            "jeder Werkstoff mit seinem Gesetz und bis zu seiner Grenze. Ganz "
            "gedrückt darf der Beton nur bis −ε_c1d gestaucht werden, und der Stahl "
            "darin nicht weiter. Der Umrechnungsfaktor η_i deckt, was die "
            "Herstellung im Boden dem Querschnitt antun kann, ohne dass man es "
            "sieht: Fehlstellen im Beton, verschobene Bewehrung.")
        p.text("Einzugeben ist der kleinste Querschnitt längs des Pfahls "
               "(SIA 267:2013, 9.5.2.4.5).")
        werte = Zwischenwerte(self.id)
        p.titel("Querschnitt", ebene=3)
        masse, A_s, A_c = (self._bohrpfahl(e, p, werte) if f.bohrpfahl
                           else self._mikropfahl(e, p, werte))
        werkstoffe = [werkstoff(s, e.si_nach_id(), WAHL) for s in f.stoffe]
        for s, w in zip(f.stoffe, werkstoffe):
            gesetz_protokollieren(p, e, s, w.gesetz, WAHL, self.id)
        q = querschnitt(masse, werkstoffe)
        R_mat = self._normalkraft(p, werte, q, werkstoffe, A_s, A_c, zug=False)
        R_mat_zug = self._normalkraft(p, werte, q, werkstoffe, A_s, A_c, zug=True)
        p.titel("Bemessungswert", ebene=3)
        if e.g("eta_i").si > ETA_I_REGEL:
            p.hinweis(f"η_i über {ETA_I_REGEL:g} setzt eine verlässliche Prüfung der Integrität "
                      f"des ganzen Pfahls voraus (SIA 267:2013, 9.5.2.4.9).")
        R_id = self._bemessung(e, p, werte, R_mat, zug=False)
        R_id_zug = self._bemessung(e, p, werte, R_mat_zug, zug=True)
        p.hinweis("Knicken ist nicht nachgewiesen. Ein schlanker Pfahl, der seitlich nicht "
                  "oder nur schwach gebettet ist -- in sehr weichem Boden, frei über dem "
                  "Terrain --, kann knicken (SIA 267:2013, 9.5.1.1).")
        befund = Innenbefund(masse, A_s.groesse.si, R_mat.groesse.si, R_mat_zug.groesse.si,
                             R_id.groesse.si, R_id_zug.groesse.si)
        return Ausfuehrung({}, self.faelle(p, R_id, R_id_zug), befund)

    # -- Querschnitt ----------------------------------------------------------

    def _bohrpfahl(self, e: Eingaben, p: Protokoll,
                   werte: Zwischenwerte) -> Tuple[Masse, Wert, Optional[Wert]]:
        D, n, phi_l, c, phi_w = e["D"], e["n"], e["phi_l"], e["c"], e["phi_w"]
        A_c = werte.flaeche("A_c", "A_c", math.pi * D.groesse.si ** 2 / 4.0,
                            "Fläche des Pfahlquerschnitts")
        p.formel(A_c, r"\frac{\pi \cdot @D^{2}}{4}", {"D": D}, titel="Fläche des Pfahlquerschnitts",
                 referenz="SIA 267:2013, 9.5.2.4.7", name="Fläche des Pfahlquerschnitts")
        zahl = round(n.groesse.si)
        A_s = werte.flaeche("A_s", "A_s", zahl * math.pi * phi_l.groesse.si ** 2 / 4.0,
                            "Fläche der Längsbewehrung")
        p.formel(A_s, r"@n \cdot \frac{\pi \cdot @phi^{2}}{4}", {"n": n, "phi": phi_l},
                 titel="Fläche der Längsbewehrung", referenz="",
                 name="Fläche der Längsbewehrung")
        r_s = werte.laenge("r_s", "r_s", D.groesse.si / 2.0 - c.groesse.si - phi_w.groesse.si
                           - phi_l.groesse.si / 2.0, "Radius des Bewehrungskreises")
        p.formel(r_s, r"\frac{@D}{2} - @c - @phi_w - \frac{@phi_l}{2}",
                 {"D": D, "c": c, "phi_w": phi_w, "phi_l": phi_l},
                 titel="Radius des Kreises, auf dem die Längsstäbe liegen", referenz="",
                 name="Radius des Bewehrungskreises")
        p.text(f"Die {zahl} Stäbe liegen gleichmässig auf diesem Kreis; sie verdrängen den "
               f"Beton, in dem sie liegen.")
        masse = Masse(D=D.groesse.si, r_s=r_s.groesse.si, n=zahl, phi_l=phi_l.groesse.si)
        return masse, A_s, A_c

    def _mikropfahl(self, e: Eingaben, p: Protokoll,
                    werte: Zwischenwerte) -> Tuple[Masse, Wert, Optional[Wert]]:
        d_a, dt = e["d_a"], e["dt"]
        d_aussen = d_a.groesse.si - 2.0 * dt.groesse.si
        p.text("Es trägt nur das Tragglied aus Stahl, aussen um die Abrostung Δt "
               "verkleinert (SIA 267:2013, 9.5.2.4.8; 9.6.1.5.2).")
        if self.pfahl.tragglied is Tragglied.ROHR:
            t = e["t_r"]
            d_innen = d_a.groesse.si - 2.0 * t.groesse.si
            A_s = werte.flaeche("A_s", "A_s", math.pi * (d_aussen ** 2 - d_innen ** 2) / 4.0,
                                "Fläche des Tragrohrs")
            p.formel(A_s, r"\frac{\pi \cdot \left(\left(@d_a - 2 \cdot @dt\right)^{2}"
                          r" - \left(@d_a - 2 \cdot @t\right)^{2}\right)}{4}",
                     {"d_a": d_a, "dt": dt, "t": t}, titel="Fläche des Tragrohrs nach der Abrostung",
                     referenz="SIA 267:2013, 9.6.1.5.2", name="Fläche des Tragrohrs nach Abrostung")
            p.annahme("Der Mörtel im Rohr zählt nicht -- nach Vorgabe, nicht nachgeschlagen. "
                      "SIA 267:2013, 9.5.2.4.8, liesse ihn zu; nach SIA 262 gerechnet, endete "
                      "mit ihm aber das Ganze bei −ε_c1d, und das Rohr flösse nicht mehr.")
        else:
            d_innen = 0.0
            A_s = werte.flaeche("A_s", "A_s", math.pi * d_aussen ** 2 / 4.0,
                                "Fläche des Tragstabs")
            p.formel(A_s, r"\frac{\pi \cdot \left(@d - 2 \cdot @dt\right)^{2}}{4}",
                     {"d": d_a, "dt": dt}, titel="Fläche des Tragstabs nach der Abrostung",
                     referenz="SIA 267:2013, 9.6.1.5.2", name="Fläche des Tragstabs nach Abrostung")
        p.annahme("Das Tragglied rechnet als Stahl nach SIA 262, mit dessen γ_s -- nach "
                  "Vorgabe, nicht nachgeschlagen; SIA 263 für Baustahl liegt nicht vor.")
        return Masse(d_aussen=d_aussen, d_innen=d_innen), A_s, None

    # -- Normalkraft ----------------------------------------------------------

    def _normalkraft(self, p: Protokoll, werte: Zwischenwerte, q: Querschnitt,
                     werkstoffe: Sequence[Werkstoff], A_s: Wert, A_c: Optional[Wert], *,
                     zug: bool) -> Wert:
        """
        R_mat,d in einer Richtung: die Dehnung aus der Interaktion, die
        Spannungen aus den Gesetzen, die Kraft als Summe -- Druck und Zug
        als Beträge.
        """
        was = "Zug" if zug else "Druck"
        z = "_zug" if zug else ""
        p.titel(f"Materialwiderstand auf {was}", ebene=3)
        punkt = q.reine_normalkraft(zug)
        eps = werte.dehnung(f"eps{z}", r"\varepsilon", punkt.eps_m,
                            f"Dehnung im Bruchzustand auf {was}")
        p.wert(eps, titel=f"Dehnung im Bruchzustand auf {was}, über den Querschnitt gleich",
               referenz="")
        stahl = werkstoffe[-1]
        sigma_s = werte.spannung(f"sigma_s{z}", r"\sigma_s", abs(stahl.gesetz(punkt.eps_m)),
                                 f"Spannung im Stahl auf {was}, als Betrag")
        p.wert(sigma_s, referenz="")
        R = werte.kraft(f"R_mat{z}", "R_{mat,d,Z}" if zug else "R_{mat,d}", abs(punkt.N),
                        f"Materialwiderstand auf {was}", stellen=0)
        if A_c is not None and not zug:
            sigma_c = werte.spannung("sigma_c", r"\sigma_c",
                                     abs(werkstoffe[0].gesetz(punkt.eps_m)),
                                     "Spannung im Beton auf Druck, als Betrag", stellen=1)
            p.wert(sigma_c, referenz="")
            p.formel(R, r"\left(@A_c - @A_s\right) \cdot @sigma_c + @A_s \cdot @sigma_s",
                     {"A_c": A_c, "A_s": A_s, "sigma_c": sigma_c, "sigma_s": sigma_s},
                     titel="Materialwiderstand auf Druck: Beton ohne die Stäbe, dazu die Stäbe",
                     referenz="SIA 267:2013, 9.5.2.4.2", name="Materialwiderstand auf Druck")
        else:
            if A_c is not None:
                p.text("Auf Zug trägt der Beton nichts.")
            p.formel(R, r"@A_s \cdot @sigma_s", {"A_s": A_s, "sigma_s": sigma_s},
                     titel=f"Materialwiderstand auf {was}: nur der Stahl",
                     referenz="SIA 267:2013, 9.5.2.4.2", name="Materialwiderstand des Stahls")
        return R

    def _bemessung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, R_mat: Wert, *,
                   zug: bool) -> Wert:
        """R_i,d = η_i · R_mat,d (50)."""
        was = "Zug" if zug else "Druck"
        R_id = werte.kraft("R_id_zug" if zug else "R_id", "R_{i,d,Z}" if zug else "R_{i,d}",
                           e.g("eta_i").si * R_mat.groesse.si,
                           f"Innerer Widerstand auf {was}", stellen=0)
        p.formel(R_id, r"@eta \cdot @R", {"eta": e["eta_i"], "R": R_mat},
                 titel=f"Innerer Widerstand auf {was}, Bemessungswert",
                 referenz="SIA 267:2013, 9.5.2.4.1, (50)", name="Innerer Widerstand des Pfahls")
        return R_id
