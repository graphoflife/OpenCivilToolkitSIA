"""
opencivil/nachweis/spannungsbegrenzung.py -- Stahlspannung unter Gebrauchslasten.

VERANTWORTUNG:
Bestimmt je Lastfall die Stahlspannung im gerissenen Querschnitt und haelt sie
gegen eine Grenze. Zwei Nachweise teilen sich diese Rechnung:

* **Gegen Fliessen**, unter *haeufiger* Einwirkung: ``sigma_s <= f_yd - 80
  N/mm²`` (SIA 262:2025, Tabelle 17). Nur bei erhoehter und hoher
  Anforderung -- bei normaler steht in der Tabelle ein Strich.
* **Aus der Rissbreite**, unter *quasi-staendiger* Einwirkung:
  ``sigma_s <= sigma_s,adm``, dieselbe zulaessige Spannung wie bei der
  Zwaengung -- ``f_yk`` bei normaler Anforderung, die Wurzelformel mit
  ``w_nom`` bei erhoehter und hoher. Immer gefuehrt.

EINE KLASSE, ZWEI GRENZEN:
Die Rechnung ist in beiden Faellen dieselbe: derselbe Loeser, dieselbe
Fallschleife, dieselbe groesste Zugdehnung. Verschieden ist allein die
Grenze -- ihre Zahl, die Eingaben, aus denen sie entsteht, und ihr Absatz in
der Herleitung. Die drei gehoeren zusammen und stehen darum in einer Klasse,
die dem Nachweis mitgegeben wird
(:class:`~opencivil.nachweis.spannungsgrenzen.Spannungsgrenze`, mit den
Stellen in ihrem eigenen Modul). Zwei Klassen mit kopiertem Kern waeren genau
die Fehlerklasse, vor der ``zustand2.py`` warnt: zwei Nachweise, die fuer
denselben Querschnitt verschiedene sigma_s melden.

EINE KLASSE, ZWEI GEOMETRIEN:
Dasselbe gilt fuer die Platte und den gezeichneten Querschnitt. Gemessen
wird an **Stellen** -- bei der Platte an ihren Lagen, beim gezeichneten
Querschnitt an jedem Stab --, und was der Nachweis von der Geometrie wissen
muss, sagt ihm ein schmaler Anschluss (:class:`Stahlspannungsort`): die
Ebene je Fall, die Stellen, die Grenze aus der Rissbreite und die Absaetze,
die nur die Geometrie schreiben kann. Welche Stelle massgebend ist, wie
verglichen und geurteilt wird, steht einmal, hier. Bis 2026-10-17 stand der
gezeichnete Querschnitt in einer Abschrift dieser Klasse daneben, mit
kopiertem Urteil und kopiertem Vergleich.

WIE DIE SPANNUNG ENTSTEHT:
Ueber :mod:`opencivil.nachweis.querschnittsloeser`: gesucht wird die
Dehnungsebene, die ``M_Ed`` und ``N_Ed`` des Lastfalls im Gleichgewicht
haelt -- am gezeichneten Querschnitt mit gedrehter Nulllinie
(:mod:`opencivil.nachweis.gebrauchsebene`). Der Beton nimmt keinen Zug auf.
Womit gerechnet wird, waehlt das Kapitel
(:class:`~opencivil.querschnitt.gesetzwahl.Rechenwahl`): die Kriechzahl, den
Wertesatz und die Rechenart. Die Vorgabe ist, wie bis 2026-10-09 fest:
**elastisch** -- der Beton im Druck linear mit dem wirksamen Modul
``E_cm/(1+phi)`` -- mit den **charakteristischen** Festigkeiten: der Stahl
fliesst bei ``f_yk``, der Beton traegt hoechstens ``f_ck``.

Die gedrueckte Bewehrung wirkt mit, wie im Querschnitt -- nur in der
Rechenart «Handrechnung» nicht. Gemessen wird an der am staerksten
gezogenen Stelle. (Bis 2026-10-09 stand hier, nur gezogene Bewehrung zaehle;
gerechnet wurde aber schon damals mit beiden.)

WENN DER STAHL FLIESST:
Auf dem Plateau bleibt die Spannung bei ``f_yk`` stehen. Bei normaler
Anforderung ist aber gerade ``f_yk`` die Grenze -- ein fliessender Stahl
haette dann ``sigma_s = sigma_s,adm`` und stuende mit Erfuellungsgrad 1.00
als «erfuellt» in der Tabelle. Darum wird an der **Dehnung** gemessen::

    alpha = sigma_s,adm / (E_s * eps_s)

Solange der Stahl elastisch bleibt, ist ``E_s * eps_s`` genau ``sigma_s``, und
das ist der uebliche Spannungsvergleich, Bit fuer Bit. Fliesst er, waechst die
Dehnung weiter, waehrend die Spannung stehen bleibt: der Nachweis faellt
durch, und zwar um so deutlicher, je weiter die Bewehrung ueber die Grenze
gedehnt ist. Das braucht auch die Bewehrungssuche -- ein Erfuellungsgrad, der
auf dem Plateau festsitzt, zeigt ihr keine Richtung.

WAS IN DER MITSCHRIFT STEHT:
Der **Ablauf** der Suche (aus :func:`querschnittsloeser.protokoll_verfahren`),
die Festlegungen dahinter -- Kriechzahl, Werkstoffgesetze, Grenze --, dann je
Fall die gefundene Ebene und die **Probe**: mit diesem ``eps_m`` und ``chi``
entstehen genau ``N_Ed`` und ``M_Ed``. Die einzelnen Halbierungen stehen nicht
da; sie sind kein Rechenschritt, sondern der Weg zu einem, und belegt wird der
durch die Probe.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Sequence, Tuple, Type

from opencivil.core.berechnung import (
    NICHT_FUEHRBAR, Ausfuehrung, Ausgang, Eingabebezug, Eingaben, Fallausgang, Fallbefund,
    Nachweis, NachweisUrteil, Vergleich, grad_def,
)
from opencivil.core.einheiten import KN, KNM, Groesse
from opencivil.core.latex import als_text, angabe, bedingung, vergleich
from opencivil.core.protokoll import Abschnitt, Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.material.basis import Baustoff
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis.mindestbewehrung import (
    protokoll_zulaessige_stahlspannung, zulaessige_stahlspannung,
)
from opencivil.nachweis.querschnittsloeser import (
    Ebene, Querschnittsloeser, protokoll_verfahren, protokoll_wirksamer_modul,
)
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz
from opencivil.nachweis.rechenwahl import (
    Betonkennwerte, betonbezuege, bezuege_vereinen, gesetze, lagenbezuege, protokoll_gesetze,
    protokoll_rechenwahl, staehle, stahlbezuege, stahllagen, stahlname,
)
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.spannungsgrenzen import (
    GrenzeAusRissbreite, Grenzen, Spannungsgrenze, Stahlzustand, Stelle, je_stahl, nach_stahl,
)
from opencivil.nachweis.zustand2 import wertigkeit
from opencivil.querschnitt.platte import Richtung

#: Womit die Stahlspannungen rechnen, wenn das Kapitel nichts anderes waehlt:
#: elastisch, mit charakteristischen Werten -- ein Gebrauchsnachweis fragt,
#: was der Querschnitt tut, nicht was er darf.
VORGABE = Rechenwahl(satz=Werkstoffsatz.CHARAKTERISTISCH, art=Rechenart.ELASTISCH)


@dataclass(frozen=True)
class Gebrauchsfall:
    """
    Eine Schnittgroessenkombination unter Gebrauchslast -- an der Platte.

    Haeufig oder quasi-staendig -- das sagt nicht der Fall, sondern der
    Nachweis, dem er mitgegeben wird. Der gezeichnete Querschnitt nimmt
    seinen :class:`~opencivil.querschnitt.analyse.Lastfall`.
    """

    name: str
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


# ===========================================================================
# Was jede Stahlspannung festlegt
# ===========================================================================


def protokoll_festlegungen(p: Protokoll, wahl: Rechenwahl) -> None:
    """
    Die ersten beiden der drei Festlegungen hinter jeder Stahlspannung:
    Kriechen und Werkstoffgesetze. Die dritte, die Grenze, schreibt danach
    die Grenze selbst (:meth:`Spannungsgrenze.festlegung`). Fuer die Platte
    und den gezeichneten Querschnitt dieselben Absaetze.
    """
    p.titel("Welche Werte angesetzt werden", ebene=3)
    p.erklaerung(
        "Drei Festlegungen stecken in jeder Zahl unten, und alle drei "
        "sind Auslegung der Norm und nicht Rechnung. Erstens das "
        "Kriechen: angesetzt wird das φ dieses Kapitels. Ein grösseres φ "
        "weicht den Beton auf, die Druckzone wächst, der Hebelarm wird "
        "kleiner und die Stahlspannung damit grösser; mit φ = 0 gehen die "
        "Spannungen zurück, und der Nachweis geht leichter auf. Mit dem "
        "Spannungsblock hängt kein Gesetz am Modul – dort wirkt φ nicht."
    )
    if wahl.satz is Werkstoffsatz.CHARAKTERISTISCH:
        p.erklaerung(
            "Zweitens die Werkstoffgesetze: sie rechnen mit den "
            "charakteristischen Festigkeiten. Der Stahl ist linear bis f_yk "
            "und fliesst dann, der Beton trägt höchstens f_ck. Ein "
            "Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was "
            "er darf – der Teilsicherheitsbeiwert gehört in die "
            "Tragsicherheit. Läge das Plateau bei f_yd, bliebe jede "
            "Stahlspannung darunter, und eine Grenze darüber könnte nie "
            "überschritten werden."
        )
    else:
        p.erklaerung(
            "Zweitens die Werkstoffgesetze: sie rechnen hier mit den "
            "Bemessungswerten f_cd und f_yd. Das Plateau des Stahls liegt "
            "damit bei f_yd – eine Stahlspannung darüber gibt es nicht, und "
            "eine Grenze darüber kann nicht überschritten werden."
        )
    if wahl.art.mit_block:
        p.erklaerung(
            "Mit dem Spannungsblock trägt der Beton unter (1 − 0.85)·ε_c2d "
            "nichts. Unter Gebrauchslast liegt die Druckresultierende damit "
            "am Rand, und der Hebelarm wird beinahe d – die Stahlspannung "
            "kleiner, als der Querschnitt sie hat. Der Block ist ein Modell "
            "für den Bruch.")


#: Was verglichen wird, wenn die Bewehrung fliesst -- siehe Dateikopf.
VERGLEICH_BEIM_FLIESSEN = (
    "Fliesst die Bewehrung, bleibt ihre Spannung am Plateau stehen, "
    "während die Dehnung weiterwächst. Verglichen wird dann die "
    "Dehnung: ε_s gegen ε_s,adm = σ_s,adm / E_s. Solange der Stahl "
    "elastisch bleibt, ist das genau der Spannungsvergleich; fliesst "
    "er, fällt der Nachweis durch, und zwar um so deutlicher, je "
    "weiter er gedehnt ist."
)


# ===========================================================================
# Wo die Stahlspannung nachgewiesen wird
# ===========================================================================


class Stahlebene(Protocol):
    """Was der Nachweis von der Ebene eines Falls liest -- je Stelle Dehnung und Spannung."""

    konvergiert: bool
    verfehlt: bool
    eps_s: Tuple[float, ...]
    sigma_s: Tuple[float, ...]


class Stahlspannungsort(ABC):
    """
    Was :class:`Spannungsbegrenzung` von seiner Geometrie wissen muss -- und
    nicht mehr: die Platte je Tragrichtung (:class:`PlattenStellen`), der
    gezeichnete Querschnitt
    (:class:`~opencivil.nachweis.qa_gebrauch.AnalyseStellen`).

    Je Rechnung bereitet der Ort seinen Zustand vor (:meth:`zustand`): die
    Stellen, an denen gemessen wird, und was er sonst braucht. Je Fall findet
    er die Ebene (:meth:`ebene`). Die Grenze aus der Rissbreite gehoert ihm
    (:meth:`aus_rissbreite`), und die Absaetze, die nur er schreiben kann.

    Was in Kennungen, Zeichen und Titeln anders heisst, sagen die Woerter
    unten -- so blieben Bericht und Kennungen beider Geometrien, wie sie vor
    der Zusammenlegung waren (2026-10-17).
    """

    name: str
    abschnitt: Abschnitt

    #: Die Tragrichtung, wo es eine gibt -- sie steht im Namen jedes Urteils.
    richtung: Optional[Richtung] = None
    #: Im Index des Erfuellungsgrads nach der Grenze -- bei der Platte «,x».
    zeichen: str = ""
    #: Im Titel des Nachweises nach «Einwirkung» -- bei der Platte « in x-Richtung».
    beschriftung: str = ""
    #: Im Titel der Herleitung -- bei der Platte « – in x-Richtung».
    titelzusatz: str = ""
    #: Der Index an ε_s und σ_s -- bei der Platte «{s,x}».
    stahlindex: str = "s"
    #: Woran gemessen wird: der zweite Satz der Herleitung.
    messung: str = ""
    #: Mit welchem Durchmesser die Grenze aus der Rissbreite gilt, als Satz.
    regel_der_rissbreite: str = ""

    @abstractmethod
    def basis(self, grenze: Type[Spannungsgrenze]) -> str:
        """Die Kennung des Nachweises mit dieser Grenze."""

    @abstractmethod
    def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]:
        """Was die Rechnung liest, mit jeder Grenze."""

    def stahlbezuege(self, kennwerte: Sequence[str]) -> List[Eingabebezug]:
        """Diese Kennwerte je Stahl -- wo sie nicht schon in :meth:`bezuege` stehen."""
        return []

    def rissbreitenbezuege(self) -> List[Eingabebezug]:
        """Was die Grenze aus der Rissbreite liest, ueber :meth:`bezuege` hinaus."""
        return []

    @abstractmethod
    def zustand(self, e: Eingaben, wahl: Rechenwahl) -> Stahlzustand:
        """Was eine Rechnung braucht, aus ihren Eingaben."""

    @abstractmethod
    def aus_rissbreite(self, zustand: Stahlzustand, e: Eingaben, p: Protokoll,
                       anforderung: Rissanforderung, basis: str) -> Grenzen:
        """``sigma_s,adm`` jeder Stelle aus der Rissbreite -- gerechnet und hergeleitet."""

    @abstractmethod
    def ebene(self, zustand: Stahlzustand, fall) -> Stahlebene:
        """Die Dehnungsebene, die den Fall traegt -- auch eine ohne Gleichgewicht."""

    @abstractmethod
    def keine_ebene(self, fall) -> str:
        """Was dasteht, wo sich zum Fall keine Ebene findet."""

    @abstractmethod
    def begruendung(self, zustand: Stahlzustand, erg: "Fallergebnis") -> str:
        """Die Begruendung des Urteils -- mit dem Satz des Vergleichs."""

    @abstractmethod
    def dehnungsgrenze(self, basis: str, werte: Zwischenwerte, erg: "Fallergebnis") -> Wert:
        """``eps_s,adm`` als Wert, fuer den Vergleich, wenn der Stahl fliesst."""

    def protokoll_vor_den_grenzen(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand,
                                  wahl: Rechenwahl, phi: Wert, basis: str) -> None:
        """Was vor der Grenze steht -- bei der Platte der wirksame Modul."""

    @abstractmethod
    def protokoll_gesetze(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand,
                          wahl: Rechenwahl, basis: str) -> None:
        """Die Werkstoffgesetze, wie gerechnet wird."""

    @abstractmethod
    def protokoll_verfahren(self, p: Protokoll, zustand: Stahlzustand,
                            wahl: Rechenwahl) -> None:
        """Wie die Dehnungsebene gefunden wird."""

    @abstractmethod
    def protokoll_einwirkung(self, p: Protokoll, fall, index: str) -> None:
        """Die Schnittgroessen des Falls."""

    @abstractmethod
    def protokoll_ebene(self, p: Protokoll, werte: Zwischenwerte, zustand: Stahlzustand,
                        grenzen: Grenzen, erg: "Fallergebnis") -> None:
        """Die gefundene Ebene, ihre Probe und was der Ort dazu sagt."""


@dataclass
class Fallergebnis(Fallausgang):
    """Was der Nachweis fuer einen Lastfall gefunden hat."""

    fall: object
    """Bei der Platte ein :class:`Gebrauchsfall`, am gezeichneten Querschnitt ein Lastfall."""

    ebene: Optional[Stahlebene] = None
    """Die Ebene, die der Ort fand -- fehlt nur ohne Bewehrung."""

    stelle: int = 0
    """Die massgebende Stelle: die gezogene mit dem kleinsten Erfuellungsgrad."""

    eps_s: float = 0.0
    """Ihre Dehnung -- die groesste Zugdehnung, wo nur ein Stahl liegt."""

    sigma_s: float = 0.0
    """Die Spannung dazu, in Pa -- auf dem Plateau ``f_yk``."""

    E_s: float = 0.0
    sigma_s_adm: float = 0.0
    eps_s_adm: float = 0.0
    """``sigma_s_adm / E_s`` -- dagegen wird gemessen, wenn der Stahl fliesst."""

    eps_y: float = 0.0
    """Die Fliessdehnung ``f_s / E_s``."""

    stahl: Optional[Baustoff] = None
    """
    Der Stahl der massgebenden Stelle -- seine Grenze, sein ``E_s`` und seine
    Fliessdehnung gelten. Mit verschiedenen Staehlen ist massgebend die
    gezogene Stelle mit dem kleinsten Erfuellungsgrad, nicht die am
    staerksten gedehnte.
    """

    konvergiert: bool = True
    ausgang: Ausgang = NICHT_FUEHRBAR
    """
    Was gegeneinander steht: Spannungen, solange der Stahl elastisch bleibt.
    Fliesst er, Dehnungen -- sonst stuende ``f_yk`` neben ``f_yk`` und
    daneben «nicht erfuellt», richtig gerechnet und doch nicht zu lesen.
    Entschieden wird das einmal, in :meth:`Spannungsbegrenzung._vergleich`.
    Nicht fuehrbar ohne Bewehrung und ohne Gleichgewichtslage.
    """

    satz: str = ""
    """Der Vergleich als Satz, fuer die Begruendung."""

    begruendung: str = ""

    @property
    def fliesst(self) -> bool:
        """Ob die massgebende Stelle auf dem Plateau liegt."""
        return self.eps_s > self.eps_y


# ===========================================================================
# Die Platte
# ===========================================================================


@dataclass(frozen=True)
class _Plattenzustand(Stahlzustand):
    """Dazu der Loeser der Tragrichtung und die Kennwerte des Betons."""

    loeser: Querschnittsloeser
    w: Betonkennwerte


class PlattenStellen(Stahlspannungsort):
    """
    Die Platte in einer Tragrichtung: Stellen sind ihre Lagen -- in der
    Handrechnung je Seite eine. Die Grenze aus der Rissbreite gilt mit dem
    dicksten Stab der Tragrichtung, fuer jede Lage dieselbe.

    **Massgebend ist der dickste Stab der Tragrichtung.** Anders als bei der
    Rissnormalkraft, wo je Lage ein Urteil faellt und die Grenze zu *dieser*
    Lage gehoert: hier kommt sigma_s aus dem Faserintegral ueber den ganzen
    Querschnitt, und welche Lage die groesste Zugspannung traegt, wechselt mit
    dem Lastfall -- bei einem Feldmoment die untere, bei einem Stuetzmoment
    die obere. Der dickste Stab gibt die kleinste zulaessige Spannung; das
    liegt fuer jede der beiden auf der sicheren Seite.
    """

    regel_der_rissbreite = (
        "Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die "
        "grösste Zugspannung trägt, wechselt mit dem Lastfall – bei einem "
        "Feldmoment die untere, bei einem Stützmoment die obere –, und der "
        "dickste Stab gibt die kleinste zulässige Spannung. Das liegt für "
        "beide auf der sicheren Seite.")

    def __init__(self, querschnitt, richtung: Richtung) -> None:
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"liegt keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.staehle = tuple(staehle(self.posten))
        """
        Die Staehle dieser Richtung -- je Seite einer, der Editor laesst sie
        verschieden waehlen. Jeder bekommt seine eigene Grenze.
        """
        self.marken = [f"{lage.nummer}{art.kuerzel}" for lage, art, _, _, _ in self.posten]
        self.name = querschnitt.name
        self.abschnitt = querschnitt.abschnitt
        r = richtung.value
        self.zeichen = f",{r}"
        self.beschriftung = f" {richtung.beschriftung}"
        self.titelzusatz = f" – {richtung.beschriftung}"
        self.stahlindex = f"{{s,{r}}}"
        mehrere = (" Liegen unten und oben verschiedene Stähle, hat jeder seine "
                   "Grenze, und massgebend ist die gezogene Lage mit dem kleinsten "
                   "Erfüllungsgrad." if len(self.staehle) > 1 else "")
        self.messung = (
            f"Gerechnet wird am gerissenen Querschnitt: der "
            f"Beton nimmt keinen Zug auf. Die Bewehrung wirkt auf Zug und auf "
            f"Druck – nur in der Handrechnung zählt die gedrückte nicht. "
            f"Gemessen wird an der am stärksten gezogenen Lage.{mehrere}")

    def basis(self, grenze: Type[Spannungsgrenze]) -> str:
        return f"{self.querschnitt.id}.nachweis.{grenze.idteil}.{self.richtung.value}"

    def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]:
        q = self.querschnitt
        return [
            Eingabebezug("h", q.id_von("h")),
            Eingabebezug("b", q.id_breite(self.richtung)),
        ] + betonbezuege(wahl.satz, q.beton) + lagenbezuege(self.posten, wahl.satz)

    def stahlbezuege(self, kennwerte: Sequence[str]) -> List[Eingabebezug]:
        return stahlbezuege(self.posten, kennwerte)

    def rissbreitenbezuege(self) -> List[Eingabebezug]:
        return stahlbezuege(self.posten, ("f_yk", "E_s")) + [
            Eingabebezug("f_ctm", self.querschnitt.beton.id_von("f_ctm")),
        ] + [
            Eingabebezug(f"dm_{m}", self.querschnitt.id_von(f"lage.{m}.phi"))
            for m in self.marken
        ]

    def zustand(self, e: Eingaben, wahl: Rechenwahl) -> _Plattenzustand:
        w = Betonkennwerte.aus_eingaben(e, wahl.satz)
        lagen = stahllagen(self.posten, wahl.satz, e.si_nach_id())
        loeser = gesetze(wahl, w).loeser(h=e.g("h").si, b=e.g("b").si, lagen=lagen)
        nach_sorte = {kennung_aus(s.id): s for s in self.staehle}
        return _Plattenzustand(
            stellen=tuple(Stelle(stahl=nach_sorte[l.sorte], E_s=l.stahl.E_s, eps_y=l.stahl.eps_yd)
                          for l in loeser.lagen),
            staehle=self.staehle, loeser=loeser, w=w)

    def aus_rissbreite(self, zustand: Stahlzustand, e: Eingaben, p: Protokoll,
                       anforderung: Rissanforderung, basis: str) -> Grenzen:
        f_ctm = e.g("f_ctm").si
        durchmesser = max(e.g(f"dm_{m}").si for m in self.marken)
        werte = Zwischenwerte(basis)
        dm = werte.laenge("dm_max", r"\varnothing_{max}", durchmesser, stellen=0)
        if anforderung.rissbreite is not None:
            p.wert(dm, titel="Dickster Stab der Tragrichtung")

        grenzen = nach_stahl(zustand, lambda stahl: zulaessige_stahlspannung(
            anforderung=anforderung, f_yk=e.g(stahlname("f_yk", stahl)).si,
            E_s=e.g(stahlname("E_s", stahl)).si, f_ctm=f_ctm, durchmesser=durchmesser))
        for gruppe in grenzen.gruppen:
            stahl = gruppe.stahl
            name, symbol = je_stahl("sigma_s_adm", r"\sigma_{s,adm}", stahl, self.staehle)
            gruppe.wert = Zwischenwerte(basis).spannung(name, symbol, gruppe.sigma, "Widerstand")
            protokoll_zulaessige_stahlspannung(
                p, gruppe.wert, anforderung=anforderung, f_yk=e[stahlname("f_yk", stahl)],
                E_s=e[stahlname("E_s", stahl)], f_ctm=e["f_ctm"], durchmesser=dm,
                basis=basis if len(self.staehle) == 1 else f"{basis}.{kennung_aus(stahl.id)}",
                referenz=GrenzeAusRissbreite.referenz)
        return grenzen

    def ebene(self, zustand: _Plattenzustand, fall: Gebrauchsfall) -> Ebene:
        return zustand.loeser.loese(N_Ed=fall.N_Ed.si, M_Ed=fall.M_Ed.si)

    def keine_ebene(self, fall: Gebrauchsfall) -> str:
        return (f"Keine Dehnungsebene für M = {fall.M_Ed.formatiert(1, KNM)} kNm, "
                f"N = {fall.N_Ed.formatiert(1, KN)} kN → nicht aufnehmbar.")

    def begruendung(self, zustand: Stahlzustand, erg: Fallergebnis) -> str:
        return (f"ε_m = {erg.ebene.eps_m * 1e3:.4f} ‰, χ = {erg.ebene.chi:.5f} 1/m. "
                f"{erg.satz}")

    def dehnungsgrenze(self, basis: str, werte: Zwischenwerte, erg: Fallergebnis) -> Wert:
        name, symbol = je_stahl("eps_s_adm", r"\varepsilon_{s,adm}", erg.stahl, self.staehle)
        return Zwischenwerte(basis).dehnung(name, symbol, erg.eps_s_adm, "Widerstand")

    def protokoll_vor_den_grenzen(self, p: Protokoll, e: Eingaben, zustand: _Plattenzustand,
                                  wahl: Rechenwahl, phi: Wert, basis: str) -> None:
        if not wahl.art.mit_kriechzahl:
            return
        nachsatz = ""
        if wahl.art is Rechenart.ELASTISCH:
            nachsatz = self._wertigkeiten(zustand, wahl, basis)
        protokoll_wirksamer_modul(p, e["E_cm"], phi, basis,
                                  titel="Wirksamer Elastizitätsmodul", nachsatz=nachsatz)

    def _wertigkeiten(self, zustand: _Plattenzustand, wahl: Rechenwahl, basis: str) -> str:
        """
        ``n = E_s / E_c,eff`` hinter dem wirksamen Modul -- einmal, solange
        alle Staehle denselben Modul haben, sonst je Stahl.
        """
        moduln = {l.sorte: l.stahl.E_s for l in zustand.loeser.lagen}
        nach_sorte = {kennung_aus(s.id): s for s in self.staehle}
        if len(set(moduln.values())) == 1:
            paare = [("n", "n", next(iter(moduln.values())))]
        else:
            paare = [(*je_stahl("n", "n", nach_sorte[sorte], self.staehle), E_s)
                     for sorte, E_s in moduln.items()]
        werte = Zwischenwerte(basis)
        angaben = []
        for name, symbol, E_s in paare:
            n = wertigkeit(E_s=E_s, E_cm=zustand.w.E_cm, phi=wahl.kriechzahl)
            angaben.append(rf"\qquad {angabe(werte.zahl(name, symbol, n, stellen=2))}")
        return "".join(angaben)

    def protokoll_gesetze(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand,
                          wahl: Rechenwahl, basis: str) -> None:
        protokoll_gesetze(p, wahl, e, basis, titel="Werkstoffgesetze im Gebrauchszustand",
                          posten=self.posten)

    def protokoll_verfahren(self, p: Protokoll, zustand: _Plattenzustand,
                            wahl: Rechenwahl) -> None:
        protokoll_verfahren(p, eps_c2d=zustand.w.eps_c2d,
                            verdraengt=wahl.art is not Rechenart.HANDRECHNUNG,
                            suche=zustand.loeser.suche)

    def protokoll_einwirkung(self, p: Protokoll, fall: Gebrauchsfall, index: str) -> None:
        p.gleichung(
            rf"M_{{Ed,{index}}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed,{index}}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

    def protokoll_ebene(self, p: Protokoll, werte: Zwischenwerte, zustand: Stahlzustand,
                        grenzen: Grenzen, erg: Fallergebnis) -> None:
        ebene = erg.ebene
        eps_m = werte.dehnung("eps_m", r"\varepsilon_m", ebene.eps_m, stellen=4)
        chi = werte.kruemmung("chi", r"\chi", ebene.chi)
        p.gleichung(
            rf"{angabe(eps_m)} \qquad {angabe(chi)} \qquad "
            r"\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)",
            titel="Gefundene Dehnungsebene")
        N_int = werte.kraft("N_int", "N_{int}", ebene.N_int)
        M_int = werte.moment("M_int", "M_{int}", ebene.M_int)
        p.gleichung(
            rf"{angabe(N_int)} \;\checkmark \qquad {angabe(M_int)} \;\checkmark",
            titel="Probe: die Ebene erzeugt die Einwirkung")


# ===========================================================================
# Der Nachweis
# ===========================================================================


class Spannungsbegrenzung(Nachweis):
    """
    Stahlspannung unter Gebrauchslast gegen eine Grenze -- an der Platte je
    Tragrichtung, am gezeichneten Querschnitt; wo, sagt ``ort``.

    Ein Urteil je Lastfall. Gerechnet wird am gerissenen Querschnitt, womit,
    sagt ``wahl``; wogegen gehalten wird, sagt ``grenze``.
    """

    @property
    def thema(self) -> str:
        """Je Grenze eines: gegen Fliessen oder aus der Rissbreite."""
        return self.grenze.thema

    @property
    def langname(self) -> str:
        return self.grenze.langname

    def __init__(
        self,
        ort: Stahlspannungsort,
        faelle: Sequence,
        *,
        grenze: Type[Spannungsgrenze],
        anforderung: Rissanforderung,
        wahl: Rechenwahl = VORGABE,
    ) -> None:
        if not faelle:
            raise ValueError("Ohne Lastfall gibt es nichts zu begrenzen.")
        self.ort = ort
        self.richtung = ort.richtung
        self.faelle = list(faelle)
        self.grenze = grenze
        self.anforderung = anforderung
        self.wahl = wahl

        basis = ort.basis(grenze)
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,{grenze.symbolteil}{ort.zeichen},{als_text(f.name)}}}",
                f"Erfüllungsgrad {grenze.thema}{ort.beschriftung} – {f.name}",
                grenze.referenz,
            )
            for f in self.faelle
        }
        # Was die Grenze braucht, kann schon dastehen -- E_s und f_yk braucht
        # auch das Werkstoffgesetz. Dieselbe Zahl unter zwei Namen zu fuehren
        # hiesse, sie zweimal zu lesen.
        bezuege = bezuege_vereinen(ort.bezuege(wahl), grenze.bezuege(ort))
        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Stahlspannung unter {grenze.einwirkung} Einwirkung"
                   f"{ort.beschriftung} – {ort.name}"),
            referenz=grenze.referenz,
            abschnitt=ort.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        zustand = self.ort.zustand(e, self.wahl)
        grenzen = self._protokoll_ansatz(p, e, zustand)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()
        for fall in self.faelle:
            # Ausgeschaltete Lastfaelle rechnen mit und schweigen dabei.
            leise = self.leise(fall.name)
            erg = self._einen_fall(zustand, grenzen, fall)
            befund.ergebnisse.append(erg)
            if not leise:
                self._protokoll_fall(p, e, zustand, grenzen, erg)
            urteile.append(self.urteil(self.d_ausnutzung[fall.name], fall.name, erg.ausgang,
                                       erg.begruendung, art=self.grenze.art, still=leise))
        return Ausfuehrung({}, urteile, befund)

    def _einen_fall(self, zustand: Stahlzustand, grenzen: Grenzen, fall) -> Fallergebnis:
        erg = Fallergebnis(fall=fall)
        stellen = zustand.stellen
        if not stellen:
            erg.begruendung = "Ohne Bewehrung gibt es keine Stahlspannung."
            return erg
        erg.ebene = ebene = self.ort.ebene(zustand, fall)
        # Nur gezogene Bewehrung: eine gedrueckte Stelle hat keine
        # Zugspannung, die zu begrenzen waere. Massgebend ist der kleinste
        # Erfuellungsgrad, gemessen an der *Dehnung* -- auf dem Plateau haben
        # mehrere Stellen dieselbe Spannung, aber nur eine ist am weitesten
        # gedehnt. Bei einem Stahl ist das die am staerksten gedehnte Stelle;
        # bei mehreren zaehlt die Grenze jeder Stelle mit. Ohne gezogene
        # Stelle steht die strengste Grenze da.
        zug = ([(grenzen.sigma(i) / (st.E_s * eps), -eps, i)
                for i, (st, eps) in enumerate(zip(stellen, ebene.eps_s)) if eps > 0.0]
               if ebene.konvergiert else [])
        i = erg.stelle = min(zug)[2] if zug else grenzen.strengste
        stelle = stellen[i]
        erg.stahl, erg.E_s, erg.eps_y = stelle.stahl, stelle.E_s, stelle.eps_y
        erg.sigma_s_adm = grenze = grenzen.sigma(i)
        erg.eps_s_adm = grenze / stelle.E_s
        if zug:
            erg.eps_s, erg.sigma_s = ebene.eps_s[i], ebene.sigma_s[i]
        erg.konvergiert = ebene.konvergiert
        if not ebene.konvergiert:
            erg.begruendung = (
                self.wahl.art.ohne_ebene if ebene.verfehlt else self.ort.keine_ebene(fall))
            return erg

        erg.ausgang = self._vergleich(erg, grenzen)
        erg.satz = self._satz(erg)
        erg.begruendung = self.ort.begruendung(zustand, erg)
        return erg

    def _vergleich(self, erg: Fallergebnis, grenzen: Grenzen) -> Vergleich:
        """
        Spannungen oder Dehnungen -- die eine Stelle, die das entscheidet.

        Gemessen wird an der Dehnung, siehe Dateikopf: elastisch ist
        ``E_s * eps_s`` dieselbe Zahl wie ``sigma_s`` -- Bit fuer Bit, denn das
        Gesetz rechnet dort genau dieses Produkt. Ohne Zug steht null da, und
        es gibt nichts zu begrenzen.
        """
        werte = Zwischenwerte(f"{self.id}.{erg.fall.kennung}")
        index = self.ort.stahlindex
        if erg.fliesst:
            return Vergleich(
                werte.dehnung("eps_s", rf"\varepsilon_{index}", erg.eps_s, "Einwirkung"),
                self.ort.dehnungsgrenze(self.id, werte, erg))
        return Vergleich(
            werte.spannung("sigma_s", rf"\sigma_{index}", erg.sigma_s, "Einwirkung"),
            grenzen.gruppe(erg.stelle).wert)

    @staticmethod
    def _satz(erg: Fallergebnis) -> str:
        """Der Vergleich als Satz -- in der Groesse, die verglichen wurde."""
        zeichen = "≤" if erg.erfuellt else ">"
        if erg.fliesst:
            return (f"Stahl fliesst (ε_s = {erg.eps_s * 1e3:.2f} ‰ > ε_y = "
                    f"{erg.eps_y * 1e3:.2f} ‰): ε_s {zeichen} "
                    f"ε_s,adm = {erg.eps_s_adm * 1e3:.2f} ‰.")
        return (f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² {zeichen} "
                f"σ_s,adm = {erg.sigma_s_adm / 1e6:.0f} N/mm².")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand) -> Grenzen:
        """Was fuer alle Faelle gilt -- und die Grenzen, die dabei entstehen."""
        g, ort, wahl = self.grenze, self.ort, self.wahl
        p.titel(f"Stahlspannung unter {g.einwirkung} Einwirkung{ort.titelzusatz}")
        p.erklaerung(f"{g.einleitung} {ort.messung}")
        phi = protokoll_rechenwahl(p, wahl, self.id)
        ort.protokoll_vor_den_grenzen(p, e, zustand, wahl, phi, self.id)
        grenzen = g.bestimmen(ort, zustand, e, p, self.anforderung, self.id)
        protokoll_festlegungen(p, wahl)
        ort.protokoll_gesetze(p, e, zustand, wahl, self.id)
        g.festlegung(p, ort)
        p.erklaerung(VERGLEICH_BEIM_FLIESSEN)
        p.titel("Wie die Dehnungsebene gefunden wird", ebene=3)
        ort.protokoll_verfahren(p, zustand, wahl)
        return grenzen

    def _protokoll_fall(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand,
                        grenzen: Grenzen, erg: Fallergebnis) -> None:
        fall = erg.fall
        p.titel(f"{self.grenze.fallwort} – {fall.name}", ebene=3)
        self.ort.protokoll_einwirkung(p, fall, self.grenze.lastindex)
        if not erg.machbar:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        self.ort.protokoll_ebene(p, werte, zustand, grenzen, erg)
        wirkt, grenze = erg.ausgang.einwirkung, erg.ausgang.widerstand
        if erg.fliesst:
            self._protokoll_fliessen(p, e, erg, grenzen, werte, wirkt, grenze)
        else:
            p.gleichung(bedingung(angabe(wirkt), r"\le", angabe(grenze), erg.erfuellt),
                        titel="Grösste Zugspannung in der Bewehrung")
        erg.ausgang.zeile(p, self.d_ausnutzung[fall.name])

    def _protokoll_fliessen(self, p: Protokoll, e: Eingaben, erg: Fallergebnis,
                            grenzen: Grenzen, werte: Zwischenwerte, wirkt: Wert,
                            grenze: Wert) -> None:
        """Der Fall, in dem die Spannung am Plateau stehen bleibt."""
        E_s = e[stahlname("E_s", erg.stahl)]
        p.text(f"Stahl fliesst (σ_s = {erg.sigma_s / 1e6:.0f} N/mm²) → "
               f"Vergleich über die Dehnung.")
        p.formel(werte.dehnung("eps_y", r"\varepsilon_y", erg.eps_y),
                 r"\frac{@f_s}{@E_s}", {"f_s": e[stahlname(self.wahl.satz.stahl, erg.stahl)],
                                        "E_s": E_s},
                 titel="Grösste Zugdehnung in der Bewehrung", name=FLIESSDEHNUNG,
                 nachsatz=rf"\quad < \quad {angabe(wirkt)}")
        p.formel(grenze, r"\frac{@sigma}{@E_s}",
                 {"sigma": grenzen.gruppe(erg.stelle).wert, "E_s": E_s},
                 titel="Zulässige Dehnung",
                 nachsatz=vergleich(r"\ge", angabe(wirkt), erg.erfuellt))
