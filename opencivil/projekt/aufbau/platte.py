"""
opencivil/projekt/aufbau/platte.py -- eine Platte wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.platte.QuerschnittEintrag` der
Plattenquerschnitt und alle Nachweise, die an ihm haengen: M-N, Querkraft,
die Nachweise je x-Lage, die Stahlspannungen, Verformung und Knicken, dazu
Vergroesserungsfaktor und Kennzahlen. Nachgewiesen wird nur die
Tragrichtung x (:func:`bauen`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Mapping, Sequence

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, KN_PRO_M, M, MM, Groesse
from opencivil.material.basis import Baustoff
from opencivil.nachweis.biegung_normalkraft import BiegungNormalkraft, Schnittgroessen
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.knicken import Knicken
from opencivil.nachweis.fehlende_bewehrung import Ausgefallen, FehlendeBewehrung
from opencivil.nachweis.mindestbewehrung import Rissnormalkraft, ZwaengungBiegung
from opencivil.nachweis.spannungsbegrenzung import Gebrauchsfall, PlattenStellen
from opencivil.nachweis import dehnungsfaecher
from opencivil.nachweis.verformung import Vergroesserungsfaktor, Verformung, Verformungsfall
from opencivil.nachweis.kennzahlen import Plattenkennzahlen
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.nachweis.querkraft import Querkraft, Querkraftfall
from opencivil.querschnitt.platte import Bewehrungslage, Plattenquerschnitt, Richtung
from opencivil.projekt.eintraege import KombinationEintrag, VerformungsfallEintrag
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.platte import QuerschnittEintrag

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, knickfall, material, spannungsnachweise

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: QuerschnittEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Eine Platte: der Querschnitt und alle Nachweise, die an ihm haengen.

    Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen im
    Querschnitt -- sie tragen zum Bewehrungsgehalt bei und druecken die
    statische Hoehe von x nach innen --, aber kein Nachweis fragt nach ihnen.
    Vorher lief hier alles doppelt, einmal je Richtung, und die Haelfte der
    Tabelle handelte von einer Richtung, fuer die niemand Schnittgroessen
    hatte.
    """
    querschnitt = _querschnitt(eintrag, aufbau.baustoffe, praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.querschnitte[eintrag.kennung] = querschnitt
    querschnitt.ins_rechenwerk(aufbau.werk)
    # Bewehrungsmass und Distanzhalter stehen als Kennzahlen da, auch bei
    # einer Platte ohne Nachweis -- ihr Lagenaufbau rechnet darum immer.
    teil = Bauteil(eintrag.kennung, eintrag.name, art, querschnitt,
                   weitere_ziele=[f"{querschnitt.id}.lagenaufbau"],
                   kennzahlen=list(querschnitt.kennzahlen))
    schnell = aufbau.schnell

    richtung = Richtung.X
    kennung_x = f"{eintrag.kennung}.x"
    aktiv = [k for k in eintrag.kombinationen if k.aktiv]

    if richtung not in querschnitt.richtungen_mit_bewehrung:
        if aktiv:
            # Ohne Bewehrung laesst sich hier nichts aufstellen. Der
            # Nachweis entfiel frueher stillschweigend; wer eine Einwirkung
            # angegeben hatte, fand sie nirgends wieder.
            aufbau.eintragen(teil, "fehlende", kennung_x, FehlendeBewehrung(
                querschnitt, richtung, _ausgefallene(aktiv, richtung)))
        if eintrag.knickfaelle:
            aufbau.warnungen.append(
                f"Platte '{eintrag.name}': ohne x-Bewehrung kein Knicknachweis.")
        if eintrag.verformung.faelle:
            aufbau.warnungen.append(
                f"Platte '{eintrag.name}': ohne x-Bewehrung kein Verformungsnachweis.")
    else:
        # Der M-N-Nachweis entsteht auch ohne Schnittgroessen: seine
        # Eckwerte gehoeren dem Querschnitt, nicht der Einwirkung, und der
        # Nachweis gegen sproedes Versagen haelt M_Rd(N=0) dagegen. Ohne die
        # Vergleichslinie, wenn schnell gerechnet wird: sie kostet fast die
        # ganze Zeit dieses Nachweises und wird allein im Diagramm gebraucht.
        # Wer schnell rechnet, sucht eine Bewehrung und sieht dabei kein
        # Diagramm an.
        nachweis = BiegungNormalkraft(
            querschnitt, [_kombination(k) for k in aktiv], richtung,
            wahl=eintrag.tragsicherheit_wahl.wahl, mit_vergleich=not schnell,
            schritte=dehnungsfaecher.SCHRITTE_SUCHE if schnell else dehnungsfaecher.SCHRITTE)
        aufbau.eintragen(teil, "nachweise", kennung_x, nachweis)

        _lagennachweise(eintrag, querschnitt, richtung, nachweis, aufbau, teil)
        spannungsnachweise(
            eintrag, PlattenStellen(querschnitt, richtung), eintrag.kombinationen,
            lambda name, k, faktor: Gebrauchsfall(name=name, M_Ed=Groesse(faktor * k.M_Ed, KNM),
                                                   N_Ed=Groesse(faktor * k.N_Ed, KN)),
            praefix="", kennung=kennung_x, aufbau=aufbau, teil=teil)

        # Der Vergroesserungsfaktor gehoert der Platte, nicht einem Fall: er
        # rechnet immer, als Kennzahl, und der Verformungsnachweis liest ihn.
        faktor = Vergroesserungsfaktor(querschnitt, kriechzahl=eintrag.verformung.kriechzahl)
        aufbau.werk.registriere(faktor)
        verformungsfaelle = [f for f in eintrag.verformung.faelle if f.aktiv]
        if verformungsfaelle:
            aufbau.eintragen(teil, "verformung", eintrag.kennung, Verformung(
                querschnitt, [_verformungsfall(f) for f in verformungsfaelle],
                faktor=faktor))

        # Auch ohne V_Ed: dann still, nur fuer das Diagramm und die Kennzahlen.
        querkraft = Querkraft(
            querschnitt,
            [Querkraftfall(name=k.name,
                           V_Ed=Groesse(k.V_Ed, KN_PRO_M),
                           M_Ed=Groesse(k.M_Ed, KNM),
                           N_Ed=Groesse(k.N_Ed, KN))
             for k in aktiv if k.V_Ed],
            richtung, nachweis)
        aufbau.eintragen(teil, "querkraft", kennung_x, querkraft)

        # Was die Platte aufnimmt, ohne Einwirkung -- immer (Benutzer,
        # 2026-10-16). Am Ende der Platte, nach ihren Nachweisen.
        kennzahlen = Plattenkennzahlen(querschnitt, nachweis, querkraft)
        aufbau.werk.registriere(kennzahlen)
        aufbau.kennzahlen[eintrag.kennung] = kennzahlen
        teil.weitere_ziele += [faktor.id, kennzahlen.id]
        teil.kennzahlen += faktor.kennzahlen + kennzahlen.kennzahlen

        knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
        if knickfaelle:
            aufbau.eintragen(teil, "knicken", eintrag.kennung, Knicken(
                querschnitt, [knickfall(k) for k in knickfaelle],
                nachweis, verformung=eintrag.knicken_wahl_verformung.wahl,
                widerstand=eintrag.knicken_wahl_widerstand.wahl, schnell=schnell))

    aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
    if aktive:
        aufbau.spannungsfaelle[eintrag.kennung] = aktive

    if not eintrag.kombinationen:
        aufbau.warnungen.append(
            f"Platte '{eintrag.name}': keine Schnittgrössen → kein "
            f"Tragsicherheitsnachweis.")
    return teil


def _lagennachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt,
                    richtung: Richtung, nachweis: BiegungNormalkraft,
                    aufbau: Aufbau, teil: Bauteil) -> None:
    """
    Die Nachweise je x-Lage: sproedes Versagen, Zwaengung auf Biegung und
    auf Normalkraft, Duktilitaet.

    Die x-Lagen von unten nach oben; in die Zusammenfassung kommt die
    unguenstigere. Ausgeschaltet heisst still -- gerechnet wird trotzdem,
    damit ein Hinweis stehen kann.

    **Eine Lage ohne Stahl lassen sproedes Versagen, Zwaengung auf Biegung
    und Duktilitaet weg** (Benutzer, 2026-10-19): sie wird nicht
    nachgewiesen und steht nicht in der Tabelle. Bis dahin bekam sie ein
    Urteil «ohne Bewehrung → kein Nachweis», das als nicht erfuellt zaehlte --
    eine Platte nur mit unterer Bewehrung galt so als nicht erfuellt. Die
    Zwaengung auf Normalkraft waehlt ihre Lagen selbst und prueft jede.
    """
    lagen = [l.nummer for l in querschnitt.lagen if l.richtung is richtung and l.vorhanden]
    if not lagen:
        return
    kennung_x = f"{eintrag.kennung}.x"

    sproede = SproedesVersagen(querschnitt, richtung, lagen, nachweis)
    sproede.still = not eintrag.sproede
    aufbau.eintragen(teil, "sproede", kennung_x, sproede)

    biegung = ZwaengungBiegung(
        querschnitt, richtung, lagen,
        anforderung=eintrag.rissanforderung,
        kriechzahl=eintrag.zwaengung_biegung_kriechzahl)
    biegung.still = not eintrag.zwaengung_biegung
    aufbau.eintragen(teil, "zwaengung_biegung", kennung_x, biegung)

    zwang = Rissnormalkraft(
        querschnitt, richtung,
        anforderung=eintrag.rissanforderung,
        begrenzt=eintrag.zwaengung_begrenzt)
    zwang.still = not eintrag.zwaengung
    aufbau.eintragen(teil, "rissnormalkraft", kennung_x, zwang)

    duktilitaet = Duktilitaet(querschnitt, lagen, grenze=eintrag.x_d_max)
    duktilitaet.still = not eintrag.duktilitaet
    aufbau.eintragen(teil, "duktilitaet", eintrag.kennung, duktilitaet)


def _querschnitt(
    eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str
) -> Plattenquerschnitt:
    beton_stoff = material(baustoffe, eintrag.beton, "beton", f"Platte '{eintrag.name}'")
    # Ein Stahl fuer die ganze Platte, Lagen und Buegel (Benutzer, 2026-10-24)
    # -- auch fuer eine leere Lage: ihr Stahl erscheint nur, wo die
    # Mindestbewehrung sie als leer meldet.
    stahl = material(baustoffe, eintrag.stahl, "betonstahl", f"Die Bewehrung von '{eintrag.name}'")

    lagen: List[Bewehrungslage] = []
    for nummer, lage in enumerate(eintrag.lagen, start=1):
        lagen.append(Bewehrungslage(
            nummer=nummer,
            richtung=eintrag.richtung_von(nummer),
            stahl=stahl,
            grund=lage.grund.als_posten(),
            zulage=lage.zulage.als_posten(),
            unguenstig=lage.unguenstig,
        ))

    if not any(l.vorhanden for l in lagen):
        raise ProjektFehler(
            f"Platte '{eintrag.name}': ohne Bewehrung lässt sich kein "
            f"Widerstand bestimmen.")

    buegel = eintrag.querkraftbewehrung
    return Plattenquerschnitt(
        name=eintrag.name,
        h=Groesse(eintrag.h, MM),
        b=Groesse(eintrag.b, MM),
        beton=beton_stoff,
        lagen=lagen,
        ueberdeckung_unten=Groesse(eintrag.ueberdeckung_unten, MM),
        ueberdeckung_oben=Groesse(eintrag.ueberdeckung_oben, MM),
        d_max=Groesse(eintrag.d_max, MM),
        einlagenhoehe=Groesse(eintrag.einlagenhoehe, MM),
        k_c=Groesse(eintrag.k_c, EINHEITSLOS),
        querkraftbewehrung=buegel.als_bewehrung(stahl) if buegel.vorhanden else None,
        praefix=praefix,
    )


def _verformungsfall(f: VerformungsfallEintrag) -> Verformungsfall:
    """Ein Verformungsfall aus seiner Beschreibung -- w in mm, die Spannweite in m."""
    return Verformungsfall(name=f.name, w=Groesse(f.w, MM), laenge=Groesse(f.laenge, M),
                           zugseite=f.zugseite)


def _ausgefallene(
    kombinationen: Sequence[KombinationEintrag], richtung: Richtung
) -> List[Ausgefallen]:
    """
    Welche Nachweise in dieser unbewehrten Richtung ausfallen.

    Je Kombination der M-N-Nachweis, und wo eine Querkraft angegeben ist,
    auch der Querkraftnachweis: ohne Bewehrung gibt es keine statische
    Hoehe, also auch keinen Querkraftwiderstand. Beide Zeilen gehoeren in
    die Tabelle -- eine davon wegzulassen hiesse, die Luecke nur zur
    Haelfte zu schliessen.
    """
    r = richtung.value
    # Erst alle M-N, dann alle Querkraft -- dieselbe Folge wie bei den
    # Richtungen, die wirklich gerechnet werden. Zeilen derselben Art
    # gehoeren beieinander.
    return [
        Ausgefallen(
            art="M-N", langname=BiegungNormalkraft.THEMA,
            fall=k.name,
            symbol=f"M_{{Rd,{r}}}",
            einwirkung_symbol=f"M_{{Ed,{r}}}",
            einwirkung=Groesse(k.M_Ed, KNM), einheit=KNM)
        for k in kombinationen
    ] + [
        Ausgefallen(
            art="V", langname=Querkraft.THEMA, fall=k.name,
            symbol=f"V_{{Rd,{r}}}",
            einwirkung_symbol=f"V_{{Ed,{r}}}",
            einwirkung=Groesse(abs(k.V_Ed), KN_PRO_M), einheit=KN_PRO_M)
        for k in kombinationen if k.V_Ed
    ]


def _kombination(eintrag: KombinationEintrag) -> Schnittgroessen:
    """Eine Einwirkung -- welche Massstaebe es gibt, prueft ihr Feld."""
    return Schnittgroessen(
        name=eintrag.name,
        M_Ed=Groesse(eintrag.M_Ed, KNM),
        N_Ed=Groesse(eintrag.N_Ed, KN),
        art=eintrag.art,
    )
