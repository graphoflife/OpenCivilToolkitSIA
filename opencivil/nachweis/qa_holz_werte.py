"""
opencivil/nachweis/qa_holz_werte.py -- die Werte eines Holzquerschnitts, einmal fuer alle Nachweise.

VERANTWORTUNG:
:class:`HolzwerteQA` rechnet, was Kennzahlen
(:mod:`opencivil.nachweis.qa_holz_kennzahlen`), Nachweise je Lastfall
(:mod:`opencivil.nachweis.qa_holz`) und Stab
(:mod:`opencivil.nachweis.qa_holz_stabilitaet`) lesen, und schreibt es
einmal in die Herleitung:

* den Beiwert η_w der Feuchteklasse (SIA 265:2012, Tabelle 4);
* je Achse das Widerstandsmoment bis zur weitesten Faser, beim
  Brettschichtholz den Hoehenbeiwert k_h (3.4.2.3);
* je Richtung einer Querkraft die Schubflaeche ``A_V = I·b/S`` nach
  Jourawski;
* beim Rechteck das Torsionswiderstandsmoment ``W_T``.

Dazu, was die drei sonst teilen: die Kennwerte des Holzes als Eingaben
(:func:`stoffbezuege`) und der Beiwert eines Falls, ``η = η_w·η_t``
(:func:`beiwert`).

EIN HOLZ:
Gerechnet wird ein Querschnitt aus einem einzigen Holz. Aus mehreren
Hoelzern -- etwa C24 neben GL24h -- verteilten sich die Spannungen nach
ihren Moduln; das rechnet das Werkzeug noch nicht, und die Analyse sagt es
grau (:func:`~opencivil.projekt.aufbau.querschnittsanalyse.ohne_nachweise`).

LAMELLEN:
Brettschichtholz hat seine Lamellen parallel zu y, nach Vorgabe, nicht
nachgeschlagen: ``k_h`` gilt fuer die Biegung um y, mit der Hoehe in z. Um z
gilt es nicht (3.4.2.2), und ``k_sys`` (5.7.2.2) nimmt das Werkzeug nicht.
"""

from __future__ import annotations

from typing import Dict, List

from opencivil.core.berechnung import Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import CM3, EINHEITSLOS, MM2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.holzbau import gleichungen as gl
from opencivil.holzbau.querschnitt import Holzquerschnitt, k_2
from opencivil.material.basis import Baustoff
from opencivil.material.holz import (
    HOLZSORTEN, REFERENZ_ETA, REFERENZ_ETA_T, TABELLE_4, Feuchteklasse, Holzart, eta_t,
)
from opencivil.nachweis.qa_stahl_werte import WIDERSTANDSMOMENT
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.stabwerk.stabquerschnitt import keine_hauptachsen

#: Was die Nachweise je Holz lesen -- die Bemessungswerte der Tabellen 6 und 7.
KENNWERTE = ("f_m_d", "f_t_0_d", "f_c_0_d", "f_v_d")

#: Was der Stab dazu liest -- Anhang B und die Biegefestigkeit.
KENNWERTE_STAB = ("f_m_k", "f_c_0_k", "E_0_05")

#: Warum Torsion nur beim Rechteck nachgewiesen wird -- siehe :mod:`opencivil.holzbau.querschnitt`.
TORSION_NUR_RECHTECK = ("Torsion weist das Werkzeug beim Holz nur für ein Rechteck nach, die "
                        "Seiten parallel zu y und z: für einen anderen Querschnitt gibt es keine "
                        "Formel für τ_tor (nach Vorgabe, nicht nachgeschlagen).")

#: Die Widerstaende gegen Normalkraft, die Kennzahlen und Nachweise beide schreiben: je
#: Vorlage ein Name in der Formelsammlung. ``@eta`` ist η_w oder, stossartig, η_w·η_t.
ZUG = (r"@eta \cdot @f_t \cdot @A", "Zugwiderstand eines Holzquerschnitts")
DRUCK = (r"-@eta \cdot @f_c \cdot @A", "Druckwiderstand eines Holzquerschnitts")

#: Die Reihen von Saint-Venant fuer k_2 = β/c, b die kurze Seite.
K_2 = (r"\frac{1 - \frac{192}{\pi^5} \cdot \frac{@b}{@h} \sum_{n = 1, 3, 5, \ldots}"
       r" \frac{1}{n^5} \tanh\frac{n \pi \cdot @h}{2 \cdot @b}}"
       r"{3 \left(1 - \frac{8}{\pi^2} \sum_{n = 1, 3, 5, \ldots}"
       r" \frac{1}{n^2 \cosh\frac{n \pi \cdot @h}{2 \cdot @b}}\right)}")


def holzstoff(analyse: Querschnittsanalyse) -> Baustoff:
    """Das Holz der Analyse -- es gibt nur eines (siehe Dateikopf)."""
    return analyse.baustoffe[0]


def holzart(stoff: Baustoff) -> Holzart:
    """Woraus das Holz ist -- Vollholz oder Brettschichtholz, nach seiner Sorte."""
    return HOLZSORTEN[stoff.sorte].art


def stoffbezuege(stoff: Baustoff, *kennwerte: str) -> List[Eingabebezug]:
    """Die Kennwerte als Eingaben -- ohne Angabe die der Nachweise, :data:`KENNWERTE`."""
    return [stoff.bezug(k) for k in (kennwerte or KENNWERTE)]


def kennwert(e: Eingaben, stoff: Baustoff, kurz: str) -> Wert:
    """Ein Kennwert des Holzes, wie die Nachweise ihn lesen."""
    return e[stoff.eingabename(kurz)]


def beiwert(p: Protokoll, werte: Zwischenwerte, eta_w: Wert, stossartig: bool) -> Wert:
    """
    ``η = η_w·η_t`` eines Falls -- ohne stossartige Einwirkung ist ``η_t``
    eins, und ``η`` ist ``η_w``.
    """
    if not stossartig:
        return eta_w
    t = werte.zahl("eta_t", r"\eta_t", eta_t(True), "Beiwert der Einwirkungsdauer", stellen=1)
    eta = werte.zahl("eta", r"\eta", eta_w.groesse.zahl * t.groesse.zahl,
                     "Beiwert der Bemessungswerte", stellen=2)
    p.formel(eta, r"@w \cdot @t", {"w": eta_w, "t": t},
             titel="Stossartige Einwirkung: η_t = 1.4 hebt die Bemessungswerte",
             referenz=f"{REFERENZ_ETA_T}; {REFERENZ_ETA}",
             name="Beiwert der Bemessungswerte des Holzes")
    return eta


class HolzwerteQA(Prozedur):
    """Die Werte eines Holzquerschnitts, die seine Nachweise lesen -- siehe Dateikopf."""

    THEMA = "Holzquerschnitt"

    def __init__(self, analyse: Querschnittsanalyse, feuchte: Feuchteklasse) -> None:
        self.analyse = analyse
        self.feuchte = feuchte
        self.holz = Holzquerschnitt.aus(analyse.zeichnung)
        self.stoff = holzstoff(analyse)
        self.art = holzart(self.stoff)
        einachsig = analyse.biegung.einachsig
        self.achsen: List[str] = ["y"] if einachsig else ["y", "z"]
        """Die Achsen der Biegung -- einachsig nur y."""

        self.richtungen: List[str] = ["z"] if einachsig else ["z", "y"]
        """Die Richtungen der Querkraft -- einachsig nur z."""

        basis = f"{analyse.id}.holz"
        self.d: Dict[str, WertDef] = {}

        def neu(kurz: str, symbol: str, einheit, beschreibung: str, stellen: int = 1,
                referenz: str = "") -> None:
            self.d[kurz] = WertDef(id=f"{basis}.{kurz}", symbol=symbol, einheit=einheit,
                                   beschreibung=beschreibung, referenz=referenz, stellen=stellen)

        neu("eta_w", r"\eta_w", EINHEITSLOS, "Beiwert der Holzfeuchte", 2, TABELLE_4)
        for a in self.achsen:
            neu(f"W_{a}", f"W_{a}", CM3, f"Widerstandsmoment um {a}, bis zur weitesten Faser")
        if self.brettschicht:
            neu("k_h", "k_h", EINHEITSLOS, "Höhenbeiwert des Brettschichtholzes", 3,
                gl.REFERENZ_K_H)
        for r in self.richtungen:
            neu(f"A_V_{r}", rf"A_{{V,{r}}}", MM2, f"Schubfläche für eine Querkraft in {r}", 0)
        if self.holz.rechteck:
            neu("W_T", "W_T", CM3, "Torsionswiderstandsmoment des Rechtecks")
        super().__init__(basis, ausgaben=list(self.d.values()),
                         bezuege=[Eingabebezug(k, analyse.id_von(k))
                                  for k in ("A", "I_y", "I_z", "I_yz")],
                         titel=f"Holzquerschnitt – {analyse.name}", abschnitt=analyse.abschnitt)

    @property
    def brettschicht(self) -> bool:
        return self.art is Holzart.BRETTSCHICHTHOLZ

    def als_eingaben(self) -> List[Eingabebezug]:
        """Alle Werte als Eingaben eines Nachweises, unter ihrem Kurznamen."""
        return [Eingabebezug(kurz, d.id) for kurz, d in self.d.items()]

    # -- Rechnen ------------------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Werte des Holzquerschnitts")
        p.erklaerung(
            "Holz rechnet linear (SIA 265, 4.1.2): die Spannungen sind elastisch, am "
            "Bruttoquerschnitt. Was die Nachweise der Lastfälle, die Kennzahlen und der Stab "
            "daraus lesen, steht hier einmal.")
        text = keine_hauptachsen(
            f"Querschnittsanalyse «{self.analyse.name}»",
            *(e.g(k).si for k in ("I_y", "I_z", "I_yz")), was="den Querschnitt",
            folge="Die Spannungen gelten mit der Nulllinie parallel zu y oder z und sind darum "
                  "nur genähert.")
        if text:
            p.hinweis(text)
        werte = Zwischenwerte(self.id)
        ergebnis: Dict[str, Groesse] = {}

        def belegen(kurz: str, si: float) -> Wert:
            d = self.d[kurz]
            wert = d.belegen(Groesse.aus_si(si, d.einheit))
            ergebnis[d.id] = wert.groesse
            return wert

        p.wert(belegen("eta_w", self.feuchte.eta_w),
               titel=f"Feuchteklasse {self.feuchte.value} (Tabelle 3): {self.feuchte.erklaerung}",
               referenz=TABELLE_4)
        self._biegung(p, e, werte, belegen)
        self._schub(p, e, werte, belegen)
        if self.holz.rechteck:
            self._torsion(p, werte, belegen)
        return ergebnis

    def _biegung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, belegen) -> None:
        p.annahme("Die Biegespannung je Achse an der weitesten Faser, y und z als Hauptachsen – "
                  "beim Rechteck M/W, bei einem anderen Querschnitt auf der sicheren Seite (nach "
                  "Vorgabe, nicht nachgeschlagen).")
        for a in self.achsen:
            quer = "z" if a == "y" else "y"
            faser = werte.laenge(f"e_{quer}", f"e_{quer}", self.holz.faser(a) * 1e-3,
                                 f"Abstand der weitesten Faser vom Schwerpunkt, in {quer}")
            I = e[f"I_{a}"]
            p.formel(belegen(f"W_{a}", I.groesse.si / faser.groesse.si), r"\frac{@I}{@z}",
                     {"I": I, "z": faser}, titel=f"Widerstandsmoment um {a}",
                     name=WIDERSTANDSMOMENT)
        if not self.brettschicht:
            return
        hoehe = self.holz.hoehe("y")
        h = werte.laenge("h", "h", hoehe * 1e-3, "Höhe des Brettschichtholzes, in z")
        if hoehe >= gl.K_H_AB:
            p.wert(belegen("k_h", 1.0), titel=f"Höhe {h.formatiert()} mm, nicht unter 600 mm: "
                                              f"k_h = 1", referenz=gl.REFERENZ_K_H)
        else:
            p.formel(belegen("k_h", gl.k_h(hoehe)),
                     r"\min\left(\left(\frac{600\ \mathrm{mm}}{@h}\right)^{0.1};\ 1.1\right)",
                     {"h": h}, titel="Höhenbeiwert unter 600 mm Höhe, für die Biegung um y",
                     referenz=gl.REFERENZ_K_H, name="Höhenbeiwert des Brettschichtholzes")
        p.annahme("Die Lamellen liegen parallel zu y: k_h gilt für die Biegung um y, mit der "
                  "Höhe in z – nach Vorgabe, nicht nachgeschlagen. k_sys nimmt das Werkzeug "
                  "nicht.")

    def _schub(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, belegen) -> None:
        p.ansatz(r"\tau = \frac{V \cdot S}{I \cdot b} = \frac{V}{A_V} \qquad "
                 r"A_V = \frac{I \cdot b}{S}",
                 titel="Schubspannung nach Jourawski – auf dem Schnitt quer zur Querkraft, auf "
                       "dem S/b am grössten ist; S ist das statische Moment jenseits davon, "
                       "b seine Breite", name="Schubspannung aus Querkraft nach Jourawski")
        for r in self.richtungen:
            schnitt = self.holz.schubschnitt(r)
            achse = "y" if r == "z" else "z"
            S = werte.wert(f"S_{r}", rf"S_{{V,{r}}}", Groesse.aus_si(schnitt.S * 1e-9, CM3),
                           beschreibung="Statisches Moment jenseits des Schnitts")
            b = werte.laenge(f"b_{r}", rf"b_{{V,{r}}}", schnitt.b * 1e-3,
                             "Breite des Holzes auf dem Schnitt")
            I = e[f"I_{achse}"]
            p.formel(belegen(f"A_V_{r}", I.groesse.si * b.groesse.si / S.groesse.si),
                     r"\frac{@I \cdot @b}{@S}", {"I": I, "b": b, "S": S},
                     titel=f"Schubfläche für V_{r}: der Schnitt bei {r} = {schnitt.lage:.1f} mm",
                     name="Schubfläche nach Jourawski")

    def _torsion(self, p: Protokoll, werte: Zwischenwerte, belegen) -> None:
        kurz, lang = self.holz.seiten
        b = werte.laenge("b_T", "b", kurz * 1e-3, "Kurze Seite des Rechtecks")
        h = werte.laenge("h_T", "h", lang * 1e-3, "Lange Seite des Rechtecks")
        k = werte.zahl("k_2", "k_2", k_2(lang / kurz), "Torsionsbeiwert des Rechtecks")
        p.formel(k, K_2, {"b": b, "h": h},
                 titel="Torsionsbeiwert nach Saint-Venant: die grösste Schubspannung liegt in der "
                       "Mitte der langen Seite", name="Torsionsbeiwert des Rechtecks")
        p.formel(belegen("W_T", k.groesse.zahl * h.groesse.si * b.groesse.si ** 2),
                 r"@k \cdot @h \cdot @b^2", {"k": k, "h": h, "b": b},
                 titel="Torsionswiderstandsmoment: τ_tor = T/W_T",
                 name="Torsionswiderstandsmoment des Rechtecks")
