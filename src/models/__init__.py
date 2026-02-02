"""
数据模型模块
"""
from .result import Result, Error
from .product import Product, SKU, ProductStatus
from .problem import Problem, ProblemContext, ProblemType, ProblemStatus
from .solution import Solution, Step, StepAction, SolutionStats, TrustLevel
from .binding import FieldType, FieldBinding, BindingConfig

__all__ = [
    # result
    "Result",
    "Error",
    # product
    "Product",
    "SKU",
    "ProductStatus",
    # problem
    "Problem",
    "ProblemContext",
    "ProblemType",
    "ProblemStatus",
    # solution
    "Solution",
    "Step",
    "StepAction",
    "SolutionStats",
    "TrustLevel",
    # binding
    "FieldType",
    "FieldBinding",
    "BindingConfig",
]
