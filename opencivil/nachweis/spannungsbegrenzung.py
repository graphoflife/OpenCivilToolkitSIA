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
der Herleitung. Die drei gehoeren zusammen und stehen darum in einem Objekt,
das dem Nachweis mitgegeben wird (:class:`Spannungsgrenze`). Zwei Klassen
mit kopiertem Kern waeren genau die Fehlerklasse, vor der ``zustand2.py``
warnt: zwei Nachweise, die fuer denselben Querschnitt verschiedene sigma_s
melden.

WIE DIE SPANNUNG ENTSTEHT:
Ueber :mod:`opencivil.nachweis.querschnittsloeser`: gesucht wird die
Dehnungsebene, die ``M_Ed`` und ``N_Ed`` des Lastfalls im Gleichgewicht
haelt. Der Beton nimmt keinen Zug auf. Womit gerechnet wird, waehlt das
Kapitel (:class:`~opencivil.nachweis.rechenwahl.Rechenwahl`): die
Kriechzahl, den Wertesatz und die Rechenart. Die Vorgabe ist, wie bis
2026-10-09 fest: **elastisch** -- der Beton im Druck linear mit dem wirksamen
Modul ``E_cm/(1+phi)`` -- mit den **charakteristischen** Festigkeiten: der
Stahl fliesst bei ``f_yk``, der Beton traegt hoechstens ``f_ck``.

Die gedrueckte Bewehrung wirkt mit, wie im Querschnitt -- nur in der
Rechenart «Handrechnung» nicht. Gemessen wird an der am staerksten
gezogenen Lage. (Bis 2026-10-09 stand hier, nur gezogene Bewehrung zaehle;
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
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Eingabebezug, Eingaben, Fallbefund, Nachweis, NachweisUrteil, grad_def,
    grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.core.latex import als_text, angabe, bedingung, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.material.basis import Baustoff, mit_index
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis.mindestbewehrung import (
    protokoll_zulaessige_stahlspannung, zulaessige_stahlspannung,
)
from opencivil.nachweis.querschnittsloeser import (
    EPS_DRUCK, protokoll_verfahren, protokoll_wirksamer_modul,
    Querschnittsloeser, Werkstoffsatz,
)
from opencivil.nachweis.rechenwahl import (
    Betonkennwerte, Rechenart, Rechenwahl, betonbezuege, bezuege_vereinen, gesetze,
    lagenbezuege, protokoll_gesetze, protokoll_rechenwahl, stahlbezuege, stahllagen,
    stahlname, staehle,
)
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.zustand2 import wertigkeit
from opencivil.querschnitt.platte import Richtung

#: Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
FLIESSABSTAND = 80e6

#: Womit die Stahlspannungen rechnen, wenn das Kapitel nichts anderes waehlt:
#: elastisch, mit charakteristischen Werten -- ein Gebrauchsnachweis fragt,
#: was der Querschnitt tut, nicht was er darf.
VORGABE = Rechenwahl(satz=Werkstoffsatz.CHARAKTERISTISCH, art=Rechenart.ELASTISCH)


@dataclass(frozen=True)
class Gebrauchsfall:
    """
    Eine Schnittgroessenkombination unter Gebrauchslast.

    Haeufig oder quasi-staendig -- das sagt nicht der Fall, sondern der
    Nachweis, dem er mitgegeben wird.
    """

    name: str
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass(frozen=True)
class Vergleich:
    """
    Was in der Tabelle gegeneinander steht -- und wie es im Satz heisst.

    Spannungen, solange der Stahl elastisch bleibt. Fliesst er, Dehnungen:
    sonst stuende ``f_yk`` neben ``f_yk`` und daneben «nicht erfuellt» --
    richtig gerechnet und doch nicht zu lesen. Entschieden wird das einmal,
    in :meth:`Spannungsbegrenzung._einen_fall`; Urteil und Begruendung lesen
    es nur noch ab.
    """

    einwirkung: Wert
    widerstand: Wert
    satz: str


@dataclass
class Fallergebnis:
    """Was der Nachweis fuer einen Lastfall gefunden hat."""

    fall: Gebrauchsfall
    eps_m: float = 0.0
    chi: float = 0.0
    N_int: float = 0.0
    M_int: float = 0.0
    eps_s: float = 0.0
    """Groesste Zugdehnung in der Bewehrung."""

    sigma_s: float = 0.0
    """Die Spannung dazu, in Pa -- auf dem Plateau ``f_yk``."""

    sigma_s_adm: float = 0.0
    eps_s_adm: float = 0.0
    """``sigma_s_adm / E_s`` -- dagegen wird gemessen, wenn der Stahl fliesst."""

    eps_y: float = 0.0
    """Die Fliessdehnung ``f_yk / E_s``."""

    stahl: Optional[Baustoff] = None
    """
    Der Stahl der massgebenden Lage -- seine Grenze, sein ``E_s`` und seine
    Fliessdehnung gelten. Mit verschiedenen Staehlen unten und oben ist
    massgebend die gezogene Lage mit dem kleinsten Erfuellungsgrad, nicht
    die am staerksten gedehnte.
    """

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    konvergiert: bool = True
    vergleich: Optional[Vergleich] = None
    """Fehlt nur, wenn sich keine Gleichgewichtslage fand."""

    begruendung: str = ""
    hinweis: str = ""

    @property
    def fliesst(self) -> bool:
        """Ob die am staerksten gedehnte Lage auf dem Plateau liegt."""
        return self.eps_s > self.eps_y


# ===========================================================================
# Die Grenzen
# ===========================================================================


class Spannungsgrenze(ABC):
    """
    Wogegen ein Stahlspannungsnachweis haelt -- und alles, was nur dazugehoert.

    Die Zahl, die Eingaben, aus denen sie entsteht, und die Absaetze, die sie
    begruenden. Dazu die Woerter, unter denen der Nachweis ueberall erscheint:
    Wert-ID, Symbol, Tabellenzeile, Ueberschrift. Zwei Grenzen mit gleichem
    ``langname`` stuenden als zwei ununterscheidbare Zeilen in derselben
    Tabelle.

    Die Absaetze sind **nicht** zu einem Text mit Platzhaltern
    zusammenzulegen: der eine argumentiert fuer ``f_yd``, der andere fuer
    ``f_yk``. Ein Text, der beides behauptet, behauptet nichts.
    """

    #: Teil der Wert-ID: ``<querschnitt>.nachweis.<idteil>.<richtung>``.
    idteil: str
    #: Index am Erfuellungsgrad.
    symbolteil: str
    #: Kurzzeichen im Urteil.
    art: str
    #: Spalte «Nachweis» der Zusammenfassung.
    langname: str
    #: Thema in der Formelsammlung, und wovon der Erfuellungsgrad spricht.
    thema: str
    #: «häufiger» / «quasi-ständiger» -- im Titel.
    einwirkung: str
    #: Index an M_Ed und N_Ed in der Herleitung.
    lastindex: str
    #: Ueberschrift je Fall.
    fallwort: str
    referenz: str
    #: Der erste Satz der Herleitung: wozu der Nachweis da ist.
    einleitung: str

    def __init__(self, querschnitt, richtung: Richtung,
                 anforderung: Rissanforderung) -> None:
        """
        Alle Grenzen werden gleich gebaut -- aus der Platte, der Tragrichtung
        und der Rissanforderung. Was eine davon nicht braucht, laesst sie
        liegen; so kann der Aufbau beide in derselben Schleife anlegen.
        """
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"liegt keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.staehle = staehle(self.posten)
        """
        Die Staehle dieser Richtung -- je Seite einer, der Editor laesst sie
        verschieden waehlen. Jeder bekommt seine eigene Grenze.
        """

    @property
    def id(self) -> str:
        """Die Kennung des Nachweises, zu dem die Grenze gehoert."""
        return f"{self.querschnitt.id}.nachweis.{self.idteil}.{self.richtung.value}"

    def je_stahl(self, name: str, symbol: str, stahl: Baustoff) -> Tuple[str, str]:
        """
        Name und Zeichen eines Werts, der zu einem Stahl gehoert -- mit dem
        Stahl daran, sobald die Richtung mehr als einen hat.
        """
        if len(self.staehle) == 1:
            return name, symbol
        return f"{name}_{kennung_aus(stahl.id)}", mit_index(symbol, stahl.symbol_index)

    def spannung(self, sigma_adm: float, stahl: Baustoff) -> Wert:
        """``sigma_s,adm`` als Wert -- in Herleitung, Vergleich und Tabelle derselbe."""
        name, symbol = self.je_stahl("sigma_s_adm", r"\sigma_{s,adm}", stahl)
        return Zwischenwerte(self.id).spannung(name, symbol, sigma_adm, "Widerstand")

    @classmethod
    def gilt_bei(cls, anforderung: Rissanforderung) -> bool:
        """Ob der Nachweis bei dieser Rissanforderung verlangt ist."""
        return True

    @abstractmethod
    def bezuege(self) -> List[Eingabebezug]:
        """Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung."""

    @abstractmethod
    def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]:
        """
        Die zulaessige Stahlspannung in Pa, je Stahl unter seiner Kennung --
        gerechnet und mitgeschrieben.
        """

    @classmethod
    @abstractmethod
    def festlegung(cls, p: Protokoll) -> None:
        """Welche Werte die Grenze ansetzt, und warum -- ohne Platte, nur der Absatz."""


class GrenzeGegenFliessen(Spannungsgrenze):
    """
    ``f_yd - 80 N/mm²`` unter haeufiger Einwirkung -- das Fliessen verhindern.

    Nur bei erhoehter und hoher Anforderung -- bei normaler steht in
    Tabelle 17 ein Strich (:attr:`Rissanforderung.gegen_fliessen`). Der
    Aufbau fragt :meth:`gilt_bei`.
    """

    idteil = "spannung"
    symbolteil = r"\sigma"
    art = "σ_s"
    langname = "Risse: Häufige Lastfälle"
    thema = "Stahlspannung gegen Fliessen"
    einwirkung = "häufiger"
    lastindex = "häufig"
    fallwort = "Häufiger Lastfall"
    referenz = "SIA 262:2025, Tabelle 17"
    einleitung = ("Unter häufiger Einwirkung darf die Bewehrung nicht "
                  "fliessen – sonst bleiben Risse und Durchbiegung dauerhaft.")

    @classmethod
    def gilt_bei(cls, anforderung: Rissanforderung) -> bool:
        return anforderung.gegen_fliessen

    def bezuege(self) -> List[Eingabebezug]:
        return stahlbezuege(self.posten, ("f_yd",))

    def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]:
        # Die 80 N/mm² haben kein Zeichen -- sie stehen als Zahl in der Formel.
        abstand = Groesse.aus_si(FLIESSABSTAND, N_PRO_MM2).als_latex(0)
        grenzen = {}
        for stahl in self.staehle:
            f_yd = e[stahlname("f_yd", stahl)]
            sigma_adm = f_yd.groesse.si - FLIESSABSTAND
            p.formel(self.spannung(sigma_adm, stahl), f"@f_yd - {abstand}", {"f_yd": f_yd},
                     titel="Zulässige Stahlspannung", referenz=self.referenz)
            grenzen[kennung_aus(stahl.id)] = sigma_adm
        return grenzen

    @classmethod
    def festlegung(cls, p: Protokoll) -> None:
        p.erklaerung(
            "Drittens die Grenze: sie rechnet mit dem Bemessungswert, "
            "σ_s,adm = f_yd − 80 N/mm², und nicht mit f_yk − 80. Die Norm sagt "
            "an dieser Stelle nicht eindeutig, welcher Wert gemeint ist; f_yd "
            "ist die strengere Wahl – die Grenze liegt rund 15 % tiefer –, "
            "gewählt ist deshalb die Seite, auf der man nicht danebenliegen "
            "kann. Das ist etwas anderes als das Fliessplateau oben: dort geht "
            "es darum, was der Stahl tut, hier darum, wie viel Abstand man "
            "davon verlangt."
        )


class GrenzeAusRissbreite(Spannungsgrenze):
    """
    ``sigma_s,adm`` aus der Rissanforderung, unter quasi-staendiger Einwirkung.

    Dieselbe zulaessige Spannung wie bei der Zwaengung -- dieselbe Funktion,
    :func:`mindestbewehrung.zulaessige_stahlspannung`, und keine zweite
    Fassung davon. Bei normaler Anforderung ``f_yk``: die Bewehrung darf
    unter Dauerlast nicht fliessen. Bei erhoehter und hoher zusaetzlich die
    Wurzelformel mit ``w_nom``.

    **Massgebend ist der dickste Stab der Tragrichtung.** Anders als bei der
    Rissnormalkraft, wo je Lage ein Urteil faellt und die Grenze zu *dieser*
    Lage gehoert: hier kommt sigma_s aus dem Faserintegral ueber den ganzen
    Querschnitt, und welche Lage die groesste Zugspannung traegt, wechselt mit
    dem Lastfall -- bei einem Feldmoment die untere, bei einem Stuetzmoment
    die obere. Der dickste Stab gibt die kleinste zulaessige Spannung; das
    liegt fuer jede der beiden auf der sicheren Seite.
    """

    idteil = "spannung_riss"
    symbolteil = r"\sigma,w"
    art = "σ_s,w"
    langname = "Risse: Quasi-ständige Lastfälle"
    thema = "Stahlspannung aus Rissbreite"
    einwirkung = "quasi-ständiger"
    lastindex = r"\text{quasi-ständig}"
    fallwort = "Quasi-ständiger Lastfall"
    referenz = "SIA 262:2025, 4.4.2"
    einleitung = ("Unter quasi-ständiger Einwirkung begrenzt die "
                  "Stahlspannung die Rissbreite – dieselbe Grenze wie bei der "
                  "Zwängung, nur dass die Spannung hier aus den Lasten kommt "
                  "und nicht aus einer aufgezwungenen Verformung.")

    def __init__(self, querschnitt, richtung: Richtung,
                 anforderung: Rissanforderung) -> None:
        super().__init__(querschnitt, richtung, anforderung)
        self.marken = [f"{lage.nummer}{art.kuerzel}"
                       for lage, art, _, _, _ in self.posten]

    def bezuege(self) -> List[Eingabebezug]:
        return stahlbezuege(self.posten, ("f_yk", "E_s")) + [
            Eingabebezug("f_ctm", self.querschnitt.beton.id_von("f_ctm")),
        ] + [
            Eingabebezug(f"dm_{m}", self.querschnitt.id_von(f"lage.{m}.phi"))
            for m in self.marken
        ]

    def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]:
        f_ctm = e.g("f_ctm").si
        durchmesser = max(e.g(f"dm_{m}").si for m in self.marken)
        werte = Zwischenwerte(self.id)
        dm = werte.laenge("dm_max", r"\varnothing_{max}", durchmesser, stellen=0)
        if self.anforderung.rissbreite is not None:
            p.wert(dm, titel="Dickster Stab der Tragrichtung")

        grenzen = {}
        for stahl in self.staehle:
            f_yk, E_s = e[stahlname("f_yk", stahl)], e[stahlname("E_s", stahl)]
            sigma_adm = zulaessige_stahlspannung(
                anforderung=self.anforderung, f_yk=f_yk.groesse.si, E_s=E_s.groesse.si,
                f_ctm=f_ctm, durchmesser=durchmesser)
            basis = self.id if len(self.staehle) == 1 else f"{self.id}.{kennung_aus(stahl.id)}"
            protokoll_zulaessige_stahlspannung(
                p, self.spannung(sigma_adm, stahl),
                anforderung=self.anforderung, f_yk=f_yk, E_s=E_s,
                f_ctm=e["f_ctm"], durchmesser=dm, basis=basis, referenz=self.referenz)
            grenzen[kennung_aus(stahl.id)] = sigma_adm
        return grenzen

    @classmethod
    def festlegung(cls, p: Protokoll) -> None:
        p.erklaerung(
            "Drittens die Grenze: dieselbe wie bei der Zwängung, mit f_yk und "
            "bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die "
            "Rissbreite. Massgebend ist der dickste Stab der Tragrichtung. "
            "Welche Lage die grösste Zugspannung trägt, wechselt mit dem "
            "Lastfall – bei einem Feldmoment die untere, bei einem "
            "Stützmoment die obere –, und der dickste Stab gibt die kleinste "
            "zulässige Spannung. Das liegt für beide auf der sicheren Seite."
        )


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
# Der Nachweis
# ===========================================================================


class Spannungsbegrenzung(Nachweis):
    """
    Stahlspannung unter Gebrauchslast, je Tragrichtung, gegen eine Grenze.

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
        faelle: Sequence[Gebrauchsfall],
        *,
        grenze: Spannungsgrenze,
        wahl: Rechenwahl = VORGABE,
    ) -> None:
        if not faelle:
            raise ValueError("Ohne Lastfall gibt es nichts zu begrenzen.")
        # Platte, Tragrichtung und Bewehrung kennt die Grenze schon -- zweimal
        # uebergeben hiesse, pruefen zu muessen, ob beides zusammenpasst.
        self.querschnitt = querschnitt = grenze.querschnitt
        self.richtung = richtung = grenze.richtung
        self.posten = grenze.posten
        self.faelle = list(faelle)
        self.grenze = grenze
        self.wahl = wahl
        self.staehle = {kennung_aus(s.id): s for s in grenze.staehle}
        """Die Staehle dieser Richtung, nach Kennung -- wie die Lagen sie nennen."""

        r = richtung.value
        basis = grenze.id
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,{grenze.symbolteil},{r},{als_text(f.name)}}}",
                (f"Erfüllungsgrad {grenze.thema} "
                 f"{richtung.beschriftung} – {f.name}"),
                grenze.referenz,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
        ] + betonbezuege(wahl.satz, querschnitt.beton) + lagenbezuege(self.posten, wahl.satz)
        # Was die Grenze braucht, kann schon dastehen -- E_s und f_yk braucht
        # auch das Werkstoffgesetz. Dieselbe Zahl unter zwei Namen zu fuehren
        # hiesse, sie zweimal zu lesen.
        bezuege = bezuege_vereinen(bezuege, grenze.bezuege())

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Stahlspannung unter {grenze.einwirkung} Einwirkung "
                   f"{richtung.beschriftung} – {querschnitt.name}"),
            referenz=grenze.referenz,
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        wahl = self.wahl
        w = Betonkennwerte.aus_eingaben(e, wahl.satz)
        lagen = stahllagen(self.posten, wahl.satz, e.si_nach_id())
        loeser = gesetze(wahl, w).loeser(h=h, b=b, lagen=lagen)

        sigma_adm = self._protokoll_ansatz(p, e, w, loeser)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()

        for fall in self.faelle:
            # Ausgeschaltete Lastfaelle rechnen mit und schweigen dabei.
            leise = self.leise(fall.name)
            erg = self._einen_fall(loeser, fall, sigma_adm)
            befund.ergebnisse.append(erg)
            if not leise:
                self._protokoll_fall(p, e, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg, still=leise))

        return Ausfuehrung(ergebnis, urteile, befund)

    def _einen_fall(self, loeser: Querschnittsloeser, fall: Gebrauchsfall,
                    sigma_adm: Dict[str, float]) -> Fallergebnis:
        ebene = loeser.loese(N_Ed=fall.N_Ed.si, M_Ed=fall.M_Ed.si)
        # Ohne gezogene Lage gibt es nichts zu begrenzen; dann steht die
        # strengste Grenze da.
        massgebend = min(loeser.lagen, key=lambda l: sigma_adm[l.sorte])
        eps_s = sigma_s = 0.0
        if ebene.konvergiert:
            # Nur gezogene Bewehrung: eine gedrueckte Lage hat keine
            # Zugspannung, die zu begrenzen waere. Massgebend ist der kleinste
            # Erfuellungsgrad, gemessen an der *Dehnung* -- auf dem Plateau
            # haben mehrere Lagen dieselbe Spannung, aber nur eine ist am
            # weitesten gedehnt. Bei einem Stahl ist das die am staerksten
            # gedehnte Lage; bei zweien zaehlt die Grenze jeder Lage mit.
            zug = [(sigma_adm[l.sorte] / (l.stahl.E_s * eps), -eps, l, eps, sig)
                   for l, eps, sig in zip(loeser.lagen, ebene.eps_s, ebene.sigma_s)
                   if eps > 0.0]
            if zug:
                _, _, massgebend, eps_s, sigma_s = min(zug, key=lambda z: z[:2])
        grenze = sigma_adm[massgebend.sorte]
        stahl = massgebend.stahl
        erg = Fallergebnis(fall=fall, sigma_s_adm=grenze, eps_s_adm=grenze / stahl.E_s,
                           eps_y=stahl.eps_yd, stahl=self.staehle[massgebend.sorte],
                           eps_s=eps_s, sigma_s=sigma_s)
        erg.konvergiert = ebene.konvergiert
        if not ebene.konvergiert:
            erg.begruendung = erg.hinweis = (
                self.wahl.art.ohne_ebene if ebene.verfehlt else
                f"Keine Dehnungsebene für M = {fall.M_Ed.formatiert(1, KNM)} kNm, "
                f"N = {fall.N_Ed.formatiert(1, KN)} kN → nicht aufnehmbar.")
            return erg

        erg.eps_m, erg.chi = ebene.eps_m, ebene.chi
        erg.N_int, erg.M_int = ebene.N_int, ebene.M_int

        # An der Dehnung gemessen, siehe Dateikopf. Elastisch ist E_s * eps_s
        # dieselbe Zahl wie sigma_s -- Bit fuer Bit, denn das Gesetz rechnet
        # dort genau dieses Produkt.
        gedehnt = stahl.E_s * erg.eps_s
        erg.erfuellungsgrad = (float("inf") if gedehnt <= 0.0
                               else grenze / gedehnt)
        erg.erfuellt = gedehnt <= grenze
        erg.vergleich = self._vergleich(erg)
        erg.begruendung = (
            f"ε_m = {erg.eps_m * 1e3:.4f} ‰, χ = {erg.chi:.5f} 1/m. "
            f"{erg.vergleich.satz}")
        return erg

    def _vergleich(self, erg: Fallergebnis) -> Vergleich:
        """Spannungen oder Dehnungen -- die eine Stelle, die das entscheidet."""
        r = self.richtung.value
        fall = Zwischenwerte(f"{self.id}.{erg.fall.kennung}")
        if erg.fliesst:
            name, symbol = self.grenze.je_stahl("eps_s_adm", r"\varepsilon_{s,adm}", erg.stahl)
            return Vergleich(
                einwirkung=fall.dehnung(
                    "eps_s", rf"\varepsilon_{{s,{r}}}", erg.eps_s, "Einwirkung"),
                widerstand=Zwischenwerte(self.id).dehnung(
                    name, symbol, erg.eps_s_adm, "Widerstand"),
                satz=(f"Stahl fliesst (ε_s = {erg.eps_s * 1e3:.2f} ‰ > ε_y = "
                      f"{erg.eps_y * 1e3:.2f} ‰): ε_s {'≤' if erg.erfuellt else '>'} "
                      f"ε_s,adm = {erg.eps_s_adm * 1e3:.2f} ‰."))
        return Vergleich(
            einwirkung=fall.spannung(
                "sigma_s", rf"\sigma_{{s,{r}}}", erg.sigma_s, "Einwirkung"),
            widerstand=self.grenze.spannung(erg.sigma_s_adm, erg.stahl),
            satz=(f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² {'≤' if erg.erfuellt else '>'} "
                  f"σ_s,adm = {erg.sigma_s_adm / 1e6:.0f} N/mm²."))

    def _urteil(self, erg: Fallergebnis, *, still: bool = False) -> NachweisUrteil:
        """Das Urteil eines Falls -- was gegeneinander steht, sagt der Vergleich."""
        vergleich = erg.vergleich
        return NachweisUrteil(
            art=self.grenze.art,
            ziel=self.d_ausnutzung[erg.fall.name].id,
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=vergleich.einwirkung if vergleich else None,
            widerstand=vergleich.widerstand if vergleich else None,
            still=still,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, w: Betonkennwerte,
                          loeser: Querschnittsloeser) -> Dict[str, float]:
        """Was fuer alle Faelle gilt -- und die Grenzen, die dabei entstehen."""
        g = self.grenze
        wahl = self.wahl
        p.titel(f"Stahlspannung unter {g.einwirkung} Einwirkung – "
                f"{self.richtung.beschriftung}")
        mehrere = (" Liegen unten und oben verschiedene Stähle, hat jeder seine "
                   "Grenze, und massgebend ist die gezogene Lage mit dem kleinsten "
                   "Erfüllungsgrad." if len(self.staehle) > 1 else "")
        p.erklaerung(
            f"{g.einleitung} Gerechnet wird am gerissenen Querschnitt: der "
            f"Beton nimmt keinen Zug auf. Die Bewehrung wirkt auf Zug und auf "
            f"Druck – nur in der Handrechnung zählt die gedrückte nicht. "
            f"Gemessen wird an der am stärksten gezogenen Lage.{mehrere}"
        )
        phi = protokoll_rechenwahl(p, wahl, self.id)
        if wahl.art.mit_kriechzahl:
            nachsatz = ""
            if wahl.art is Rechenart.ELASTISCH:
                nachsatz = self._wertigkeiten(w, loeser)
            protokoll_wirksamer_modul(p, e["E_cm"], phi, self.id,
                                      titel="Wirksamer Elastizitätsmodul", nachsatz=nachsatz)
        sigma_adm = g.bestimmen(e, p)

        protokoll_festlegungen(p, wahl)
        protokoll_gesetze(p, wahl, e, self.id, titel="Werkstoffgesetze im Gebrauchszustand",
                          posten=self.posten)
        g.festlegung(p)
        p.erklaerung(VERGLEICH_BEIM_FLIESSEN)
        p.titel("Wie die Dehnungsebene gefunden wird", ebene=3)
        protokoll_verfahren(p, eps_druck=EPS_DRUCK, eps_zug=loeser.eps_zug,
                            verdraengt=wahl.art is not Rechenart.HANDRECHNUNG)
        return sigma_adm

    def _wertigkeiten(self, w: Betonkennwerte, loeser: Querschnittsloeser) -> str:
        """
        ``n = E_s / E_c,eff`` hinter dem wirksamen Modul -- einmal, solange
        alle Staehle denselben Modul haben, sonst je Stahl.
        """
        moduln = {l.sorte: l.stahl.E_s for l in loeser.lagen}
        if len(set(moduln.values())) == 1:
            paare = [("n", "n", next(iter(moduln.values())))]
        else:
            paare = [(*self.grenze.je_stahl("n", "n", self.staehle[sorte]), E_s)
                     for sorte, E_s in moduln.items()]
        werte = Zwischenwerte(self.id)
        angaben = []
        for name, symbol, E_s in paare:
            n = wertigkeit(E_s=E_s, E_cm=w.E_cm, phi=self.wahl.kriechzahl)
            angaben.append(rf"\qquad {angabe(werte.zahl(name, symbol, n, stellen=2))}")
        return "".join(angaben)

    def _protokoll_fall(self, p: Protokoll, e: Eingaben, erg: Fallergebnis) -> None:
        fall = erg.fall
        index = self.grenze.lastindex
        p.titel(f"{self.grenze.fallwort} – {fall.name}", ebene=3)
        p.gleichung(
            rf"M_{{Ed,{index}}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed,{index}}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

        if not erg.konvergiert:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        eps_m = werte.dehnung("eps_m", r"\varepsilon_m", erg.eps_m, stellen=4)
        chi = werte.kruemmung("chi", r"\chi", erg.chi)
        p.gleichung(
            rf"{angabe(eps_m)} \qquad {angabe(chi)} \qquad "
            r"\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)",
            titel="Gefundene Dehnungsebene")
        N_int = werte.kraft("N_int", "N_{int}", erg.N_int)
        M_int = werte.moment("M_int", "M_{int}", erg.M_int)
        p.gleichung(
            rf"{angabe(N_int)} \;\checkmark \qquad {angabe(M_int)} \;\checkmark",
            titel="Probe: die Ebene erzeugt die Einwirkung")

        wirkt, grenze = erg.vergleich.einwirkung, erg.vergleich.widerstand
        if erg.fliesst:
            self._protokoll_fliessen(p, e, erg, werte, wirkt, grenze)
        else:
            p.gleichung(bedingung(angabe(wirkt), r"\le", angabe(grenze), erg.erfuellt),
                        titel="Grösste Zugspannung in der Bewehrung")
        grad_formel(p, self.d_ausnutzung[fall.name], erg.erfuellungsgrad,
                    grenze, wirkt, erg.erfuellt)

    def _protokoll_fliessen(self, p: Protokoll, e: Eingaben, erg: Fallergebnis,
                            werte: Zwischenwerte, wirkt: Wert, grenze: Wert) -> None:
        """Der Fall, in dem die Spannung am Plateau stehen bleibt."""
        p.text(f"Stahl fliesst (σ_s = {erg.sigma_s / 1e6:.0f} N/mm²) → "
               f"Vergleich über die Dehnung.")
        p.formel(werte.dehnung("eps_y", r"\varepsilon_y", erg.eps_y),
                 r"\frac{@f_s}{@E_s}", {"f_s": e[stahlname(self.wahl.satz.stahl, erg.stahl)],
                                        "E_s": e[stahlname("E_s", erg.stahl)]},
                 titel="Grösste Zugdehnung in der Bewehrung", name=FLIESSDEHNUNG,
                 nachsatz=rf"\quad < \quad {angabe(wirkt)}")
        p.formel(grenze, r"\frac{@sigma}{@E_s}",
                 {"sigma": self.grenze.spannung(erg.sigma_s_adm, erg.stahl),
                  "E_s": e[stahlname("E_s", erg.stahl)]},
                 titel="Zulässige Dehnung",
                 nachsatz=vergleich(r"\ge", angabe(wirkt), erg.erfuellt))
