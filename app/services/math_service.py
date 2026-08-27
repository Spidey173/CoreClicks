import ast
import math
import operator
from typing import Any, Union


class MathEvaluationError(Exception):
    """Raised when mathematical expression evaluation fails or contains illegal syntax."""
    pass


SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


def _safe_factorial(n: Union[int, float]) -> int:
    val = int(round(n))
    if val < 0 or val > 100:
        raise MathEvaluationError("Factorial input must be an integer between 0 and 100.")
    return math.factorial(val)


def _safe_pow(base: float, exp: float) -> float:
    if abs(base) > 1e10 or abs(exp) > 500:
        raise MathEvaluationError("Exponentiation exceeds allowable magnitude bounds.")
    return math.pow(base, exp)


def _safe_log(x: float) -> float:
    if x <= 0:
        raise MathEvaluationError("Logarithm argument must be strictly positive.")
    return math.log10(x)


def _safe_ln(x: float) -> float:
    if x <= 0:
        raise MathEvaluationError("Natural log argument must be strictly positive.")
    return math.log(x)


def _safe_sqrt(x: float) -> float:
    if x < 0:
        raise MathEvaluationError("Square root of a negative number is undefined in real domain.")
    return math.sqrt(x)


def evaluate_ast_node(node: ast.AST, angle_mode: str = "rad") -> Union[int, float]:
    """Recursively evaluates AST nodes safely."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise MathEvaluationError(f"Unsupported constant type: {type(node.value)}")

    elif isinstance(node, ast.Name):
        name_lower = node.id.lower()
        if name_lower in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[name_lower]
        raise MathEvaluationError(f"Undefined identifier: {node.id}")

    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            operand = evaluate_ast_node(node.operand, angle_mode)
            return SAFE_OPERATORS[op_type](operand)
        raise MathEvaluationError(f"Unsupported unary operator: {op_type.__name__}")

    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        left = evaluate_ast_node(node.left, angle_mode)
        right = evaluate_ast_node(node.right, angle_mode)

        if op_type is ast.Div or op_type is ast.FloorDiv or op_type is ast.Mod:
            if right == 0:
                raise MathEvaluationError("Division by zero is undefined.")

        if op_type is ast.Pow:
            return _safe_pow(left, right)

        if op_type in SAFE_OPERATORS:
            try:
                res = SAFE_OPERATORS[op_type](left, right)
                if isinstance(res, complex):
                    raise MathEvaluationError("Complex numbers are not supported.")
                return res
            except OverflowError:
                raise MathEvaluationError("Calculation resulted in numerical overflow.")
        raise MathEvaluationError(f"Unsupported binary operator: {op_type.__name__}")

    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise MathEvaluationError("Only direct mathematical function calls are allowed.")

        func_name = node.func.id.lower()
        args = [evaluate_ast_node(arg, angle_mode) for arg in node.args]

        if not args:
            raise MathEvaluationError(f"Function {func_name} requires arguments.")

        x = args[0]

        # Trigonometry angle conversion
        def to_rad(val):
            return math.radians(val) if angle_mode == "deg" else val

        if func_name == "sqrt":
            return _safe_sqrt(x)
        elif func_name == "sin":
            return math.sin(to_rad(x))
        elif func_name == "cos":
            return math.cos(to_rad(x))
        elif func_name == "tan":
            rad_val = to_rad(x)
            if math.isclose(math.cos(rad_val), 0.0, abs_tol=1e-12):
                raise MathEvaluationError("Tangent is undefined for this angle.")
            return math.tan(rad_val)
        elif func_name == "log":
            return _safe_log(x)
        elif func_name == "ln":
            return _safe_ln(x)
        elif func_name == "abs":
            return abs(x)
        elif func_name == "round":
            return round(x, int(args[1])) if len(args) > 1 else round(x)
        elif func_name == "floor":
            return math.floor(x)
        elif func_name == "ceil":
            return math.ceil(x)
        elif func_name in ("factorial", "fact"):
            return _safe_factorial(x)
        elif func_name == "rad":
            return math.radians(x)
        elif func_name == "deg":
            return math.degrees(x)

        raise MathEvaluationError(f"Unsupported function: {func_name}")

    raise MathEvaluationError(f"Disallowed expression syntax: {type(node).__name__}")


def safe_calculate(expression: str, angle_mode: str = "rad") -> str:
    """Safely evaluates a mathematical expression string using AST parsing without eval()."""
    if not expression or not expression.strip():
        raise MathEvaluationError("Expression cannot be empty.")

    sanitized = expression.strip().replace("^", "**").replace("×", "*").replace("÷", "/")

    try:
        parsed_ast = ast.parse(sanitized, mode="eval")
    except SyntaxError as se:
        raise MathEvaluationError(f"Invalid mathematical syntax: {se.msg}")

    numeric_result = evaluate_ast_node(parsed_ast.body, angle_mode=angle_mode)

    if isinstance(numeric_result, float):
        if math.isinf(numeric_result) or math.isnan(numeric_result):
            raise MathEvaluationError("Result is infinite or undefined.")
        if numeric_result.is_integer():
            return str(int(numeric_result))
        return f"{numeric_result:.10g}"

    return str(numeric_result)
