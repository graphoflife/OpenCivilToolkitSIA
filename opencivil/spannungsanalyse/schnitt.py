"""
opencivil/spannungsanalyse/schnitt.py -- das Paar eines gezeichneten Querschnitts.

VERANTWORTUNG:
Wie ein gezeichneter Querschnitt zu den sechs Fragen kommt: das Loeserpaar
je Zugseite (:class:`Schnittpaar`, ein
:class:`~opencivil.spannungsanalyse.linie.Paar`), seine Ebenen mit kippender
Nulllinie (:class:`KippendeNulllinie`) und was seine Herleitung anders
schreibt als die Platte. Bis 2026-10-17 stand es in
``opencivil/querschnitt/schnittanalyse.py`` -- im Querschnitt, aber auf der
Analyse gebaut, die es ihrerseits erst in einer Funktion laden konnte.

JE ZUGSEITE:
Eine Analyse waehlt die Seite, die ein positives Moment zieht: unten, oben,
links oder rechts (:class:`~opencivil.querschnitt.zugseite.Zugseite`). Das
Moment wirkt um die Achse der Biegung, um die andere wirkt keines: reine
Biegung. Ein unsymmetrischer Querschnitt kippt dafuer seine Nulllinie, und
jede Ebene der Analyse sucht ihre Neigung (:class:`KippendeNulllinie`), wie
die Gebrauchsnachweise es tun -- so hat es der Benutzer am 2026-10-17
entschieden. Bis dahin blieb die Nulllinie parallel zur Achse, und das Moment
um die andere Achse, das ein L dabei weckte, zaehlte nicht: an einem L mit
Steg 200×800 und Flansch 600×200 hiess das ein Rissmoment von 132 statt
64 kNm. «Einachsig» bleibt es so, wie in der Tragsicherheit
(:class:`~opencivil.spannungsanalyse.linie.FesteNulllinie`); die Platte
rechnet immer so.

``eps_m`` ist die Dehnung im Schwerpunkt des Bruttoquerschnitts, und die
Momente beziehen sich auf ihn, wie in den Lastfaellen. «Oben» heisst der
Rand gegenueber der Zugseite, «unten» der auf ihr: bei Zug links ist oben
der rechte Rand. Kippt die Nulllinie, gelten oben und unten senkrecht zu ihr.

WOMIT GERECHNET WIRD:
Je Analyse eine Rechenwahl wie bei der Platte -- Kriechzahl, Wertesatz,
Rechenart --, fuer jeden Werkstoff des Querschnitts dieselbe. Die
Werkstoffwahl der Tragsicherheit gilt hier nicht. Staebe in derselben Tiefe,
aus demselben Stahl, werden zu einer Lage: sie haben dieselbe Dehnung.
Zerlegt wird in so viele Streifen wie die Platte in Fasern
(:data:`~opencivil.querschnitt.fasern.FASERN`), dazu die Grenzen an jeder
Ecke: eine Linie rechnet viele Ebenen, und mit den 200 Streifen der
Tragsicherheit dauerte sie dreimal so lang -- fuer ein M_Rd, das sich um
zwei Zehntelpromille aendert.

DER RISS:
Am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden Versagen
(:mod:`opencivil.nachweis.rissgroessen`)::

    M_Riss(N) = (f_ct,eff - N/A) · W        W zur Ecke, die unter reiner Biegung zuerst reisst
    N_Riss(M) = (f_ct,eff,t - σ_M) · A      σ_M aus M, an der Ecke, die zuerst reisst

Unter reiner Biegung mit dem Deviationsmoment ``I_yz``, «einachsig» mit
``W = I/v``. ``f_ct,eff`` mit ``k_t`` fuer ein Drittel der Tiefe, unter Zug
fuer die rissaktive Dicke ``min(h; b)`` -- die Regeln der Platte,
uebertragen; der Beton der Ecke gibt ``f_ctm``. Nach Vorgabe, nicht
nachgeschlagen (``notizbuch/Notizen/TODO.md``). Bei der Platte ist
``W/A = h/6`` -- dieselbe Formel.

DER AEQUIVALENTE MODUL:
Bezogen auf den Bruttoquerschnitt: ``I`` um die Achse der Biegung bzw.
``A``. Kippt die Nulllinie, kippt sie auch beim reinen Betonquerschnitt,
mit dem der Modul sich vergleicht: unter reiner Biegung kruemmt er sich wie
einer mit ``I_y - I_yz²/I_z`` (um y). Sonst zeigte ein ungerissener L schon
seiner Form wegen weniger als ``E_c,eff`` -- am L oben 0.79·E_cm statt 1.07.
So vom Benutzer bestaetigt am 2026-10-17. Bei der Platte sind es ``b·h³/12``
und ``b·h``.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.einheiten import MIO_MM3, MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.suche import Illinois, Suche
from opencivil.material.basis import Baustoff
from opencivil.nachweis.gebrauchsebene import QUER_SCHRANKE, neigung_suchen
from opencivil.nachweis.querschnittsloeser import (
    Faserloeser, Stahllage, probenschranken,
)
from opencivil.nachweis.rissgroessen import (
    MOMENTENTEILER, Bruttoquerschnitt, Rissmoment, Rissnormalkraft, beiwert_dicke,
    bruttoquerschnitt, protokoll_ecke, protokoll_spannung_ungerissen,
    protokoll_widerstandsmoment, protokoll_zugfestigkeit, rissaktive_dicke, rissmoment,
    rissnormalkraft,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse, Stabgruppe
from opencivil.querschnitt.fasern import Faserquerschnitt, Stab
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.interaktion import Querschnitt
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.art import Analyseart
from opencivil.spannungsanalyse.linie import (
    SUCHE_DER_ANALYSEN, Dehnungsebene, FesteNulllinie, Grenzzustand, Linie, Zustaende,
)

if TYPE_CHECKING:
    from opencivil.core.wert import Wert


# ===========================================================================
# Der Querschnitt in jeder Richtung
# ===========================================================================


def _betonspannung(r, gesetze: Mapping[int, Callable[[float], float]]
                   ) -> Callable[[float, float], float]:
    """
    Die Spannung des Betons an einer Stelle, fuer das Bild: in jedem Streifen
    der Beton mit der groessten Breite dort. Liegen zwei Betone in derselben
    Tiefe, zeigt das Bild den, der dort ueberwiegt.
    """
    streifen: Dict[float, Tuple[float, float, int]] = {}
    for gruppe, w in zip(r.fasern.gruppen, r.gruppen_werkstoff):
        if w not in gesetze:
            continue
        for arm, flaeche, dicke in zip(gruppe.arme, gruppe.flaechen, gruppe.dicken):
            da = streifen.get(arm)
            if da is None or flaeche > da[1]:
                streifen[arm] = (dicke, flaeche, w)
    liste = sorted((arm, dicke, w) for arm, (dicke, _, w) in streifen.items())

    def spannung(arm: float, eps: float) -> float:
        _, _, w = min(liste, key=lambda s: max(0.0, abs(arm - s[0]) - s[1] / 2.0))
        return gesetze[w](eps)
    return spannung


def _loeser(q: Querschnitt, psi: float, herkunft: Sequence[Stabgruppe],
            staehle: Mapping[int, Stahlgesetz], namen: Mapping[int, str], *,
            suche: Suche) -> Faserloeser:
    """
    Der Querschnitt in der Zugrichtung ``psi`` als :class:`Faserloeser`.
    Staebe in derselben Tiefe, aus demselben Stahl und im selben Beton werden
    eine Lage -- sie haben dieselbe Dehnung, und das Bild zeigt sie als eine.
    Ihr Arm entlang der Nulllinie ist der Schwerpunkt ihrer Flaechen: mit ihm
    stimmt das Moment um die andere Achse, nach dem die kippende Nulllinie
    sucht. Bis 2026-10-17 fiel er weg, und die Suche fand an einem L Ebenen
    mit einem Moment um die andere Achse. ``suche`` sagt, wie der Loeser
    sucht (:meth:`_Zerlegung.in_richtung`).
    """
    r = q.richtung(psi)
    oben, unten = r.beton
    gruppen: Dict[tuple, List[Tuple[Stab, str]]] = {}
    for b, stab, element in zip(q.bewehrung, r.fasern.staebe, herkunft):
        schluessel = (round(stab.arm, 9), b.werkstoff, b.verdraengt, stab.dicke)
        gruppen.setdefault(schluessel, []).append((stab, element.name))
    staebe: List[Stab] = []
    lagen: List[Stahllage] = []
    for nummer, (schluessel, liste) in enumerate(sorted(gruppen.items(), key=lambda kv: kv[0][0]),
                                                 start=1):
        erster = liste[0][0]
        flaeche = sum(s.flaeche for s, _ in liste)
        quer = sum(s.flaeche * s.quer for s, _ in liste) / flaeche if flaeche > 0.0 else 0.0
        staebe.append(Stab(arm=erster.arm, flaeche=flaeche, gesetz=erster.gesetz,
                           verdraengt=erster.verdraengt, quer=quer, dicke=erster.dicke))
        werkstoff = schluessel[1]
        lagen.append(Stahllage(
            a_s=flaeche, z=erster.arm - oben, stahl=staehle[werkstoff],
            sorte=namen[werkstoff], nummer=nummer,
            text=", ".join(dict.fromkeys(name for _, name in liste))))
    betone = {i: w for i, w in enumerate(q.werkstoffe) if w.c_punkt is not None}
    return Faserloeser(
        querschnitt=Faserquerschnitt(r.fasern.gruppen, staebe), grenzen=r.grenzen,
        oben=oben, unten=unten, lagen=lagen,
        beton=_betonspannung(r, {i: w.gesetz for i, w in betone.items()}), suche=suche)


@dataclass(frozen=True)
class _Zerlegung:
    """Ein Zustand des gezeichneten Querschnitts -- in jeder Zugrichtung zu haben."""

    querschnitt: Querschnitt
    herkunft: Tuple[Stabgruppe, ...]
    """Je Bewehrung das Element, aus dem sie stammt -- fuer die Namen der Lagen."""

    staehle: Mapping[int, Stahlgesetz]
    namen: Mapping[int, str]

    def in_richtung(self, psi: float, *,
                    suche: Suche = SUCHE_DER_ANALYSEN) -> FesteNulllinie:
        """
        Der Zustand in der Zugrichtung ``psi``, mit fester Nulllinie --
        gesucht wie in allen Analysen. Nur die gekippten Richtungen der
        kippenden Nulllinie suchen je Frage frisch (:data:`_JE_FRAGE`).
        """
        return FesteNulllinie(_loeser(self.querschnitt, psi, self.herkunft, self.staehle,
                                      self.namen, suche=suche))


class KippendeNulllinie:
    """
    Die Ebenen eines Zustands des gezeichneten Querschnitts unter reiner
    Biegung: die Nulllinie kippt, bis kein Moment um die andere Achse bleibt.

    Bei einer Neigung ϑ gegen die Zugseite ist es die Aufgabe einer festen
    Richtung (:class:`~opencivil.spannungsanalyse.linie.FesteNulllinie`): die
    Ebene traegt dort den Anteil ``M·cos ϑ`` des Moments, das zu ihr gehoert,
    bzw. ihre Kruemmung hat senkrecht zur Achse der Biegung den verlangten
    Anteil. Uebrig bleibt das Moment um die andere Achse, und gedreht wird,
    bis es null ist -- mit der Suche der Gebrauchsnachweise
    (:func:`~opencivil.nachweis.gebrauchsebene.neigung_suchen`), von der
    Neigung aus, die zuletzt gefunden wurde: die Ebenen einer Linie folgen
    sich in kleinen Schritten. Findet sie von dort nichts, sucht sie noch
    einmal bei der Zugseite selbst: die Ebene ohne Moment, mit der eine Linie
    unter Druck beginnt, kippt an einem L um +29°, ihre gebogenen Ebenen um
    -48° -- zu weit fuer eine Suche, die hoechstens 90° nach jeder Seite
    geht. Bei einem symmetrischen Querschnitt trifft schon die Zugseite, und
    es bleibt bei der Ebene, die die feste Nulllinie faende.

    Gesucht wird in jeder gekippten Richtung mit Illinois (:data:`_JE_FRAGE`),
    wie unter Gebrauchslast: halbiert kostete eine Linie am L des Dateikopfs
    viermal so lang. Ihre Loeser entstehen je Frage frisch, ohne Gedaechtnis
    -- so haengt keine Ebene an der Reihenfolge der Fragen, und Illinois darf
    auch beim Spannungsblock suchen: halbiert brauchte die N-ε-Linie des
    Kastentraegers im Pruefprojekt damit 9 s. Die Zugseite selbst sucht wie
    der Loeser des Paars -- so bleibt ein symmetrischer Querschnitt genau bei
    der Ebene der festen Nulllinie.

    Was am Moment um die andere Achse fehlt, misst jede Frage selbst: zu
    einer Kruemmung das Moment selbst; wo die gekippte Ebene ``M·cos ϑ``
    traegt -- zu N und M, zu einer Dehnung --, dasselbe geteilt durch
    ``cos ϑ``, ``M·sin ϑ + M_quer,ϑ`` (:func:`_rest_beim_moment`). Sonst waere
    bei 90° alles null, das Moment um die andere Achse mit, ohne dass die
    Ebene reine Biegung waere. Ohne Moment aber ist 90° eine Loesung: unter
    Druck kruemmt sich der Unterzug des Beispiels, oben breiter als unten, nur
    senkrecht -- bei Zug links um 90° gekippt. Jenseits von 90° laege die
    Gegenrichtung.

    Jede Antwort bleibt gemerkt. Eine Linie fragt dieselbe Stelle mehrmals --
    ihr Ende beim Suchen, fuer den Bruch, fuer das Fliessen --, und von einer
    anderen Neigung aus faende die Suche am Rand des Gleichgewichts keine
    Ebene mehr: dort gibt es sie nur bei genau einer Neigung. Am L des
    Dateikopfs fehlte so der Fliessbeginn.

    Was die Suche zu N und M findet, ohne das Moment um die andere Achse zu
    treffen -- an einem Sprung des Spannungsblocks --, ist verfehlt
    (:attr:`~opencivil.spannungsanalyse.linie.Dehnungsebene.verfehlt`). Zu
    einer Kruemmung oder einer Dehnung gibt es dann keine Ebene: dort laeuft
    eine Linie ueber die Verformung, und eine verfehlte Ebene truege sie ueber
    ihr Ende hinaus.
    """

    def __init__(self, zerlegung: _Zerlegung, seite: Zugseite) -> None:
        self._zerlegung = zerlegung
        self._psi0 = seite.psi
        self._psi = seite.psi
        """Die Zugrichtung der zuletzt gefundenen Ebene -- von dort sucht die naechste."""
        self._zugseite = zerlegung.in_richtung(seite.psi)
        """Die Zugseite selbst, wie der Loeser des Paars -- fuer jede Frage dieselbe."""
        self._gefunden: Dict[Tuple[str, float, float], Optional[Dehnungsebene]] = {}

    def _gekippt(self, aufgabe: Callable[[FesteNulllinie, float], Optional[Dehnungsebene]],
                 rest: Callable[[Dehnungsebene], float]) -> Optional[Dehnungsebene]:
        """
        Die Ebene ohne Moment um die andere Achse. ``aufgabe(fest, ϑ)`` loest
        die Aufgabe in der Richtung, die um ϑ gegen die Zugseite gekippt ist;
        ``rest(ebene)`` sagt, was ihr am Moment um die andere Achse noch fehlt.
        """
        psi0 = self._psi0
        # Was eine Neigung ergab: die Suche fragt ihren Anfang zweimal.
        gesehen: Dict[float, Tuple[float, Optional[Dehnungsebene]]] = {}

        def fest_in(psi: float) -> FesteNulllinie:
            if psi == psi0:
                return self._zugseite
            return self._zerlegung.in_richtung(psi, suche=_JE_FRAGE)

        def abweichung(psi: float) -> Tuple[float, Optional[Dehnungsebene]]:
            if psi in gesehen:
                return gesehen[psi]
            neigung = psi - psi0
            # Jenseits von 90° laege die Gegenrichtung.
            ebene = aufgabe(fest_in(psi), neigung) if math.cos(neigung) >= 0.0 else None
            if ebene is not None and neigung != 0.0:
                ebene = replace(ebene, neigung=neigung)
            gesehen[psi] = ((math.nan, None) if ebene is None
                            else (rest(ebene) / _massstab(ebene), ebene))
            return gesehen[psi]

        def geprueft(ebene: Dehnungsebene) -> Dehnungsebene:
            # Endet die Suche an einem Sprung, verfehlt die Ebene das Moment
            # um die andere Achse um mehr, als Neigung und Ebene duerfen.
            erlaubt = (QUER_SCHRANKE * _massstab(ebene)
                       + probenschranken(ebene.loeser.querschnitt, ebene.loeser.grenzen)[1])
            return ebene if abs(rest(ebene)) <= erlaubt else replace(ebene, verfehlt=True)

        def von(mitte: float) -> Optional[Dehnungsebene]:
            if abweichung(mitte)[1] is None:
                return None
            return neigung_suchen(abweichung, mitte, QUER_SCHRANKE, geprueft=geprueft)

        gefunden = von(self._psi)
        if (gefunden is None or gefunden.verfehlt) and self._psi != psi0:
            noch_einmal = von(psi0)
            if noch_einmal is not None and (gefunden is None or not noch_einmal.verfehlt):
                gefunden = noch_einmal
        # Weiter sucht man nur von einer Ebene aus, die getroffen hat.
        if gefunden is not None and not gefunden.verfehlt:
            self._psi = psi0 + gefunden.neigung
        return gefunden

    def _gemerkt(self, frage: Tuple[str, float, float],
                 aufgabe: Callable[[FesteNulllinie, float], Optional[Dehnungsebene]],
                 rest: Callable[[Dehnungsebene], float]) -> Optional[Dehnungsebene]:
        """Die Antwort auf ``frage`` -- gesucht beim ersten Mal, danach gemerkt."""
        if frage not in self._gefunden:
            self._gefunden[frage] = self._gekippt(aufgabe, rest)
        return self._gefunden[frage]

    def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]:
        return self._gemerkt(("kraefte", N, M), lambda fest, neigung: fest.zu_kraeften(
            N, M * math.cos(neigung)), _rest_beim_moment(M))

    def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]:
        def aufgabe(fest: FesteNulllinie, neigung: float) -> Optional[Dehnungsebene]:
            cos = math.cos(neigung)
            return fest.zur_kruemmung(chi / cos, N) if cos > KIPPGRENZE else None
        return _getroffen(self._gemerkt(("kruemmung", chi, N), aufgabe, lambda e: e.M_quer))

    def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]:
        return _getroffen(self._gemerkt(("dehnung", eps_m, M), lambda fest, neigung: (
            fest.zur_dehnung(eps_m, M * math.cos(neigung))), _rest_beim_moment(M)))


#: Wie eine gekippte Richtung sucht: mit Illinois, auch beim Spannungsblock --
#: ihr Loeser lebt fuer eine Frage, ein Gedaechtnis ueber Fragen hinweg hat er
#: nicht.
_JE_FRAGE = Illinois(auch_bei_sprung=True)


def _rest_beim_moment(M: float) -> Callable[[Dehnungsebene], float]:
    """
    Was einer gekippten Ebene am Moment um die andere Achse fehlt, wenn sie in
    ihrer Richtung ``M·cos ϑ`` traegt: ``M·sin ϑ + M_quer,ϑ``, das Moment um
    die andere Achse geteilt durch ``cos ϑ`` -- ohne die Null, die der Faktor
    bei 90° braechte.
    """
    def rest(ebene: Dehnungsebene) -> float:
        return ebene.kraefte.M_quer + M * math.sin(ebene.neigung)
    return rest


def _getroffen(ebene: Optional[Dehnungsebene]) -> Optional[Dehnungsebene]:
    """Die Ebene, wenn sie das Moment um die andere Achse trifft -- sonst keine."""
    return None if ebene is None or ebene.verfehlt else ebene


#: Unter diesem ``cos ϑ`` gibt es zu einer Kruemmung keine Neigung mehr: die
#: gekippte Ebene braeuchte ``chi/cos ϑ``.
KIPPGRENZE = 1e-6


def _massstab(ebene: Dehnungsebene) -> float:
    """
    Woran das Moment um die andere Achse gemessen wird: das groessere von M
    und N mit einem Hebel von einem Meter, wie unter Gebrauchslast -- so gilt
    eine Schranke fuer jede Stelle einer Linie.
    """
    return max(abs(ebene.M), abs(ebene.N), 1.0)


# ===========================================================================
# Das Paar je Zugseite
# ===========================================================================


@dataclass(frozen=True)
class Schnittpaar:
    """
    Die beiden Loeser eines gezeichneten Querschnitts in einer Zugrichtung --
    gerissen und ungerissen, wie das :class:`~opencivil.spannungsanalyse.Loeserpaar`
    der Platte --, dazu beide Zustaende in jeder anderen Richtung, fuer die
    kippende Nulllinie. Dazu der Riss am Bruttoquerschnitt und was die
    Herleitung braucht.
    """

    gerissen: Faserloeser
    ungerissen: Faserloeser
    seite: Zugseite
    wahl: Rechenwahl

    querschnitt: Querschnitt
    """Der gerissene Querschnitt im Bruchzustand -- derselbe, aus dem ``gerissen`` stammt."""

    zerlegungen: Tuple[_Zerlegung, _Zerlegung]
    """Gerissen und ungerissen, in jeder Richtung -- fuer die kippende Nulllinie."""

    A: float
    """Flaeche des Bruttoquerschnitts, m²."""

    I: float
    """Traegheitsmoment um die Achse der Biegung, m⁴."""

    brutto: Bruttoquerschnitt
    riss: Rissmoment
    """Das Rissmoment unter reiner Biegung, ohne Normalkraft -- und die Ecke, die zuerst reisst."""

    k_t_zug: float
    """
    Fuer die Rissnormalkraft: ``k_t`` fuer die rissaktive Dicke unter Zug,
    die kleinere Abmessung ``min(h; b)`` (Benutzer, 2026-10-17). Bis dahin die
    ganze Tiefe in Zugrichtung, auch wo der Querschnitt quer dazu schmaler ist.
    """

    breite: float
    """Die Ausdehnung des Betons quer zur Zugrichtung, m."""

    t_zug: float
    """Die rissaktive Dicke unter Zug, ``min(h; b)``, m."""

    E_cm: float
    """Der Modul des Betons der Ecke, die zuerst reisst -- Massstab des aequivalenten Moduls."""

    staehle: Tuple[Baustoff, ...] = ()
    ids: Mapping[str, str] = field(default_factory=dict)
    """
    Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: der Beton der Ecke,
    die zuerst reisst, und A, I -- dazu die Zugfestigkeit jedes Betons unter
    ihrer eigenen ID, denn welche Ecke unter Zug zuerst reisst, haengt am Moment.
    """

    @property
    def einachsig(self) -> bool:
        """Ob die Nulllinie parallel zur Achse der Biegung bleibt, statt zu kippen -- wie die Analyse."""
        return self.brutto.biegung.einachsig

    def ebenen(self) -> Zustaende:
        """Die Ebenen beider Zustaende: kippend, «einachsig» mit fester Nulllinie."""
        if self.einachsig:
            return Zustaende(FesteNulllinie(self.gerissen), FesteNulllinie(self.ungerissen))
        gerissen, ungerissen = (KippendeNulllinie(z, self.seite) for z in self.zerlegungen)
        return Zustaende(gerissen, ungerissen)

    @property
    def W(self) -> float:
        """Das Widerstandsmoment zur Ecke, die unter reiner Biegung zuerst reisst, m³."""
        return self.riss.W

    @property
    def M_Riss(self) -> float:
        """Das Rissmoment ohne Normalkraft."""
        return self.riss.M_Riss

    def rissmoment_bei(self, N: float) -> float:
        """``M_Riss(N) = (f_ct,eff - N/A)·W`` -- Druck hebt es, Zug senkt es."""
        return self.M_Riss - N * self.W / self.A

    def rissnormalkraft(self, M: float) -> Rissnormalkraft:
        """Die Rissnormalkraft beim Moment ``M`` -- an der Ecke, die zuerst reisst."""
        M_y, M_z = self.seite.moment
        return rissnormalkraft(self.brutto, M * M_y, M * M_z,
                               k_t=self.k_t_zug, A=self.A)

    def rissnormalkraft_bei(self, M: float) -> float:
        """``N_Riss(M) = (f_ct,eff,t - σ_M)·A`` -- ein Moment senkt sie, gleich in welche Richtung."""
        return self.rissnormalkraft(M).N_Riss

    @property
    def I_c(self) -> float:
        """
        Der reine Betonquerschnitt fuer den aequivalenten Modul: ``I`` -- kippt
        die Nulllinie, ``I - I_yz²/I_quer``, siehe Dateikopf.
        """
        if self.einachsig:
            return self.I
        b = self.brutto
        return self.I - b.I_yz ** 2 / (b.I_z if self.seite.um_y else b.I_y)

    @property
    def A_c(self) -> float:
        return self.A

    # -- Was die Herleitung nur vom gezeichneten Querschnitt weiss -----------

    #: Wo die Mitteldehnung gilt -- dort greift N an.
    bezugsort = "im Schwerpunkt"

    def tiefe(self, w: Zwischenwerte, ein: Callable[[str], "Wert"]) -> "Wert":
        """Die Ausdehnung des Betons in Zugrichtung -- aus der Zeichnung, kein Wert des Rechenwerks."""
        return w.laenge("h", "h", self.gerissen.h, "Ausdehnung des Betons in Zugrichtung")

    def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie,
                        ein: Callable[[str], "Wert"], h: "Wert") -> None:
        """Der Riss am Bruttoquerschnitt: Widerstandsmoment, Zugfestigkeit, Risskraft."""
        A, I = ein("A"), ein("I")
        momente = linie.art is Analyseart.MOMENT_KRUEMMUNG
        if self.einachsig:
            oben, unten = self.seite.raender
            v = w.laenge("v_z", "v_z", self.gerissen.unten,
                          "Abstand des gezogenen Rands vom Schwerpunkt")
            p.erklaerung(
                f"Die Nulllinie bleibt parallel zur Achse der Biegung: gezogen wird der "
                f"Rand {unten}, gedrückt der Rand {oben}. Das Moment um die andere Achse, "
                f"das ein unsymmetrischer Querschnitt dabei weckt, zählt nicht. Am "
                f"Bruttoquerschnitt reisst der gezogene Rand, wenn N/A + M/W = f_ct,eff; "
                f"W gehört zu diesem Rand, v_z ist sein Abstand vom Schwerpunkt.")
            W = w.wert("W", "W", Groesse.aus_si(self.W, MIO_MM3), stellen=2)
            p.formel(W, r"\frac{@I}{@v}", {"I": I, "v": v},
                     titel="Widerstandsmoment zum gezogenen Rand")
        else:
            p.erklaerung(
                "Unter reiner Biegung kippt die Nulllinie, bis kein Moment um die andere "
                "Achse bleibt. Am ungerissenen Bruttoquerschnitt hängt die Spannung dann "
                "auch vom Deviationsmoment I_yz ab, und es reisst die Ecke zuerst, die ihre "
                "Zugfestigkeit zuerst erreicht – bei einem unsymmetrischen Querschnitt eine "
                "Ecke, nicht der ganze Rand.")
            protokoll_spannung_ungerissen(p, self.brutto.biegung)
        if momente:
            ecke = self.riss.ecke
            if not self.einachsig:
                protokoll_ecke(p, ecke)
                W = protokoll_widerstandsmoment(p, w, self.brutto, ecke, self.W,
                                                *self.seite.moment)
            f_ct_eff = protokoll_zugfestigkeit(
                p, w, k_t=self.riss.k_t, f_ct_eff=self.riss.f_ct_eff, h=h,
                f_ctm=ein(ecke.stoff.id_von("f_ctm")), teiler=MOMENTENTEILER,
                referenz="SIA 262:2025, 4.4.1.3", titel="Beiwert für die Tiefe in Biegerichtung")
            p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                     r"\left(@f - \frac{@N}{@A}\right) \cdot @W",
                     {"f": f_ct_eff, "N": w.kraft("N", "N", linie.fest), "A": A, "W": W},
                     titel="Rissmoment bei der Normalkraft")
            return
        p.erklaerung(
            "Dieselbe Rissbedingung, nach der Normalkraft aufgelöst. Unter Zug gilt "
            "k_t für die rissaktive Dicke t, die kleinere Abmessung des Betons -- "
            "nicht für h/3 wie beim Rissmoment. Ein negatives Moment zieht den anderen "
            "Rand: dann gilt dessen Abstand.")
        t = w.laenge("t", "t", self.t_zug)
        p.formel(t, r"\min\left[@h;\ @b\right]",
                 {"h": h, "b": w.laenge("b", "b", self.breite,
                                         "Ausdehnung des Betons quer zur Zugrichtung")},
                 titel="Rissaktive Dicke unter Zug: die kleinere Abmessung",
                 name="Rissaktive Dicke des gezeichneten Querschnitts")
        M = linie.fest
        zug = self.rissnormalkraft(M)
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=self.k_t_zug, f_ct_eff=zug.f_ct_eff, h=t,
            f_ctm=ein(zug.ecke.stoff.id_von("f_ctm")), teiler=1,
            referenz="SIA 262:2025, 4.4.2", titel="Beiwert für die rissaktive Dicke")
        N_Riss = w.kraft("N_Riss_M", "N_{Riss}(M)", linie.riss)
        M_wert = w.moment("M", "M", M)
        if self.einachsig:
            rand = v if M >= 0.0 else w.laenge(
                "v_d", "v_d", self.gerissen.oben,
                "Abstand des gedrückten Rands vom Schwerpunkt, negativ")
            p.formel(N_Riss, r"\left(@f - \frac{@M \cdot @v}{@I}\right) \cdot @A",
                     {"f": f_ct_eff, "M": M_wert, "v": rand, "I": I, "A": A},
                     titel="Rissnormalkraft beim Moment")
            return
        sigma = w.spannung("sigma_M", r"\sigma_M", zug.sigma_M, "aus dem Moment allein", stellen=2)
        if M != 0.0 and zug.sigma_M > 0.0:
            # Das Moment zieht die Ecke: σ_M = |M|/W, mit W in der Richtung,
            # in die es zieht.
            M_y, M_z = self.seite.moment
            protokoll_ecke(p, zug.ecke)
            W = protokoll_widerstandsmoment(
                p, w, self.brutto, zug.ecke, abs(M) / zug.sigma_M,
                *((M_y, M_z) if M > 0.0 else (-M_y, -M_z)))
            p.formel(sigma, r"\frac{\left|@M\right|}{@W}", {"M": M_wert, "W": W},
                     titel="Spannung aus dem Moment an der Ecke, die zuerst reisst")
        else:
            p.wert(sigma, titel="Spannung aus dem Moment an der Ecke, die zuerst reisst")
        p.formel(N_Riss, r"\left(@f - @sigma\right) \cdot @A",
                 {"f": f_ct_eff, "sigma": sigma, "A": A}, titel="Rissnormalkraft beim Moment")

    def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: Grenzzustand,
                                   oben: "Wert", unten: "Wert", h: "Wert") -> None:
        """Die Dehnung im Schwerpunkt am Ende -- dort greift N an; ``h`` senkrecht zur Nulllinie."""
        p.formel(w.dehnung("eps_mu", r"\varepsilon_{m,u}", bruch.verformung),
                 r"@eps_oben + \left(@eps_unten - @eps_oben\right) \cdot \frac{@v}{@h}",
                 {"eps_oben": oben, "eps_unten": unten,
                  "v": w.laenge("v_o", "v_o", -bruch.ebene.loeser.oben,
                                "Abstand des oberen Rands vom Schwerpunkt"),
                  "h": h},
                 titel="Grösste Dehnung im Schwerpunkt")

    def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool,
                         ein: Callable[[str], "Wert"], h: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des aequivalenten Moduls: der Bruttoquerschnitt."""
        if not momente:
            bezug = w.flaeche("A_c", "A_c", self.A)
            p.erklaerung("Der reine Betonquerschnitt ist der Bruttoquerschnitt: A_c = A.")
            p.wert(bezug, titel="Reiner Betonquerschnitt")
            return bezug
        bezug = w.wert("I_c", "I_c", Groesse.aus_si(self.I_c, MIO_MM4), stellen=1)
        if self.einachsig:
            p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt, um die "
                         f"Achse der Biegung: I_c = {ein('I').symbol.replace('_', '')}.")
            p.wert(bezug, titel="Reiner Betonquerschnitt")
            return bezug
        b = self.brutto
        quer = w.wert("I_quer", "I_z" if self.seite.um_y else "I_y",
                      Groesse.aus_si(b.I_z if self.seite.um_y else b.I_y, MIO_MM4), stellen=1)
        p.erklaerung(
            "Der reine Betonquerschnitt ist der Bruttoquerschnitt. Unter reiner Biegung "
            "kippt auch seine Nulllinie, und senkrecht zur Achse der Biegung krümmt er "
            "sich darum stärker, als I allein sagt: wie ein Querschnitt mit I_c. Sonst "
            "zeigte ein ungerissener unsymmetrischer Querschnitt schon seiner Form wegen "
            "einen kleineren Modul.")
        p.formel(bezug, r"@I - \frac{@Iyz^{2}}{@quer}",
                 {"I": ein("I"), "Iyz": w.wert("Iyz", "I_{yz}", Groesse.aus_si(b.I_yz, MIO_MM4), 1),
                  "quer": quer},
                 titel="Reiner Betonquerschnitt, Nulllinie gekippt")
        return bezug


def schnittpaar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float],
                wahl: Rechenwahl) -> Optional[Schnittpaar]:
    """
    Das Loeserpaar eines gezeichneten Querschnitts in einer Zugrichtung --
    ``None`` ohne Bewehrung. ``wert`` liefert zu einer Wert-ID die Zahl in SI,
    aus einer Loesung.
    """
    if not analyse.gruppen:
        return None
    zerlegungen = []
    for ungerissen in (False, True):
        q, herkunft, staehle = analyse.querschnitt(wert, wahl, ungerissen=ungerissen)
        zerlegungen.append(_Zerlegung(q, tuple(herkunft), staehle,
                                      {i: w.name for i, w in enumerate(q.werkstoffe)}))
    gerissen, ungerissen = (z.in_richtung(seite.psi) for z in zerlegungen)
    q = zerlegungen[0].querschnitt

    # Der Riss am Bruttoquerschnitt; der Beton der Ecke, die zuerst reisst,
    # gibt E_cm und die Gesetze der Herleitung.
    brutto = bruttoquerschnitt(analyse, wert)
    riss = rissmoment(brutto, *seite.moment)
    stoff = riss.ecke.stoff
    I_id = analyse.id_von("I_y" if seite.um_y else "I_z")
    ids = {"E_cm": stoff.id_von("E_cm"), "f_c": stoff.id_von(wahl.satz.beton),
           "eps_c1d": stoff.id_von("eps_c1d"), "eps_c2d": stoff.id_von("eps_c2d"),
           "f_ctm": stoff.id_von("f_ctm"), "A": analyse.id_von("A"), "I": I_id,
           **{s.id_von("f_ctm"): s.id_von("f_ctm") for _, s in analyse.beton_ecken}}
    quer = [p[0 if seite.um_y else 1] for p, _ in analyse.beton_ecken]
    breite = (max(quer) - min(quer)) * 1e-3
    t_zug = rissaktive_dicke(h=gerissen.loeser.h, b=breite, zug=True)
    stahlstoffe = tuple({g.stahl.id: g.stahl for g in analyse.gruppen}.values())
    return Schnittpaar(
        gerissen=gerissen.loeser, ungerissen=ungerissen.loeser, seite=seite, wahl=wahl,
        querschnitt=q, zerlegungen=tuple(zerlegungen),
        A=wert(ids["A"]), I=wert(I_id), brutto=brutto, riss=riss,
        k_t_zug=beiwert_dicke(t_zug), breite=breite, t_zug=t_zug,
        E_cm=abs(wert(ids["E_cm"])), staehle=stahlstoffe, ids=ids)
