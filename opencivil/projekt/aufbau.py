"""
opencivil/projekt/aufbau.py -- aus der Beschreibung ein Rechenwerk.

VERANTWORTUNG:
:func:`aufbauen` macht aus einem :class:`Projekt` Baustoffe, Querschnitte und
Nachweise und meldet sie in einem :class:`Rechenwerk` an. Heraus kommt ein
:class:`Aufbau` -- das Werk samt allen Nachweisobjekten, nach Platte und Art
abgelegt, damit Schnittstelle, Zwischenspeicher und Bewehrungssuche sie
wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Sequence, Tuple,
)

from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, KN_PRO_M, M, MM, Groesse,
)
from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.knicken import Knickfall, Knicken
from opencivil.nachweis.fehlende_bewehrung import (
    Ausgefallen, FehlendeBewehrung,
)
from opencivil.nachweis.mindestbewehrung import (
    Rissnormalkraft, ZwaengungBiegung,
)
from opencivil.nachweis.spannungsbegrenzung import (
    GEFORDERT, Gebrauchsfall, GrenzeAusRissbreite, GrenzeGegenFliessen,
    Spannungsbegrenzung,
)
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.nachweis.querkraft import Querkraft, Querkraftfall
from opencivil.querschnitt.platte import (
    Bewehrungslage, Plattenquerschnitt, Richtung,
)
from opencivil.projekt.eintraege import (
    GebrauchsfallEintrag, KombinationEintrag, MaterialEintrag,
    ProjektFehler, SpannungsfallEintrag, _schalter_aus,
    abgeleiteter_fallname,
)
from opencivil.projekt.platte import QuerschnittEintrag

if TYPE_CHECKING:
    from opencivil.projekt.projekt import Projekt


def _masse_pruefen(eintrag: "QuerschnittEintrag") -> None:
    """
    Haelt unmoegliche Abmessungen auf, bevor daraus Zahlen werden.

    Bis hierher lief jede Geometrie durch: eine Platte mit ``h = -300`` wurde
    gerechnet, eine mit beidseitiger Ueberdeckung groesser als die Dicke auch.
    Heraus kamen Zahlen, die aussahen wie ein Ergebnis. Ein Tragwerksnachweis
    darf an so etwas nicht vorbeirechnen -- er muss sagen, was nicht stimmt.

    Geprueft wird nur, was geometrisch unmoeglich ist, nicht was unueblich
    waere. Ob 20 mm Ueberdeckung fuer die Expositionsklasse genuegen,
    entscheidet der Ingenieur.
    """
    name = eintrag.name
    for feld, wert, wie in (
        ("Dicke h", eintrag.h, "grösser als null"),
        ("Breite b", eintrag.b, "grösser als null"),
        ("Grösstkorn D_max", eintrag.d_max, "grösser als null"),
    ):
        if wert <= 0.0:
            raise ProjektFehler(
                f"Platte '{name}': {feld} muss {wie} sein, angegeben ist {wert:g} mm.")

    for feld, wert in (("Überdeckung unten", eintrag.ueberdeckung_unten),
                       ("Überdeckung oben", eintrag.ueberdeckung_oben),
                       ("Einlagenhöhe", eintrag.einlagenhoehe)):
        if wert < 0.0:
            raise ProjektFehler(
                f"Platte '{name}': {feld} kann nicht negativ sein "
                f"({wert:g} mm).")

    zusammen = eintrag.ueberdeckung_unten + eintrag.ueberdeckung_oben
    if zusammen >= eintrag.h:
        raise ProjektFehler(
            f"Platte '{name}': die Überdeckungen ergeben zusammen {zusammen:g} mm "
            f"und lassen in einer {eintrag.h:g} mm dicken Platte keinen Platz für "
            f"Bewehrung.")


# ===========================================================================
# Aufbau
# ===========================================================================


@dataclass
class Aufbau:
    """Was beim Zusammenbauen eines Projekts entsteht."""

    werk: Rechenwerk
    baustoffe: Dict[str, Baustoff] = field(default_factory=dict)
    querschnitte: Dict[str, Plattenquerschnitt] = field(default_factory=dict)
    nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)
    """
    Schluessel ist ``<querschnitt>.x``.

    Die Richtung steht noch im Schluessel, obwohl es nur eine gibt -- sie sagt
    dem Leser einer Wert-ID, welcher Querschnitt gemeint ist, und die
    Wert-IDs in abgelegten Berichten sollen nicht bei jeder Umstellung
    wechseln.
    """

    querkraft: Dict[str, Querkraft] = field(default_factory=dict)
    duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)
    """Schluessel ist die Querschnittskennung -- ein Nachweis je Platte."""

    rissnormalkraft: Dict[str, Rissnormalkraft] = field(default_factory=dict)
    """Schluessel ist ``<querschnitt>.x``."""

    sproede: Dict[str, SproedesVersagen] = field(default_factory=dict)
    """Mindestbewehrung gegen sproedes Versagen, je ``<querschnitt>.x``."""

    zwaengung_biegung: Dict[str, ZwaengungBiegung] = field(default_factory=dict)
    """Zwaengung auf Biegung, je ``<querschnitt>.x``."""

    spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Stahlspannung gegen Fliessen unter haeufiger Einwirkung, je ``<querschnitt>.x``."""

    spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Stahlspannung aus der Rissbreite unter quasi-staendiger Einwirkung, je ``<querschnitt>.x``."""

    knicken: Dict[str, Knicken] = field(default_factory=dict)
    """Nachweis am verformten System, je Querschnitt -- nur in x-Richtung."""

    fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)
    """
    Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind.

    Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine
    Zeile mit Erfuellungsgrad null steht statt gar nichts.
    """

    spannungsfaelle: Dict[str, List["SpannungsfallEintrag"]] = field(
        default_factory=dict)
    """
    Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als
    Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand
    anderes brauchen koennte, und nichts haengt von ihnen ab.
    """

    warnungen: List[str] = field(default_factory=list)

    #: Die Felder, in denen die Nachweise einer Platte stehen -- die eine
    #: Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach
    #: Kennung geschluesselt (``q1`` oder ``q1.x``) und alle tragen Nachweise
    #: mit ``d_ausnutzung``. Daraus ergeben sich Rechenziele, Aufteilen nach
    #: Platte und Zwischenspeichern von selbst; frueher stand dieselbe Liste
    #: viermal da, und wer einen Nachweis hinzufuegte, musste alle vier
    #: finden.
    NACHWEISFELDER = ("nachweise", "querkraft", "duktilitaet", "fehlende",
                      "rissnormalkraft", "sproede", "zwaengung_biegung",
                      "spannung_riss", "spannung", "knicken")

    def nachweise_je_feld(self):
        """Alle Nachweise, Feld fuer Feld und in der Reihenfolge der Liste."""
        for feld in self.NACHWEISFELDER:
            yield feld, getattr(self, feld)

    def alle_nachweise(self):
        """Jeden Nachweis einmal, in derselben Reihenfolge wie im Protokoll."""
        for _, eintraege in self.nachweise_je_feld():
            yield from eintraege.values()

    def alle_nachweisziele(self) -> List[str]:
        return [d.id for n in self.alle_nachweise()
                for d in n.d_ausnutzung.values()]

    def gehoert_zu(self, schluessel: str, kennung: str) -> bool:
        """Ob ein Feldschluessel (``q1`` oder ``q1.x``) zu dieser Platte gehoert."""
        return schluessel == kennung or schluessel.startswith(f"{kennung}.")

    def teile_von(self, kennung: str) -> Dict[str, Dict[str, Any]]:
        """
        Alle Nachweisobjekte einer Platte, nach Feld geordnet.

        Gebraucht vom Zwischenspeicher: ein uebernommenes Ergebnis besteht
        nicht nur aus Zahlen, sondern auch aus dem, was die Nachweise sich
        beim Rechnen gemerkt haben -- Interaktionslinien, Fallergebnisse,
        Iterationsschritte. Die Schnittstelle liest das aus den Objekten, also
        muessen die Objekte mitwandern und nicht bloss ihre Ausgabewerte.
        """
        return {feld: {s: w for s, w in eintraege.items()
                       if self.gehoert_zu(s, kennung)}
                for feld, eintraege in self.nachweise_je_feld()}

    def teile_setzen(self, kennung: str, teile: Mapping[str, Dict[str, Any]]) -> None:
        """Die Nachweisobjekte einer Platte durch frueher gerechnete ersetzen."""
        for feld, eintraege in teile.items():
            ziel = getattr(self, feld)
            for schluessel in [s for s in ziel if self.gehoert_zu(s, kennung)]:
                del ziel[schluessel]
            ziel.update(eintraege)

    def ziele_von(self, kennung: str) -> List[str]:
        """Die Rechenziele einer einzelnen Platte -- Eckwerte und Nachweise."""
        alle = self.eckwertziele() + self.alle_nachweisziele()
        raeume = {w.id for _, eintraege in self.nachweise_je_feld()
                  for s, w in eintraege.items() if self.gehoert_zu(s, kennung)}
        return [z for z in alle if any(z.startswith(f"{r}.") for r in raeume)]

    def eckwertziele(self) -> List[str]:
        return [d.id for n in self.nachweise.values() for d in n.d_eckwerte.values()]

    def alle_ziele(self) -> List[str]:
        """
        Was ein vollstaendiger Lauf rechnet, in der Reihenfolge der Herleitung.

        Erst die Baustoffe, dann Platte fuer Platte ihre Eckwerte und
        Nachweise. Die Oberflaeche rechnet dieselben Ziele in derselben
        Folge, nur plattenweise mit Zwischenspeicher
        (:func:`opencivil.web.dienst._stromabwaerts`); wer ohne Oberflaeche
        rechnet, bekommt so denselben Bericht.
        """
        ziele = self.materialziele()
        for kennung in self.querschnitte:
            ziele += self.ziele_von(kennung)
        return ziele

    def urteile_von(self, kennung: str, urteile: Iterable[NachweisUrteil],
                    ) -> List[NachweisUrteil]:
        """
        Die Urteile einer Platte -- erkannt am Namensraum ihres Nachweises.

        Nicht am Namen: den Anzeigetext zu zerlegen hat schon einmal die
        Nachweise mehrerer Platten in dieselbe Tabelle gepackt.
        """
        raum = self.querschnitte[kennung].id
        return [u for u in urteile
                if u.raum == raum or u.raum.startswith(f"{raum}.")]

    def materialziele(self) -> List[str]:
        """
        Saemtliche Kennwerte aller Materialien -- Beton zuerst, dann Betonstahl.

        Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
        waere sonst nie Ziel und bliebe ungerechnet -- im Editor staenden dann
        leere Felder, obwohl die Sorte alles hergibt.

        Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
        arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
        stehen im Bericht erst die Baustoffe und dann die Bauteile.
        """
        nach_art = {"beton": [], "betonstahl": []}
        for stoff in self.baustoffe.values():
            nach_art.setdefault(stoff.art.value, []).extend(
                d.id for d in stoff.definitionen.values())
        return nach_art["beton"] + nach_art["betonstahl"]


def aufbauen(projekt: "Projekt", *, schnell: bool = False) -> Aufbau:
    """
    Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

    Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
    etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.

    Mit ``schnell`` lassen Nachweise teure Nebenrechnungen weg, die das
    Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
    genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
    nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
    rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
    das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.
    """
    projekt.pruefen()
    werk = Rechenwerk()
    aufbau = Aufbau(werk=werk)

    def eintragen(feld: str, schluessel: str, nachweis) -> None:
        """
        Einen Nachweis anmelden -- ausser er ist ganz still, und es wird
        schnell gerechnet.

        Den schnellen Weg nimmt nur die Bewehrungssuche, und die zaehlt
        stille Urteile nicht (:func:`bewehrungssuche.bewerte`). Ein ganz
        stiller Nachweis kann ihr Ergebnis also nicht aendern, er kostet
        nur Zeit -- und bei der Stahlspannung, die immer mitlaeuft, ist
        das der groessere Teil der ganzen Rechnung. Exakt und nicht
        genaehert: gezaehlt wird dasselbe wie vorher.
        """
        if schnell and nachweis.still:
            return
        werk.registriere(nachweis)
        getattr(aufbau, feld)[schluessel] = nachweis

    # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
    # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
    je_art: Dict[str, int] = {}
    for m in projekt.materialien:
        je_art[m.art] = je_art.get(m.art, 0) + 1

    for eintrag in projekt.materialien:
        index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
        aufbau.baustoffe[eintrag.kennung] = _baustoff(eintrag, index)

    for eintrag in projekt.querschnitte:
        querschnitt = _querschnitt(eintrag, aufbau.baustoffe)
        aufbau.querschnitte[eintrag.kennung] = querschnitt
        querschnitt.ins_rechenwerk(werk)

        bewehrt = set(querschnitt.richtungen_mit_bewehrung)

        # Die vier Schalter durch denselben Leser wie beim Einlesen.
        # Wer eine alte Beschreibung im Speicher haelt, traegt dort noch
        # eine Liste -- und `[False, False, False, False]` ist als Wahrheit
        # *wahr*. Der Nachweis stuende dann eingeschaltet da, obwohl jeder
        # einzelne Haken aus ist.
        an_duktil = _schalter_aus(eintrag.duktilitaet)
        an_sproede = _schalter_aus(eintrag.sproede)
        an_biegung = _schalter_aus(eintrag.zwaengung_biegung)
        an_zwang = _schalter_aus(eintrag.zwaengung)

        # Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen
        # im Querschnitt -- sie tragen zum Bewehrungsgehalt bei und
        # druecken die statische Hoehe von x nach innen --, aber kein
        # Nachweis fragt nach ihnen. Vorher lief hier alles doppelt,
        # einmal je Richtung, und die Haelfte der Tabelle handelte von
        # einer Richtung, fuer die niemand Schnittgroessen hatte.
        richtung = Richtung.X
        aktiv = [k for k in eintrag.kombinationen if k.aktiv]

        if richtung not in bewehrt:
            if aktiv:
                # Ohne Bewehrung laesst sich hier nichts aufstellen. Der
                # Nachweis entfiel frueher stillschweigend; wer eine
                # Einwirkung angegeben hatte, fand sie nirgends wieder.
                fehlend = FehlendeBewehrung(
                    querschnitt, richtung,
                    _ausgefallene(aktiv, richtung))
                werk.registriere(fehlend)
                aufbau.fehlende[f"{eintrag.kennung}.x"] = fehlend
        else:
            # Der M-N-Nachweis entsteht auch ohne Schnittgroessen: seine
            # Eckwerte gehoeren dem Querschnitt, nicht der Einwirkung, und
            # der Nachweis gegen sproedes Versagen haelt M_Rd(N=0) dagegen.
            # Ohne die genaue Resistenzlinie, wenn schnell gerechnet wird:
            # sie kostet fast die ganze Zeit dieses Nachweises und wird
            # allein im Diagramm gebraucht. Wer schnell rechnet, sucht eine
            # Bewehrung und sieht dabei kein Diagramm an.
            nachweis = BiegungNormalkraft(
                querschnitt, [_kombination(k) for k in aktiv], richtung,
                mit_linie=not schnell)
            werk.registriere(nachweis)
            aufbau.nachweise[f"{eintrag.kennung}.x"] = nachweis

            # Die beiden x-Lagen, von unten nach oben. Beide werden
            # gerechnet; in die Zusammenfassung kommt die unguenstigere.
            lagen = [l.nummer for l in querschnitt.lagen
                     if l.richtung is richtung]
            if lagen:
                nachweis_sv = SproedesVersagen(
                    querschnitt, richtung, lagen, nachweis)
                nachweis_sv.still = not an_sproede
                eintragen("sproede", f"{eintrag.kennung}.x", nachweis_sv)

                biegung = ZwaengungBiegung(
                    querschnitt, richtung, lagen,
                    anforderung=eintrag.rissanforderung,
                    kriechzahl=eintrag.kriechzahl)
                biegung.still = not an_biegung
                eintragen("zwaengung_biegung", f"{eintrag.kennung}.x",
                          biegung)

                zwang = Rissnormalkraft(
                    querschnitt, richtung,
                    anforderung=eintrag.rissanforderung,
                    begrenzt=eintrag.zwaengung_begrenzt)
                zwang.still = not an_zwang
                eintragen("rissnormalkraft", f"{eintrag.kennung}.x", zwang)

                duktilitaet = Duktilitaet(querschnitt, lagen)
                duktilitaet.still = not an_duktil
                eintragen("duktilitaet", eintrag.kennung, duktilitaet)

            # Stahlspannung aus der Rissbreite unter quasi-staendiger
            # Einwirkung. Bei jeder Anforderung -- bei normaler ist die
            # Grenze f_yk, aber auch dort darf die Bewehrung unter
            # Dauerlast nicht fliessen.
            faelle, laute = _gebrauchsfaelle(
                eintrag, eigene=eintrag.quasistaendige,
                ableiten=eintrag.quasistaendige_aus_tragsicherheit,
                anteil=eintrag.quasistaendige_anteil)
            if faelle:
                riss = Spannungsbegrenzung(
                    querschnitt, richtung, faelle,
                    grenze=GrenzeAusRissbreite(eintrag.rissanforderung))
                riss.stillstellen([f.name for f in faelle], laute)
                eintragen("spannung_riss", f"{eintrag.kennung}.x", riss)

            # Stahlspannung gegen Fliessen unter haeufiger Einwirkung. Nur
            # bei erhoehter und hoher Anforderung -- bei normaler steht in
            # Tabelle 17 ein Strich.
            faelle, laute = _gebrauchsfaelle(
                eintrag, eigene=eintrag.haeufige,
                ableiten=eintrag.haeufige_aus_tragsicherheit,
                anteil=eintrag.haeufige_anteil)
            if faelle and eintrag.rissanforderung in GEFORDERT:
                spannung = Spannungsbegrenzung(
                    querschnitt, richtung, faelle,
                    grenze=GrenzeGegenFliessen())
                spannung.stillstellen([f.name for f in faelle], laute)
                eintragen("spannung", f"{eintrag.kennung}.x", spannung)

            mit_querkraft = [k for k in aktiv if k.V_Ed]
            if mit_querkraft:
                querkraft = Querkraft(
                    querschnitt,
                    [Querkraftfall(name=k.name,
                                   V_Ed=Groesse(k.V_Ed, KN_PRO_M),
                                   M_Ed=Groesse(k.M_Ed, KNM),
                                   N_Ed=Groesse(k.N_Ed, KN))
                     for k in mit_querkraft],
                    richtung, nachweis)
                werk.registriere(querkraft)
                aufbau.querkraft[f"{eintrag.kennung}.x"] = querkraft

            knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
            if knickfaelle:
                knick = Knicken(
                    querschnitt,
                    [Knickfall(name=k.name,
                               N_Ed=Groesse(k.N_Ed, KN),
                               M_Ed_1=Groesse(k.M_Ed_1, KNM),
                               laenge=Groesse(k.laenge, M),
                               knicklaenge=Groesse(k.knicklaenge, M))
                     for k in knickfaelle],
                    nachweis, schnell=schnell)
                werk.registriere(knick)
                aufbau.knicken[eintrag.kennung] = knick
        if richtung not in bewehrt and eintrag.knickfaelle:
            aufbau.warnungen.append(
                f"Platte '{eintrag.name}': Knicken braucht Bewehrung in "
                f"x-Richtung; ohne sie entfällt der Nachweis.")

        aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
        if aktive:
            aufbau.spannungsfaelle[eintrag.kennung] = aktive

        if not eintrag.kombinationen:
            aufbau.warnungen.append(
                f"Platte '{eintrag.name}': keine Schnittgrössen angegeben, "
                f"also kein Tragsicherheitsnachweis möglich.")

    for baustoff in aufbau.baustoffe.values():
        baustoff.ins_rechenwerk(werk)

    _ueberschreibungen_setzen(projekt, werk, aufbau)
    return aufbau


def _baustoff(eintrag: MaterialEintrag, symbol_index: str) -> Baustoff:
    bauer = {"beton": beton, "betonstahl": betonstahl}[eintrag.art]
    roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
    # Jeder Kennwert dieser beiden Baustoffe ist seiner Natur nach positiv:
    # Festigkeiten, Moduln, Dehnungen, Teilsicherheitsbeiwerte. Eine Null
    # oder ein negativer Wert liefert keine falsche Zahl, sondern gar keine
    # -- gamma_c = 0 endete in einem ZeroDivisionError, ein negatives f_ck
    # in einer komplexen Wurzel. Beides kam als Absturzmeldung beim
    # Benutzer an.
    for topf, wie in ((eintrag.abweichungen, "abweichender Wert"),
                      (eintrag.ueberschreibungen, "überschriebener Wert")):
        for kurzname, zahl in topf.items():
            if zahl <= 0.0:
                raise ProjektFehler(
                    f"'{eintrag.anzeigename}': {kurzname} muss grösser als null "
                    f"sein, angegeben ist {zahl:g} ({wie}).")
    abweichungen = {
        kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
        for kurzname, zahl in eintrag.abweichungen.items()
        if kurzname in roh.definitionen
    }
    return bauer(
        eintrag.sorte,
        name=eintrag.anzeigename,
        praefix=f"{eintrag.art}.{eintrag.kennung}",
        abweichungen=abweichungen,
        symbol_index=symbol_index,
    )


def _querschnitt(
    eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff]
) -> Plattenquerschnitt:
    beton_stoff = baustoffe.get(eintrag.beton)
    if beton_stoff is None:
        raise ProjektFehler(
            f"Platte '{eintrag.name}' verweist auf das Material "
            f"'{eintrag.beton}', das es nicht (mehr) gibt.")
    _masse_pruefen(eintrag)

    lagen: List[Bewehrungslage] = []
    for nummer, lage in enumerate(eintrag.lagen, start=1):
        stahl = baustoffe.get(lage.stahl)
        if stahl is None and lage.vorhanden:
            raise ProjektFehler(
                f"Die {nummer}. Lage von '{eintrag.name}' verweist auf den Stahl "
                f"'{lage.stahl}', den es nicht (mehr) gibt.")
        lagen.append(Bewehrungslage(
            nummer=nummer,
            richtung=eintrag.richtung_von(nummer),
            stahl=stahl or next(iter(
                s for s in baustoffe.values() if s.art.value == "betonstahl"), None),
            grund=lage.grund.als_posten(),
            zulage=lage.zulage.als_posten(),
            unguenstig=lage.unguenstig,
        ))

    if not any(l.vorhanden for l in lagen):
        raise ProjektFehler(
            f"Platte '{eintrag.name}': ohne Bewehrung lässt sich kein "
            f"Widerstand bestimmen.")

    buegel = eintrag.querkraftbewehrung
    buegel.pruefen(f"Platte '{eintrag.name}'")
    buegelstahl = baustoffe.get(buegel.stahl)
    if buegelstahl is None and buegel.stahl:
        raise ProjektFehler(
            f"Die Querkraftbewehrung von '{eintrag.name}' verweist auf den "
            f"Stahl '{buegel.stahl}', den es nicht (mehr) gibt.")
    if buegelstahl is None:
        # Kein Stahl angegeben -- wie bei den Lagen gilt dann der erste im
        # Projekt. Eine Beschreibung aus der Zeit vor den Buegeln nennt
        # keinen, und daran soll der ganze Lauf nicht scheitern.
        buegelstahl = next(
            (s for s in baustoffe.values() if s.art.value == "betonstahl"), None)
    if buegel.vorhanden and buegelstahl is None:
        raise ProjektFehler(
            f"Die Querkraftbewehrung von '{eintrag.name}' braucht einen "
            f"Betonstahl, im Projekt gibt es aber keinen.")

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
        kriechzahl=Groesse(eintrag.kriechzahl, EINHEITSLOS),
        querkraftbewehrung=(buegel.als_bewehrung(buegelstahl)
                            if buegel.vorhanden else None),
        praefix=f"querschnitt.{eintrag.kennung}",
    )


def _gebrauchsfaelle(
    eintrag: "QuerschnittEintrag", *,
    eigene: Sequence["GebrauchsfallEintrag"], ableiten: bool,
    anteil: float,
) -> Tuple[List[Gebrauchsfall], List[str]]:
    """
    Die Lastfaelle eines Stahlspannungsnachweises -- und welche laut sind.

    Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
    Listen werden gleich gebildet und unterscheiden sich nur im Anteil.

    Die eigens angegebenen, und zusaetzlich die Tragsicherheitsfaelle mit
    ``anteil`` Prozent. Beides nebeneinander: der Anteil ist eine bequeme
    Abschaetzung, deckt aber nicht den Fall ab, den es nur unter
    Gebrauchslast gibt. Wer einen solchen kennt, soll ihn dazustellen
    koennen, ohne die Abschaetzung fuer alle anderen aufzugeben.

    Die abgeleiteten Faelle entstehen auch dann, wenn ``ableiten`` aus ist
    -- dann eben still. Sie ganz wegzulassen hiesse, den Nachweis erst auf
    Verlangen zu fuehren; so steht wenigstens ein Hinweis da, wenn die
    Abschaetzung nicht aufgeht.

    **Was das kostet.** Jeder Fall ist ein Gleichgewicht am gerissenen
    Querschnitt, also ein Durchlauf des Faserloesers -- rund 8 ms.
    Gemessen an der Beispielplatte mit drei Kombinationen: der
    quasi-staendige Nachweis laeuft immer und hebt die ganze Rechnung von
    27 auf 52 ms; bei erhoehter Anforderung kommt der haeufige dazu, 79 ms.
    Die Bewehrungssuche zahlt davon nichts, solange beide still sind --
    im schnellen Aufbau entstehen ganz stille Nachweise gar nicht (2.5
    statt 29 ms je Bewertung bei erhoehter Anforderung). Wer die Zeit
    auch in der Anzeige zurueckhaben will, kommt nicht an dieser Stelle
    weiter, sondern am Loeser.

    Die Rechnung steht hier und nicht in der Oberflaeche: dort waere sie
    eine zweite Wahrheit.
    """
    faktor = anteil / 100.0
    abgeleitet = [
        Gebrauchsfall(
            name=abgeleiteter_fallname(k.name, anteil),
            M_Ed=Groesse(faktor * k.M_Ed, KNM),
            N_Ed=Groesse(faktor * k.N_Ed, KN))
        for k in eintrag.kombinationen if k.aktiv
    ]
    eigen = [
        Gebrauchsfall(name=h.name,
                      M_Ed=Groesse(h.M_Ed, KNM),
                      N_Ed=Groesse(h.N_Ed, KN))
        for h in eigene if h.aktiv
    ]
    laute = [f.name for f in eigen]
    if ableiten:
        laute += [f.name for f in abgeleitet]
    return abgeleitet + eigen, laute


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
            art="M-N", langname="Biegung und Normalkraft",
            fall=k.name,
            symbol=f"M_{{Rd,{r}}}",
            einwirkung_symbol=f"M_{{Ed,{r}}}",
            einwirkung=Groesse(k.M_Ed, KNM), einheit=KNM)
        for k in kombinationen
    ] + [
        Ausgefallen(
            art="V", langname="Querkraft", fall=k.name,
            symbol=f"V_{{Rd,{r}}}",
            einwirkung_symbol=f"V_{{Ed,{r}}}",
            einwirkung=Groesse(abs(k.V_Ed), KN_PRO_M), einheit=KN_PRO_M)
        for k in kombinationen if k.V_Ed
    ]


def _kombination(eintrag: KombinationEintrag) -> Schnittgroessen:
    try:
        art = Erfuellungsart(eintrag.art)
    except ValueError:
        raise ProjektFehler(
            f"Unbekannter Massstab '{eintrag.art}'. Möglich sind: "
            f"{', '.join(a.value for a in Erfuellungsart)}.") from None
    return Schnittgroessen(
        name=eintrag.name,
        M_Ed=Groesse(eintrag.M_Ed, KNM),
        N_Ed=Groesse(eintrag.N_Ed, KN),
        art=art,
    )


def _ueberschreibungen_setzen(projekt: "Projekt", werk: Rechenwerk,
                              aufbau: Aufbau) -> None:
    for eintrag in projekt.materialien:
        baustoff = aufbau.baustoffe[eintrag.kennung]
        for kurzname, zahl in eintrag.ueberschreibungen.items():
            if kurzname not in baustoff.definitionen:
                aufbau.warnungen.append(
                    f"Material '{baustoff.name}': Kennwert '{kurzname}' ist "
                    f"unbekannt, die Überschreibung wird übergangen.")
                continue
            definition = baustoff.definition(kurzname)
            werk.setze(definition.id, Groesse(zahl, definition.einheit))

