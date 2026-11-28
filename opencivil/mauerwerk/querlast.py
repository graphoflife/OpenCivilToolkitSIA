"""
opencivil/mauerwerk/querlast.py -- eine Wand quer zu ihrer Ebene belastet, auch im Erdbeben.

VERANTWORTUNG:
Die Ersatzkraft des Erdbebens quer zur Wand (:func:`p_E`, SIA 261:2020,
16.7.2, Gl. (49)) samt ihrer Herleitung (:func:`erdbeben_schreiben`), was
zum Erdbeben am Mauerwerk zu sagen ist (:func:`erdbebenhinweise`, SIA
266:2015, 4.7.1.4 und 4.7.1.5), und je Pfeiler und Kombination zwei
Nachweise: die Querlast über die Druckgewölbe (:class:`Querlastnachweis`,
4.3.4) und, wo das Gebäude mit q = 2.0 rechnet, das Normalkraftniveau nach
Gl. (27) (:class:`Normalkraftniveau`).

DIE ERSATZKRAFT (Gl. (49)):
Im Schwerpunkt der Wand wirkt quer zu ihr F_a, aus ihrem Eigengewicht G_a;
je m² Wand ist G_a das Eigengewicht g_k. Mit der Schwingzeit der Wand gleich
der des Gebäudes, T_a = T_1, ist die Klammer der Gl. (49) am grössten:
p_E = γ_f · a_gd · S · g_k / (g · q_a) · [3 · (1 + z_a/h) − 0.5] -- nach
Vorgabe, nicht nachgeschlagen, die ungünstigste Annahme, auch für eine
tragende Wand (Benutzer, 2026-11-27). Die untere Grenze der Gl. (49) gilt
damit nie. q_a = 1.5 (16.7.3). p_E wirkt in beiden Richtungen.

DIE QUERLAST (4.3.4):
Quer zur Wand trägt unbewehrtes Mauerwerk über Druckgewölbe (4.3.4.2,
Figur 11), mit der Druckfestigkeit nach 4.3.2.1 (4.3.4.4):

- lotrecht zwischen Kopf und Fuss mit der Normalkraft: die verformte Wand
  nach Theorie 2. Ordnung wie beim Knicken, die Querlast dazu
  (:func:`~opencivil.mauerwerk.knicken.querlast`). Gerechnet wird immer
  nach Theorie 2. Ordnung; Gl. (19) und (20) erlaubten sonst, sie zu
  vernachlässigen -- so liegt die Rechnung auf der sicheren Seite.
- waagrecht zwischen den Rändern, wenn beide gehalten sind, die Wand keine
  Öffnung hat und die Stossfugen vollfugig sind (4.3.4.3): ein Bogen mit
  drei Gelenken, an jedem über t_w/2 mit f_yd gedrückt, also
  p_Rd,h = 2 · f_yd · t_w² / L². Effekte 2. Ordnung vernachlässigt er,
  darum nur, wo Gl. (19) und (20) mit L statt h_w gelten; w_d ist dabei die
  Durchbiegung des waagrechten Streifens, elastisch, ungerissen, mit E_xd.

Nach Vorgabe, nicht nachgeschlagen: die Normalkraft des lotrechten Gewölbes
ist die in halber Höhe, N_m = N_Ld + (N_xd − N_Ld)/2, über die ganze Höhe;
ein Pfeiler bekommt die Querlast bis zur Mitte der Öffnungen neben ihm,
am Ende der Wand bis zu diesem; es gilt das stärkere der beiden Gewölbe,
nicht ihre Summe.

DAS NORMALKRAFTNIVEAU (Gl. (27)):
Rechnet das Gebäude mit q = 2.0, muss jede Wand N_xd/(l_w · t_w · f_xd) ≤
0.20 erfüllen (4.7.1.5) -- in den Kombinationen mit diesem Erdbeben.

EINHEITEN:
SI-Basis; Querlasten in N/m².
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

from opencivil.core.einheiten import KN_PRO_M2, M, M_PRO_S2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.sprache import satzanfang
from opencivil.core.wert import Wert
from opencivil.erdbeben.ersatzkraft import Bauwerksklasse, Erdbebenzone
from opencivil.mauerwerk import knicken
from opencivil.mauerwerk.lasten import Abtrag
from opencivil.mauerwerk.modell import Pfeiler, Querlast, Seitenrand, Verhaltensbeiwert, Wand
from opencivil.mauerwerk.nachweise import (
    NULL, Stelle, Stellenausgang, Wandnachweis, ausmitten, ohne_einwirkung, pfeiler_von, zug,
)
from opencivil.stabwerk.system import Meldung

if TYPE_CHECKING:
    from opencivil.mauerwerk.werk import Wandbefund

#: Wo die Regeln stehen.
REFERENZ_GL_49 = "SIA 261:2020, 16.7.2, Gl. (49)"
REFERENZ_Q_A = "SIA 261:2020, 16.7.3"
REFERENZ_GL_19 = "SIA 266:2015, 4.3.4.1, Gl. (19)"
REFERENZ_GL_20 = "SIA 266:2015, 4.3.4.1, Gl. (20)"
REFERENZ_VOLLFUGIG = "SIA 266:2015, 4.3.4.3"
REFERENZ_GL_27 = "SIA 266:2015, 4.7.1.5, Gl. (27)"
REFERENZ_VERFORMUNG = "SIA 266:2015, 4.7.1.4"

#: Der Verhaltensbeiwert einer Wand als sekundäres Bauteil (16.7.3).
Q_A = 1.5

#: Wie schlank das waagrechte Gewölbe höchstens ist, und wie weit es sich biegt -- Gl. (19), (20).
SCHLANKHEIT = 15.0
DURCHBIEGUNG = 0.002

#: Wie stark ein Pfeiler höchstens gedrückt ist, wenn das Gebäude mit q = 2.0 rechnet -- Gl. (27).
NIVEAU = 0.20


# ===========================================================================
# Die Ersatzkraft des Erdbebens
# ===========================================================================


def klammer(z_a: float, h: float) -> float:
    """Die Klammer der Gl. (49) mit T_a = T_1: 3 · (1 + z_a/h) − 0.5 -- siehe Dateikopf."""
    return 3.0 * (1.0 + z_a / h) - 0.5


def p_E(g_k: float, g: float, q: Querlast) -> float:
    """
    Die Ersatzkraft des Erdbebens je m² Wand, in N/m² -- ``g_k`` ihr
    Eigengewicht je m² in N/m², ``g`` in m/s². Siehe Dateikopf.
    """
    e = q.erdbeben
    return (e.bauwerksklasse.gamma_f * e.zone.a_gd * e.baugrund.werte.S * g_k / (g * Q_A)
            * max(klammer(e.z_a, e.h), 1.0))


def erdbeben_schreiben(p: Protokoll, zw: Zwischenwerte, q: Querlast, g_k: Wert,
                       g: Wert) -> None:
    """Die Ersatzkraft einer Querlast aus dem Erdbeben, nach Gl. (49) hergeleitet."""
    e = q.erdbeben
    p.titel(f"Erdbeben quer zur Wand – {q.name}", ebene=4)
    p.text(f"Zone {e.zone.value}, Baugrundklasse {e.baugrund.value}, Bauwerksklasse "
           f"{e.bauwerksklasse.value}. Die Wand schwingt so wie das Gebäude, T_a = T_1: dann ist "
           f"die Klammer der Gl. (49) am grössten, und ihre untere Grenze gilt nie – nach "
           f"Vorgabe, nicht nachgeschlagen, auch für eine tragende Wand. Die Kraft wirkt in "
           f"beiden Richtungen.")
    werte = {
        "gf": zw.zahl(f"{q.name}.gamma_f", r"\gamma_f", e.bauwerksklasse.gamma_f,
                      "Bedeutungsbeiwert der Bauwerksklasse", stellen=1),
        "a": zw.wert(f"{q.name}.a_gd", "a_{gd}", Groesse.aus_si(e.zone.a_gd, M_PRO_S2), 1,
                     "Bemessungswert der Bodenbeschleunigung"),
        "S": zw.zahl(f"{q.name}.S", "S", e.baugrund.werte.S, "Bodenparameter", stellen=2),
        "q": zw.zahl(f"{q.name}.q_a", "q_a", Q_A, "Verhaltensbeiwert der Wand", stellen=1),
        "z": zw.wert(f"{q.name}.z_a", "z_a", Groesse.aus_si(e.z_a, M), 2,
                     "Höhe der Wand über dem Fundament"),
        "h": zw.wert(f"{q.name}.h", "h", Groesse.aus_si(e.h, M), 2, "Höhe des Gebäudes"),
    }
    for kurz, referenz in (("gf", "SIA 261:2020, 16.3, Tabelle 25"),
                           ("a", "SIA 261:2020, 16.2.1.2"),
                           ("S", "SIA 261:2020, 16.2.2, Tabelle 24"), ("q", REFERENZ_Q_A),
                           ("z", None), ("h", None)):
        p.wert(werte[kurz], referenz=referenz)
    ergebnis = zw.wert(f"{q.name}.p_E", "p_E",
                       Groesse.aus_si(p_E(g_k.groesse.si, g.groesse.si, q), KN_PRO_M2), 2,
                       "Ersatzkraft des Erdbebens je m² Wand")
    p.formel(ergebnis, r"\frac{@gf \cdot @a \cdot @S \cdot @gk}{@g \cdot @q} \cdot "
                       r"\left[3 \cdot \left(1 + \frac{@z}{@h}\right) - 0.5\right]",
             {**werte, "gk": g_k, "g": g},
             titel="Ersatzkraft des Erdbebens je m² Wand, mit T_a = T_1",
             referenz=REFERENZ_GL_49, name="Ersatzkraft des Erdbebens quer zu einer Wand")


def erdbebenhinweise(wand: Wand) -> List[Meldung]:
    """
    Was zum Erdbeben am Mauerwerk zu sagen ist, grau, je Querlast des
    Erdbebens: wo es ein erhöhtes Verformungsvermögen braucht -- in
    Bauwerksklasse III, in II in den Zonen Z3a und Z3b (4.7.1.4) --, und
    dass q = 2.5 es durch Versuche nachweisen muss (4.7.2). Beides prüft
    das Werkzeug nicht.
    """
    hinweise = []
    for q in (q for lf in wand.lastfaelle for q in lf.querlasten if q.erdbeben):
        e = q.erdbeben
        if e.bauwerksklasse is Bauwerksklasse.III or (
                e.bauwerksklasse is Bauwerksklasse.II
                and e.zone in (Erdbebenzone.Z3A, Erdbebenzone.Z3B)):
            wo = f"Bauwerksklasse {e.bauwerksklasse.value}" + (
                f" und Zone {e.zone.value}" if e.bauwerksklasse is Bauwerksklasse.II else "")
            hinweise.append(Meldung(
                f"{q.name}: in {wo} braucht das Mauerwerk ein erhöhtes Verformungsvermögen "
                f"({REFERENZ_VERFORMUNG}) – das prüft das Werkzeug nicht.", (q.name,),
                fehler=False))
        if e.q is Verhaltensbeiwert.Q_25:
            hinweise.append(Meldung(
                f"{q.name}: mit q = 2.5 muss das erhöhte Verformungsvermögen durch Versuche an "
                f"Schubwänden nachgewiesen sein (SIA 266:2015, 4.7.2) – das prüft das Werkzeug "
                f"nicht.", (q.name,), fehler=False))
    return hinweise


# ===========================================================================
# Die Querlast
# ===========================================================================


@dataclass(frozen=True)
class _Richtung:
    """Eine Richtung, in der die Querlast wirkt: ``p_d`` mit Vorzeichen, und was die Wand trägt."""

    p_d: float
    lotrecht: knicken.Querergebnis
    p_Rd_v: float
    p_Rd_h: Optional[float]
    """``None``, wo das waagrechte Gewölbe nicht trägt."""

    @property
    def p_Rd(self) -> float:
        return max(self.p_Rd_v, self.p_Rd_h or 0.0)

    @property
    def grad(self) -> float:
        return self.p_Rd / abs(self.p_d)


def einwirkungen(a: Abtrag) -> List[float]:
    """
    Die Querlasten der Kombination je Richtung, mit Vorzeichen: p ± p_E
    mit dem Erdbeben, sonst p allein -- leer ohne Querlast.
    """
    if a.p_E > NULL:
        return [a.p + a.p_E, a.p - a.p_E]
    return [a.p] if abs(a.p) > NULL else []


def einzugsbreite(befund: "Wandbefund", pf: Pfeiler) -> Tuple[float, float]:
    """
    Von wo bis wo ein Pfeiler Querlast bekommt, in m: bis zur Mitte der
    Öffnungen neben ihm, am Ende der Wand bis zu diesem (Dateikopf).
    """
    alle, r = befund.pfeiler, befund.wand.flaeche
    i = alle.index(pf)
    links = r.x0 if i == 0 else (alle[i - 1].x1 + pf.x0) / 2.0
    rechts = r.x1 if i == len(alle) - 1 else (pf.x1 + alle[i + 1].x0) / 2.0
    return links, rechts


def waagrechtes_gewoelbe(befund: "Wandbefund") -> Optional[str]:
    """
    Warum die Wand kein waagrechtes Gewölbe hat, als Satz -- ``None``, wenn
    sie eines haben kann: ohne Öffnung, beide Ränder gehalten, vollfugig.
    Gl. (19) und (20) prüft :class:`Querlastnachweis`.
    """
    w = befund.wand
    if w.links is not Seitenrand.GEHALTEN or w.rechts is not Seitenrand.GEHALTEN:
        return "Die Wand ist nicht links und rechts gehalten: kein waagrechtes Gewölbe."
    if w.oeffnungen:
        return "Die Wand hat Öffnungen: das waagrechte Gewölbe zählt nur ohne – nach Vorgabe."
    if not w.vollfugig:
        return (f"Die Stossfugen sind nicht vollfugig vermauert: ein waagrechtes Gewölbe ginge "
                f"durch sie ({REFERENZ_VOLLFUGIG}) und zählt nicht.")
    return None


class Querlastnachweis(Wandnachweis):
    """Die Querlast über die Druckgewölbe -- siehe Dateikopf."""

    LANGNAME = "Querlast"
    ART = "Q"
    FELD = "querlast"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Quer zu ihrer Ebene trägt eine Wand aus unbewehrtem Mauerwerk über Druckgewölbe: "
            "lotrecht zwischen Kopf und Fuss mit ihrer Normalkraft, und waagrecht zwischen "
            "gehaltenen Rändern (Figur 11). Das lotrechte Gewölbe ist die verformte Wand: die "
            "Querlast gibt ihr eine Ausmitte dazu, und wie bei der Normalkraft darf diese "
            "nirgends über die Grenze der Figur 4.")
        p.ansatz(r"e_z(x) = e_u + \left(e_o - e_u\right) \cdot \frac{x}{h_w} + "
                 r"\frac{p_d \cdot b_q \cdot x \cdot \left(h_w - x\right)}{2 \cdot N_m} + w(x)",
                 titel="Ausmitte der Wand unter Normalkraft und Querlast, w(x) nach Figur 3",
                 referenz=knicken.REFERENZ_GEWOELBE, name="Ausmitte einer Wand unter Querlast")
        p.text("Gerechnet wird immer nach Theorie 2. Ordnung, wie bei der Normalkraft: Gl. (19) "
               "und (20) erlaubten sonst, ihre Effekte zu vernachlässigen – so liegt die "
               "Rechnung auf der sicheren Seite. Dass Kopf, Fuss und gehaltene Ränder die Kräfte "
               "der Gewölbe aufnehmen und weiterleiten (4.3.4.5), prüft das Werkzeug nicht.")
        p.annahme("Das lotrechte Gewölbe rechnet über die ganze Höhe mit der Normalkraft in "
                  "halber Höhe, N_m; ein Pfeiler bekommt die Querlast bis zur Mitte der "
                  "Öffnungen neben ihm, am Ende der Wand bis zu diesem; das waagrechte Gewölbe "
                  "ist ein Bogen mit drei Gelenken, an jedem über t_w/2 gedrückt, und zählt "
                  "nur ohne Öffnungen; es gilt das stärkere Gewölbe, nicht beide zusammen – "
                  "nach Vorgabe, nicht nachgeschlagen.")

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        pf = pfeiler_von(befund, s.ort)
        a = befund.kombinationen[s.kombination]
        zw = Zwischenwerte(f"{self.id}.{s.kennung}")
        p.titel(f"{self.LANGNAME} – {s.name}", ebene=3)
        lasten = einwirkungen(a)
        if not lasten:
            return ohne_einwirkung(p, s)
        ohne_druck = zug(p, s, pf, a)
        if ohne_druck is not None:
            return ohne_druck
        t, h, werte = befund.t, befund.wand.flaeche.hoehe, befund.werte
        links, rechts = einzugsbreite(befund, pf)
        b_q = zw.wert("b_q", "b_q", Groesse.aus_si(rechts - links, M), 2,
                      "Breite, von der der Pfeiler Querlast bekommt")
        p.wert(b_q, titel=f"Breite, von der der Pfeiler Querlast bekommt: von "
                          f"{links:.2f} m bis {rechts:.2f} m, bis zur Mitte der Öffnungen neben "
                          f"ihm, am Ende der Wand bis zu diesem")
        e_o, e_u = ausmitten(p, zw, befund, a, pf)
        N_m = self._normalkraft(p, zw, a, pf)
        n = N_m.groesse.si / (pf.b * t * werte.f_xd * 1e6)
        grund_h = waagrechtes_gewoelbe(befund)
        richtungen = [self._richtung(befund, pf, n, e_o, e_u, p_d, b_q.groesse.si, grund_h)
                      for p_d in lasten]
        r = min(richtungen, key=lambda x: x.grad)
        if a.p_E > NULL:
            self._beide(p, zw, a, richtungen, r)
        p_d = zw.wert("p_d", "p_d", Groesse.aus_si(abs(r.p_d), KN_PRO_M2), 2,
                      "Querlast der Kombination, Betrag")
        p.wert(p_d, titel=f"Querlast der Kombination, {_seite(r.p_d)}"
                          + (" – die massgebende Richtung" if a.p_E > NULL else ""))
        p_Rd_v = self._lotrecht(p, zw, r, N_m, h, t)
        p_Rd = p_Rd_v
        if grund_h is not None:
            p.text(grund_h)
        else:
            p_Rd_h = self._waagrecht(p, zw, befund, pf, r, p_d)
            if p_Rd_h is not None:
                p_Rd = zw.wert("p_Rd", "p_{Rd}", Groesse.aus_si(r.p_Rd, KN_PRO_M2), 2,
                               "Widerstand gegen Querlast")
                p.formel(p_Rd, r"\max\left(@v;\ @h\right)", {"v": p_Rd_v, "h": p_Rd_h},
                         titel="Es trägt das stärkere der beiden Gewölbe",
                         name="Querlastwiderstand einer Wand aus Mauerwerk")
        v = self.vergleichen(p, p_d, p_Rd, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v,
                              begruendung=self.satz(v, ("p_d", "p_Rd"), "kN/m²"))

    @staticmethod
    def _normalkraft(p: Protokoll, zw: Zwischenwerte, a: Abtrag, pf: Pfeiler) -> Wert:
        """N_m: die Normalkraft in halber Höhe des Pfeilers -- die des lotrechten Gewölbes."""
        N = zw.kraft("N_xd", "N_{xd}", a.N[pf.name], "Normalkraft am Fuss des Pfeilers")
        N_L = zw.kraft("N_Ld", "N_{Ld}", a.N_L[pf.name],
                       "Normalkraft aus den Lasten am Kopf, ohne Eigengewicht")
        N_m = zw.kraft("N_m", "N_m", (a.N[pf.name] + a.N_L[pf.name]) / 2.0,
                       "Normalkraft in halber Höhe")
        p.formel(N_m, r"@L + \frac{@N - @L}{2}", {"N": N, "L": N_L},
                 titel="Normalkraft in halber Höhe: die Lasten am Kopf und die Hälfte des "
                       "Eigengewichts, das bis zum Fuss dazukommt",
                 name="Normalkraft eines Pfeilers in halber Höhe")
        return N_m

    @staticmethod
    def _richtung(befund: "Wandbefund", pf: Pfeiler, n: float, e_o: Optional[Wert],
                  e_u: Optional[Wert], p_d: float, b_q: float,
                  grund_h: Optional[str]) -> _Richtung:
        """Was die Wand in der Richtung von ``p_d`` trägt -- noch ohne Herleitung."""
        t, h, werte = befund.t, befund.wand.flaeche.hoehe, befund.werte
        lotrecht = knicken.querlast(h / t, None if e_u is None else e_u.groesse.si / t,
                                    None if e_o is None else e_o.groesse.si / t,
                                    werte.E_xd / werte.f_xd, n, 1 if p_d > 0 else -1)
        p_Rd_v = lotrecht.lam * t * t * werte.f_xd * 1e6 / (h * h) * pf.b / b_q
        p_Rd_h = None
        if grund_h is None and _gewoelbe_haelt(befund, pf.b, abs(p_d)):
            p_Rd_h = 2.0 * werte.f_yd * 1e6 * t * t / (pf.b * pf.b)
        return _Richtung(p_d, lotrecht, p_Rd_v, p_Rd_h)

    @staticmethod
    def _beide(p: Protokoll, zw: Zwischenwerte, a: Abtrag, richtungen: List[_Richtung],
               r: _Richtung) -> None:
        """Mit dem Erdbeben: beide Richtungen in einem Satz, die massgebende zuerst."""
        p_E = zw.wert("p_E", "p_E", Groesse.aus_si(a.p_E, KN_PRO_M2), 2,
                      "Querlast aus dem Erdbeben in der Kombination")
        p.wert(p_E, titel="Querlast aus dem Erdbeben in der Kombination, in beiden Richtungen – "
                          "hergeleitet bei der Wand", referenz=REFERENZ_GL_49)
        if abs(a.p) > NULL:
            p_h = zw.wert("p", "p", Groesse.aus_si(a.p, KN_PRO_M2), 2,
                          "Querlast von Hand in der Kombination")
            p.wert(p_h, titel="Querlast von Hand in der Kombination, positiv zur Seite, von der "
                              "aus man die Ansicht sieht")
        saetze = [f"{_seite(x.p_d)}: p_d = {abs(x.p_d) / 1e3:.2f} kN/m², p_Rd = "
                  f"{x.p_Rd / 1e3:.2f} kN/m²" for x in [r, *(x for x in richtungen if x is not r)]]
        p.text(f"Das Erdbeben wirkt in beiden Richtungen. {satzanfang('; '.join(saetze))}. "
               f"Massgebend ist die erste, sie steht hier.")

    @staticmethod
    def _lotrecht(p: Protokoll, zw: Zwischenwerte, r: _Richtung, N_m: Wert, h: float,
                  t: float) -> Wert:
        """Das lotrechte Gewölbe: was die Rechnung nach Theorie 2. Ordnung fand."""
        p_Rd_v = zw.wert("p_Rd_v", r"p_{Rd,v}", Groesse.aus_si(r.p_Rd_v, KN_PRO_M2), 2,
                         "Widerstand des lotrechten Gewölbes")
        p.wert(p_Rd_v, titel="Grösste Querlast, die das lotrechte Gewölbe unter N_m trägt, nach "
                             "Theorie 2. Ordnung gerechnet",
               referenz=f"{knicken.REFERENZ_GEWOELBE}; {knicken.REFERENZ_FIGUR_3}")
        z = r.lotrecht.grenzzustand
        if N_m.groesse.si <= NULL:
            p.text("Ohne Normalkraft in halber Höhe trägt das lotrechte Gewölbe nichts.")
        elif z is None:
            p.text("Schon ohne Querlast hält die Wand N_m nicht – siehe den Nachweis der "
                   "Normalkraft: das lotrechte Gewölbe trägt nichts.")
        elif r.lotrecht.grund == knicken.AUSMITTE:
            p.text(f"Unter p_Rd,v erreicht die Ausmitte {_wo(z.hoehe, h)} mit "
                   f"{abs(z.e_max) * t * 1e3:.0f} mm die Grenze nach Gl. (6) und Figur 4.")
        else:
            p.text("Über p_Rd,v findet die Wand kein Gleichgewicht mehr.")
        return p_Rd_v

    @staticmethod
    def _waagrecht(p: Protokoll, zw: Zwischenwerte, befund: "Wandbefund", pf: Pfeiler,
                   r: _Richtung, p_d: Wert) -> Optional[Wert]:
        """
        Das waagrechte Gewölbe einer Wand ohne Öffnung zwischen gehaltenen
        Rändern: Gl. (19) und (20) mit L, dann sein Widerstand -- ``None``,
        wo eine der beiden nicht gilt.
        """
        t, werte = befund.t, befund.werte
        L = zw.wert("L", "L", Groesse.aus_si(pf.b, M), 2, "Spannweite des waagrechten Gewölbes")
        t_w = zw.laenge("t_w", "t_w", t, "Dicke der Wand", stellen=0)
        p.wert(L, titel="Spannweite des waagrechten Gewölbes, von Rand zu Rand")
        if pf.b > SCHLANKHEIT * t:
            p.text(f"L/t_w = {pf.b / t:.2f} > 15: Gl. (19) gilt nicht, das waagrechte Gewölbe "
                   f"zählt nicht – nach Vorgabe, nicht nachgeschlagen.")
            return None
        E_xd = zw.spannung("E_xd", "E_{xd}", werte.E_xd * 1e6, "Elastizitätsmodul der Wand")
        w_d = zw.laenge("w_d", "w_d", _durchbiegung(befund, pf.b, abs(r.p_d)),
                        "Durchbiegung des waagrechten Streifens", stellen=2)
        p.formel(w_d, r"\frac{5 \cdot @p \cdot @L^{4}}{32 \cdot @E \cdot @t^{3}}",
                 {"p": p_d, "L": L, "E": E_xd, "t": t_w},
                 titel="Durchbiegung der Wand als waagrechter Streifen zwischen den Rändern, "
                       "elastisch und ungerissen, mit E_xd",
                 referenz=REFERENZ_GL_20, name="Durchbiegung einer Wand als waagrechter Streifen")
        grenze = DURCHBIEGUNG * pf.b
        if w_d.groesse.si > grenze:
            p.text(f"w_d > 0.002 · L = {grenze * 1e3:.2f} mm: Gl. (20) gilt nicht, das waagrechte "
                   f"Gewölbe zählt nicht – nach Vorgabe, nicht nachgeschlagen.")
            return None
        p.text(f"L/t_w = {pf.b / t:.2f} ≤ 15 ({REFERENZ_GL_19}) und w_d ≤ 0.002 · L = "
               f"{grenze * 1e3:.2f} mm: die Effekte 2. Ordnung bleiben weg (4.3.4.1).")
        f_yd = zw.spannung("f_yd", "f_{yd}", werte.f_yd * 1e6,
                           "Druckfestigkeit der Wand parallel zu den Lagerfugen", stellen=2)
        p_Rd_h = zw.wert("p_Rd_h", r"p_{Rd,h}", Groesse.aus_si(r.p_Rd_h, KN_PRO_M2), 2,
                         "Widerstand des waagrechten Gewölbes")
        p.formel(p_Rd_h, r"2 \cdot @f \cdot \frac{@t^{2}}{@L^{2}}", {"f": f_yd, "t": t_w, "L": L},
                 titel="Widerstand des waagrechten Gewölbes: ein Bogen mit drei Gelenken, an "
                       "jedem über t_w/2 mit f_yd gedrückt",
                 referenz=knicken.REFERENZ_GEWOELBE,
                 name="Widerstand des waagrechten Druckgewölbes einer Wand")
        return p_Rd_h


def _gewoelbe_haelt(befund: "Wandbefund", L: float, p_d: float) -> bool:
    """Ob Gl. (19) und (20) mit der Spannweite ``L`` statt h_w gelten -- siehe Dateikopf."""
    return L <= SCHLANKHEIT * befund.t and _durchbiegung(befund, L, p_d) <= DURCHBIEGUNG * L


def _durchbiegung(befund: "Wandbefund", L: float, p_d: float) -> float:
    """w_d des waagrechten Streifens, elastisch, ungerissen, mit E_xd: 5 p L⁴ / (384 E t³/12)."""
    return 5.0 * p_d * L ** 4 / (32.0 * befund.werte.E_xd * 1e6 * befund.t ** 3)


def _seite(p_d: float) -> str:
    """Wohin eine Querlast drückt, in Worten."""
    return ("zur Seite, von der aus man die Ansicht sieht" if p_d > 0
            else "zur anderen Seite")


def _wo(hoehe: float, h: float) -> str:
    """Wo in der Wand -- ``hoehe`` als Anteil ab dem Fuss."""
    if hoehe <= 0.0:
        return "am Fuss"
    if hoehe >= 1.0:
        return "am Kopf"
    return f"{hoehe * h:.2f} m über dem Fuss"


# ===========================================================================
# Das Normalkraftniveau
# ===========================================================================


class Normalkraftniveau(Wandnachweis):
    """Gl. (27), wo das Gebäude mit q = 2.0 rechnet -- siehe Dateikopf."""

    LANGNAME = "Normalkraftniveau"
    ART = "n"
    FELD = "normalkraftniveau"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Rechnet das Gebäude im Erdbeben mit q = 2.0, darf jede Wand, die zur "
            "Tragsicherheit zählt, nur mässig gedrückt sein. Dazu muss das Gebäude regelmässig "
            "sein nach SIA 261 – das prüft das Werkzeug hier nicht.")

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        pf = pfeiler_von(befund, s.ort)
        a = befund.kombinationen[s.kombination]
        zw = Zwischenwerte(f"{self.id}.{s.kennung}")
        p.titel(f"{self.LANGNAME} – {s.name}", ebene=3)
        N = zw.kraft("N_xd", "N_{xd}", a.N[pf.name], "Normalkraft am Fuss des Pfeilers")
        p.wert(N, titel="Normalkraft am Fuss des Pfeilers, aus dem Lastabtrag")
        if N.groesse.si <= NULL:
            return ohne_einwirkung(p, s)
        l_w = zw.laenge("l_w", "l_w", pf.b, "Breite des Pfeilers", stellen=0)
        t_w = zw.laenge("t_w", "t_w", befund.t, "Dicke der Wand", stellen=0)
        f_xd = zw.spannung("f_xd", "f_{xd}", befund.werte.f_xd * 1e6, "Druckfestigkeit der Wand",
                           stellen=2)
        n_d = zw.zahl("n_d", "n_d", N.groesse.si / (pf.b * befund.t * f_xd.groesse.si),
                      "Normalkraftniveau des Pfeilers", stellen=3)
        p.formel(n_d, r"\frac{@N}{@l \cdot @t \cdot @f}", {"N": N, "l": l_w, "t": t_w, "f": f_xd},
                 referenz=REFERENZ_GL_27, name="Normalkraftniveau eines Pfeilers")
        grenze = zw.zahl("n_Rd", "n_{Rd}", NIVEAU, "Grenze des Normalkraftniveaus", stellen=2)
        p.wert(grenze, titel="So stark darf ein Pfeiler höchstens gedrückt sein, wenn das "
                             "Gebäude mit q = 2.0 rechnet", referenz=REFERENZ_GL_27)
        v = self.vergleichen(p, n_d, grenze, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v, begruendung=self.satz(v, ("n_d", "n_Rd"), ""))
