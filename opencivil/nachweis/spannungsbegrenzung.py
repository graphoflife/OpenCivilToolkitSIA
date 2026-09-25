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

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Sequence

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, N_PRO_MM2, PROMILLE, Groesse,
)
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import mit_index
from opencivil.nachweis.mindestbewehrung import (
    RISSBREITE, zulaessige_stahlspannung,
)
from opencivil.nachweis.querschnittsloeser import (
    EPS_DRUCK, EPS_ZUG, protokoll_verfahren,
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_elastisch,
    stahl_bilinear,
)
from opencivil.nachweis.zustand2 import wertigkeit
from opencivil.querschnitt.platte import Richtung

#: Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
FLIESSABSTAND = 80e6

#: Anforderungen, bei denen der Nachweis gegen Fliessen gefuehrt wird. Bei
#: *normal* steht in der Tabelle ein Strich. Der Nachweis aus der Rissbreite
#: kennt keine solche Liste -- er laeuft immer.
GEFORDERT = ("erhoeht", "hoch")

#: Womit die Werkstoffgesetze rechnen. Ein Gebrauchsnachweis fragt, was der
#: Querschnitt tut, nicht was er darf.
WERKSTOFFE = Werkstoffsatz.CHARAKTERISTISCH


def _formelzeichen(kurzname: str) -> str:
    """``f_yk`` wird zu ``f_{yk}`` -- der ganze Index tief gestellt."""
    zeichen, _, index = kurzname.partition("_")
    return f"{zeichen}_{{{index}}}"


def fallkennung(name: str) -> str:
    """
    Der Fallname, wie er in einer Wert-ID stehen darf.

    Alles ausser Buchstaben und Ziffern wird zum Unterstrich. Damit bilden
    «Feld A» und «Feld-A» auf dieselbe Kennung ab -- wer Fallnamen prueft,
    muss darum auch die Kennungen pruefen, nicht nur die Namen.
    """
    return "".join(z if z.isalnum() else "_" for z in name)


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
        return fallkennung(self.name)


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
    #: «häufiger» / «quasi-ständiger» -- im Titel.
    einwirkung: str
    #: Index an M_Ed und N_Ed in der Herleitung.
    lastindex: str
    #: Ueberschrift je Fall.
    fallwort: str
    referenz: str

    @abstractmethod
    def bezuege(self, querschnitt, posten) -> List[Eingabebezug]:
        """
        Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung.

        Einmal je Nachweis aufgerufen, beim Bauen. Die Grenze merkt sich
        dabei, was sie spaeter zum Rechnen und Schreiben braucht -- eine
        Grenze gehoert darum zu genau einem Nachweis.
        """

    @abstractmethod
    def einleitung(self) -> str:
        """Der erste Satz der Herleitung: wozu der Nachweis da ist."""

    @abstractmethod
    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        """Die zulaessige Stahlspannung in Pa -- gerechnet und mitgeschrieben."""

    @abstractmethod
    def festlegung(self, p: Protokoll) -> None:
        """Welche Werte die Grenze ansetzt, und warum."""


class GrenzeGegenFliessen(Spannungsgrenze):
    """
    ``f_yd - 80 N/mm²`` unter haeufiger Einwirkung -- das Fliessen verhindern.

    Nur bei erhoehter und hoher Anforderung (:data:`GEFORDERT`). Das
    entscheidet der Aufbau, der den Nachweis gar nicht erst baut; die Grenze
    selbst kennt keine Anforderung.
    """

    idteil = "spannung"
    symbolteil = r"\sigma"
    urteilsname = "Stahlspannung"
    art = "σ_s"
    langname = "Stahlspannung gegen Fliessen"
    einwirkung = "häufiger"
    lastindex = "häufig"
    fallwort = "Häufiger Lastfall"
    referenz = "SIA 262:2025, Tabelle 17"

    def bezuege(self, querschnitt, posten) -> List[Eingabebezug]:
        stahl = posten[0][0].stahl
        self.s_f_yd = mit_index("f_{yd}", stahl.symbol_index)
        return [Eingabebezug("f_yd", stahl.id_von("f_yd"))]

    def einleitung(self) -> str:
        return ("Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – "
                "sonst bleiben Risse und Durchbiegung dauerhaft.")

    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        f_yd = e.g("f_yd").si
        sigma_adm = f_yd - FLIESSABSTAND
        p.gleichung(
            rf"\sigma_{{s,adm}} = {self.s_f_yd} - {FLIESSABSTAND / 1e6:.0f}"
            rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {f_yd / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" - {FLIESSABSTAND / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {sigma_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Zulässige Stahlspannung",
            referenz=self.referenz)
        return sigma_adm

    def festlegung(self, p: Protokoll) -> None:
        p.text(
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
    langname = "Stahlspannung aus Rissbreite"
    einwirkung = "quasi-ständiger"
    lastindex = r"\text{quasi-ständig}"
    fallwort = "Quasi-ständiger Lastfall"
    referenz = "SIA 262:2025, 4.4.2"

    def __init__(self, anforderung: str) -> None:
        if anforderung not in RISSBREITE:
            raise ValueError(
                f"Unbekannte Rissanforderung '{anforderung}'. Möglich sind: "
                f"{', '.join(RISSBREITE)}.")
        self.anforderung = anforderung
        self.marken: List[str] = []

    def bezuege(self, querschnitt, posten) -> List[Eingabebezug]:
        stahl = posten[0][0].stahl
        self.marken = [f"{lage.nummer}{art.kuerzel}"
                       for lage, art, _, _, _ in posten]
        self.s_f_yk = mit_index("f_{yk}", stahl.symbol_index)
        self.s_f_ctm = mit_index("f_{ctm}", querschnitt.beton.symbol_index)
        return [
            Eingabebezug("f_yk", stahl.id_von("f_yk")),
            Eingabebezug("E_s", stahl.id_von("E_s")),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
        ] + [
            Eingabebezug(f"dm_{m}", querschnitt.id_von(f"lage.{m}.phi"))
            for m in self.marken
        ]

    def einleitung(self) -> str:
        return ("Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung "
                "die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur "
                "dass die Spannung hier aus den Lasten kommt und nicht aus "
                "einer aufgezwungenen Verformung.")

    def bestimmen(self, e: Eingaben, p: Protokoll) -> float:
        f_yk = e.g("f_yk").si
        E_s = e.g("E_s").si
        f_ctm = e.g("f_ctm").si
        durchmesser = max(e.g(f"dm_{m}").si for m in self.marken)
        sigma_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung, f_yk=f_yk, E_s=E_s, f_ctm=f_ctm,
            durchmesser=durchmesser)

        w_nom = RISSBREITE[self.anforderung]
        if w_nom is None:
            p.gleichung(
                rf"\sigma_{{s,adm}} = {self.s_f_yk} = {sigma_adm / 1e6:.0f}"
                rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
                titel="Zulässige Stahlspannung (normale Anforderung)",
                referenz=self.referenz)
            return sigma_adm

        p.gleichung(
            rf"\varnothing_{{max}} = {durchmesser * 1e3:.0f}\,\mathrm{{mm}}",
            titel="Dickster Stab der Tragrichtung")
        p.gleichung(
            rf"\sigma_{{s,adm}} = \min\left[\sqrt{{\frac{{9 \cdot E_s \cdot "
            rf"{self.s_f_ctm} \cdot w_{{nom}}}}{{\varnothing_{{max}}}}}};\ "
            rf"{self.s_f_yk}\right]"
            "\n= "
            rf"\min\left[\sqrt{{\frac{{9 \cdot {E_s / 1e6:.0f} \cdot "
            rf"{f_ctm / 1e6:.2f} \cdot {w_nom * 1e3:.1f}}}"
            rf"{{{durchmesser * 1e3:.0f}}}}};\ "
            rf"{f_yk / 1e6:.0f}\right]"
            rf" = {sigma_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel=(f"Zulässige Stahlspannung (Rissbreite "
                   f"w_nom = {w_nom * 1e3:.1f} mm)"),
            referenz=self.referenz)
        return sigma_adm

    def festlegung(self, p: Protokoll) -> None:
        p.text(
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

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        faelle: Sequence[Gebrauchsfall],
        *,
        grenze: Spannungsgrenze,
    ) -> None:
        if not faelle:
            raise ValueError("Ohne Lastfall gibt es nichts zu begrenzen.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"liegt keine Bewehrung.")

        self.querschnitt = querschnitt
        self.richtung = richtung
        self.faelle = list(faelle)
        self.grenze = grenze
        self.ergebnisse: List[Fallergebnis] = []

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.{grenze.idteil}.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,{grenze.symbolteil},{r},{als_text(f.name)}}}",
                einheit=EINHEITSLOS,
                beschreibung=(f"Erfüllungsgrad {grenze.langname} "
                              f"{richtung.beschriftung} – {f.name}"),
                referenz=grenze.referenz,
                stellen=2,
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
        for b in grenze.bezuege(querschnitt, self.posten):
            if b.name not in vorhanden:
                bezuege.append(b)
            elif vorhanden[b.name] != b.wert_id:
                raise ValueError(
                    f"Die Grenze meldet '{b.name}' als {b.wert_id}, der "
                    f"Nachweis führt denselben Namen als {vorhanden[b.name]}.")

        self.s_E_cm = mit_index("E_{cm}", beton.symbol_index)
        self.s_f_s = mit_index(_formelzeichen(WERKSTOFFE.stahl),
                               stahl.symbol_index)
        self.s_f_c = mit_index(_formelzeichen(WERKSTOFFE.beton),
                               beton.symbol_index)

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
        E_c_eff = E_cm / (1.0 + phi)

        loeser = Querschnittsloeser(
            h=h, b=b, lagen=lagen,
            beton=beton_elastisch(E_c=E_c_eff, f_c=f_c),
            stahl=stahl_bilinear(E_s=E_s, f_sd=f_s))

        sigma_adm = self._protokoll_ansatz(p, e, E_cm, phi, n, E_c_eff,
                                           E_s, f_s, f_c)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            # Ausgeschaltete Lastfaelle rechnen mit und schweigen dabei.
            leise = self.leise(fall.name)
            erg = self._einen_fall(loeser, fall, sigma_adm, E_s=E_s, f_s=f_s)
            self.ergebnisse.append(erg)
            if not leise:
                self._protokoll_fall(p, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
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
                f"Für {fall.name} lässt sich keine Dehnungsebene finden, die "
                f"M = {fall.M_Ed.formatiert(1, KNM)} kNm und "
                f"N = {fall.N_Ed.formatiert(1, KN)} kN im Gleichgewicht hält. "
                f"Der Querschnitt kann diese Kombination nicht aufnehmen.")
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
        ebene_text = (f"Gerissener Querschnitt: ε_m = {erg.eps_m * 1e3:.4f} ‰, "
                      f"χ = {erg.chi:.5f} 1/m.")
        if erg.fliesst:
            erg.begruendung = (
                f"{ebene_text} Die Bewehrung fliesst: ε_s = "
                f"{erg.eps_s * 1e3:.2f} ‰ über der Fliessdehnung "
                f"{erg.eps_y * 1e3:.2f} ‰, gegen ε_s,adm = "
                f"{erg.eps_s_adm * 1e3:.2f} ‰ aus σ_s,adm = "
                f"{sigma_adm / 1e6:.0f} N/mm².")
        else:
            erg.begruendung = (
                f"{ebene_text} Grösste Zugspannung "
                f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² gegen "
                f"σ_s,adm = {sigma_adm / 1e6:.0f} N/mm².")
        return erg

    def _urteil(self, erg: Fallergebnis, *, still: bool = False) -> NachweisUrteil:
        """
        Das Urteil eines Falls.

        Einwirkung und Widerstand sind Spannungen, solange der Stahl
        elastisch bleibt. Fliesst er, sind es Dehnungen: in der Tabelle
        stuende sonst ``f_yk`` neben ``f_yk`` und daneben «nicht erfuellt» --
        richtig gerechnet und doch nicht zu lesen.
        """
        r = self.richtung.value
        if erg.fliesst:
            einwirkung = WertDef(
                id=f"{self.id}.{erg.fall.kennung}.eps_s",
                symbol=rf"\varepsilon_{{s,{r}}}",
                einheit=PROMILLE, beschreibung="Einwirkung", stellen=2,
            ).belegen(Groesse.aus_si(erg.eps_s, PROMILLE))
            widerstand = WertDef(
                id=f"{self.id}.eps_s_adm",
                symbol=r"\varepsilon_{s,adm}",
                einheit=PROMILLE, beschreibung="Widerstand", stellen=2,
            ).belegen(Groesse.aus_si(erg.eps_s_adm, PROMILLE))
        else:
            einwirkung = WertDef(
                id=f"{self.id}.{erg.fall.kennung}.sigma_s",
                symbol=rf"\sigma_{{s,{r}}}",
                einheit=N_PRO_MM2, beschreibung="Einwirkung", stellen=0,
            ).belegen(Groesse.aus_si(erg.sigma_s, N_PRO_MM2))
            widerstand = WertDef(
                id=f"{self.id}.sigma_s_adm",
                symbol=r"\sigma_{s,adm}",
                einheit=N_PRO_MM2, beschreibung="Widerstand", stellen=0,
            ).belegen(Groesse.aus_si(erg.sigma_s_adm, N_PRO_MM2))
        return NachweisUrteil(
            name=f"{self.grenze.urteilsname} {r} – {erg.fall.name}",
            art=self.grenze.art,
            langname=self.grenze.langname,
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if erg.konvergiert else None,
            widerstand=widerstand if erg.konvergiert else None,
            still=still,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, E_cm: float,
                          phi: float, n: float, E_c_eff: float, E_s: float,
                          f_s: float, f_c: float) -> float:
        """Was fuer alle Faelle gilt -- und die Grenze, die dabei entsteht."""
        g = self.grenze
        p.titel(f"Stahlspannung unter {g.einwirkung} Einwirkung – "
                f"{self.richtung.beschriftung}")
        p.text(
            f"{g.einleitung()} Gerechnet wird am gerissenen Querschnitt: der "
            f"Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem "
            f"wirksamen Modul. Gezählt wird nur gezogene Bewehrung."
        )
        p.gleichung(
            rf"E_{{c,eff}} = \frac{{{self.s_E_cm}}}{{1 + \varphi}}"
            rf" = \frac{{{E_cm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}}}"
            rf"{{1 + {phi:.2f}}}"
            rf" = {E_c_eff / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \qquad n = {n:.2f}",
            titel="Wirksamer Elastizitätsmodul")
        sigma_adm = g.bestimmen(e, p)

        p.titel("Welche Werte angesetzt werden", ebene=3)
        p.text(
            "Drei Festlegungen stecken in jeder Zahl unten, und alle drei "
            "sind Auslegung der Norm und nicht Rechnung. Erstens das "
            "Kriechen: angesetzt wird dasselbe φ wie sonst, hier aus der "
            "Eingabe. Das liegt auf der sicheren Seite – ein grösseres φ "
            "weicht den Beton auf, die Druckzone wächst, der Hebelarm wird "
            "kleiner und die Stahlspannung damit grösser. Wer φ = 0 setzte, "
            "bekäme kleinere Spannungen und einen Nachweis, der leichter "
            "aufgeht."
        )
        p.text(
            "Zweitens die Werkstoffgesetze: sie rechnen mit den "
            "charakteristischen Festigkeiten. Der Stahl ist linear bis f_yk "
            "und fliesst dann, der Beton linear bis f_ck. Ein "
            "Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was "
            "er darf – der Teilsicherheitsbeiwert gehört in die "
            "Tragsicherheit. Läge das Plateau bei f_yd, bliebe jede "
            "Stahlspannung darunter, und eine Grenze darüber könnte nie "
            "überschritten werden."
        )
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {self.s_f_s}"
            rf"\right] \quad {self.s_f_s} = {f_s / 1e6:.0f}"
            rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}} \qquad "
            rf"\sigma_c = \max\left[E_{{c,eff}} \cdot \varepsilon_c;\ "
            rf"-{self.s_f_c}\right] \quad {self.s_f_c} = {f_c / 1e6:.0f}"
            rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Werkstoffgesetze im Gebrauchszustand")
        g.festlegung(p)
        p.text(
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

    def _protokoll_fall(self, p: Protokoll, erg: Fallergebnis) -> None:
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

        p.gleichung(
            rf"\varepsilon_m = {erg.eps_m * 1e3:.4f}\,\text{{‰}} \qquad "
            rf"\chi = {erg.chi:.5f}\,\mathrm{{m}}^{{-1}}"
            rf" \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot "
            rf"\left(z - \tfrac{{h}}{{2}}\right)",
            titel="Gefundene Dehnungsebene")
        p.gleichung(
            rf"N_{{int}} = {erg.N_int / 1e3:.1f}\,\mathrm{{kN}} \;\checkmark"
            rf" \qquad M_{{int}} = {erg.M_int / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \;\checkmark",
            titel="Probe: die Ebene erzeugt die Einwirkung")

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        grad = ("\\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")

        if erg.fliesst:
            self._protokoll_fliessen(p, erg, zustand, grad)
            return

        vergleich = r"\le" if erg.erfuellt else ">"
        p.gleichung(
            rf"\sigma_s = {erg.sigma_s / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \quad {vergleich} \quad \sigma_{{s,adm}} = "
            rf"{erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Grösste Zugspannung in der Bewehrung")
        # Ohne Zug in der Bewehrung gibt es nichts einzusetzen -- dann stuende
        # dort eine Null im Nenner.
        eingesetzt = (
            rf" = \frac{{{erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}}}"
            rf"{{{erg.sigma_s / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}}}"
            if erg.sigma_s > 0.0 else "")
        p.gleichung(
            rf"\alpha_{{eff,\sigma}} = "
            rf"\frac{{\sigma_{{s,adm}}}}{{\sigma_s}}{eingesetzt} = {grad}",
            titel="Erfüllungsgrad")

    def _protokoll_fliessen(self, p: Protokoll, erg: Fallergebnis,
                            zustand: str, grad: str) -> None:
        """Der Fall, in dem die Spannung am Plateau stehen bleibt."""
        p.text(
            f"Die Bewehrung fliesst: die grösste Zugdehnung liegt über der "
            f"Fliessdehnung, die Spannung steht bei {erg.sigma_s / 1e6:.0f} "
            f"N/mm² und sagt nichts mehr darüber, wie weit die Grenze "
            f"überschritten ist. Verglichen wird die Dehnung."
        )
        p.gleichung(
            rf"\varepsilon_s = {erg.eps_s * 1e3:.2f}\,\text{{‰}} \quad > \quad "
            rf"\varepsilon_{{y}} = \frac{{{self.s_f_s}}}{{E_s}}"
            rf" = {erg.eps_y * 1e3:.2f}\,\text{{‰}}",
            titel="Grösste Zugdehnung in der Bewehrung")
        vergleich = r"\le" if erg.erfuellt else ">"
        p.gleichung(
            rf"\varepsilon_{{s,adm}} = \frac{{\sigma_{{s,adm}}}}{{E_s}}"
            rf" = {erg.eps_s_adm * 1e3:.2f}\,\text{{‰}} \qquad "
            rf"\varepsilon_s = {erg.eps_s * 1e3:.2f}\,\text{{‰}} \quad "
            rf"{vergleich} \quad \varepsilon_{{s,adm}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Zulässige Dehnung")
        p.gleichung(
            rf"\alpha_{{eff,\sigma}} = "
            rf"\frac{{\varepsilon_{{s,adm}}}}{{\varepsilon_s}}"
            rf" = \frac{{{erg.eps_s_adm * 1e3:.2f}\,\text{{‰}}}}"
            rf"{{{erg.eps_s * 1e3:.2f}\,\text{{‰}}}} = {grad}",
            titel="Erfüllungsgrad")
