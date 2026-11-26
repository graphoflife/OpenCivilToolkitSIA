"""
opencivil/projekt/lesen.py -- was in einer Projektdatei stehen darf, und wie es gelesen wird.

VERANTWORTUNG:
Ein Leser fuer jeden Eintrag und eine Pruefung fuer jedes Feld, beide aus den
Feldern der Datenklassen. Was ein Feld annehmen darf, steht an ihm selbst:

* sein Typ -- Text, Zahl, ganze Zahl, Schalter, Liste, Zuordnung, Eintrag,
  oder eine Wahl (:class:`~opencivil.core.wahl.Wahl`), deren Mitglieder es
  annimmt;
* eine Teilmenge davon (:func:`einer_von`) -- die Werte, die es gibt;
* bei der Kennung eines Materials die Arten, die es nehmen darf
  (:func:`materialfeld`) -- geprueft erst beim Aufbau, denn welches Material
  welche Art hat, weiss nur das Projekt;
* ein Text ohne Vorgabe ist Pflicht und darf nicht leer sein -- ausser einem
  Namen: ohne ihn haelt erst das Rechnen sein Bauteil an
  (:func:`inhalt_pruefen`);
* ein Bereich (:func:`bereich`) -- wo seine Zahl liegen muss.

STRENG:
Gelesen wird, was dasteht, und nichts sonst. Ein Feld, das es nicht gibt, ein
Text statt einer Zahl, eine Wahl, die es nicht gibt -- jedes meldet sich, mit
dem Ort in der Datei und dem Wert. Umgedeutet wird nichts: ein unbekanntes
Feld ist meist ein Tippfehler, und ein still uebergangener Tippfehler rechnet
mit der Vorgabe statt mit der Zahl des Benutzers. Alte Dateiformate liest
niemand mehr; alte Speicherstaende muessen seit 2026-10-11 nicht mehr gehen
(Benutzer).

Was fehlt, bekommt die Vorgabe: die des Feldes -- und bei einem Eintrag, der
in einem Eintrag steht, die eines frischen an dieser Stelle. Die Rechenwahl
des Knickens rechnet ohne Angabe praezise, nicht von Hand wie eine Rechenwahl
fuer sich.

EINE TUER:
Dieselbe Pruefung laeuft vor jedem Rechnen ueber das ganze Projekt
(:meth:`~opencivil.projekt.projekt.Projekt.pruefen`). Was in Python gebaut
wurde, ohne Datei, geht durch dieselbe Tuer wie eine Datei: ein «festt» im
Linienlager meldet sich hier und wird nicht still zur Feder.

FORM BEIM LESEN, INHALT VOR DEM RECHNEN:
Beim Lesen zaehlt die Form: Typ, Wahl, Pflicht. Was erst das Rechnen braucht
-- der Bereich eines Feldes, eine Dicke groesser als null, die Regeln ueber
mehrere Felder (``regeln``) --, prueft :func:`inhalt_pruefen` vor jedem
Rechnen; das Material, auf das eine Platte zeigt, der Aufbau. Eine abgelegte
Platte mit h = 0 soll sich oeffnen und korrigieren lassen. Bis 2026-10-17
hielt eine negative Kriechzahl schon das Oeffnen auf, eine negative
Ueberdeckung erst das Rechnen.

WAHLEN SIND MITGLIEDER:
Ein Wahlfeld haelt das Mitglied seiner Wahl, nicht den Text: aus «hoch» in
der Datei wird ``Rissanforderung.HOCH``, und wer im Code einen Text
zuweist, bekommt ebenso das Mitglied (:func:`wahl_aus_text`, aufgerufen von
``Beschreibung.__setattr__``). Geschrieben wird der Text -- ``json.dumps``
schreibt eine Wahl als ihren Wert, die Dateien bleiben Zeichen fuer Zeichen
gleich. Bis 2026-10-17 hielten die Felder Text, und rund dreissig Stellen
machten daraus wieder das Mitglied. Dasselbe gilt fuer jeden Wert einer
Zuordnung von Wahlen, etwa den Wertesatz je Material (:func:`je_material`).
"""

from __future__ import annotations

import copy
import dataclasses
import difflib
import enum
import functools
import math
import typing
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from opencivil.core.bereich import Bereich
from opencivil.core.einheiten import EINHEITSLOS, Einheit, Groesse


class ProjektFehler(Exception):
    """
    Die Projektbeschreibung ist in sich nicht stimmig. ``grund`` sagt, was
    nicht stimmt, als Satz mit Punkt; ``wo``, wo -- wie der Eintrag in
    Meldungen heisst (:func:`ort`), «Platte 'Decke'», tiefer «Pfahl 'P',
    Schicht 2» --, leer, wo es das ganze Projekt betrifft. Die Meldung ist
    beides: «Platte 'Decke': noch keine Bewehrung.»

    Bis 2026-11-20 stand der Ort nur im Text, und wer den Grund an seiner
    Stelle brauchte, schnitt ihn wieder heraus.
    """

    def __init__(self, grund: str, *, wo: str = "") -> None:
        super().__init__(f"{wo}: {grund}" if wo else grund)
        self.grund = grund
        self.wo = wo

    def grund_bei(self, wo: str) -> str:
        """
        Der Fehler, wie er an der Stelle ``wo`` steht, ohne Punkt am Ende:
        dort nur der Grund, unter ihr mit dem Rest des Orts -- «Schicht 2:
        …» bei «Pfahl 'P'» --, anderswo die ganze Meldung.
        """
        if self.wo == wo:
            text = self.grund
        elif self.wo.startswith(f"{wo}, "):
            text = f"{self.wo[len(wo) + 2:]}: {self.grund}"
        else:
            text = str(self)
        return text.removesuffix(".")


def anhalten(grund: str, wo: str) -> None:
    """
    Haelt mit ``grund`` an der Stelle ``wo`` an -- nichts, wenn ``grund``
    leer ist: was ein :class:`~opencivil.core.bereich.Bereich` abweist, als
    :class:`ProjektFehler`.
    """
    if grund:
        raise ProjektFehler(grund, wo=wo)


# ===========================================================================
# Was an einem Feld steht
# ===========================================================================


def einer_von(moeglich: Iterable[Any], vorgabe: Any = dataclasses.MISSING) -> Any:
    """Ein Feld, das nur einen dieser Werte annimmt -- die Pruefung kennt sie von hier."""
    return dataclasses.field(default=vorgabe, metadata={"wahl": tuple(moeglich)})


def materialfeld(*arten: str) -> Any:
    """
    Ein Feld mit der Kennung eines Materials des Projekts, leer, solange
    keines gewaehlt ist -- und die Arten, die es nehmen darf: die eine Stelle
    dafuer. Der Aufbau prueft die Wahl damit
    (:func:`~opencivil.projekt.aufbau.kern.material`), die Zeichnung ebenso,
    und die Maske bietet nur diese Arten an (:func:`feldangaben`,
    ``stoffe``). Seit 2026-11-26 nimmt eine Flaeche der Querschnittsanalyse
    Beton, Baustahl oder Holz; bis dahin stand «beton» an drei Stellen fest.
    """
    return dataclasses.field(default="", metadata={"stoffe": tuple(arten)})


def stoffe_des_felds(cls: type, feld: str) -> Tuple[str, ...]:
    """Die Arten von Material, die das Feld ``feld`` nimmt (:func:`materialfeld`)."""
    return next(f for f in dataclasses.fields(cls) if f.name == feld).metadata["stoffe"]


def teil(fabrik: Callable[[], Any], *, heisst: str) -> Any:
    """
    Ein Feld, das einen ganzen Eintrag haelt -- die Grundbewehrung einer Lage,
    die Rechenwahl der Tragsicherheit --, mit dem Wort, unter dem es in
    Meldungen steht: wie die Maske es nennt, «Lage 2, Grund», nicht wie die
    Datei, «Lage 2, grund» (Benutzer, 2026-11-21). Ein Element einer Liste
    nennt seine Klasse (``IM_ORT``, :func:`_ort`).
    """
    return dataclasses.field(default_factory=fabrik, metadata={"heisst": heisst})


def _im_ort(f: dataclasses.Field) -> str:
    """Wie das Feld ``f`` als Teil eines Orts heisst -- sein Wort (:func:`teil`), sonst sein Name."""
    return f.metadata.get("heisst", f.name)


def je_material(vorgabe: Any, moeglich: Optional[Iterable[Any]] = None) -> Any:
    """
    Ein Feld, das je Material eine Wahl haelt, unter der Kennung des
    Materials -- den Wertesatz etwa. Ein Material ohne eigene Wahl waehlt
    ``vorgabe`` (:func:`vorgabe_je_material`); ``moeglich`` begrenzt die Wahl
    wie bei :func:`einer_von`. Eine Zuordnung und keine Liste: zwei Wahlen
    fuer dasselbe Material kann es so nicht geben. Bis 2026-11-20 hielt die
    Querschnittsanalyse eine Liste und wies doppelte Eintraege eigens ab.
    """
    metadata: Dict[str, Any] = {"je_material": vorgabe}
    if moeglich is not None:
        metadata["wahl"] = tuple(moeglich)
    return dataclasses.field(default_factory=dict, metadata=metadata)


def vorgabe_je_material(cls: type, feld: str) -> Any:
    """Was ein Material im Feld ``feld`` (:func:`je_material`) waehlt, solange es keine eigene Wahl hat."""
    return next(f for f in dataclasses.fields(cls) if f.name == feld).metadata["je_material"]


def bereich(vorgabe: Any = dataclasses.MISSING, *, heisst: str,
            einheit: Optional[Einheit] = None, ueber: Optional[float] = None,
            ab: Optional[float] = None, bis: Optional[float] = None,
            unter: Optional[float] = None, bis_feld: Optional[str] = None,
            bis_faktor: float = 1.0, quer_zu: Optional[Tuple[str, float]] = None,
            fabrik: Optional[Callable[[], Any]] = None) -> Any:
    """
    Ein Feld, dessen Zahl in einem :class:`Bereich` liegen muss -- eine
    Kriechzahl ab null etwa. Bei einer Liste von Zahlen gilt er fuer jede,
    und leer ist sie nie (:func:`inhalt_pruefen`); ihre Vorgabe kommt dann
    aus ``fabrik``.
    """
    metadata = {"bereich": Bereich(heisst, einheit, ueber=ueber, ab=ab, bis=bis, unter=unter,
                                   bis_feld=bis_feld, bis_faktor=bis_faktor, quer_zu=quer_zu)}
    if fabrik is not None:
        return dataclasses.field(default_factory=fabrik, metadata=metadata)
    return dataclasses.field(default=vorgabe, metadata=metadata)


def als_groesse(eintrag: Any, feld: str) -> Groesse:
    """
    Die Zahl eines Feldes als Groesse, in der Einheit seines Bereichs -- der,
    in der die Maske sie zeigt (:func:`feldangaben`); ohne Einheit
    einheitslos. So steht die Einheit einer Eingabe nur an ihrem Feld.
    """
    f = next(f for f in dataclasses.fields(eintrag) if f.name == feld)
    return Groesse(getattr(eintrag, feld), f.metadata["bereich"].einheit or EINHEITSLOS)


def feldangaben(cls: type) -> Dict[str, Dict[str, Any]]:
    """
    Was die Oberflaeche je Feld eines Eintrags vom Kern wissen muss, fuer den
    Katalog: die Einheit, in der eine Zahl gemeint ist, wo sie liegen muss
    (``ueber``, ``ab``, ``bis``, ``unter`` wie :class:`Bereich`) und ob sie
    ganz sein muss. Hat das Feld Grenzen, dazu, was es sagt, wenn eine Zahl
    sie verletzt (``heisst``, ``verlangt``: «Dicke h» «muss grösser als null
    sein») -- das Feld weist sie mit dem Satz ab, der sonst beim Rechnen
    kaeme. Was eine Wahl annehmen kann, steht nicht hier: das sagen die
    Wahllisten des Katalogs, mit Beschriftung.

    Begrenzt ein Feld ein anderes (:attr:`Bereich.bis_feld`), steht das an
    beiden, mit dem Namen des anderen Feldes und dem Satz, den das Feld
    sagt: ``bis_feld`` bei α_min, ``ab_feld`` bei α_max -- mit ``faktor``,
    wo die Grenze ein Vielfaches des anderen ist (:attr:`Bereich.bis_faktor`,
    beim anderen Feld sein Kehrwert). Ebenso ``quer_zu``
    an beiden Feldern, mit dem kleinsten Abstand als Linien in Grad
    (:attr:`Bereich.quer_zu`, ``mindestens``). Die Zahl des anderen Feldes
    kennt erst die Maske.

    Nimmt ein Feld ein Material (:func:`materialfeld`), steht dort, welche
    Arten: ``stoffe``.

    Haelt ein Feld je Material eine Wahl (:func:`je_material`), steht dort,
    was ein Material ohne eigene waehlt: ``vorgabe`` -- und ist die Wahl
    begrenzt, was sie annehmen kann, in ihrer Folge: ``wahl``. Danach
    stellt die Maske die Rechenart je Beton, mit ihren Stellungen.

    Steht es am Feld, steht es einmal. Bis 2026-10-18 standen die Einheiten
    des Grundbruchs dreimal da -- am Feld, beim Bauen und in grundbruch.js --,
    und wichen zwei davon ab, galt eine Zahl still um 10³ anders.
    """
    typen = _typen(cls)
    bereiche = _bereiche(cls)
    angaben: Dict[str, Dict[str, Any]] = {}
    for f in dataclasses.fields(cls):
        b = bereiche.get(f.name)
        angabe = b.angabe() if b is not None else {}
        art, innen = _art(typen.get(f.name))
        if (innen if art == "optional" else typen.get(f.name)) is int:
            angabe["ganz"] = True
        if "stoffe" in f.metadata:
            angabe["stoffe"] = list(f.metadata["stoffe"])
        if "je_material" in f.metadata:
            angabe["vorgabe"] = f.metadata["je_material"]
            if "wahl" in f.metadata:
                angabe["wahl"] = [m.value for m in f.metadata["wahl"]]
        if angabe:
            angaben[f.name] = angabe
    for name, b in bereiche.items():
        if b.bis_feld is not None:
            hier, dort = b.gegen(bereiche[b.bis_feld])
            oben = {"feld": b.bis_feld, "satz": hier}
            unten = {"feld": name, "satz": dort}
            if b.bis_faktor != 1.0:
                oben["faktor"], unten["faktor"] = b.bis_faktor, 1.0 / b.bis_faktor
            angaben.setdefault(name, {})["bis_feld"] = oben
            angaben.setdefault(b.bis_feld, {})["ab_feld"] = unten
        if b.quer_zu is not None:
            feld, mindestens = b.quer_zu
            hier, dort = b.quer(bereiche[feld])
            angaben.setdefault(name, {})["quer_zu"] = {"feld": feld, "mindestens": mindestens, "satz": hier}
            angaben.setdefault(feld, {})["quer_zu"] = {"feld": name, "mindestens": mindestens, "satz": dort}
    return angaben


#: Wie ein Blatt in :func:`feldtypen` heisst, nach seinem Typ.
_BLAETTER = {bool: "ja/nein", int: "ganz", float: "zahl", str: "text"}


def feldtypen(cls: type) -> Dict[str, Dict[str, Any]]:
    """
    Was jedes Feld einer Klasse von Eintraegen haelt -- fuer wer ohne Maske
    schreibt, den MCP-Zugang (:mod:`opencivil.mcp`). ``art`` ist ``zahl``,
    ``ganz``, ``text``, ``ja/nein``, ``wahl`` (mit ``wahl``: was sie annehmen
    kann, :func:`wahl_von`), ``eintrag`` (mit ``klasse``: ihr Name im Katalog,
    :func:`katalogname`), ``liste`` oder ``zuordnung`` (mit ``von``: was darin
    steht). ``leer``, wo statt eines Wertes auch keiner stehen darf;
    ``stoffe`` bei der Kennung eines Materials, welche Arten das Feld nimmt
    (:func:`materialfeld`). Einheit und Grenzen sagt :func:`feldangaben`.
    """
    typen = _typen(cls)
    return {f.name: _feldtyp(typen[f.name], f) for f in dataclasses.fields(cls)}


def _feldtyp(typ: Any, f: dataclasses.Field) -> Dict[str, Any]:
    art, innen = _art(typ)
    if art == "optional":
        return {**_feldtyp(innen, f), "leer": True}
    if art in ("liste", "zuordnung"):
        return {"art": art, "von": _feldtyp(innen, f)}
    if art == "eintrag":
        return {"art": "eintrag", "klasse": katalogname(innen)}
    if _ist_wahl(innen):
        return {"art": "wahl", "wahl": [m.value for m in f.metadata.get("wahl") or innen]}
    if "stoffe" in f.metadata:
        return {"art": "text", "stoffe": list(f.metadata["stoffe"])}
    return {"art": _BLAETTER.get(innen, "wert")}


@functools.lru_cache(maxsize=None)
def _bereiche(cls: type) -> Dict[str, Bereich]:
    """Die Bereiche der Felder einer Klasse, nach Feldnamen -- je Klasse einmal."""
    return {f.name: f.metadata["bereich"] for f in dataclasses.fields(cls)
            if "bereich" in f.metadata}


def katalogname(cls: type) -> str:
    """
    Wie eine Klasse von Eintraegen im Katalog der Oberflaeche heisst: ohne
    «Eintrag», klein -- ``grundbruch``, ``raumlinie``. Unter diesem Namen
    stehen ihre Feldangaben und ihre Vorlage.
    """
    return cls.__name__.removesuffix("Eintrag").lower()


def eintragsklassen(cls: type) -> List[type]:
    """
    Jede Klasse von Eintraegen, die unter ``cls`` vorkommt, ``cls`` zuerst --
    gefunden auf dem Weg, auf dem :func:`lesen` eine Datei ablaeuft: durch
    Felder, Listen, Zuordnungen und Optionale. Fuer den Katalog der
    Feldangaben (:func:`feldangaben`).
    """
    gefunden: Dict[type, None] = {}

    def durch(k: type) -> None:
        if k in gefunden:
            return
        gefunden[k] = None
        typen = _typen(k)
        for f in dataclasses.fields(k):
            art, innen = _art(typen[f.name])
            while art in ("optional", "liste", "zuordnung"):
                art, innen = _art(innen)
            if art == "eintrag":
                durch(innen)

    durch(cls)
    return list(gefunden)


# ===========================================================================
# Lesen
# ===========================================================================


#: Ein Feld ohne Vorgabe.
_KEINE = object()


def unbekanntes_feld(wo: str, name: Any, felder: Iterable[str]) -> ProjektFehler:
    """
    Der Fehler zu einem Feld, das es nicht gibt -- mit dem ähnlichsten, das
    es gibt. Beim Lesen einer Datei und bei einer Zuweisung aus Python
    derselbe Satz.
    """
    aehnlich = difflib.get_close_matches(str(name), list(felder), n=1)
    return ProjektFehler(f"ein Feld '{name}' gibt es nicht."
                         + (f" Gemeint ist vielleicht '{aehnlich[0]}'?" if aehnlich else ""), wo=wo)


def lesen(cls: type, roh: Any, wo: str, basis: Any = None) -> Any:
    """
    Ein Eintrag der Klasse ``cls`` aus ``roh``, einem Woerterbuch aus der Datei.

    ``wo`` nennt den Ort in Meldungen. ``basis`` ist der Eintrag, dessen Werte
    fuer fehlende Felder gelten -- ohne sie die Vorgaben der Klasse. Jeder
    gelesene Eintrag ist danach geprueft (:func:`felder_pruefen`).

    Aus Python darf ``roh`` auch schon ein Eintrag der Klasse sein, etwa ein
    Stichwort der Fassade: er bleibt, wie er ist, und wird ganz geprueft.

    Kennt eine Klasse ein Feld, das in ``roh`` fehlt, aber aus dem folgt,
    was dasteht -- eine Datei von frueher kennt es noch nicht --, ergaenzt
    sie es vorher selbst: ``cls.ergaenzt(roh, basis)``, etwa
    :meth:`~opencivil.projekt.decke.DeckenplatteEintrag.ergaenzt`.
    """
    if isinstance(roh, cls):
        felder_pruefen(roh, wo)
        return roh
    if not isinstance(roh, Mapping):
        raise ProjektFehler(f"hier gehört ein Eintrag mit Feldern hin, "
                            f"nicht {_zeigen(roh)}.", wo=wo)
    ergaenzt = getattr(cls, "ergaenzt", None)
    if ergaenzt is not None:
        roh = ergaenzt(roh, basis)
    felder = {f.name: f for f in dataclasses.fields(cls) if f.init}
    for schluessel in roh:
        if schluessel not in felder:
            raise unbekanntes_feld(wo, schluessel, felder)
    typen = _typen(cls)
    werte: Dict[str, Any] = {}
    for name, f in felder.items():
        vorbild = getattr(basis, name) if basis is not None else _vorgabe(f)
        if name in roh:
            werte[name] = _wert_lesen(roh[name], typen[name], wo, f, vorbild)
        elif vorbild is _KEINE:
            raise ProjektFehler(f"das Feld '{name}' fehlt.", wo=wo)
        elif basis is not None:
            werte[name] = copy.deepcopy(vorbild)
    eintrag = cls(**werte)
    felder_pruefen(eintrag, wo, tief=False)
    return eintrag


def _wert_lesen(roh: Any, typ: Any, wo: str, f: dataclasses.Field, vorbild: Any) -> Any:
    """
    Ein Feld aus der Datei. Eintraege und Listen von Eintraegen werden
    gelesen; Zahlen bleiben, was sie sind -- nur eine ganze Zahl aus JSON wird
    dort, wo eine Zahl hingehoert, zur Gleitkommazahl, und eine ganze
    Gleitkommazahl dort, wo eine ganze Zahl hingehoert, zur ganzen. Ob der
    Wert passt, sagt danach :func:`felder_pruefen`.
    """
    art, innen = _art(typ)
    if art == "optional":
        return None if roh is None else _wert_lesen(roh, innen, wo, f, vorbild)
    if art == "eintrag":
        basis = vorbild if isinstance(vorbild, innen) else None
        return lesen(innen, roh, f"{wo}, {_im_ort(f)}", basis)
    if art == "liste":
        if not isinstance(roh, list):
            raise ProjektFehler(f"'{f.name}' muss eine Liste sein, nicht {_zeigen(roh)}.",
                                wo=wo)
        innere, _ = _art(innen)
        if innere == "eintrag":
            return [lesen(innen, element, element_ort(element, innen, wo, f.name, i))
                    for i, element in enumerate(roh)]
        return [_zahl_lesen(element, innen) for element in roh]
    if art == "zuordnung":
        if not isinstance(roh, Mapping):
            raise ProjektFehler(f"'{f.name}' muss eine Zuordnung sein, "
                                f"nicht {_zeigen(roh)}.", wo=wo)
        return {schluessel: _zahl_lesen(wert, innen) for schluessel, wert in roh.items()}
    return _zahl_lesen(roh, typ)


def _zahl_lesen(roh: Any, typ: Any) -> Any:
    """Eine Zahl, wie JSON sie bringt, in der Art des Feldes -- alles andere unveraendert."""
    if typ is float and type(roh) is int:
        return float(roh)
    if typ is int and type(roh) is float and roh.is_integer():
        return int(roh)
    return roh


def ort(cls: type, roh: Any) -> str:
    """
    Wie ein Eintrag fuer sich in Meldungen heisst: «Platte 'Decke'», ohne
    Namen mit seiner Kennung, sonst nur seine Art.
    """
    bezeichnung = getattr(cls, "BEZEICHNUNG", cls.__name__)
    if not isinstance(roh, Mapping):
        return bezeichnung
    return _benannt(bezeichnung, roh.get("name"), roh.get("kennung")) or bezeichnung


def ort_von(eintrag: Any) -> str:
    """
    :func:`ort` eines gelesenen Eintrags -- ein Material heisst nach seiner
    Anzeige, ohne eigenen Namen nach der Sorte.
    """
    name = getattr(eintrag, "anzeigename", None) or eintrag.name
    return ort(type(eintrag), {"name": name, "kennung": eintrag.kennung})


def element_ort(element: Any, cls: type, wo: str, feld: str, i: int) -> str:
    """
    Wie das Element ``i`` der Liste ``feld`` in Meldungen heisst -- aus der
    Datei, vor dem Lesen. Auch fuer ein neues, das Python anlegt
    (``MitStaeben._gelesen``): bis 2026-11-21 hiess es dort nach seiner
    Liste, «linien».
    """
    if not isinstance(element, Mapping):
        return _ort(cls, None, None, wo, feld, i)
    return _ort(cls, element.get("name"), element.get("kennung"), wo, feld, i)


def _ort(cls: type, name: Any, kennung: Any, wo: str, feld: str, i: int) -> str:
    """
    Ein Bauteil oder Material heisst wie in der Oberflaeche -- «Platte 'Decke'»,
    und dort beginnt der Ort neu; alles darin mit seinem Namen, davor das
    Wort seiner Klasse (``IM_ORT``: «Wand 'W1'» im Erdbeben, «Kombination
    'GZT'»). Bis 2026-11-21 stand ohne Wort das Feld der Datei davor,
    «kombinationen 'GZT'»; ein Test wacht, dass jede Klasse eines hat. Nur
    Leerzeichen sind kein Name.

    Ohne Namen heisst ein Element, wie die Maske es nennt: mit dem Wort
    seiner Klasse und seiner Nummer (``IM_ORT``: «Lage 2», «Linie 3» wie in
    der Zeichnung einer Querschnittsanalyse), sonst mit seiner Kennung
    («A1», wie im Balkensystem), sonst nach Feld und Nummer. Bis 2026-11-20
    hiess es immer nach Feld und Nummer: «lagen 2», «lager 1».
    """
    bezeichnung = getattr(cls, "BEZEICHNUNG", None)
    if bezeichnung:
        return _benannt(bezeichnung, name, kennung) or f"{bezeichnung} {i + 1}"
    im_ort = getattr(cls, "IM_ORT", None)
    if isinstance(name, str) and name.strip():
        return f"{wo}, {im_ort or feld} '{name}'"
    if im_ort:
        return f"{wo}, {im_ort} {i + 1}"
    if isinstance(kennung, str) and kennung:
        return f"{wo}, {kennung}"
    return f"{wo}, {feld} {i + 1}"


def _benannt(bezeichnung: str, name: Any, kennung: Any) -> Optional[str]:
    """«Platte 'Decke'», ohne Namen «Platte q1» -- ``None`` ohne beides."""
    if isinstance(name, str) and name.strip():
        return f"{bezeichnung} '{name}'"
    if isinstance(kennung, str) and kennung:
        return f"{bezeichnung} {kennung}"
    return None


# ===========================================================================
# Pruefen
# ===========================================================================


def felder_pruefen(eintrag: Any, wo: str, *, tief: bool = True) -> None:
    """
    Prueft die Form jedes Feldes eines Eintrags gegen das, was an ihm steht:
    Typ, Wahl, Pflicht. ``tief``: auch jeden Eintrag darin.
    """
    typen = _typen(type(eintrag))
    for f in dataclasses.fields(eintrag):
        _wert_pruefen(getattr(eintrag, f.name), typen[f.name], f, wo, tief)


def _wert_pruefen(wert: Any, typ: Any, f: dataclasses.Field, wo: str, tief: bool) -> None:
    art, innen = _art(typ)
    if art == "optional":
        if wert is not None:
            _wert_pruefen(wert, innen, f, wo, tief)
        return
    if art == "eintrag":
        if not isinstance(wert, innen):
            raise ProjektFehler(f"'{f.name}' muss ein {innen.__name__} sein, "
                                f"nicht {_zeigen(wert)}.", wo=wo)
        if tief:
            felder_pruefen(wert, f"{wo}, {_im_ort(f)}")
        return
    if art == "liste":
        if not isinstance(wert, list):
            raise ProjektFehler(f"'{f.name}' muss eine Liste sein, nicht {_zeigen(wert)}.",
                                wo=wo)
        innere, _ = _art(innen)
        for i, element in enumerate(wert):
            if innere != "eintrag":
                _blatt_pruefen(element, innen, f, wo)
            elif not isinstance(element, innen):
                raise ProjektFehler(f"in '{f.name}' gehört ein {innen.__name__} hin, "
                                    f"nicht {_zeigen(element)}.", wo=wo)
            elif tief:
                felder_pruefen(element, _ort_von(element, wo, f.name, i))
        return
    if art == "zuordnung":
        if not isinstance(wert, dict) or not all(isinstance(k, str) for k in wert):
            raise ProjektFehler(f"'{f.name}' muss eine Zuordnung sein, "
                                f"nicht {_zeigen(wert)}.", wo=wo)
        for schluessel, element in wert.items():
            _blatt_pruefen(element, innen, f, f"{wo}, {f.name} '{schluessel}'")
        return
    _blatt_pruefen(wert, typ, f, wo)


def _blatt_pruefen(wert: Any, typ: Any, f: dataclasses.Field, wo: str) -> None:
    """Ein Text, eine Zahl, ein Schalter, eine Wahl -- und was an seinem Feld steht."""
    if _ist_wahl(typ):
        moeglich = f.metadata.get("wahl") or tuple(typ)
        if not isinstance(wert, typ) or wert not in moeglich:
            raise ProjektFehler(f"{_zeigen(wert)} gibt es als '{f.name}' nicht. "
                                f"Möglich sind: {', '.join(str(m) for m in moeglich)}.", wo=wo)
        return
    if typ is str:
        if not isinstance(wert, str):
            raise ProjektFehler(f"'{f.name}' muss ein Text sein, nicht {_zeigen(wert)}.",
                                wo=wo)
        if not wert and _vorgabe(f) is _KEINE and not _ist_name(f):
            raise ProjektFehler(f"'{f.name}' darf nicht leer sein.", wo=wo)
    elif typ is bool:
        if not isinstance(wert, bool):
            raise ProjektFehler(f"'{f.name}' ist ein Schalter, true oder false – "
                                f"nicht {_zeigen(wert)}.", wo=wo)
    elif typ is int:
        if isinstance(wert, bool) or not isinstance(wert, int):
            raise ProjektFehler(f"'{f.name}' muss eine ganze Zahl sein, "
                                f"nicht {_zeigen(wert)}.", wo=wo)
    elif typ is float:
        if isinstance(wert, bool) or not isinstance(wert, (int, float)) \
                or not math.isfinite(wert):
            raise ProjektFehler(f"'{f.name}' muss eine Zahl sein, nicht {_zeigen(wert)}.",
                                wo=wo)
    moeglich = f.metadata.get("wahl")
    if moeglich is not None and wert not in moeglich:
        raise ProjektFehler(f"{_zeigen(wert)} gibt es als '{f.name}' nicht. "
                            f"Möglich sind: {', '.join(str(m) for m in moeglich)}.", wo=wo)


def inhalt_pruefen(eintrag: Any, wo: str, ohne: Iterable[str] = ()) -> None:
    """
    Prueft, was erst das Rechnen braucht -- nach der Form, vor jedem Rechnen:
    jede Zahl gegen ihren Bereich (:func:`bereich`) -- eine Liste davon mit
    mindestens einer --, jeden Eintrag darin ebenso, jede gegen das Feld,
    das sie begrenzt (:attr:`Bereich.bis_feld`, :attr:`Bereich.quer_zu`),
    und danach die Namen seiner Faelle (``fallnamen()``) und die Regeln des
    Eintrags ueber mehrere Felder, ``regeln(wo)``. Die Form ist da schon geprueft: ein Eintrag steht, wo
    einer hingehoert, eine Zahl, wo eine Zahl hingehoert. Die Felder in
    ``ohne`` prueft, wer sie einzeln prueft -- der Aufbau jedes Material und
    jedes Bauteil fuer sich (:func:`~opencivil.projekt.aufbau.aufbauen`).

    Zuerst der Name, wo einer Pflicht ist (:func:`_ist_name`): leer oder nur
    Leerzeichen sagt «noch kein Name», wie das Namensfeld ihn abweist.
    """
    if any(_ist_name(f) for f in dataclasses.fields(eintrag)) and not eintrag.name.strip():
        raise ProjektFehler("noch kein Name.", wo=wo)
    for f in dataclasses.fields(eintrag):
        if f.name in ohne:
            continue
        wert = getattr(eintrag, f.name)
        bereich_ = f.metadata.get("bereich")
        teile = wert if isinstance(wert, list) else [wert]
        if bereich_ is not None and not teile:
            raise ProjektFehler(f"{bereich_.heisst}: noch keine Zahl – es braucht "
                                f"mindestens eine.", wo=wo)
        for i, teil in enumerate(teile):
            if dataclasses.is_dataclass(teil):
                inhalt_pruefen(teil, _ort_von(teil, wo, f.name, i) if teile is wert
                               else f"{wo}, {_im_ort(f)}")
            elif bereich_ is not None and teil is not None:
                anhalten(bereich_.grund(teil), wo)
        if bereich_ is not None and bereich_.bis_feld is not None:
            anhalten(bereich_.grund_gegen(wert, _bereiche(type(eintrag))[bereich_.bis_feld],
                                          getattr(eintrag, bereich_.bis_feld)), wo)
        if bereich_ is not None and bereich_.quer_zu is not None:
            feld = bereich_.quer_zu[0]
            anhalten(bereich_.grund_quer(wert, _bereiche(type(eintrag))[feld], getattr(eintrag, feld)), wo)
    for liste in eintrag.fallnamen():
        liste.pruefen(wo)
    eintrag.regeln(wo)


def _ist_name(f: dataclasses.Field) -> bool:
    """
    Ob ein Feld der Name seines Eintrags ist, ohne Vorgabe. Leer haelt er
    nicht schon das Lesen auf, sondern erst das Rechnen seines Bauteils
    (:func:`inhalt_pruefen`): bis 2026-11-19 liess ein leerer Fallname aus
    einer bearbeiteten Datei das ganze Projekt nicht mehr oeffnen (Benutzer:
    nur seine Platte oder Analyse rechnet nicht).
    """
    return f.name == "name" and _vorgabe(f) is _KEINE


def _ort_von(element: Any, wo: str, feld: str, i: int) -> str:
    """Wie ein gebautes Listenelement in Meldungen heisst -- wie :func:`element_ort` vor dem Lesen."""
    return _ort(type(element), getattr(element, "name", None),
                getattr(element, "kennung", None), wo, feld, i)


# ===========================================================================
# Die Typen der Felder
# ===========================================================================


@functools.lru_cache(maxsize=None)
def _typen(cls: type) -> Dict[str, Any]:
    """Die Typen der Felder, aufgeloest -- je Klasse einmal."""
    return typing.get_type_hints(cls)


def _ist_wahl(typ: Any) -> bool:
    return isinstance(typ, type) and issubclass(typ, enum.Enum)


@functools.lru_cache(maxsize=None)
def _wahlfelder(cls: type) -> Dict[str, type]:
    """Je Wahlfeld einer Datenklasse seine Wahl -- je Klasse einmal."""
    return {name: typ for name, typ in _typen(cls).items() if _ist_wahl(typ)}


@functools.lru_cache(maxsize=None)
def _wahlzuordnungen(cls: type) -> Dict[str, type]:
    """Je Feld, das eine Zuordnung von Wahlen haelt (:func:`je_material`), die Wahl seiner Werte."""
    heraus = {}
    for name, typ in _typen(cls).items():
        art, innen = _art(typ)
        if art == "zuordnung" and _ist_wahl(innen):
            heraus[name] = innen
    return heraus


def wahl_von(cls: type, feld: str) -> tuple:
    """Was ein Wahlfeld annehmen kann -- seine Teilmenge, sonst jedes Mitglied seiner Wahl."""
    f = next(f for f in dataclasses.fields(cls) if f.name == feld)
    return tuple(f.metadata.get("wahl") or _wahlfelder(cls)[feld])


def wahl_aus_text(cls: type, feld: str, wert: Any) -> Any:
    """
    Text in einem Wahlfeld wird sein Mitglied -- beim Lesen einer Datei und
    wo Python einen Text zuweist. Ein Text, den es nicht gibt, bleibt Text:
    die Pruefung meldet ihn dann mit seinem Ort (:func:`felder_pruefen`).
    """
    wahl = _wahlfelder(cls).get(feld)
    if wahl is not None:
        return _mitglied(wahl, wert)
    wahl = _wahlzuordnungen(cls).get(feld)
    if wahl is not None and isinstance(wert, dict):
        return {schluessel: _mitglied(wahl, w) for schluessel, w in wert.items()}
    return wert


def _mitglied(wahl: type, wert: Any) -> Any:
    """Ein Text als Mitglied der Wahl -- ein Text, den es nicht gibt, bleibt Text."""
    if not isinstance(wert, str) or isinstance(wert, wahl):
        return wert
    try:
        return wahl(wert)
    except ValueError:
        return wert


def _art(typ: Any):
    """
    Was fuer ein Feld es ist: ``optional``, ``liste``, ``zuordnung``,
    ``eintrag`` -- mit dem Typ darin -- oder ein Blatt.
    """
    herkunft = typing.get_origin(typ)
    argumente = typing.get_args(typ)
    if herkunft is typing.Union:
        innen = [a for a in argumente if a is not type(None)]
        return "optional", innen[0]
    if herkunft is list:
        return "liste", argumente[0]
    if herkunft is dict:
        return "zuordnung", argumente[1]
    if dataclasses.is_dataclass(typ):
        return "eintrag", typ
    return "blatt", typ


def _vorgabe(f: dataclasses.Field) -> Any:
    """Die Vorgabe eines Feldes -- auch eine aus ``default_factory`` --, sonst :data:`_KEINE`."""
    if f.default is not dataclasses.MISSING:
        return f.default
    if f.default_factory is not dataclasses.MISSING:
        return f.default_factory()
    return _KEINE


def _zeigen(wert: Any) -> str:
    """Ein Wert, wie er in einer Meldung steht -- ein Text in Anfuehrungszeichen."""
    if isinstance(wert, str):
        return f"'{wert}'"
    if isinstance(wert, Mapping):
        return "ein Eintrag mit Feldern"
    if isinstance(wert, list):
        return "eine Liste"
    return repr(wert)
