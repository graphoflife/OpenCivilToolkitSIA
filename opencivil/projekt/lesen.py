"""
opencivil/projekt/lesen.py -- was in einer Projektdatei stehen darf, und wie es gelesen wird.

VERANTWORTUNG:
Ein Leser fuer jeden Eintrag und eine Pruefung fuer jedes Feld, beide aus den
Feldern der Datenklassen. Was ein Feld annehmen darf, steht an ihm selbst:

* sein Typ -- Text, Zahl, ganze Zahl, Schalter, Liste, Zuordnung, Eintrag,
  oder eine Wahl (:class:`~opencivil.core.wahl.Wahl`), deren Mitglieder es
  annimmt;
* eine Teilmenge davon (:func:`einer_von`) -- die Werte, die es gibt;
* ein Text ohne Vorgabe ist Pflicht und darf nicht leer sein;
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
machten daraus wieder das Mitglied.
"""

from __future__ import annotations

import copy
import dataclasses
import difflib
import enum
import functools
import math
import typing
from typing import Any, Dict, Iterable, Mapping, Optional

from opencivil.core.einheiten import EINHEITSLOS, Einheit, Groesse
from opencivil.material.beton import BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN


class ProjektFehler(Exception):
    """Die Projektbeschreibung ist in sich nicht stimmig."""


# ===========================================================================
# Was an einem Feld steht
# ===========================================================================


def einer_von(moeglich: Iterable[Any], vorgabe: Any = dataclasses.MISSING) -> Any:
    """Ein Feld, das nur einen dieser Werte annimmt -- die Pruefung kennt sie von hier."""
    return dataclasses.field(default=vorgabe, metadata={"wahl": tuple(moeglich)})


@dataclasses.dataclass(frozen=True)
class Bereich:
    """
    Wo die Zahl eines Feldes liegen muss -- jede Grenze darf fehlen, ``ueber``
    und ``unter`` schliessen die Grenze aus, ``ab`` und ``bis`` ein. Geprueft
    vor dem Rechnen (:func:`inhalt_pruefen`).
    """

    heisst: str
    """Wie das Feld in der Meldung heisst -- wie an der Maske: «Dicke h»."""

    einheit: Optional[Einheit] = None
    ueber: Optional[float] = None
    ab: Optional[float] = None
    bis: Optional[float] = None
    unter: Optional[float] = None

    def pruefen(self, wert: float, wo: str) -> None:
        if ((self.ueber is None or wert > self.ueber) and (self.ab is None or wert >= self.ab)
                and (self.bis is None or wert <= self.bis)
                and (self.unter is None or wert < self.unter)):
            return
        raise ProjektFehler(f"{wo}: {self.heisst} {self.verlangt}, angegeben ist "
                            f"{self._zahl(wert)}.")

    @property
    def verlangt(self) -> str:
        """Was die Grenzen verlangen: «muss grösser als null sein»."""
        grenzen = [(wort, g) for wort, g in (("grösser als", self.ueber), ("mindestens", self.ab),
                                             ("kleiner als", self.unter), ("höchstens", self.bis))
                   if g is not None]
        if grenzen == [("mindestens", 0.0)]:
            return "kann nicht negativ sein"
        return "muss " + " und ".join(
            f"{wort} {'null' if g == 0.0 else self._zahl(g)}" for wort, g in grenzen) + " sein"

    def _zahl(self, wert: float) -> str:
        """Eine Zahl mit der Einheit des Feldes: «300 mm», «30°», «0.9»."""
        if self.einheit is None or self.einheit.name in ("", "-"):
            return f"{wert:g}"
        return f"{wert:g}{'' if self.einheit.klebt else ' '}{self.einheit.beschriftung}"


def bereich(vorgabe: Any = dataclasses.MISSING, *, heisst: str,
            einheit: Optional[Einheit] = None, ueber: Optional[float] = None,
            ab: Optional[float] = None, bis: Optional[float] = None,
            unter: Optional[float] = None) -> Any:
    """Ein Feld, dessen Zahl in einem :class:`Bereich` liegen muss -- eine Kriechzahl ab null etwa."""
    return dataclasses.field(default=vorgabe, metadata={
        "bereich": Bereich(heisst, einheit, ueber=ueber, ab=ab, bis=bis, unter=unter)})


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
    ganz sein muss. Was eine Wahl annehmen kann, steht nicht hier: das sagen
    die Wahllisten des Katalogs, mit Beschriftung.

    Steht es am Feld, steht es einmal. Bis 2026-10-18 standen die Einheiten
    des Grundbruchs dreimal da -- am Feld, beim Bauen und in grundbruch.js --,
    und wichen zwei davon ab, galt eine Zahl still um 10³ anders.
    """
    typen = _typen(cls)
    angaben: Dict[str, Dict[str, Any]] = {}
    for f in dataclasses.fields(cls):
        angabe: Dict[str, Any] = {}
        b = f.metadata.get("bereich")
        if b is not None:
            if b.einheit is not None and b.einheit.name not in ("", "-"):
                angabe["einheit"] = b.einheit.beschriftung
            angabe.update({grenze: getattr(b, grenze) for grenze in ("ueber", "ab", "bis", "unter")
                           if getattr(b, grenze) is not None})
        if typen.get(f.name) is int:
            angabe["ganz"] = True
        if angabe:
            angaben[f.name] = angabe
    return angaben


def sorten(art: str) -> Mapping[str, Any]:
    """Die Normsorten einer Materialart."""
    return {"beton": BETONSORTEN, "betonstahl": STAHLSORTEN}[art]


# ===========================================================================
# Lesen
# ===========================================================================


#: Ein Feld ohne Vorgabe.
_KEINE = object()


def lesen(cls: type, roh: Any, wo: str, basis: Any = None) -> Any:
    """
    Ein Eintrag der Klasse ``cls`` aus ``roh``, einem Woerterbuch aus der Datei.

    ``wo`` nennt den Ort in Meldungen. ``basis`` ist der Eintrag, dessen Werte
    fuer fehlende Felder gelten -- ohne sie die Vorgaben der Klasse. Jeder
    gelesene Eintrag ist danach geprueft (:func:`felder_pruefen`).

    Aus Python darf ``roh`` auch schon ein Eintrag der Klasse sein, etwa ein
    Stichwort der Fassade: er bleibt, wie er ist, und wird ganz geprueft.
    """
    if isinstance(roh, cls):
        felder_pruefen(roh, wo)
        return roh
    if not isinstance(roh, Mapping):
        raise ProjektFehler(f"{wo}: hier gehört ein Eintrag mit Feldern hin, "
                            f"nicht {_zeigen(roh)}.")
    felder = {f.name: f for f in dataclasses.fields(cls) if f.init}
    for schluessel in roh:
        if schluessel not in felder:
            aehnlich = difflib.get_close_matches(str(schluessel), felder, n=1)
            raise ProjektFehler(
                f"{wo}: ein Feld '{schluessel}' gibt es nicht."
                + (f" Gemeint ist vielleicht '{aehnlich[0]}'?" if aehnlich else ""))
    typen = _typen(cls)
    werte: Dict[str, Any] = {}
    for name, f in felder.items():
        vorbild = getattr(basis, name) if basis is not None else _vorgabe(f)
        if name in roh:
            werte[name] = _wert_lesen(roh[name], typen[name], wo, name, vorbild)
        elif vorbild is _KEINE:
            raise ProjektFehler(f"{wo}: das Feld '{name}' fehlt.")
        elif basis is not None:
            werte[name] = copy.deepcopy(vorbild)
    eintrag = cls(**werte)
    felder_pruefen(eintrag, wo, tief=False)
    return eintrag


def _wert_lesen(roh: Any, typ: Any, wo: str, feld: str, vorbild: Any) -> Any:
    """
    Ein Feld aus der Datei. Eintraege und Listen von Eintraegen werden
    gelesen; Zahlen bleiben, was sie sind -- nur eine ganze Zahl aus JSON wird
    dort, wo eine Zahl hingehoert, zur Gleitkommazahl, und eine ganze
    Gleitkommazahl dort, wo eine ganze Zahl hingehoert, zur ganzen. Ob der
    Wert passt, sagt danach :func:`felder_pruefen`.
    """
    art, innen = _art(typ)
    if art == "optional":
        return None if roh is None else _wert_lesen(roh, innen, wo, feld, vorbild)
    if art == "eintrag":
        basis = vorbild if isinstance(vorbild, innen) else None
        return lesen(innen, roh, f"{wo}, {feld}", basis)
    if art == "liste":
        if not isinstance(roh, list):
            raise ProjektFehler(f"{wo}: '{feld}' muss eine Liste sein, nicht {_zeigen(roh)}.")
        innere, _ = _art(innen)
        if innere == "eintrag":
            return [lesen(innen, element, _ort_roh(element, innen, wo, feld, i))
                    for i, element in enumerate(roh)]
        return [_zahl_lesen(element, innen) for element in roh]
    if art == "zuordnung":
        if not isinstance(roh, Mapping):
            raise ProjektFehler(f"{wo}: '{feld}' muss eine Zuordnung sein, "
                                f"nicht {_zeigen(roh)}.")
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


def _ort_roh(element: Any, cls: type, wo: str, feld: str, i: int) -> str:
    """Wie ein Listenelement in Meldungen heisst -- aus der Datei, vor dem Lesen."""
    if not isinstance(element, Mapping):
        return f"{wo}, {feld} {i + 1}"
    return _ort(cls, element.get("name"), element.get("kennung"), wo, feld, i)


def _ort(cls: type, name: Any, kennung: Any, wo: str, feld: str, i: int) -> str:
    """
    Ein Bauteil oder Material heisst wie in der Oberflaeche -- «Platte 'Decke'»,
    und dort beginnt der Ort neu; alles darin nach seinem Feld und seinem
    Namen, ohne Namen nach seiner Nummer: «lagen 2».
    """
    bezeichnung = getattr(cls, "BEZEICHNUNG", None)
    if bezeichnung:
        return _benannt(bezeichnung, name, kennung) or f"{bezeichnung} {i + 1}"
    if isinstance(name, str) and name:
        return f"{wo}, {feld} '{name}'"
    return f"{wo}, {feld} {i + 1}"


def _benannt(bezeichnung: str, name: Any, kennung: Any) -> Optional[str]:
    """«Platte 'Decke'», ohne Namen «Platte q1» -- ``None`` ohne beides."""
    if isinstance(name, str) and name:
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
            raise ProjektFehler(f"{wo}: '{f.name}' muss ein {innen.__name__} sein, "
                                f"nicht {_zeigen(wert)}.")
        if tief:
            felder_pruefen(wert, f"{wo}, {f.name}")
        return
    if art == "liste":
        if not isinstance(wert, list):
            raise ProjektFehler(f"{wo}: '{f.name}' muss eine Liste sein, nicht {_zeigen(wert)}.")
        innere, _ = _art(innen)
        for i, element in enumerate(wert):
            if innere != "eintrag":
                _blatt_pruefen(element, innen, f, wo)
            elif not isinstance(element, innen):
                raise ProjektFehler(f"{wo}: in '{f.name}' gehört ein {innen.__name__} hin, "
                                    f"nicht {_zeigen(element)}.")
            elif tief:
                felder_pruefen(element, _ort_von(element, wo, f.name, i))
        return
    if art == "zuordnung":
        if not isinstance(wert, dict) or not all(isinstance(k, str) for k in wert):
            raise ProjektFehler(f"{wo}: '{f.name}' muss eine Zuordnung sein, "
                                f"nicht {_zeigen(wert)}.")
        for schluessel, element in wert.items():
            _blatt_pruefen(element, innen, f, f"{wo}, {f.name} '{schluessel}'")
        return
    _blatt_pruefen(wert, typ, f, wo)


def _blatt_pruefen(wert: Any, typ: Any, f: dataclasses.Field, wo: str) -> None:
    """Ein Text, eine Zahl, ein Schalter, eine Wahl -- und was an seinem Feld steht."""
    if _ist_wahl(typ):
        moeglich = f.metadata.get("wahl") or tuple(typ)
        if not isinstance(wert, typ) or wert not in moeglich:
            raise ProjektFehler(f"{wo}: {_zeigen(wert)} gibt es als '{f.name}' nicht. "
                                f"Möglich sind: {', '.join(str(m) for m in moeglich)}.")
        return
    if typ is str:
        if not isinstance(wert, str):
            raise ProjektFehler(f"{wo}: '{f.name}' muss ein Text sein, nicht {_zeigen(wert)}.")
        if not wert and _vorgabe(f) is _KEINE:
            raise ProjektFehler(f"{wo}: '{f.name}' darf nicht leer sein.")
    elif typ is bool:
        if not isinstance(wert, bool):
            raise ProjektFehler(f"{wo}: '{f.name}' ist ein Schalter, true oder false -- "
                                f"nicht {_zeigen(wert)}.")
    elif typ is int:
        if isinstance(wert, bool) or not isinstance(wert, int):
            raise ProjektFehler(f"{wo}: '{f.name}' muss eine ganze Zahl sein, "
                                f"nicht {_zeigen(wert)}.")
    elif typ is float:
        if isinstance(wert, bool) or not isinstance(wert, (int, float)) \
                or not math.isfinite(wert):
            raise ProjektFehler(f"{wo}: '{f.name}' muss eine Zahl sein, nicht {_zeigen(wert)}.")
    moeglich = f.metadata.get("wahl")
    if moeglich is not None and wert not in moeglich:
        raise ProjektFehler(f"{wo}: {_zeigen(wert)} gibt es als '{f.name}' nicht. "
                            f"Möglich sind: {', '.join(str(m) for m in moeglich)}.")


def inhalt_pruefen(eintrag: Any, wo: str) -> None:
    """
    Prueft, was erst das Rechnen braucht -- nach der Form, vor jedem Rechnen:
    jede Zahl gegen ihren Bereich (:func:`bereich`), jeden Eintrag darin
    ebenso, und danach die Regeln des Eintrags ueber mehrere Felder,
    ``regeln(wo)``. Die Form ist da schon geprueft: ein Eintrag steht, wo
    einer hingehoert, eine Zahl, wo eine Zahl hingehoert.
    """
    for f in dataclasses.fields(eintrag):
        wert = getattr(eintrag, f.name)
        bereich_ = f.metadata.get("bereich")
        teile = wert if isinstance(wert, list) else [wert]
        for i, teil in enumerate(teile):
            if dataclasses.is_dataclass(teil):
                inhalt_pruefen(teil, _ort_von(teil, wo, f.name, i) if teile is wert
                               else f"{wo}, {f.name}")
            elif bereich_ is not None and teil is not None:
                bereich_.pruefen(teil, wo)
    eintrag.regeln(wo)


def _ort_von(element: Any, wo: str, feld: str, i: int) -> str:
    """Wie ein gebautes Listenelement in Meldungen heisst -- wie :func:`_ort_roh` vor dem Lesen."""
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
    if wahl is None or not isinstance(wert, str) or isinstance(wert, wahl):
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
