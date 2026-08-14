"""
civil_toolkit/engine/material_engine.py – Material definitions and calculations.

RESPONSIBILITY:
Single source of truth for all material properties and code-based equations
for construction materials (concrete, reinforcing steel per SIA 262:2025).
Transforms material definitions (e.g. C30/37) into complete sets of
MyVar instances used by other engines (e.g. plate_engine).

USABLE STANDALONE:
    from civil_toolkit.engine.material_engine import get_material_vars, create_default_properties
    vars = get_material_vars(mat_dict)
    print(vars['f_cd'].to_latex_equation())
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import sympy as sp

from civil_toolkit.math_engine import MyVar
from civil_toolkit.engine.types import (
    EditorConfig, ReportExtraDef, Material, MaterialType,
    ConcreteGrade, SteelGrade, ConcreteTemplate, SteelTemplate,
    VarGroup, VarId, Unit,
)

# =============================================================================
# TEMPLATES – Standardised norm values per grade
# =============================================================================

#: Concrete grade templates per SIA 262:2025:3.1.2.2.7.
BETON_VORLAGEN: Dict[ConcreteGrade, ConcreteTemplate] = {
    ConcreteGrade.C12_15: ConcreteTemplate(fck=12, fctm=1.6),
    ConcreteGrade.C16_20: ConcreteTemplate(fck=16, fctm=1.9),
    ConcreteGrade.C20_25: ConcreteTemplate(fck=20, fctm=2.2),
    ConcreteGrade.C25_30: ConcreteTemplate(fck=25, fctm=2.6),
    ConcreteGrade.C30_37: ConcreteTemplate(fck=30, fctm=2.9),
    ConcreteGrade.C35_45: ConcreteTemplate(fck=35, fctm=3.2),
    ConcreteGrade.C40_50: ConcreteTemplate(fck=40, fctm=3.5),
    ConcreteGrade.C45_55: ConcreteTemplate(fck=45, fctm=3.8),
    ConcreteGrade.C50_60: ConcreteTemplate(fck=50, fctm=4.1),
}

#: Steel grade templates per SIA 262:2025:3.2.2.3.
STAHL_VORLAGEN: Dict[SteelGrade, SteelTemplate] = {
    SteelGrade.B500A: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=2.5, eps_ud=2.0),
    SteelGrade.B500B: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=5.0, eps_ud=4.5),
    SteelGrade.B500C: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=7.5, eps_ud=6.5),
    SteelGrade.B700B: SteelTemplate(fyk=700, fyk_minus=700, eps_uk=5.0, eps_ud=4.5),
    SteelGrade.STAHL_II: SteelTemplate(fyk=345, fyk_minus=345, eps_uk=5.0, eps_ud=4.5),
}

# =============================================================================
# SYMBOLS
# =============================================================================

class ConcreteSymbols:
    f_ck = sp.Symbol(r"f_{ck}")
    gamma_c = sp.Symbol(r"\gamma_c")
    f_cm = sp.Symbol(r"f_{cm}")
    k_e = sp.Symbol(r"k_e")
    gamma_cE = sp.Symbol(r"\gamma_{cE}")
    E_cm = sp.Symbol(r"E_{cm}")
    eta_fc = sp.Symbol(r"\eta_{fc}")
    E_cd = sp.Symbol(r"E_{cd}")
    f_cd = sp.Symbol(r"f_{cd}")

class SteelSymbols:
    f_yk = sp.Symbol(r"f_{yk}")
    f_yk_minus = sp.Symbol(r"f_{yk}^{-}")
    gamma_s = sp.Symbol(r"\gamma_s")

# =============================================================================
# TEMPLATES – Standardised norm values per grade
# =============================================================================

#: Concrete grade templates per SIA 262:2025:3.1.2.2.7.
BETON_VORLAGEN: Dict[ConcreteGrade, ConcreteTemplate] = {
    ConcreteGrade.C12_15: ConcreteTemplate(fck=12, fctm=1.6),
    ConcreteGrade.C16_20: ConcreteTemplate(fck=16, fctm=1.9),
    ConcreteGrade.C20_25: ConcreteTemplate(fck=20, fctm=2.2),
    ConcreteGrade.C25_30: ConcreteTemplate(fck=25, fctm=2.6),
    ConcreteGrade.C30_37: ConcreteTemplate(fck=30, fctm=2.9),
    ConcreteGrade.C35_45: ConcreteTemplate(fck=35, fctm=3.2),
    ConcreteGrade.C40_50: ConcreteTemplate(fck=40, fctm=3.5),
    ConcreteGrade.C45_55: ConcreteTemplate(fck=45, fctm=3.8),
    ConcreteGrade.C50_60: ConcreteTemplate(fck=50, fctm=4.1),
}

#: Steel grade templates per SIA 262:2025:3.2.2.3.
STAHL_VORLAGEN: Dict[SteelGrade, SteelTemplate] = {
    SteelGrade.B500A: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=2.5, eps_ud=2.0),
    SteelGrade.B500B: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=5.0, eps_ud=4.5),
    SteelGrade.B500C: SteelTemplate(fyk=500, fyk_minus=500, eps_uk=7.5, eps_ud=6.5),
    SteelGrade.B700B: SteelTemplate(fyk=700, fyk_minus=700, eps_uk=5.0, eps_ud=4.5),
    SteelGrade.STAHL_II: SteelTemplate(fyk=345, fyk_minus=345, eps_uk=5.0, eps_ud=4.5),
}

# =============================================================================
# CONCRETE – Variable definitions
# =============================================================================

BETON_VARIABLEN: List[MyVar] = [
    MyVar(
        id=VarId.F_CK,
        symbol="f_{ck}",
        unit=Unit.MPA,
        description="Charakteristische Zylinderdruckfestigkeit",
        reference="SIA 262:2025:3.1.2.2.7",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.5, row=0),
    ),
    MyVar(
        id=VarId.GAMMA_C,
        symbol=r"\gamma_c",
        unit=Unit.NONE,
        description="Teilsicherheitsbeiwert Beton",
        reference="SIA 262:2025:2.4.2.6",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.05, row=0),
    ),
    MyVar(
        id=VarId.F_CTM,
        symbol="f_{ctm}",
        unit=Unit.MPA,
        description="Mittlere Zugfestigkeit",
        reference="SIA 262:2025:3.1.2.2.7",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.1, row=1),
    ),
    MyVar(
        id=VarId.EPS_C1D,
        symbol=r"\epsilon_{c1d}",
        unit=Unit.NONE,
        description="Dehnungsgrenze Parabel-Beziehung",
        reference="SIA 262:2025:4.2.1.4",
        precision=4,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.0001, row=2),
    ),
    MyVar(
        id=VarId.EPS_C2D,
        symbol=r"\epsilon_{c2d}",
        unit=Unit.NONE,
        description="Bruchdehnungsgrenze Beton",
        reference="SIA 262:2025:4.2.1.4",
        precision=4,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.0001, row=2),
    ),
    MyVar(
        id=VarId.TAU_CD,
        symbol=r"\tau_{cd}",
        unit=Unit.MPA,
        description="Bemessungswert der Schubfestigkeit",
        reference="SIA 262:2025:2.4.2.4",
        precision=2,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.01),
        calc_fn=lambda deps: 0.3 * math.sqrt(deps["f_ck"].value) / deps["gamma_c"].value,
        sympy_expr=sp.Rational(3, 10) * sp.sqrt(ConcreteSymbols.f_ck) / ConcreteSymbols.gamma_c,
        sympy_symbol_map={"f_ck": ConcreteSymbols.f_ck, "gamma_c": ConcreteSymbols.gamma_c},
        dep_ids=[VarId.F_CK, VarId.GAMMA_C],
    ),
    MyVar(
        id=VarId.F_CM,
        symbol="f_{cm}",
        unit=Unit.MPA,
        description="Mittlere Zylinderdruckfestigkeit",
        reference="SIA 262:2025:3.1.2.2.2",
        precision=2,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.5),
        calc_fn=lambda deps: deps["f_ck"].value + 8,
        formula_template="{f_ck} + 8\\,\\text{MPa}",
        dep_ids=[VarId.F_CK],
    ),
    MyVar(
        id=VarId.K_E,
        symbol="k_e",
        unit=Unit.NONE,
        description="Aggregate Koeffizient",
        reference="SIA 262:2025:3.1.2.3.3",
        precision=0,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=100),
        calc_fn=lambda deps: 10000,
    ),
    MyVar(
        id=VarId.GAMMA_CE,
        symbol=r"\gamma_{cE}",
        unit=Unit.NONE,
        description="Teilsicherheitsbeiwert für E-Modul",
        reference="SIA 262:2025:4.2.1.15",
        precision=2,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.05),
        calc_fn=lambda deps: 1.0,
    ),
    MyVar(
        id=VarId.E_CM,
        symbol="E_{cm}",
        unit=Unit.MPA,
        description="Elastizitätsmodul",
        reference="SIA 262:2025:3.1.2.3.3",
        precision=0,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=500),
        calc_fn=lambda deps: round(deps["k_e"].value * (deps["f_cm"].value ** (1 / 3))),
        sympy_expr=ConcreteSymbols.k_e * ConcreteSymbols.f_cm ** sp.Rational(1, 3),
        sympy_symbol_map={"k_e": ConcreteSymbols.k_e, "f_cm": ConcreteSymbols.f_cm},
        dep_ids=[VarId.K_E, VarId.F_CM],
    ),
    MyVar(
        id=VarId.E_CD,
        symbol="E_{cd}",
        unit=Unit.MPA,
        description="Bemessungswert des Elastizitätsmoduls",
        reference="SIA 262:2025:4.2.1.15",
        precision=0,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=500),
        calc_fn=lambda deps: round(deps["E_cm"].value / deps["gamma_cE"].value),
        sympy_expr=ConcreteSymbols.E_cm / ConcreteSymbols.gamma_cE,
        sympy_symbol_map={"E_cm": ConcreteSymbols.E_cm, "gamma_cE": ConcreteSymbols.gamma_cE},
        dep_ids=[VarId.E_CM, VarId.GAMMA_CE],
    ),
    MyVar(
        id=VarId.ETA_FC,
        symbol=r"\eta_{fc}",
        unit=Unit.NONE,
        description="Beiwert Festigkeitsminderung",
        reference="SIA 262:2025:2.4.2.3",
        precision=3,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.001),
        calc_fn=lambda deps: min((40 / deps["f_ck"].value) ** (1 / 3), 1.0),
        formula_template=r"\min\left[\left(\frac{40\,\text{MPa}}{{f_ck}}\right)^{1/3},\; 1.0\right]",
        dep_ids=[VarId.F_CK],
    ),
    MyVar(
        id=VarId.F_CD,
        symbol="f_{cd}",
        unit=Unit.MPA,
        description="Bemessungswert der Druckfestigkeit",
        reference="SIA 262:2025:2.4.2.3",
        precision=1,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.1),
        calc_fn=lambda deps: round(deps["eta_fc"].value * deps["f_ck"].value / deps["gamma_c"].value, 1),
        sympy_expr=ConcreteSymbols.eta_fc * ConcreteSymbols.f_ck / ConcreteSymbols.gamma_c,
        sympy_symbol_map={"eta_fc": ConcreteSymbols.eta_fc, "f_ck": ConcreteSymbols.f_ck, "gamma_c": ConcreteSymbols.gamma_c},
        dep_ids=[VarId.ETA_FC, VarId.F_CK, VarId.GAMMA_C],
    ),
    MyVar(
        id=VarId.K_SIGMA,
        symbol=r"k_{\sigma}",
        unit=Unit.NONE,
        description="Krümmungsbeiwert der Spannungs-Dehnungs-Linie",
        reference="SIA 262:2025:4.2.1.6",
        precision=3,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=0.01),
        calc_fn=lambda deps: deps["E_cd"].value / (400 * deps["f_cd"].value),
        sympy_expr=ConcreteSymbols.E_cd / (400 * ConcreteSymbols.f_cd),
        sympy_symbol_map={"E_cd": ConcreteSymbols.E_cd, "f_cd": ConcreteSymbols.f_cd},
        dep_ids=[VarId.E_CD, VarId.F_CD],
    ),
]

# =============================================================================
# STEEL – Variable definitions
# =============================================================================

STAHL_VARIABLEN: List[MyVar] = [
    MyVar(
        id=VarId.F_YK,
        symbol="f_{yk}",
        unit=Unit.MPA,
        description="Charakteristische Streckgrenze",
        reference="SIA 262:2025:3.2.2.3",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=5, row=0),
    ),
    MyVar(
        id=VarId.F_YK_MINUS,
        symbol="f_{yk}^{-}",
        unit=Unit.MPA,
        description="Charakteristische Streckgrenze (Druck)",
        reference="SIA 262:2025:3.2.2.3",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=5, row=0),
    ),
    MyVar(
        id=VarId.E_S,
        symbol="E_s",
        unit=Unit.MPA,
        description="Elastizitätsmodul Stahl",
        reference="SIA 262:2025:3.2.2.4",
        precision=0,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=1000, row=1),
    ),
    MyVar(
        id=VarId.GAMMA_S,
        symbol=r"\gamma_s",
        unit=Unit.NONE,
        description="Teilsicherheitsbeiwert Stahl",
        reference="SIA 262:2025:2.4.2.6",
        precision=2,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.05, row=1),
    ),
    MyVar(
        id=VarId.EPS_UK,
        symbol=r"\epsilon_{uk}",
        unit=Unit.PERCENT,
        description="Dehnung bei Höchstlast",
        reference="SIA 262:2025:3.2.2.3",
        precision=1,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.1, row=2),
    ),
    MyVar(
        id=VarId.EPS_UD,
        symbol=r"\epsilon_{ud}",
        unit=Unit.PERCENT,
        description="Bemessungswert der Dehnung bei Höchstlast",
        reference="SIA 262:2025:4.2.2.1",
        precision=1,
        fundamental=True,
        editor=EditorConfig(group=VarGroup.BASIS, step=0.1, row=2),
    ),
    MyVar(
        id=VarId.F_YD,
        symbol="f_{yd}",
        unit=Unit.MPA,
        description="Bemessungswert der Streckgrenze",
        reference="SIA 262:2025:2.4.2.5",
        precision=0,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=1),
        calc_fn=lambda deps: round(deps["f_yk"].value / deps["gamma_s"].value),
        sympy_expr=SteelSymbols.f_yk / SteelSymbols.gamma_s,
        sympy_symbol_map={"f_yk": SteelSymbols.f_yk, "gamma_s": SteelSymbols.gamma_s},
        dep_ids=[VarId.F_YK, VarId.GAMMA_S],
    ),
    MyVar(
        id=VarId.F_YD_MINUS,
        symbol="f_{yd}^{-}",
        unit=Unit.MPA,
        description="Bemessungswert der Druck-Streckgrenze",
        reference="SIA 262:2025:2.4.2.5",
        precision=0,
        fundamental=False,
        editor=EditorConfig(group=VarGroup.BERECHNET, step=1),
        calc_fn=lambda deps: round(deps["f_yk_minus"].value / deps["gamma_s"].value),
        sympy_expr=SteelSymbols.f_yk_minus / SteelSymbols.gamma_s,
        sympy_symbol_map={"f_yk_minus": SteelSymbols.f_yk_minus, "gamma_s": SteelSymbols.gamma_s},
        dep_ids=[VarId.F_YK_MINUS, VarId.GAMMA_S],
    ),
]

# =============================================================================
# REPORT EXTRAS – Additional report items (formulas, diagrams)
# =============================================================================

BETON_EXTRAS: List[ReportExtraDef] = [
    ReportExtraDef(
        id="parabola_formula",
        type="formula",
        title="Parabel-Rechteck-Beziehung Formel",
        reference="SIA 262:2025:4.2.1.6",
        dependencies=["f_cd", "eps_c1d", "eps_c2d", "k_sigma"],
        latex=(
            r"\sigma_{c} = \begin{cases}"
            r" f_{cd} \cdot \frac{k_{\sigma} \cdot \eta - \eta^2}{1 + (k_{\sigma} - 2) \cdot \eta}"
            r" & \text{für } 0 \le \epsilon_c \le \epsilon_{c1d} \text{ mit } \eta = \frac{\epsilon_c}{\epsilon_{c1d}} \\"
            r" f_{cd} & \text{für } \epsilon_{c1d} < \epsilon_c \le \epsilon_{c2d}"
            r" \end{cases}"
        ),
    ),
    ReportExtraDef(
        id="parabola_diagram",
        type="diagram",
        diagram_type="parabola",
        title="Spannungs-Dehnungs-Diagramm",
        reference="SIA 262:2025:4.2.1.6 / 4.2.1.4",
        dependencies=["f_cd", "eps_c1d", "eps_c2d", "k_sigma"],
    ),
]

STAHL_EXTRAS: List[ReportExtraDef] = [
    ReportExtraDef(
        id="steel_diagram",
        type="diagram",
        diagram_type="steel",
        title="Spannungs-Dehnungs-Beziehung für Betonstahl",
        reference="SIA 262:2025:4.2.2.4",
        dependencies=["f_yd", "f_yd_minus", "E_s", "eps_ud"],
    ),
]

# =============================================================================
# PUBLIC API
# =============================================================================


def get_variable_defs(mat_type: MaterialType) -> List[MyVar]:
    """Returns the variable definition list for a material type."""
    return BETON_VARIABLEN if mat_type == MaterialType.CONCRETE else STAHL_VARIABLEN


def get_report_extras(mat_type: MaterialType) -> List[ReportExtraDef]:
    """Returns the report extras for a material type."""
    return BETON_EXTRAS if mat_type == MaterialType.CONCRETE else STAHL_EXTRAS


def get_var_id_to_prop(mat_type: MaterialType) -> Dict[str, str]:
    """Returns a mapping of variable ID → storage key (now the same as ID)."""
    return {str(d.id): str(d.id) for d in get_variable_defs(mat_type)}


def get_all_property_keys(mat_type: MaterialType) -> List[str]:
    """Returns all property keys for a material type (vars + extras)."""
    var_keys = [str(d.id) for d in get_variable_defs(mat_type)]
    extra_keys = [e.id for e in get_report_extras(mat_type)]
    return var_keys + extra_keys


def get_material_vars(mat: Material) -> Dict[str, MyVar]:
    """
    Builds and returns all MyVar instances for a material.

    Parameters
    ----------
    mat : Material
        Material pydantic model.

    Returns
    -------
    dict
        Mapping of variable ID → MyVar (e.g. ``'f_cd'`` → MyVar).
    """
    defs = get_variable_defs(mat.type)
    props = mat.properties
    mat_id = mat.id
    vars_: Dict[str, MyVar] = {}

    # First pass: create all MyVars
    for d in defs:
        is_fundamental = d.fundamental
        has_calc = d.calc_fn is not None

        var = MyVar(
            id=f"{d.id}_{mat_id}",
            symbol=d.symbol,
            unit=d.unit,
            description=d.description,
            value=props.get(str(d.id)),
            fundamental=is_fundamental or not has_calc,
            overridden=props.get(str(d.id) + "_overridden", False),
            calc_fn=d.calc_fn,
            sympy_expr=d.sympy_expr,
            sympy_symbol_map=d.sympy_symbol_map or {},
            formula_template=d.formula_template,
            precision=d.precision,
            reference=d.reference,
        )
        var.material_id = mat_id
        var.prop = str(d.id)  # storage key now equals the VarId string
        var.active = not props.get(str(d.id) + "_inactive", False)
        vars_[d.id] = var

    # Second pass: wire up dependencies
    for d in defs:
        var = vars_[d.id]
        if not var.fundamental:
            dep_ids = d.dep_ids
            var.dependencies = {dep_id: vars_[dep_id] for dep_id in dep_ids if dep_id in vars_}

    return vars_


def create_default_properties(mat_type: str, grade: str) -> Dict[str, Any]:
    """
    Creates the default property dict for a new material of the given type and grade.
    """
    defs = get_variable_defs(mat_type)

    if mat_type == MaterialType.CONCRETE:
        try:
            grade_enum = ConcreteGrade(grade)
        except ValueError:
            raise ValueError(f"Unbekannte Betonsorte '{grade}'. Verfügbare Vorlagen: {[g.value for g in ConcreteGrade]}")
        vorlage = BETON_VORLAGEN[grade_enum]
        props: Dict[str, Any] = {
            str(VarId.F_CK):    vorlage.fck,
            str(VarId.F_CTM):   vorlage.fctm,
            str(VarId.GAMMA_C): 1.5,
            str(VarId.EPS_C1D): 0.002,
            str(VarId.EPS_C2D): 0.0035,
            "simplified":       True,
        }
    elif mat_type == MaterialType.STEEL:
        try:
            grade_enum = SteelGrade(grade)
        except ValueError:
            raise ValueError(f"Unbekannte Stahlsorte '{grade}'. Verfügbare Vorlagen: {[g.value for g in SteelGrade]}")
        vorlage = STAHL_VORLAGEN[grade_enum]
        props = {
            str(VarId.F_YK):       vorlage.fyk,
            str(VarId.F_YK_MINUS): vorlage.fyk_minus,
            str(VarId.E_S):        200000,
            str(VarId.GAMMA_S):    1.15,
            str(VarId.EPS_UK):     vorlage.eps_uk,
            str(VarId.EPS_UD):     vorlage.eps_ud,
        }
    else:
        raise ValueError(f"Unbekannter Materialtyp '{mat_type}'. Gültige Typen: 'concrete', 'steel'")

    # Initialise computed properties to null with override=False
    for d in defs:
        if d.editor.group == VarGroup.BERECHNET:
            props[str(d.id)] = None
            props[str(d.id) + "_overridden"] = False

    return props
