"""
opencivil/core/einheiten.py -- Dimensionen, Einheiten und Groessen.

VERANTWORTUNG:
Stellt den physikalischen Zahlentyp des gesamten Toolkits bereit. Eine
``Groesse`` traegt immer ihren Wert *und* ihre Dimension mit sich. Rechnen mit
inkompatiblen Groessen (z.B. ``mm + MPa``) wirft sofort einen Fehler, statt
still eine falsche Zahl zu liefern.

Intern wird jede Groesse in SI-Basiseinheiten (m, kg, s, K) gespeichert. Die
Anzeige-Einheit ist reine Darstellung und beeinflusst das Resultat nie.

EMPIRISCHE NORMFORMELN:
Viele SIA-Formeln sind dimensionell inhomogen, z.B.

    tau_cd = 0.3 * sqrt(f_ck) / gamma_c        (SIA 262:2025, 2.4.2.4)

Hier ist stillschweigend vorausgesetzt, dass ``f_ck`` in N/mm^2 eingesetzt wird
und das Resultat in N/mm^2 herauskommt. Solche Formeln duerfen nicht ueber die
normale Arithmetik laufen. Dafuer gibt es :func:`empirisch`: dort muss man
explizit deklarieren, in welcher Einheit jeder Eingabewert einzusetzen ist und
welche Einheit das Resultat traegt. Damit wird die implizite Einheiten-Konvention
der Norm sichtbar, pruefbar und im Bericht darstellbar.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.einheiten import Groesse, MM, MPA, KN
    h = Groesse(300, MM)
    print(h.formatiert(0))            # '300'
    print((h * h).in_einheit(MM**2))  # 90000.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Union

Zahl = Union[int, float]


# ===========================================================================
# Dimension
# ===========================================================================


@dataclass(frozen=True)
class Dimension:
    """
    Physikalische Dimension als Exponentenvektor ueber den SI-Basisgroessen.

    Die Exponenten sind ``Fraction``, damit auch Wurzeln darstellbar bleiben
    (z.B. ``sqrt(Kraft/Flaeche)``). Das ist noetig, damit empirische Formeln
    nicht schon beim Zwischenschritt abstuerzen.
    """

    laenge: Fraction = Fraction(0)      # L, Meter
    masse: Fraction = Fraction(0)       # M, Kilogramm
    zeit: Fraction = Fraction(0)        # T, Sekunde
    temperatur: Fraction = Fraction(0)  # Theta, Kelvin

    def __post_init__(self) -> None:
        # Erlaubt die bequeme Konstruktion mit int/float und normalisiert auf Fraction.
        for feld in ("laenge", "masse", "zeit", "temperatur"):
            wert = getattr(self, feld)
            if not isinstance(wert, Fraction):
                object.__setattr__(self, feld, Fraction(wert).limit_denominator(1000))

    # -- Algebra ------------------------------------------------------------

    def __mul__(self, andere: "Dimension") -> "Dimension":
        return Dimension(
            self.laenge + andere.laenge,
            self.masse + andere.masse,
            self.zeit + andere.zeit,
            self.temperatur + andere.temperatur,
        )

    def __truediv__(self, andere: "Dimension") -> "Dimension":
        return Dimension(
            self.laenge - andere.laenge,
            self.masse - andere.masse,
            self.zeit - andere.zeit,
            self.temperatur - andere.temperatur,
        )

    def __pow__(self, exponent: Union[Zahl, Fraction]) -> "Dimension":
        e = exponent if isinstance(exponent, Fraction) else Fraction(exponent).limit_denominator(1000)
        return Dimension(
            self.laenge * e,
            self.masse * e,
            self.zeit * e,
            self.temperatur * e,
        )

    @property
    def ist_dimensionslos(self) -> bool:
        return self == DIMENSIONSLOS

    # -- Darstellung --------------------------------------------------------

    def __str__(self) -> str:
        if self.ist_dimensionslos:
            return "1"
        teile = []
        for zeichen, exponent in (
            ("L", self.laenge),
            ("M", self.masse),
            ("T", self.zeit),
            ("Theta", self.temperatur),
        ):
            if exponent == 0:
                continue
            teile.append(zeichen if exponent == 1 else f"{zeichen}^{exponent}")
        return "*".join(teile)

    def __repr__(self) -> str:
        return f"Dimension({self})"


DIMENSIONSLOS = Dimension()
LAENGE = Dimension(laenge=1)
MASSE = Dimension(masse=1)
ZEIT = Dimension(zeit=1)
TEMPERATUR = Dimension(temperatur=1)

FLAECHE = LAENGE**2
VOLUMEN = LAENGE**3
KRAFT = MASSE * LAENGE / ZEIT**2                 # N   = kg*m/s^2
SPANNUNG = KRAFT / FLAECHE                       # Pa  = N/m^2
MOMENT = KRAFT * LAENGE                          # Nm
KRAFT_PRO_LAENGE = KRAFT / LAENGE                # N/m
MOMENT_PRO_LAENGE = MOMENT / LAENGE              # Nm/m
DICHTE = MASSE / VOLUMEN                         # kg/m^3
FLAECHE_PRO_LAENGE = FLAECHE / LAENGE            # m^2/m
KRUEMMUNG = DIMENSIONSLOS / LAENGE               # 1/m


# ===========================================================================
# Einheit
# ===========================================================================


@dataclass(frozen=True)
class Einheit:
    """
    Eine benannte Einheit: Dimension plus Umrechnungsfaktor auf SI-Basis.

    ``faktor`` ist so definiert, dass gilt::

        wert_in_SI = wert_in_dieser_Einheit * faktor

    Einheiten lassen sich multiplizieren, dividieren und potenzieren, sodass
    zusammengesetzte Einheiten wie ``KN / M`` direkt entstehen. Zusammengesetzte
    Einheiten bekommen einen mechanisch erzeugten Namen; wo ein bestimmter Name
    gewuenscht ist (z.B. ``kNm/m``), wird die Einheit unten explizit definiert.
    """

    name: str
    """Maschinenlesbarer Name, zugleich Schluessel im Katalog: ``N/mm^2``."""

    dimension: Dimension
    faktor: float = 1.0
    latex: Optional[str] = None

    klebt: bool = False
    """
    Ob das Zeichen unmittelbar an der Zahl haengt, ohne schmalen Abstand.

    Der Regelfall ist der Abstand: ``30\\,\\mathrm{mm}``. Das Gradzeichen
    gehoert dagegen an die Zahl -- ``30°``, nicht ``30 °``.
    """

    beschriftung: Optional[str] = None
    """
    Lesbare Schreibweise fuer die Oberflaeche: ``N/mm²``.

    Der ``name`` bleibt ASCII, weil er als Schluessel dient und in IDs
    vorkommt. Wo eine Zahl ohne LaTeX-Satz neben ihrer Einheit steht -- in der
    Werteliste, an den Eingabefeldern --, gehoert die lesbare Form hin.
    Andernfalls stuende dort ``N/mm^2``, waehrend die Herleitung daneben
    ``N/mm²`` setzt.
    """

    def __post_init__(self) -> None:
        if self.latex is None:
            object.__setattr__(self, "latex", _name_zu_latex(self.name))
        if self.beschriftung is None:
            object.__setattr__(self, "beschriftung", _name_zu_text(self.name))

    # -- Algebra ------------------------------------------------------------

    def __mul__(self, andere: "Einheit") -> "Einheit":
        if andere.dimension.ist_dimensionslos and andere.faktor == 1.0:
            return self
        if self.dimension.ist_dimensionslos and self.faktor == 1.0:
            return andere
        return Einheit(
            name=f"{self.name}*{andere.name}",
            dimension=self.dimension * andere.dimension,
            faktor=self.faktor * andere.faktor,
            latex=rf"{self.latex}\,{andere.latex}",
            beschriftung=f"{self.beschriftung}·{andere.beschriftung}",
        )

    def __truediv__(self, andere: "Einheit") -> "Einheit":
        if andere.dimension.ist_dimensionslos and andere.faktor == 1.0:
            return self
        return Einheit(
            name=f"{self.name}/{andere.name}",
            dimension=self.dimension / andere.dimension,
            faktor=self.faktor / andere.faktor,
            latex=rf"{self.latex}/{andere.latex}",
            beschriftung=f"{self.beschriftung}/{andere.beschriftung}",
        )

    def __pow__(self, exponent: Zahl) -> "Einheit":
        if exponent == 1:
            return self
        return Einheit(
            name=f"{self.name}^{exponent}",
            dimension=self.dimension**exponent,
            faktor=self.faktor**exponent,
            latex=rf"{self.latex}^{{{_exponent_text(exponent)}}}",
            beschriftung=_name_zu_text(f"{self.beschriftung}^{exponent}"),
        )

    # -- Darstellung --------------------------------------------------------

    def __str__(self) -> str:
        return self.name

    def als_latex(self) -> str:
        """LaTeX-Fragment der Einheit, mit vorangestelltem schmalem Abstand."""
        if not self.name or self.name == "-":
            return ""
        return (self.latex or "") if self.klebt else rf"\," + (self.latex or "")


def _name_zu_latex(name: str) -> str:
    """Baut aus einem einfachen Einheitennamen ein aufrechtes LaTeX-Fragment."""
    if not name or name == "-":
        return ""
    if name.startswith("\\"):  # bereits ein LaTeX-Befehl, z.B. \%
        return name
    if "^" in name:
        basis, _, exponent = name.partition("^")
        return rf"\mathrm{{{basis}}}^{{{_exponent_text(exponent)}}}"
    return rf"\mathrm{{{name}}}"


#: Hochgestellte Ziffern, soweit es sie als eigenes Zeichen gibt.
_HOCHGESTELLT = {"1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
                 "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "0": "⁰"}


def _name_zu_text(name: str) -> str:
    """
    Macht aus dem ASCII-Namen die lesbare Schreibweise: ``mm^2`` -> ``mm²``.

    Nur die Potenzen, und nur solange jede Ziffer ein hochgestelltes Zeichen
    hat. Fuer alles Weitere -- ``‰`` etwa -- gibt die Einheit ihre
    ``beschriftung`` selbst an; mechanisch ableiten liesse sich das nicht.
    """
    if not name or name == "-":
        return ""
    basis, trenner, exponent = name.partition("^")
    if not trenner or not all(z in _HOCHGESTELLT for z in exponent):
        return name
    return basis + "".join(_HOCHGESTELLT[z] for z in exponent)


def _exponent_text(exponent: Any) -> str:
    if isinstance(exponent, float) and exponent.is_integer():
        return str(int(exponent))
    return str(exponent)


# -- Einheitenkatalog -------------------------------------------------------

EINHEITSLOS = Einheit("-", DIMENSIONSLOS, 1.0, latex="")
PROZENT = Einheit("%", DIMENSIONSLOS, 0.01, latex=r"\%")
PROMILLE = Einheit("promille", DIMENSIONSLOS, 0.001, latex="\\text{‰}",
                   beschriftung="‰")

# Laenge
M = Einheit("m", LAENGE, 1.0)
DM = Einheit("dm", LAENGE, 1e-1)
CM = Einheit("cm", LAENGE, 1e-2)
MM = Einheit("mm", LAENGE, 1e-3)
KM = Einheit("km", LAENGE, 1e3)

# Flaeche
M2 = Einheit("m^2", FLAECHE, 1.0)
CM2 = Einheit("cm^2", FLAECHE, 1e-4)
MM2 = Einheit("mm^2", FLAECHE, 1e-6)

# Kraft
N = Einheit("N", KRAFT, 1.0)
KN = Einheit("kN", KRAFT, 1e3)
MN = Einheit("MN", KRAFT, 1e6)

# Spannung
PA = Einheit("Pa", SPANNUNG, 1.0)
KPA = Einheit("kPa", SPANNUNG, 1e3)
MPA = Einheit("MPa", SPANNUNG, 1e6)
GPA = Einheit("GPa", SPANNUNG, 1e9)
N_PRO_MM2 = Einheit("N/mm^2", SPANNUNG, 1e6, latex=r"\mathrm{N}/\mathrm{mm}^{2}")
KN_PRO_M2 = Einheit("kN/m^2", SPANNUNG, 1e3, latex=r"\mathrm{kN}/\mathrm{m}^{2}")

# Moment
NM = Einheit("Nm", MOMENT, 1.0)
KNM = Einheit("kNm", MOMENT, 1e3)
MNM = Einheit("MNm", MOMENT, 1e6)

# Auf die Breite bezogene Groessen (Platten pro Laufmeter)
KN_PRO_M = Einheit("kN/m", KRAFT_PRO_LAENGE, 1e3, latex=r"\mathrm{kN}/\mathrm{m}")
KNM_PRO_M = Einheit("kNm/m", MOMENT_PRO_LAENGE, 1e3, latex=r"\mathrm{kNm}/\mathrm{m}")
MM2_PRO_M = Einheit("mm^2/m", FLAECHE_PRO_LAENGE, 1e-6, latex=r"\mathrm{mm}^{2}/\mathrm{m}")
PRO_M = Einheit("1/m", KRUEMMUNG, 1.0, latex=r"\mathrm{m}^{-1}", beschriftung="1/m")

# Masse und Dichte
KG = Einheit("kg", MASSE, 1.0)
T = Einheit("t", MASSE, 1e3)
KG_PRO_M3 = Einheit("kg/m^3", DICHTE, 1.0, latex=r"\mathrm{kg}/\mathrm{m}^{3}")

# Winkel (dimensionslos, aber mit Umrechnungsfaktor)
RAD = Einheit("rad", DIMENSIONSLOS, 1.0)
# Das Gradzeichen braucht eine Basis, an die es sich haengen kann: `\,^{\circ}`
# ist ein Exponent ohne davorstehendes Zeichen, und daran bricht KaTeX ab -- im
# Bericht stand dann der rohe Quelltext statt 30°. Die leere Gruppe ist diese
# Basis; `klebt` nimmt zugleich den schmalen Abstand weg, der vor einem
# Gradzeichen ohnehin nicht hingehoert.
GRAD = Einheit("Grad", DIMENSIONSLOS, math.pi / 180.0,
               latex=r"{}^{\circ}", beschriftung="°", klebt=True)

#: Alle benannten Einheiten, nach Namen auffindbar.
EINHEITEN: Dict[str, Einheit] = {
    e.name: e
    for e in (
        EINHEITSLOS, PROZENT, PROMILLE,
        M, DM, CM, MM, KM,
        M2, CM2, MM2,
        N, KN, MN,
        PA, KPA, MPA, GPA, N_PRO_MM2, KN_PRO_M2,
        NM, KNM, MNM,
        KN_PRO_M, KNM_PRO_M, MM2_PRO_M, PRO_M,
        KG, T, KG_PRO_M3,
        RAD, GRAD,
    )
}


def einheit(name: str) -> Einheit:
    """Sucht eine benannte Einheit im Katalog."""
    try:
        return EINHEITEN[name]
    except KeyError:
        raise UnbekannteEinheitFehler(
            f"Unbekannte Einheit '{name}'. Bekannt sind: {', '.join(sorted(EINHEITEN))}"
        ) from None


# ===========================================================================
# Fehler
# ===========================================================================


class EinheitenFehler(Exception):
    """Basisklasse fuer alle Einheiten- und Dimensionsfehler."""


class DimensionsFehler(EinheitenFehler):
    """Zwei Groessen mit unvertraeglichen Dimensionen wurden verknuepft."""


class UnbekannteEinheitFehler(EinheitenFehler):
    """Eine Einheit wurde ueber einen unbekannten Namen angefordert."""


# ===========================================================================
# Groesse
# ===========================================================================


class Groesse:
    """
    Ein physikalischer Zahlenwert mit Dimension.

    Der Wert wird intern immer in SI-Basiseinheiten gehalten (:attr:`si`).
    ``anzeige`` merkt sich lediglich, in welcher Einheit die Groesse dargestellt
    werden soll -- das Rechenergebnis haengt nie davon ab.

    Beispiele::

        h = Groesse(300, MM)
        b = Groesse(1.0, M)
        flaeche = h * b                    # Dimension L^2
        print(flaeche.in_einheit(MM2))     # 300000.0

        h + Groesse(30, MPA)               # -> DimensionsFehler
    """

    __slots__ = ("si", "anzeige")

    def __init__(self, wert: Zahl, anzeige: Einheit = EINHEITSLOS) -> None:
        if isinstance(wert, Groesse):
            raise TypeError(
                "Groesse(...) mit einer Groesse aufgerufen. Gemeint war vermutlich "
                "'.in_einheit(...)' oder '.als(...)'."
            )
        self.si: float = float(wert) * anzeige.faktor
        self.anzeige: Einheit = anzeige

    # -- Alternative Konstruktoren -----------------------------------------

    @classmethod
    def aus_si(cls, si_wert: Zahl, anzeige: Einheit) -> "Groesse":
        """Baut eine Groesse aus einem bereits in SI-Basis vorliegenden Wert."""
        g = cls.__new__(cls)
        g.si = float(si_wert)
        g.anzeige = anzeige
        return g

    # -- Zugriff ------------------------------------------------------------

    @property
    def dimension(self) -> Dimension:
        return self.anzeige.dimension

    def in_einheit(self, ziel: Einheit) -> float:
        """Gibt den Zahlenwert in der gewuenschten Einheit zurueck."""
        self._pruefe_dimension(ziel.dimension, "umrechnen nach")
        return self.si / ziel.faktor

    @property
    def zahl(self) -> float:
        """Zahlenwert in der aktuellen Anzeige-Einheit."""
        return self.si / self.anzeige.faktor

    def als(self, ziel: Einheit) -> "Groesse":
        """Gleiche physikalische Groesse, andere Anzeige-Einheit."""
        self._pruefe_dimension(ziel.dimension, "darstellen als")
        return Groesse.aus_si(self.si, ziel)

    # -- Arithmetik ---------------------------------------------------------

    def __add__(self, andere: "Groesse") -> "Groesse":
        andere = self._als_groesse(andere, "addieren")
        anzeige = self._vertraegliche_anzeige(andere, "addieren")
        return Groesse.aus_si(self.si + andere.si, anzeige)

    def __radd__(self, andere: Any) -> "Groesse":
        # Erlaubt sum(...) mit Startwert 0.
        return self.__add__(self._als_groesse(andere, "addieren"))

    def __sub__(self, andere: "Groesse") -> "Groesse":
        andere = self._als_groesse(andere, "subtrahieren")
        anzeige = self._vertraegliche_anzeige(andere, "subtrahieren")
        return Groesse.aus_si(self.si - andere.si, anzeige)

    def __rsub__(self, andere: Any) -> "Groesse":
        return self._als_groesse(andere, "subtrahieren").__sub__(self)

    def __mul__(self, andere: Union["Groesse", Zahl]) -> "Groesse":
        if isinstance(andere, (int, float)):
            return Groesse.aus_si(self.si * andere, self.anzeige)
        return Groesse.aus_si(self.si * andere.si, self.anzeige * andere.anzeige)

    def __rmul__(self, andere: Zahl) -> "Groesse":
        return self.__mul__(andere)

    def __truediv__(self, andere: Union["Groesse", Zahl]) -> "Groesse":
        if isinstance(andere, (int, float)):
            return Groesse.aus_si(self.si / andere, self.anzeige)
        return Groesse.aus_si(self.si / andere.si, self.anzeige / andere.anzeige)

    def __rtruediv__(self, andere: Zahl) -> "Groesse":
        kehrwert = Einheit(
            name=f"1/{self.anzeige.name}",
            dimension=DIMENSIONSLOS / self.dimension,
            faktor=1.0 / self.anzeige.faktor,
            latex=rf"1/{self.anzeige.latex}",
        )
        return Groesse.aus_si(andere / self.si, kehrwert)

    def __pow__(self, exponent: Zahl) -> "Groesse":
        return Groesse.aus_si(self.si**exponent, self.anzeige**exponent)

    def __neg__(self) -> "Groesse":
        return Groesse.aus_si(-self.si, self.anzeige)

    def __pos__(self) -> "Groesse":
        return self

    def __abs__(self) -> "Groesse":
        return Groesse.aus_si(abs(self.si), self.anzeige)

    def wurzel(self) -> "Groesse":
        """Quadratwurzel. Halbiert die Dimensionsexponenten."""
        return self ** 0.5

    # -- Vergleiche ---------------------------------------------------------

    def __eq__(self, andere: object) -> bool:
        if not isinstance(andere, Groesse):
            return NotImplemented
        return self.dimension == andere.dimension and self.si == andere.si

    def __hash__(self) -> int:
        return hash((self.si, self.dimension))

    def __lt__(self, andere: "Groesse") -> bool:
        self._pruefe_dimension(andere.dimension, "vergleichen")
        return self.si < andere.si

    def __le__(self, andere: "Groesse") -> bool:
        self._pruefe_dimension(andere.dimension, "vergleichen")
        return self.si <= andere.si

    def __gt__(self, andere: "Groesse") -> bool:
        self._pruefe_dimension(andere.dimension, "vergleichen")
        return self.si > andere.si

    def __ge__(self, andere: "Groesse") -> bool:
        self._pruefe_dimension(andere.dimension, "vergleichen")
        return self.si >= andere.si

    def nahe(self, andere: "Groesse", rel: float = 1e-9, abs_: float = 0.0) -> bool:
        """Toleranter Vergleich -- fuer Tests und Iterationsabbrueche."""
        self._pruefe_dimension(andere.dimension, "vergleichen")
        return math.isclose(self.si, andere.si, rel_tol=rel, abs_tol=abs_)

    # -- Formatierung -------------------------------------------------------

    def formatiert(self, stellen: int = 2, einheit_: Optional[Einheit] = None) -> str:
        """
        Formatiert den Zahlenwert (ohne Einheit) mit fester Nachkommastellenzahl.

        Nachlaufende Nullen werden entfernt, damit ``18.70`` als ``18.7``
        erscheint -- so wie es im Bericht gelesen werden soll.
        """
        ziel = einheit_ or self.anzeige
        wert = self.in_einheit(ziel)
        text = f"{wert:.{max(stellen, 0)}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        # Was auf null rundet, hat kein Vorzeichen: «-0» sieht nach etwas aus.
        return "0" if text in ("", "-0") else text

    def als_latex(self, stellen: int = 2, einheit_: Optional[Einheit] = None) -> str:
        """Formatierter Zahlenwert samt Einheit als LaTeX-Fragment."""
        ziel = einheit_ or self.anzeige
        return f"{self.formatiert(stellen, ziel)}{ziel.als_latex()}"

    def __str__(self) -> str:
        einheit_text = f" {self.anzeige.name}" if self.anzeige.name not in ("", "-") else ""
        return f"{self.formatiert(3)}{einheit_text}"

    def __repr__(self) -> str:
        return f"Groesse({self.formatiert(6)}, {self.anzeige.name})"

    def __format__(self, spezifikation: str) -> str:
        if not spezifikation:
            return str(self)
        return format(self.zahl, spezifikation)

    def __float__(self) -> float:
        """
        Nur fuer dimensionslose Groessen erlaubt.

        Bewusst restriktiv: ein stillschweigendes ``float(kraft)`` wuerde die
        Einheit verlieren und ist fast immer ein Fehler. Fuer bewusste
        Umrechnung gibt es :meth:`in_einheit`.
        """
        if not self.dimension.ist_dimensionslos:
            raise DimensionsFehler(
                f"Groesse mit Dimension {self.dimension} laesst sich nicht direkt "
                f"in eine Zahl umwandeln. Bitte '.in_einheit(...)' verwenden."
            )
        return self.si

    # -- Intern -------------------------------------------------------------

    def _pruefe_dimension(self, andere: Dimension, aktion: str) -> None:
        """Strenge Dimensionspruefung -- fuer Vergleiche und Umrechnungen."""
        if self.dimension != andere:
            raise DimensionsFehler(
                f"Kann Groessen mit unvertraeglichen Dimensionen nicht {aktion}: "
                f"{self.dimension} (Anzeige {self.anzeige.name}) gegen {andere}."
            )

    def _vertraegliche_anzeige(self, andere: "Groesse", aktion: str) -> Einheit:
        """
        Prueft Addierbarkeit und waehlt die Anzeige-Einheit des Resultats.

        Eine dimensionslose Null gilt als neutrales Element und darf zu jeder
        Groesse addiert werden -- sonst waere ``summe([])`` oder das Aufsummieren
        einer anfangs leeren Liste unnoetig umstaendlich. Die Anzeige-Einheit
        kommt dann vom dimensionsbehafteten Operanden.
        """
        if self.dimension == andere.dimension:
            return self.anzeige
        if andere.si == 0.0 and andere.dimension.ist_dimensionslos:
            return self.anzeige
        if self.si == 0.0 and self.dimension.ist_dimensionslos:
            return andere.anzeige
        raise DimensionsFehler(
            f"Kann Groessen mit unvertraeglichen Dimensionen nicht {aktion}: "
            f"{self.dimension} (Anzeige {self.anzeige.name}) gegen "
            f"{andere.dimension} (Anzeige {andere.anzeige.name})."
        )

    @staticmethod
    def _als_groesse(wert: Any, aktion: str) -> "Groesse":
        if isinstance(wert, Groesse):
            return wert
        if isinstance(wert, (int, float)):
            if wert == 0:
                # 0 ist dimensionsneutral und darf zu allem addiert werden.
                return Groesse(0.0, EINHEITSLOS)
            raise DimensionsFehler(
                f"Kann blanke Zahl {wert} nicht mit einer Groesse {aktion}. "
                f"Bitte mit Einheit angeben, z.B. Groesse({wert}, MM)."
            )
        raise TypeError(f"Kann {type(wert).__name__} nicht mit einer Groesse {aktion}.")


# -- Bequeme Konstruktoren --------------------------------------------------


def null(anzeige: Einheit = EINHEITSLOS) -> Groesse:
    """Nullgroesse in der gewuenschten Einheit."""
    return Groesse(0.0, anzeige)


def summe(groessen: Iterable[Groesse], anzeige: Optional[Einheit] = None) -> Groesse:
    """
    Summiert Groessen und liefert bei leerer Eingabe eine passende Null.

    ``sum()`` von Python startet bei ``0`` und funktioniert deshalb nicht
    zuverlaessig mit Groessen.
    """
    ergebnis: Optional[Groesse] = None
    for g in groessen:
        ergebnis = g if ergebnis is None else ergebnis + g
    if ergebnis is None:
        return null(anzeige or EINHEITSLOS)
    return ergebnis.als(anzeige) if anzeige else ergebnis


# ===========================================================================
# Empirische Normformeln
# ===========================================================================


@dataclass(frozen=True)
class EmpirischeEinsetzung:
    """Protokolliert, in welcher Einheit ein Wert in eine Normformel einging."""

    name: str
    groesse: Groesse
    erwartete_einheit: Einheit

    @property
    def zahlenwert(self) -> float:
        return self.groesse.in_einheit(self.erwartete_einheit)


@dataclass(frozen=True)
class EmpirischesErgebnis:
    """Resultat einer empirischen Formel samt der getroffenen Annahmen."""

    wert: Groesse
    einsetzungen: Tuple[EmpirischeEinsetzung, ...]
    ergebnis_einheit: Einheit

    def annahmen_text(self) -> str:
        """Einzeiler fuer den Bericht: welche Einheiten vorausgesetzt wurden."""
        teile = [f"{e.name} in {e.erwartete_einheit.beschriftung}" for e in self.einsetzungen]
        return (
            f"Empirische Formel -- eingesetzt werden {', '.join(teile)}; "
            f"das Resultat ist in {self.ergebnis_einheit.beschriftung} zu lesen."
        )

    def annahmen_latex(self) -> str:
        teile = [
            rf"{e.name}\ \text{{in}}\ {e.erwartete_einheit.latex}"
            for e in self.einsetzungen
        ]
        return (
            r"\text{empirisch, mit }"
            + r",\ ".join(teile)
            + r"\text{; Resultat in }"
            + (self.ergebnis_einheit.latex or "-")
        )


def empirisch(
    funktion: Callable[..., float],
    *,
    ergebnis: Einheit,
    **eingaben: Tuple[Groesse, Einheit],
) -> EmpirischesErgebnis:
    """
    Wertet eine dimensionell inhomogene Normformel kontrolliert aus.

    Jede Eingabe wird als Paar ``(Groesse, erwartete Einheit)`` uebergeben. Die
    Groesse wird in genau diese Einheit umgerechnet (mit Dimensionspruefung!),
    als blanke Zahl in ``funktion`` eingesetzt, und das Resultat bekommt die
    deklarierte Ergebnis-Einheit.

    So bleibt die Einheiten-Konvention der Norm explizit und nachvollziehbar,
    statt als unsichtbare Annahme im Code zu verschwinden.

    Beispiel -- SIA 262:2025, 2.4.2.4::

        erg = empirisch(
            lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
            ergebnis=N_PRO_MM2,
            f_ck=(f_ck_groesse, N_PRO_MM2),
            gamma_c=(gamma_c_groesse, EINHEITSLOS),
        )
        print(erg.wert)            # z.B. '1.0 N/mm^2'
        print(erg.annahmen_text())
    """
    einsetzungen = []
    zahlenwerte: Dict[str, float] = {}
    for name, paar in eingaben.items():
        if not (isinstance(paar, tuple) and len(paar) == 2):
            raise TypeError(
                f"Eingabe '{name}' muss als Paar (Groesse, erwartete Einheit) "
                f"uebergeben werden, erhalten: {paar!r}"
            )
        groesse, erwartete = paar
        if not isinstance(groesse, Groesse):
            raise TypeError(f"Eingabe '{name}' ist keine Groesse, sondern {type(groesse).__name__}.")
        einsetzung = EmpirischeEinsetzung(name=name, groesse=groesse, erwartete_einheit=erwartete)
        # in_einheit() prueft die Dimension und wirft bei Unvertraeglichkeit.
        zahlenwerte[name] = einsetzung.zahlenwert
        einsetzungen.append(einsetzung)

    roh = funktion(**zahlenwerte)
    return EmpirischesErgebnis(
        wert=Groesse(roh, ergebnis),
        einsetzungen=tuple(einsetzungen),
        ergebnis_einheit=ergebnis,
    )
