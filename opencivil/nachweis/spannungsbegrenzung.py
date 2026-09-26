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
haelt. Der Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem
wirksamen Modul ``E_cm/(1+phi)``. Die Plateaus liegen bei den
**charakteristischen** Festigkeiten (:class:`Werkstoffsatz`): der Stahl
fliesst bei ``f_yk``, der Beton traegt hoechstens ``f_ck``. **Nur gezogene
Bewehrung zaehlt** -- eine gedrueckte Lage wuerde den Hebelarm vergroessern
und den Nachweis guenstiger machen, als er ist.

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
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.core.latex import als_text, angabe, bedingung, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.nachweis.mindestbewehrung import (
    RISSBREITE, protokoll_zulaessige_stahlspannung, zulaessige_stahlspannung,
)
from opencivil.nachweis.querschnittsloeser import (
    EPS_DRUCK, EPS_ZUG, protokoll_verfahren, protokoll_wirksamer_modul, wirksamer_modul,
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_elastisch,
    stahl_bilinear,
)
from opencivil.nachweis.zustand2 import wertigkeit
from opencivil.querschnitt.platte import Richtung

#: Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
FLIESSABSTAND = 80e6

#: Anforderungen, bei denen der Nachweis gegen Fliessen gefuehrt wird. Bei
#: *normal* steht in der Tabelle ein Strich. Von aussen fragt man
#: :meth:`GrenzeGegenFliessen.gilt_bei` -- die Liste gehoert der Grenze.
_GEFORDERT = ("erhoeht", "hoch")

#: Womit die Werkstoffgesetze rechnen. Ein Gebrauchsnachweis fragt, was der
#: Querschnitt tut, nicht was er darf.
WERKSTOFFE = Werkstoffsatz.CHARAKTERISTISCH


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
    #: Anfang des Urteilsnamens, vor Richtung und Fall.
    urteilsname: str
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

    def __init__(self, querschnitt, richtung: Richtung, anforderung: str) -> None:
        """
        Alle Grenzen werden gleich gebaut -- aus der Platte, der Tragrichtung
        und der Rissanforderung. Was eine davon nicht braucht, laesst sie
        liegen; so kann der Aufbau beide in derselben Schleife anlegen.
        """
        if anforderung not in RISSBREITE:
            raise ValueError(
                f"Unbekannte Rissanforderung '{anforderung}'. Möglich sind: "
                f"{', '.join(RISSBREITE)}.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"liegt keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.stahl = self.posten[0][0].stahl

    @property
    def id(self) -> str:
        """Die Kennung des Nachweises, zu dem die Grenze gehoert."""
        return f"{self.querschnitt.id}.nachweis.{self.idteil}.{self.richtung.value}"

    def spannung(self, sigma_adm: float) -> Wert:
        """``sigma_s,adm`` als Wert -- in Herleitung, Vergleich und Tabelle derselbe."""
        return Zwischenwerte(self.id).spannung(
            "sigma_s_adm", r"\sigma_{s,adm}", sigma_adm, "Widerstand")

    @classmethod
    def gilt_bei(cls, anforderung: str) -> bool:
        """Ob der Nachweis bei dieser Rissanforderung verlangt ist."""
        return True

    @abstractmethod
    def bezuege(self) -> List[Eingabebezug]:
        """Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung."""

    @abstractmethod
    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        """Die zulaessige Stahlspannung in Pa -- gerechnet und mitgeschrieben."""

    @abstractmethod
    def festlegung(self, p: Protokoll) -> None:
        """Welche Werte die Grenze ansetzt, und warum."""


class GrenzeGegenFliessen(Spannungsgrenze):
    """
    ``f_yd - 80 N/mm²`` unter haeufiger Einwirkung -- das Fliessen verhindern.

    Nur bei erhoehter und hoher Anforderung -- bei normaler steht in
    Tabelle 17 ein Strich. Das sagt :meth:`gilt_bei`; der Aufbau fragt, und
    der Katalog der Oberflaeche auch.
    """

    idteil = "spannung"
    symbolteil = r"\sigma"
    urteilsname = "Stahlspannung"
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
    def gilt_bei(cls, anforderung: str) -> bool:
        return anforderung in _GEFORDERT

    def bezuege(self) -> List[Eingabebezug]:
        return [Eingabebezug("f_yd", self.stahl.id_von("f_yd"))]

    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        sigma_adm = e.g("f_yd").si - FLIESSABSTAND
        # Die 80 N/mm² haben kein Zeichen -- sie stehen als Zahl in der Formel.
        abstand = Groesse.aus_si(FLIESSABSTAND, N_PRO_MM2).als_latex(0)
        p.formel(self.spannung(sigma_adm), f"@f_yd - {abstand}", {"f_yd": e["f_yd"]},
                 titel="Zulässige Stahlspannung", referenz=self.referenz)
        return sigma_adm

    def festlegung(self, p: Protokoll) -> None:
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
    urteilsname = "Stahlspannung (Rissbreite)"
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

    def __init__(self, querschnitt, richtung: Richtung, anforderung: str) -> None:
        super().__init__(querschnitt, richtung, anforderung)
        self.marken = [f"{lage.nummer}{art.kuerzel}"
                       for lage, art, _, _, _ in self.posten]

    def bezuege(self) -> List[Eingabebezug]:
        return [
            Eingabebezug("f_yk", self.stahl.id_von("f_yk")),
            Eingabebezug("E_s", self.stahl.id_von("E_s")),
            Eingabebezug("f_ctm", self.querschnitt.beton.id_von("f_ctm")),
        ] + [
            Eingabebezug(f"dm_{m}", self.querschnitt.id_von(f"lage.{m}.phi"))
            for m in self.marken
        ]

    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        f_yk = e.g("f_yk").si
        E_s = e.g("E_s").si
        f_ctm = e.g("f_ctm").si
        durchmesser = max(e.g(f"dm_{m}").si for m in self.marken)
        sigma_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung, f_yk=f_yk, E_s=E_s, f_ctm=f_ctm,
            durchmesser=durchmesser)

        werte = Zwischenwerte(self.id)
        dm = werte.laenge("dm_max", r"\varnothing_{max}", durchmesser, stellen=0)
        if RISSBREITE[self.anforderung] is not None:
            p.wert(dm, titel="Dickster Stab der Tragrichtung")
        protokoll_zulaessige_stahlspannung(
            p, self.spannung(sigma_adm),
            anforderung=self.anforderung, f_yk=e["f_yk"], E_s=e["E_s"],
            f_ctm=e["f_ctm"], durchmesser=dm, basis=self.id, referenz=self.referenz)
        return sigma_adm

    def festlegung(self, p: Protokoll) -> None:
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
# Der Nachweis
# ===========================================================================


class Spannungsbegrenzung(Nachweis):
    """
    Stahlspannung unter Gebrauchslast, je Tragrichtung, gegen eine Grenze.

    Ein Urteil je Lastfall. Gerechnet wird am gerissenen Querschnitt mit dem
    wirksamen Elastizitätsmodul und charakteristischen Festigkeiten; gezählt
    wird nur die gezogene Bewehrung. Wogegen gehalten wird, sagt ``grenze``.
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
        self.ergebnisse: List[Fallergebnis] = []

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

        stahl = self.posten[0][0].stahl
        beton = querschnitt.beton
        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
            Eingabebezug("E_cm", beton.id_von("E_cm")),
            Eingabebezug("phi", querschnitt.id_von("kriechzahl")),
            Eingabebezug("E_s", stahl.id_von("E_s")),
            Eingabebezug(WERKSTOFFE.stahl, stahl.id_von(WERKSTOFFE.stahl)),
            Eingabebezug(WERKSTOFFE.beton, beton.id_von(WERKSTOFFE.beton)),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            bezuege += [
                Eingabebezug(f"a_s_{marke}", as_id),
                Eingabebezug(f"z_{marke}", z_id),
            ]
        # Was die Grenze braucht, kann schon dastehen -- E_s und f_yk braucht
        # auch das Werkstoffgesetz. Doppelt anmelden ginge nicht, und dieselbe
        # Zahl unter zwei Namen zu fuehren hiesse, sie zweimal zu lesen.
        vorhanden = {b.name: b.wert_id for b in bezuege}
        for b in grenze.bezuege():
            if b.name not in vorhanden:
                bezuege.append(b)
            elif vorhanden[b.name] != b.wert_id:
                raise ValueError(
                    f"Die Grenze meldet '{b.name}' als {b.wert_id}, der "
                    f"Nachweis führt denselben Namen als {vorhanden[b.name]}.")

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
        E_cm = e.g("E_cm").si
        phi = e.g("phi").si
        E_s = e.g("E_s").si
        f_s = e.g(WERKSTOFFE.stahl).si
        f_c = e.g(WERKSTOFFE.beton).si

        lagen = [Stahllage(a_s=e.g(f"a_s_{l.nummer}{a.kuerzel}").si,
                           z=e.g(f"z_{l.nummer}{a.kuerzel}").si,
                           nummer=l.nummer)
                 for l, a, _, _, _ in self.posten]
        n = wertigkeit(E_s=E_s, E_cm=E_cm, phi=phi)
        E_c_eff = wirksamer_modul(E_cm, phi)

        loeser = Querschnittsloeser(
            h=h, b=b, lagen=lagen,
            beton=beton_elastisch(E_c=E_c_eff, f_c=f_c),
            stahl=stahl_bilinear(E_s=E_s, f_sd=f_s))

        sigma_adm = self._protokoll_ansatz(p, e, n)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            # Ausgeschaltete Lastfaelle rechnen mit und schweigen dabei.
            leise = self.leise(fall.name)
            erg = self._einen_fall(loeser, fall, sigma_adm, E_s=E_s, f_s=f_s)
            self.ergebnisse.append(erg)
            if not leise:
                self._protokoll_fall(p, e, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg, still=leise))

        return ergebnis, urteile

    def _einen_fall(self, loeser: Querschnittsloeser, fall: Gebrauchsfall,
                    sigma_adm: float, *, E_s: float, f_s: float) -> Fallergebnis:
        erg = Fallergebnis(fall=fall, sigma_s_adm=sigma_adm,
                           eps_s_adm=sigma_adm / E_s, eps_y=f_s / E_s)
        ebene = loeser.loese(N_Ed=fall.N_Ed.si, M_Ed=fall.M_Ed.si)
        erg.konvergiert = ebene.konvergiert
        if not ebene.konvergiert:
            erg.begruendung = erg.hinweis = (
                f"Keine Dehnungsebene für M = {fall.M_Ed.formatiert(1, KNM)} kNm, "
                f"N = {fall.N_Ed.formatiert(1, KN)} kN → nicht aufnehmbar.")
            return erg

        erg.eps_m, erg.chi = ebene.eps_m, ebene.chi
        erg.N_int, erg.M_int = ebene.N_int, ebene.M_int
        # Nur gezogene Bewehrung: eine gedrueckte Lage hat keine Zugspannung,
        # die zu begrenzen waere. Gesucht wird die groesste *Dehnung* -- auf
        # dem Plateau haben mehrere Lagen dieselbe Spannung, aber nur eine
        # ist am weitesten gedehnt.
        zug = [(eps, sig) for eps, sig in zip(ebene.eps_s, ebene.sigma_s)
               if eps > 0.0]
        if zug:
            erg.eps_s, erg.sigma_s = max(zug)

        # An der Dehnung gemessen, siehe Dateikopf. Elastisch ist E_s * eps_s
        # dieselbe Zahl wie sigma_s -- Bit fuer Bit, denn das Gesetz rechnet
        # dort genau dieses Produkt.
        gedehnt = E_s * erg.eps_s
        erg.erfuellungsgrad = (float("inf") if gedehnt <= 0.0
                               else sigma_adm / gedehnt)
        erg.erfuellt = gedehnt <= sigma_adm
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
            return Vergleich(
                einwirkung=fall.dehnung(
                    "eps_s", rf"\varepsilon_{{s,{r}}}", erg.eps_s, "Einwirkung"),
                widerstand=Zwischenwerte(self.id).dehnung(
                    "eps_s_adm", r"\varepsilon_{s,adm}", erg.eps_s_adm, "Widerstand"),
                satz=(f"Stahl fliesst (ε_s = {erg.eps_s * 1e3:.2f} ‰ > ε_y = "
                      f"{erg.eps_y * 1e3:.2f} ‰): ε_s {'≤' if erg.erfuellt else '>'} "
                      f"ε_s,adm = {erg.eps_s_adm * 1e3:.2f} ‰."))
        return Vergleich(
            einwirkung=fall.spannung(
                "sigma_s", rf"\sigma_{{s,{r}}}", erg.sigma_s, "Einwirkung"),
            widerstand=self.grenze.spannung(erg.sigma_s_adm),
            satz=(f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² {'≤' if erg.erfuellt else '>'} "
                  f"σ_s,adm = {erg.sigma_s_adm / 1e6:.0f} N/mm²."))

    def _urteil(self, erg: Fallergebnis, *, still: bool = False) -> NachweisUrteil:
        """Das Urteil eines Falls -- was gegeneinander steht, sagt der Vergleich."""
        r = self.richtung.value
        vergleich = erg.vergleich
        return NachweisUrteil(
            name=f"{self.grenze.urteilsname} {r} – {erg.fall.name}",
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

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, n: float) -> float:
        """Was fuer alle Faelle gilt -- und die Grenze, die dabei entsteht."""
        g = self.grenze
        p.titel(f"Stahlspannung unter {g.einwirkung} Einwirkung – "
                f"{self.richtung.beschriftung}")
        p.erklaerung(
            f"{g.einleitung} Gerechnet wird am gerissenen Querschnitt: der "
            f"Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem "
            f"wirksamen Modul. Gezählt wird nur gezogene Bewehrung."
        )
        wertigkeit = Zwischenwerte(self.id).zahl("n", "n", n, stellen=2)
        protokoll_wirksamer_modul(p, e, self.id, titel="Wirksamer Elastizitätsmodul",
                                  nachsatz=rf"\qquad {angabe(wertigkeit)}")
        sigma_adm = g.bestimmen(e, p)

        p.titel("Welche Werte angesetzt werden", ebene=3)
        p.erklaerung(
            "Drei Festlegungen stecken in jeder Zahl unten, und alle drei "
            "sind Auslegung der Norm und nicht Rechnung. Erstens das "
            "Kriechen: angesetzt wird dasselbe φ wie sonst, hier aus der "
            "Eingabe. Das liegt auf der sicheren Seite – ein grösseres φ "
            "weicht den Beton auf, die Druckzone wächst, der Hebelarm wird "
            "kleiner und die Stahlspannung damit grösser. Wer φ = 0 setzte, "
            "bekäme kleinere Spannungen und einen Nachweis, der leichter "
            "aufgeht."
        )
        p.erklaerung(
            "Zweitens die Werkstoffgesetze: sie rechnen mit den "
            "charakteristischen Festigkeiten. Der Stahl ist linear bis f_yk "
            "und fliesst dann, der Beton linear bis f_ck. Ein "
            "Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was "
            "er darf – der Teilsicherheitsbeiwert gehört in die "
            "Tragsicherheit. Läge das Plateau bei f_yd, bliebe jede "
            "Stahlspannung darunter, und eine Grenze darüber könnte nie "
            "überschritten werden."
        )
        f_s, f_c = e[WERKSTOFFE.stahl], e[WERKSTOFFE.beton]
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {f_s.symbol}\right]"
            rf" \quad {angabe(f_s)} \qquad "
            rf"\sigma_c = \max\left[E_{{c,eff}} \cdot \varepsilon_c;\ -{f_c.symbol}\right]"
            rf" \quad {angabe(f_c)}",
            titel="Werkstoffgesetze im Gebrauchszustand")
        g.festlegung(p)
        p.erklaerung(
            "Fliesst die Bewehrung, bleibt ihre Spannung bei f_yk stehen, "
            "während die Dehnung weiterwächst. Verglichen wird dann die "
            "Dehnung: ε_s gegen ε_s,adm = σ_s,adm / E_s. Solange der Stahl "
            "elastisch bleibt, ist das genau der Spannungsvergleich; fliesst "
            "er, fällt der Nachweis durch, und zwar um so deutlicher, je "
            "weiter er gedehnt ist."
        )
        p.titel("Wie die Dehnungsebene gefunden wird", ebene=3)
        protokoll_verfahren(p, eps_druck=EPS_DRUCK, eps_zug=EPS_ZUG)
        return sigma_adm

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
                 r"\frac{@f_s}{@E_s}", {"f_s": e[WERKSTOFFE.stahl], "E_s": e["E_s"]},
                 titel="Grösste Zugdehnung in der Bewehrung",
                 nachsatz=rf"\quad < \quad {angabe(wirkt)}")
        p.formel(grenze, r"\frac{@sigma}{@E_s}",
                 {"sigma": self.grenze.spannung(erg.sigma_s_adm), "E_s": e["E_s"]},
                 titel="Zulässige Dehnung",
                 nachsatz=vergleich(r"\ge", angabe(wirkt), erg.erfuellt))
