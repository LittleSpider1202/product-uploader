"""
知识库基类
"""
from pathlib import Path

from src.models import Problem, Solution, ProblemType, Result
from .problem import ProblemStorage
from .solution import SolutionStorage


class KnowledgeBase:
    """知识库：统一管理问题和方案"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("data")
        self.problems = ProblemStorage(data_dir / "problems")
        self.solutions = SolutionStorage(data_dir / "solutions")

    def report_problem(self, problem: Problem) -> Result[Problem]:
        """上报问题"""
        return self.problems.save(problem)

    def find_solution(self, problem: Problem) -> Result[Solution | None]:
        """为问题查找方案"""
        context = {
            "page_url": problem.context.page_url,
            "element_selector": problem.context.element_selector,
            "expected_value": problem.context.expected_value,
            "actual_value": problem.context.actual_value
        }
        return self.solutions.find_matching(problem.type, context)

    def save_solution(self, solution: Solution) -> Result[Solution]:
        """保存方案"""
        return self.solutions.save(solution)

    def link_solution(self, problem_id: str, solution_id: str) -> Result[Problem]:
        """关联问题和方案"""
        return self.problems.mark_solved(problem_id, solution_id)

    def get_stats(self) -> dict:
        """获取知识库统计"""
        problems_result = self.problems.list()
        solutions_result = self.solutions.list()

        problems = problems_result.data if problems_result.success else []
        solutions = solutions_result.data if solutions_result.success else []

        # 统计问题状态
        problem_stats = {}
        for p in problems:
            status = p["status"]
            problem_stats[status] = problem_stats.get(status, 0) + 1

        # 统计方案信任等级
        solution_stats = {}
        for s in solutions:
            level = s["trust_level"]
            solution_stats[level] = solution_stats.get(level, 0) + 1

        return {
            "total_problems": len(problems),
            "problem_by_status": problem_stats,
            "total_solutions": len(solutions),
            "solution_by_level": solution_stats
        }
