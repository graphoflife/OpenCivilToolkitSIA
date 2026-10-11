"""
opencivil/notizbuch/bibliothek.py -- die Python-Bibliothek als Seiten.

VERANTWORTUNG:
Je Modul und je Paket eine Seite im Notizbuch, aus den Docstrings: was das
Modul verantwortet, seine Klassen und Funktionen samt Signatur, seine
Konstanten, was es braucht und wer es braucht, und welche Formeln es
schreibt. Gelesen wird mit ``ast`` -- nichts wird dafuer importiert. Was ueber
ein Modul zu sagen ist, steht in seinem Docstring; die Seite ist ganz
erzeugt, ohne eigenen Teil.

AUS DEM DOCSTRING WIRD MARKDOWN:
* Die Kopfzeile ``opencivil/<pfad>.py -- Kurzbeschreibung.`` wird zur
  Kurzbeschreibung oben auf der Seite.
* Eine Zeile in GROSSBUCHSTABEN wird zur Ueberschrift -- im Docstring eines
  Moduls oder Pakets; in dem einer Klasse oder Funktion bleibt sie fett. Eine
  Klammer gehoert dazu (``VORZEICHEN (wie in …):``), ein Schwanz nach
  `` -- `` in Kleinbuchstaben beginnt den Absatz darunter.
* Eingerueckt wird Code: nach ``::``, direkt unter einer Ueberschrift und nach
  einer Leerzeile. Eingerueckte Zeilen direkt nach einer Textzeile setzen
  deren Absatz fort.
* ``x`` wird `x`; eine Rolle wie ``:class:`~opencivil.x.Y``` wird ein Link
  auf die Seite des Moduls und die Ueberschrift dort. Was sich nicht
  aufloesen laesst, bleibt Code -- ein Test haelt die Liste leer.
* Was Markdown, Obsidian oder MathJax anders lesen wuerden -- ``$``, ``<``,
  ``|``, ``%%``, ``==``, ``[[`` --, wird maskiert.

WIE EIN NAME AUFGELOEST WIRD:
In dieser Folge: ein ganzes Modul; das laengste Modul am Anfang des Namens;
eine Klasse oder Funktion im eigenen Modul; was das Modul importiert; ein
Modul mit diesem Ende (``latex.Mathe``); ein Name, den es im ganzen Paket
nur einmal gibt.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from opencivil.notizbuch.namen import sortierschluessel
from opencivil.notizbuch.tresor import Seite

ORDNER = "Python"
PAKET = Path(__file__).resolve().parents[1]
WURZEL = PAKET.parent

#: Wie weit der Wert einer Konstanten gezeigt wird.
WERTLAENGE = 70

#: Eine Ueberschrift im Docstring: Woerter in Grossbuchstaben, mindestens vier
#: Buchstaben, danach hoechstens ein Satzzeichen, eine Klammer oder `` -- ``.
_UEBERSCHRIFT = re.compile(
    r"^(?P<titel>[A-ZÄÖÜ][A-ZÄÖÜ0-9]*(?![a-zäöüß])"
    r"(?:[ ,/-]+[A-ZÄÖÜ0-9]+(?![a-zäöüß]))*)(?P<rest>.*)$")
_ROLLE = re.compile(r":(?:class|func|meth|attr|mod|data|exc|obj):`([^`]+)`")
_CODE = re.compile(r"``(.+?)``")
_LISTE = re.compile(r"^(\s*)([*-]|\d+\.)\s")
_KOPF = re.compile(r"^opencivil[\w/.]*\s+--\s+(.*)$")


@dataclass
class Eintrag:
    """Eine Klasse, Funktion oder Methode -- eine Ueberschrift auf der Seite."""

    anker: str
    knoten: ast.AST
    stufe: int


@dataclass
class Modul:
    name: str
    pfad: Path
    baum: ast.Module
    zeilen: List[str]
    paket: bool
    importe: Dict[str, str] = field(default_factory=dict)
    """Lokaler Name -> voller Name, wie das Modul ihn importiert."""

    braucht: Set[str] = field(default_factory=set)
    eintraege: List[Eintrag] = field(default_factory=list)

    @property
    def doc(self) -> str:
        return ast.get_docstring(self.baum) or ""

    @property
    def kurz(self) -> str:
        erste = self.doc.split("\n", 1)[0]
        m = _KOPF.match(erste)
        return (m.group(1) if m else erste).strip()

    @property
    def anker(self) -> Set[str]:
        return {e.anker for e in self.eintraege}


class Bibliothek:
    """Alle Module des Pakets, gelesen und verknuepft."""

    def __init__(self, module: Dict[str, Modul]) -> None:
        self.module = module
        self.offen: List[Tuple[str, str]] = []
        """Rollen, die sich nicht aufloesen liessen: (Modul, Ziel)."""

    @classmethod
    def lesen(cls, paket: Path = PAKET) -> "Bibliothek":
        module: Dict[str, Modul] = {}
        for pfad in sorted(paket.rglob("*.py")):
            if "__pycache__" in pfad.parts:
                continue
            teile = pfad.relative_to(paket.parent).with_suffix("").parts
            paketmodul = teile[-1] == "__init__"
            name = ".".join(teile[:-1] if paketmodul else teile)
            quelltext = pfad.read_text(encoding="utf-8")
            module[name] = Modul(name, pfad, ast.parse(quelltext), quelltext.split("\n"),
                                 paketmodul)
        bibliothek = cls(module)
        for modul in module.values():
            bibliothek._verknuepfen(modul)
        return bibliothek

    # -- Lesen -------------------------------------------------------------

    def _verknuepfen(self, modul: Modul) -> None:
        paket = modul.name if modul.paket else modul.name.rpartition(".")[0]
        for knoten in ast.walk(modul.baum):
            if isinstance(knoten, ast.Import):
                for a in knoten.names:
                    if a.name.startswith("opencivil"):
                        modul.importe[a.asname or a.name.split(".")[0]] = (
                            a.name if a.asname else a.name.split(".")[0])
                        modul.braucht.add(self._modul_von(a.name))
            elif isinstance(knoten, ast.ImportFrom):
                herkunft = knoten.module or ""
                if knoten.level:
                    basis = paket.split(".")
                    basis = basis[:len(basis) - knoten.level + 1]
                    herkunft = ".".join([*basis, herkunft] if herkunft else basis)
                if not herkunft.startswith("opencivil"):
                    continue
                for a in knoten.names:
                    voll = f"{herkunft}.{a.name}"
                    modul.importe[a.asname or a.name] = voll
                    modul.braucht.add(voll if voll in self.module else herkunft)
        modul.braucht.discard(modul.name)
        modul.braucht = {b for b in modul.braucht if b in self.module}
        modul.eintraege = list(_eintraege(modul.baum))

    def _modul_von(self, name: str) -> str:
        teile = name.split(".")
        for n in range(len(teile), 0, -1):
            if ".".join(teile[:n]) in self.module:
                return ".".join(teile[:n])
        return name

    # -- Aufloesen ---------------------------------------------------------

    def ziel(self, text: str, modul: Modul, klasse: Optional[str] = None,
             tiefe: int = 0) -> Optional[Tuple[str, str]]:
        """
        ``(Modul, Anker)`` zu einem Namen, wie ihn ein Docstring nennt -- Anker
        leer: die Seite. ``klasse`` ist die Klasse, in deren Docstring er steht.
        """
        text = text.strip().lstrip("~").removesuffix("()")
        if tiefe > 4 or not text:
            return None
        if text in self.module:
            return text, ""
        if text.startswith("."):
            paket = modul.name if modul.paket else modul.name.rpartition(".")[0]
            return self.ziel(f"{paket}{text}", modul, None, tiefe + 1)
        teile = text.split(".")
        for n in range(len(teile) - 1, 0, -1):
            kopf = ".".join(teile[:n])
            if kopf in self.module:
                return self._in_modul(self.module[kopf], ".".join(teile[n:]), tiefe)
        if klasse and f"{klasse}.{text}" in modul.anker:
            return modul.name, f"{klasse}.{text}"
        anker = self._im_modul(modul, text)
        if anker:
            return modul.name, anker
        if teile[0] in modul.importe:
            return self.ziel(".".join([modul.importe[teile[0]], *teile[1:]]), modul, None,
                             tiefe + 1)
        if klasse and klasse in modul.anker:
            # Ein Feld der Klasse: es steht bei ihr.
            return modul.name, klasse
        passend = [m for m in self.module if m.endswith("." + teile[0])]
        if len(passend) == 1:
            return self._in_modul(self.module[passend[0]], ".".join(teile[1:]), tiefe)
        for n in range(len(teile), 0, -1):
            kopf = ".".join(teile[:n])
            passend = [(m.name, a) for m in self.module.values() for a in m.anker
                       if a == kopf or a.endswith("." + kopf)]
            if len(passend) == 1:
                return passend[0]
            if passend:
                break
        return None

    def _im_modul(self, modul: Modul, rest: str) -> Optional[str]:
        """
        Die Ueberschrift zu einem Namen in diesem Modul: genau so, oder die
        Klasse davor, oder die einzige Methode dieses Namens -- eine Konstante
        steht unter «Konstanten».
        """
        teile = rest.split(".")
        for n in range(len(teile), 0, -1):
            if ".".join(teile[:n]) in modul.anker:
                return ".".join(teile[:n])
        endung = [a for a in modul.anker if a.endswith("." + rest)]
        if len(endung) == 1:
            return endung[0]
        if _hat_konstante(modul, teile[0]):
            return "Konstanten"
        return None

    def _in_modul(self, modul: Modul, rest: str, tiefe: int) -> Tuple[str, str]:
        """In einem bestimmten Modul: die Ueberschrift, sonst was es weiterreicht, sonst die Seite."""
        anker = self._im_modul(modul, rest) if rest else None
        if anker:
            return modul.name, anker
        erstes = rest.split(".")[0] if rest else ""
        if erstes in modul.importe:
            # Was ein Paket nur weiterreicht, steht in dem Modul, aus dem es kommt.
            weiter = self.ziel(".".join([modul.importe[erstes], *rest.split(".")[1:]]),
                               modul, None, tiefe + 1)
            if weiter:
                return weiter
        return modul.name, ""

    def verweis(self, text: str, modul: Modul, klasse: Optional[str] = None) -> str:
        """Der Link fuer eine Rolle -- oder Code, wenn sich nichts findet. Mit ``~`` zeigt er nur den letzten Teil."""
        rein = text.lstrip("~")
        zeigen = rein.split(".")[-1] if text.startswith("~") else rein
        ziel = self.ziel(rein, modul, klasse)
        if ziel is None:
            self.offen.append((modul.name, rein))
            return f"`{zeigen}`"
        seite, anker = ziel
        if anker:
            return f"[[{seite}#{anker}|{zeigen}]]"
        return f"[[{seite}]]" if zeigen == seite else f"[[{seite}|{zeigen}]]"

    def codestelle(self, stelle: str) -> str:
        """Ein Link zu ``modul:Klasse.methode`` -- so weit die Seite sie kennt."""
        modulname, _, wo = stelle.partition(":")
        modul = self.module.get(modulname)
        if modul is None:
            return f"`{stelle}`"
        if not wo:
            return f"[[{modulname}]]"
        anker = self._im_modul(modul, wo) or ""
        anker = anker if anker != "Konstanten" else ""
        return f"[[{modulname}#{anker}|{wo}]]" if anker else f"[[{modulname}|{wo}]]"

    # -- Seiten ------------------------------------------------------------

    def seiten(self, formeln: Dict[str, List[Tuple[str, str]]]) -> List[Seite]:
        """
        Die Uebersicht, je Paket und je Modul eine Seite. ``formeln`` nennt je
        Modul die Formeln, die es schreibt: ``(Formelname, Funktion)``.
        """
        gebraucht: Dict[str, Set[str]] = {m: set() for m in self.module}
        for modul in self.module.values():
            for ziel in modul.braucht:
                gebraucht[ziel].add(modul.name)
        heraus = [self._uebersicht()]
        for name in sorted(self.module, key=sortierschluessel):
            heraus.append(self._seite(self.module[name], gebraucht[name],
                                      formeln.get(name, [])))
        return heraus

    def _uebersicht(self) -> Seite:
        zeilen = [
            "Je Modul der Bibliothek `opencivil` eine Seite, aus seinen Docstrings: was "
            "es verantwortet, seine Klassen und Funktionen, was es braucht und wer es "
            "braucht, und welche Formeln es schreibt. Wie alles zusammen rechnet, sagt "
            "[[opencivil]].", ""]
        for name in sorted(self.module, key=sortierschluessel):
            modul = self.module[name]
            tiefe = name.count(".") - (1 if modul.paket else 0)
            einzug = "  " * max(tiefe, 0)
            zeilen.append(f"{einzug}- [[{name}]] – {_text(modul.kurz)}" if modul.kurz
                          else f"{einzug}- [[{name}]]")
        return Seite(pfad=f"{ORDNER}/{ORDNER}.md", art="verzeichnis",
                     rumpf="\n".join(zeilen))

    def _seite(self, modul: Modul, gebraucht_von: Set[str],
               formeln: List[Tuple[str, str]]) -> Seite:
        datei = modul.pfad.relative_to(WURZEL).as_posix()
        zeilen = [f"> [!abstract] {datei}"]
        if modul.kurz:
            zeilen.append(f"> {self._inline(modul.kurz, modul)}")
        oben = modul.name.rpartition(".")[0]
        kopf = [f"[Quelltext](../../{datei})"]
        if oben:
            kopf.insert(0, f"Paket [[{oben}]]")
        zeilen += ["> " + " · ".join(kopf), ""]

        doc = modul.doc.split("\n")
        if doc and _KOPF.match(doc[0]) or (doc and modul.kurz == doc[0].strip()):
            doc = doc[1:]
        zeilen += self._docstring("\n".join(doc), modul, ueberschriften=True)

        if modul.paket:
            unter = sorted((m for m in self.module.values()
                            if m.name.rpartition(".")[0] == modul.name), key=lambda m: m.name)
            if unter:
                zeilen += ["", "## Module", ""]
                zeilen += [f"- [[{m.name}]]" + (f" – {_text(m.kurz)}" if m.kurz else "")
                           for m in unter]

        inhalt = self._inhalt(modul)
        if inhalt:
            zeilen += ["", "## Inhalt", "", *inhalt]
        konstanten = self._konstanten(modul)
        if konstanten:
            zeilen += ["", "## Konstanten", "", *konstanten]
        if modul.braucht:
            zeilen += ["", "## Braucht", "",
                       *(f"- [[{n}]]" for n in sorted(modul.braucht, key=sortierschluessel))]
        if gebraucht_von:
            zeilen += ["", "## Gebraucht von", "",
                       *(f"- [[{n}]]" for n in sorted(gebraucht_von, key=sortierschluessel))]
        if formeln:
            zeilen += ["", "## Formeln aus diesem Modul", ""]
            zeilen += [f"- [[{name}]]" + (f" · `{wo}`" if wo else "")
                       for name, wo in sorted(set(formeln),
                                              key=lambda f: (sortierschluessel(f[0]), f[1]))]
        stichworte = [e.anker for e in modul.eintraege]
        return Seite(pfad=f"{ORDNER}/{modul.name}.md", art="modul", rumpf="\n".join(zeilen),
                     verzeichnis=(("kurz", modul.kurz), ("stichworte", stichworte)))

    def _inhalt(self, modul: Modul) -> List[str]:
        zeilen: List[str] = []
        for eintrag in modul.eintraege:
            knoten = eintrag.knoten
            zeilen += [f"{'#' * eintrag.stufe} {eintrag.anker}", "", "```python",
                       *_signatur(knoten), "```", ""]
            doc = ast.get_docstring(knoten)
            klasse = eintrag.anker.split(".")[0] if (
                isinstance(knoten, ast.ClassDef) or eintrag.stufe == 4) else None
            if doc:
                zeilen += self._docstring(doc, modul, ueberschriften=False, klasse=klasse) + [""]
            if isinstance(knoten, ast.ClassDef):
                felder = list(self._felder(knoten, modul))
                if felder:
                    zeilen += felder + [""]
        return zeilen

    def _felder(self, klasse: ast.ClassDef, modul: Modul) -> Iterable[str]:
        """Die Felder einer Klasse mit ihrem Docstring oder ``#:``-Kommentar."""
        koerper = klasse.body
        for i, knoten in enumerate(koerper):
            if not isinstance(knoten, (ast.AnnAssign, ast.Assign)):
                continue
            ziel = knoten.target if isinstance(knoten, ast.AnnAssign) else knoten.targets[0]
            if not isinstance(ziel, ast.Name) or ziel.id.startswith("__"):
                continue
            text = _kommentar(modul, knoten)
            folgt = koerper[i + 1] if i + 1 < len(koerper) else None
            if (isinstance(folgt, ast.Expr) and isinstance(folgt.value, ast.Constant)
                    and isinstance(folgt.value.value, str)):
                text = " ".join(folgt.value.value.split())
            kopf = ziel.id
            if isinstance(knoten, ast.AnnAssign):
                kopf += f": {ast.unparse(knoten.annotation)}"
            wert = getattr(knoten, "value", None)
            if wert is not None:
                kopf += f" = {_kurz(ast.unparse(wert))}"
            yield f"- `{kopf}`" + (
                f" – {self._inline(text, modul, klasse=klasse.name)}" if text else "")

    def _konstanten(self, modul: Modul) -> List[str]:
        zeilen = []
        for knoten in modul.baum.body:
            if not isinstance(knoten, (ast.Assign, ast.AnnAssign)):
                continue
            ziel = knoten.target if isinstance(knoten, ast.AnnAssign) else knoten.targets[0]
            if not isinstance(ziel, ast.Name) or knoten.value is None:
                continue
            text = _kommentar(modul, knoten)
            if not (ziel.id.isupper() or text) or ziel.id.startswith("__"):
                continue
            zeilen.append(f"- `{ziel.id} = {_kurz(ast.unparse(knoten.value))}`"
                          + (f" – {self._inline(text, modul)}" if text else ""))
        return zeilen

    # -- Docstring -> Markdown -----------------------------------------------

    def _docstring(self, text: str, modul: Modul, *, ueberschriften: bool,
                   klasse: Optional[str] = None) -> List[str]:
        heraus: List[str] = []
        zeilen = text.split("\n")
        i = 0
        vorher = "leer"          # leer | text | ueberschrift
        code_folgt = False
        while i < len(zeilen):
            zeile = zeilen[i]
            if not zeile.strip():
                heraus.append("")
                vorher = "leer"
                i += 1
                continue
            einzug = len(zeile) - len(zeile.lstrip())
            if einzug and (code_folgt or vorher in ("leer", "ueberschrift")) \
                    and not _LISTE.match(zeile) and not _ist_fortsetzung(heraus):
                block, i = _block(zeilen, i)
                heraus += ["```" + ("python" if _ist_python(block) else ""), *block, "```"]
                vorher, code_folgt = "leer", False
                continue
            if einzug and vorher == "text" and not _LISTE.match(zeile) \
                    and not _ist_fortsetzung(heraus):
                # Eingerueckt direkt nach Text: der Absatz geht weiter.
                zeile = zeile.strip()
            m = _UEBERSCHRIFT.match(zeile) if einzug == 0 else None
            if m and _ist_ueberschrift(m):
                titel, rest, code_folgt = _ueberschrift(m)
                if ueberschriften:
                    heraus += ["", f"## {self._inline(titel, modul, roh=True, klasse=klasse)}", ""]
                else:
                    heraus += [f"**{self._inline(titel, modul, klasse=klasse)}**", ""]
                vorher = "ueberschrift"
                if rest:
                    heraus.append(self._inline(rest, modul, klasse=klasse))
                    vorher = "text"
                i += 1
                continue
            code_folgt = zeile.rstrip().endswith("::")
            if code_folgt:
                zeile = zeile.rstrip()[:-2].rstrip()
                zeile = zeile + ":" if zeile and not zeile.endswith(":") else zeile
            heraus.append(self._inline(zeile, modul, klasse=klasse) if zeile.strip() else "")
            vorher = "text"
            i += 1
        while heraus and not heraus[-1].strip():
            heraus.pop()
        while heraus and not heraus[0].strip():
            heraus.pop(0)
        return heraus

    def _inline(self, text: str, modul: Modul, *, roh: bool = False,
                klasse: Optional[str] = None) -> str:
        """Eine Zeile Docstring als Markdown: Code, Rollen als Links, der Rest maskiert."""
        teile = []
        stelle = 0
        muster = re.compile(f"{_ROLLE.pattern}|{_CODE.pattern}")
        for m in muster.finditer(text):
            teile.append(_maskieren(text[stelle:m.start()], am_anfang=not teile and not roh))
            if m.group(1) is not None:
                teile.append(self.verweis(m.group(1), modul, klasse))
            else:
                code = m.group(2)
                teile.append(f"`` {code} ``" if "`" in code else f"`{code}`")
            stelle = m.end()
        teile.append(_maskieren(text[stelle:], am_anfang=not teile and not roh))
        return "".join(teile)


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------


def _eintraege(baum: ast.Module) -> Iterable[Eintrag]:
    """Klassen, Funktionen und ihre Methoden -- oeffentlich, oder privat mit Docstring."""
    def zeigen(knoten) -> bool:
        name = knoten.name
        if name.startswith("__") and name.endswith("__"):
            return False
        return not name.startswith("_") or ast.get_docstring(knoten) is not None

    for knoten in baum.body:
        if isinstance(knoten, ast.ClassDef) and zeigen(knoten):
            yield Eintrag(knoten.name, knoten, 3)
            for methode in knoten.body:
                if isinstance(methode, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and zeigen(methode):
                    yield Eintrag(f"{knoten.name}.{methode.name}", methode, 4)
        elif isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)) and zeigen(knoten):
            yield Eintrag(knoten.name, knoten, 3)


def _signatur(knoten: ast.AST) -> List[str]:
    zeilen = [f"@{ast.unparse(d)}" for d in getattr(knoten, "decorator_list", [])]
    if isinstance(knoten, ast.ClassDef):
        basen = [ast.unparse(b) for b in knoten.bases]
        zeilen.append(f"class {knoten.name}" + (f"({', '.join(basen)})" if basen else ""))
    else:
        art = "async def" if isinstance(knoten, ast.AsyncFunctionDef) else "def"
        rueck = f" -> {ast.unparse(knoten.returns)}" if knoten.returns else ""
        zeilen.append(f"{art} {knoten.name}({ast.unparse(knoten.args)}){rueck}")
    return zeilen


def _kommentar(modul: Modul, knoten: ast.AST) -> str:
    """Die ``#:``-Zeilen direkt ueber einer Zuweisung, zu einem Satz verbunden."""
    zeilen = []
    i = knoten.lineno - 2
    while i >= 0:
        m = re.match(r"^\s*#:\s?(.*)$", modul.zeilen[i])
        if not m:
            break
        zeilen.insert(0, m.group(1))
        i -= 1
    return " ".join(z.strip() for z in zeilen if z.strip())


def _hat_konstante(modul: Modul, name: str) -> bool:
    """Ob ``name`` unter «Konstanten» steht -- dieselbe Auswahl wie dort."""
    for knoten in modul.baum.body:
        if isinstance(knoten, ast.AnnAssign):
            ziel = knoten.target
        elif isinstance(knoten, ast.Assign):
            ziel = knoten.targets[0]
        else:
            continue
        if isinstance(ziel, ast.Name) and ziel.id == name and knoten.value is not None:
            return (name.isupper() or bool(_kommentar(modul, knoten))) and not name.startswith("__")
    return False


def _kurz(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= WERTLAENGE else text[:WERTLAENGE - 1] + "…"


def _ist_ueberschrift(m: re.Match) -> bool:
    titel, rest = m.group("titel"), m.group("rest")
    if sum(z.isalpha() for z in titel) < 4:
        return False
    if rest[:1].islower() or rest[:1].isalnum():
        return False
    return (rest.strip() in ("", ":", "::", ".", "?")
            or rest.startswith(" -- ") or rest.startswith(" ("))


def _ueberschrift(m: re.Match) -> Tuple[str, str, bool]:
    """Titel, der Rest als Beginn des Absatzes, und ob ein Codeblock folgt."""
    titel, rest = m.group("titel"), m.group("rest").rstrip()
    code = rest.endswith("::")
    rest = rest[:-2] if code else rest.rstrip(":.")
    if rest.startswith(" ("):
        klammer = rest.find(")")
        if klammer >= 0 and not rest[klammer + 1:].strip(" :"):
            return f"{titel}{rest[:klammer + 1]}", "", code
    if rest.startswith(" -- "):
        schwanz = rest[4:]
        if schwanz == schwanz.upper():
            return f"{titel} – {schwanz.rstrip('?:.')}" + ("?" if schwanz.endswith("?") else ""), "", code
        return titel, schwanz + (":" if code else ""), code
    if m.group("rest").strip() == "?":
        titel += "?"
    return titel, rest.strip(), code


def _block(zeilen: List[str], i: int) -> Tuple[List[str], int]:
    """Ein eingerueckter Block ab ``i``, gemeinsam ausgerueckt -- Leerzeilen darin bleiben."""
    block = []
    while i < len(zeilen) and (not zeilen[i].strip() or zeilen[i][:1] in (" ", "\t")):
        block.append(zeilen[i])
        i += 1
    while block and not block[-1].strip():
        block.pop()
        i -= 1
    rand = min(len(z) - len(z.lstrip()) for z in block if z.strip())
    return [z[rand:] for z in block], i


def _ist_python(block: List[str]) -> bool:
    return bool(re.match(r"^(from |import |>>> |p\.|\w+(\.\w+)*\(|\w+ = \w+(\.\w+)*\()",
                         block[0]))


def _ist_fortsetzung(heraus: List[str]) -> bool:
    """Ob die letzte Zeile ein Listenpunkt ist -- dann gehoert Eingeruecktes zu ihm."""
    for zeile in reversed(heraus):
        if not zeile.strip():
            return False
        if _LISTE.match(zeile):
            return True
        if not zeile.startswith(" "):
            return False
    return False


def _maskieren(text: str, *, am_anfang: bool) -> str:
    """Was Markdown, Obsidian oder MathJax anders lesen wuerden."""
    text = text.replace("\\", "\\\\")
    for zeichen in ("$", "<", "|"):
        text = text.replace(zeichen, "\\" + zeichen)
    for doppelt in ("%%", "==", "[["):
        text = text.replace(doppelt, "\\" + doppelt[0] + "\\" + doppelt[1])
    if am_anfang:
        text = re.sub(r"^(\s*)([#>])", r"\1\\\2", text)
    return text


def _text(text: str) -> str:
    """Eine Kurzbeschreibung in einer Liste: ohne Rollen, maskiert."""
    text = _ROLLE.sub(lambda m: f"`{m.group(1).lstrip('~')}`", text)
    teile = re.split(r"(``.+?``)", text)
    return "".join(f"`{t[2:-2]}`" if t.startswith("``") else _maskieren(t, am_anfang=False)
                   for t in teile)
