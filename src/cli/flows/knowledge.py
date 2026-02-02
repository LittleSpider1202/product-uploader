"""
知识库管理流程
"""
from src.cli.ui import UI
from src.infra import KnowledgeBase
from src.models import TrustLevel
from .base import BaseFlow, FlowResult


class KnowledgeFlow(BaseFlow):
    """知识库管理流程"""

    def __init__(self, ui: UI, knowledge_base: KnowledgeBase):
        super().__init__(ui)
        self.knowledge_base = knowledge_base

    async def run(self) -> FlowResult:
        """执行知识库管理流程"""
        self.ui.print_header("知识库管理")
        self.ui.print()

        # 显示统计
        stats = self.knowledge_base.get_stats()
        self.ui.print(f"  问题总数: {stats['total_problems']}")
        self.ui.print(f"  方案总数: {stats['total_solutions']}")
        self.ui.print()

        options = [
            "查看问题列表",
            "查看方案列表",
            "查看统计详情",
            "返回"
        ]

        idx = self.select(options)

        if idx == 0:
            return await self._list_problems()
        elif idx == 1:
            return await self._list_solutions()
        elif idx == 2:
            return self._show_stats(stats)
        else:
            return FlowResult.cancelled("用户返回")

    async def _list_problems(self) -> FlowResult:
        """列出问题"""
        result = self.knowledge_base.problems.list()
        if not result.success:
            self.ui.print_error(result.error.message)
            return FlowResult.failed(result.error.message)

        problems = result.data
        if not problems:
            self.ui.print_info("暂无问题记录")
            return FlowResult.success()

        self.ui.print()
        headers = ["ID", "类型", "状态", "创建时间"]
        rows = [
            [p["id"], p["type"], p["status"], p["created_at"][:10]]
            for p in problems[:10]
        ]
        self.ui.table(headers, rows)

        if len(problems) > 10:
            self.ui.print()
            self.ui.print_info(f"共 {len(problems)} 条，仅显示前 10 条")

        return FlowResult.success()

    async def _list_solutions(self) -> FlowResult:
        """列出方案"""
        result = self.knowledge_base.solutions.list()
        if not result.success:
            self.ui.print_error(result.error.message)
            return FlowResult.failed(result.error.message)

        solutions = result.data
        if not solutions:
            self.ui.print_info("暂无解决方案")
            return FlowResult.success()

        self.ui.print()
        headers = ["ID", "名称", "信任等级", "成功率"]
        rows = [
            [
                s["id"],
                s["name"][:20],
                s["trust_level"],
                f"{s['success_rate']*100:.0f}%"
            ]
            for s in solutions[:10]
        ]
        self.ui.table(headers, rows)

        if len(solutions) > 10:
            self.ui.print()
            self.ui.print_info(f"共 {len(solutions)} 条，仅显示前 10 条")

        self.ui.print()

        # 提供操作选项
        if solutions:
            options = ["提升方案信任等级", "返回"]
            idx = self.select(options)
            if idx == 0:
                return await self._promote_solution(solutions)

        return FlowResult.success()

    async def _promote_solution(self, solutions: list[dict]) -> FlowResult:
        """提升方案信任等级"""
        # 选择方案
        options = [s["name"][:30] for s in solutions[:5]]
        options.append("取消")

        idx = self.select(options, "选择要提升的方案")
        if idx >= len(solutions) or idx >= 5:
            return FlowResult.cancelled()

        solution_id = solutions[idx]["id"]

        # 选择目标等级
        levels = ["testing (测试中)", "trusted (可信任)"]
        level_idx = self.select(levels, "选择目标信任等级")

        target_level = TrustLevel.TESTING if level_idx == 0 else TrustLevel.TRUSTED

        # 获取方案
        get_result = self.knowledge_base.solutions.get(solution_id)
        if not get_result.success:
            self.ui.print_error(get_result.error.message)
            return FlowResult.failed(get_result.error.message)

        solution = get_result.data
        solution.trust_level = target_level

        save_result = self.knowledge_base.solutions.save(solution)
        if save_result.success:
            self.ui.print_success(f"已将方案提升为 {target_level.value}")
            return FlowResult.success()
        else:
            self.ui.print_error(save_result.error.message)
            return FlowResult.failed(save_result.error.message)

    def _show_stats(self, stats: dict) -> FlowResult:
        """显示详细统计"""
        self.ui.print()
        self.ui.print("问题统计：")
        for status, count in stats.get("problem_by_status", {}).items():
            self.ui.print(f"  {status}: {count}")

        self.ui.print()
        self.ui.print("方案统计：")
        for level, count in stats.get("solution_by_level", {}).items():
            self.ui.print(f"  {level}: {count}")

        return FlowResult.success()
