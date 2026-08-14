"""
civil_toolkit/math_engine.py – Core variable and formula engine.

RESPONSIBILITY:
Provides MyVar, the fundamental data structure for all engineering calculations.
A MyVar knows:
  - Its current value (computed or manually set)
  - Its sympy expression (for symbolic LaTeX generation)
  - Its dependencies (other MyVars it depends on)
  - How to render itself as a full LaTeX equation string

This replaces the JS mathEngine.js + hand-written AST parser with sympy,
which handles symbolic math, LaTeX rendering, and numeric substitution natively.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Union

import sympy as sp

from civil_toolkit.engine.types import Unit, VarId


class MyVar:
    """
    A single engineering variable with optional computed formula.

    Parameters
    ----------
    id : str
        Unique identifier, e.g. ``'f_cd'``.
    symbol : str
        LaTeX symbol string, e.g. ``'f_{cd}'``.
    unit : str
        Physical unit string, e.g. ``'MPa'``.
    description : str
        Human-readable description.
    value : float | None
        Direct (fundamental) value. For computed vars this is the
        cached/overridden value; the live value comes from ``calc_fn``.
    fundamental : bool
        If True the variable has no formula – it is a direct input.
    overridden : bool
        If True a computed var is using a manually set value instead of
        evaluating its formula.
    calc_fn : Callable[[dict[str, MyVar]], float] | None
        A plain Python function ``(deps) -> float`` that computes the value
        from its dependency variables.
    sympy_expr : sp.Expr | None
        A sympy expression that represents the formula symbolically.
        When not supplied for a computed var, LaTeX output falls back to the
        numeric-only form.
    dependencies : dict[str, MyVar]
        Maps dependency name → MyVar instance. For computed vars these are
        the variables referenced by ``calc_fn`` / ``sympy_expr``.
    formula_template : str | None
        Optional manually specified LaTeX template string.  When set it takes
        priority over the auto-generated sympy output.
        Placeholders use the format ``{dep_name}`` and are substituted with
        the dependency's symbol or formatted numeric value.
    precision : int
        Number of decimal places used when formatting numeric values.
    reference : str
        Norm reference, e.g. ``'SIA 262:2025:2.4.2.3'``.
    """

    def __init__(
        self,
        *,
        id: Union[VarId, str],
        prop: Optional[str] = None,
        editor: Optional[Any] = None,
        dep_ids: Optional[List[str]] = None,
        symbol: str,
        unit: Union[Unit, str] = Unit.NONE,
        description: str = "",
        value: Optional[float] = None,
        fundamental: bool = True,
        overridden: bool = False,
        calc_fn: Optional[Callable[..., float]] = None,
        sympy_expr: Optional[sp.Expr] = None,
        sympy_symbol_map: Optional[Dict[str, sp.Symbol]] = None,
        dependencies: Optional[Dict[str, "MyVar"]] = None,
        formula_template: Optional[str] = None,
        precision: int = 2,
        reference: str = "",
    ) -> None:
        self.id = id
        self.symbol = symbol
        self.unit = unit
        self.description = description
        self.fundamental = fundamental
        self.overridden = overridden
        self.calc_fn = calc_fn
        self.sympy_expr = sympy_expr
        # Maps dep variable name → sympy Symbol used in sympy_expr
        self.sympy_symbol_map: Dict[str, sp.Symbol] = sympy_symbol_map or {}
        self.dependencies: Dict[str, "MyVar"] = dependencies or {}
        self.formula_template = formula_template
        self.precision = precision
        self.reference = reference
        self._manual_value: Optional[float] = float(value) if value is not None else None

        self.prop: Optional[str] = prop
        self.editor: Optional[Any] = editor
        self.dep_ids: List[str] = dep_ids or []
        
        # Extra metadata (set by engines)
        self.material_id: Optional[str] = None
        self.active: bool = True

    # ------------------------------------------------------------------
    # Value access
    # ------------------------------------------------------------------

    @property
    def value(self) -> Optional[float]:
        """
        Returns the active numeric value.

        Priority:
          1. Manual/fundamental value (if ``fundamental`` or ``overridden`` or ``calc_fn is None``)
          2. Result of ``calc_fn(dependencies)``
          3. ``_manual_value`` fallback
        """
        if self.fundamental or self.overridden or self.calc_fn is None:
            return self._manual_value
        if self.calc_fn:
            try:
                result = self.calc_fn(self.dependencies)
                return float(result) if result is not None else self._manual_value
            except Exception as exc:
                import warnings
                warnings.warn(f"[MyVar] Error computing '{self.id}': {exc}")
                return self._manual_value
        return self._manual_value

    @value.setter
    def value(self, val: Any) -> None:
        if val is None or val == "":
            self._manual_value = None
            if not self.fundamental:
                self.overridden = False
        else:
            self._manual_value = float(val)

    def reset_override(self) -> None:
        """Clears a manual override so the variable uses its formula again."""
        if not self.fundamental:
            self.overridden = False
            self._manual_value = None

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    def format_value(self, val: Optional[float] = None) -> str:
        """
        Formats a numeric value as a string using this variable's precision.

        For large integers (≥1000, no decimal part) the integer form is returned
        without decimal places, matching the JS behaviour.
        """
        v = val if val is not None else self.value
        if v is None:
            return "?"
        if abs(v) >= 1000 and v % 1 == 0:
            return str(int(v))
        factor = 10 ** self.precision
        rounded = round(v * factor) / factor
        # Remove trailing zeros for cleanliness
        if self.precision > 0:
            return f"{rounded:.{self.precision}f}".rstrip("0").rstrip(".")
        return str(int(rounded))

    def get_formatted_unit(self) -> str:
        """
        Returns a LaTeX-formatted unit string with proper \\,\\text{} wrapping.

        Examples::

            'MPa'   → '\\\\,\\\\text{MPa}'
            'mm^2'  → '\\\\,\\\\text{mm}^{2}'
            ''      → ''
        """
        unit = self.unit
        if not unit or unit in ("-", "1"):
            return ""
        if "^" in unit:
            parts = unit.split("^", 1)
            return f"\\,\\text{{{parts[0]}}}^{{{parts[1]}}}"
        if unit.startswith("\\"):
            # Already a LaTeX command (e.g. \%)
            return f"\\,{unit}"
        return f"\\,\\text{{{unit}}}"

    # ------------------------------------------------------------------
    # LaTeX generation
    # ------------------------------------------------------------------

    def to_latex_equation(self) -> str:
        """
        Builds a step-by-step LaTeX equation string::

            symbol = symbolic_formula = numeric_formula = result unit

        Examples::

            f_{cd} = \\frac{\\eta_{fc} \\cdot f_{ck}}{\\gamma_c}
                   = \\frac{0.933 \\cdot 30\\,\\text{MPa}}{1.5}
                   = 18.7\\,\\text{MPa}
        """
        symbol_str = self.symbol
        unit_str = self.get_formatted_unit()
        val = self.value
        formatted_val = self.format_value(val)

        # Fundamental or overridden (without formula template): just show the value
        if (self.fundamental or self.overridden) and not self.formula_template:
            return f"{symbol_str} = {formatted_val}{unit_str}"


        symbolic_str = ""
        numeric_str = ""

        if self.formula_template:
            # Manual LaTeX template takes priority
            symbolic_str = self.formula_template
            numeric_str = self.formula_template
            for dep_name, dep_var in self.dependencies.items():
                placeholder = "{" + dep_name + "}"
                symbolic_str = symbolic_str.replace(placeholder, dep_var.symbol)
                dep_unit = dep_var.get_formatted_unit()
                dep_val_str = f"{dep_var.format_value()}{dep_unit}"
                numeric_str = numeric_str.replace(placeholder, dep_val_str)

        elif self.sympy_expr is not None:
            # Auto-generate from sympy expression
            symbolic_str = self._sympy_to_symbolic_latex()
            numeric_str = self._sympy_to_numeric_latex()

        if symbolic_str:
            if symbolic_str == numeric_str:
                if symbolic_str == formatted_val:
                    return f"{symbol_str} = {formatted_val}{unit_str}"
                return f"{symbol_str} = {symbolic_str} = {formatted_val}{unit_str}"
            if numeric_str == formatted_val:
                return f"{symbol_str} = {symbolic_str} = {formatted_val}{unit_str}"
            return f"{symbol_str} = {symbolic_str} = {numeric_str} = {formatted_val}{unit_str}"

        return f"{symbol_str} = {formatted_val}{unit_str}"

    def _sympy_to_symbolic_latex(self) -> str:
        """
        Renders the sympy expression as LaTeX with dependency symbols substituted.
        """
        expr = self.sympy_expr
        subs = {}
        for dep_name, dep_var in self.dependencies.items():
            sym = self.sympy_symbol_map.get(dep_name)
            if sym is not None:
                # Replace the symbol in the expression with the dep's own symbol string
                # We do this by converting the sympy symbol to the dep's LaTeX symbol
                subs[sym] = sp.Symbol(dep_var.symbol)
        expr_subs = expr.subs(subs)
        return sp.latex(expr_subs)

    def _sympy_to_numeric_latex(self) -> str:
        """
        Renders the sympy expression as LaTeX with numeric values + units substituted.

        Uses ``sp.Symbol`` instead of ``sp.Float`` to prevent sympy from
        numerically evaluating the expression before LaTeX rendering.
        The unit string is embedded in the symbol name so it appears in
        the rendered output (e.g. ``30\\,\\text{MPa}``).
        """
        expr = self.sympy_expr
        subs = {}
        for dep_name, dep_var in self.dependencies.items():
            sym = self.sympy_symbol_map.get(dep_name)
            if sym is not None and dep_var.value is not None:
                formatted = dep_var.format_value()
                unit_str = dep_var.get_formatted_unit()   # e.g. r"\,\text{MPa}" or ""
                # Embed value + unit as an opaque symbol so sympy renders it
                # in-place without triggering numeric simplification.
                subs[sym] = sp.Symbol(formatted + unit_str)
        expr_subs = expr.subs(subs)
        return sp.latex(expr_subs)


    # ------------------------------------------------------------------
    # Dependency traversal
    # ------------------------------------------------------------------

    def get_calculation_steps(self) -> list["MyVar"]:
        """
        Returns all variables in the dependency tree in topological order
        (dependencies before dependents), with no duplicates.
        """
        steps: list[MyVar] = []
        visited: set[str] = set()

        def visit(v: MyVar) -> None:
            if not v or v.id in visited:
                return
            visited.add(v.id)
            for dep in v.dependencies.values():
                visit(dep)
            steps.append(v)

        visit(self)
        return steps

    # ------------------------------------------------------------------
    # Serialisation (for API responses)
    # ------------------------------------------------------------------

    def to_dict(self, visited: Optional[set] = None) -> dict:
        """Returns a JSON-serialisable dict for API responses."""
        if visited is None:
            visited = set()

        deps_dict = {}
        if self.id not in visited:
            visited.add(self.id)
            if self.dependencies:
                for k, v in self.dependencies.items():
                    if hasattr(v, "to_dict"):
                        deps_dict[k] = v.to_dict(visited=visited.copy())
                    elif isinstance(v, dict):
                        deps_dict[k] = v
                    elif isinstance(v, str):
                        deps_dict[k] = {"id": v}

        return {
            "id": self.id,
            "symbol": self.symbol,
            "unit": self.unit,
            "description": self.description,
            "value": self.value,
            "formatted_value": self.format_value(),
            "fundamental": self.fundamental,
            "overridden": self.overridden,
            "reference": self.reference,
            "precision": self.precision,
            "latex_equation": self.to_latex_equation(),
            "dependencies": deps_dict,
        }

    def __repr__(self) -> str:
        return f"MyVar(id={self.id!r}, value={self.value}, unit={self.unit!r})"
