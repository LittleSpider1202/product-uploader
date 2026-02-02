"""
方案库存储
"""
import uuid
import re
from pathlib import Path

from src.models import Solution, ProblemType, TrustLevel, Result
from src.infra.storage.base import BaseStorage


class SolutionStorage(BaseStorage[Solution]):
    """方案库存储"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("data/solutions")
        super().__init__(data_dir)

    def _empty_index(self) -> dict:
        return {"solutions": []}

    def _to_index_entry(self, solution: Solution) -> dict:
        return {
            "id": solution.id,
            "name": solution.name,
            "problem_type": solution.problem_type.value,
            "trust_level": solution.trust_level.value,
            "success_rate": solution.stats.success_rate,
            "updated_at": solution.updated_at.isoformat()
        }

    def generate_id(self) -> str:
        """生成唯一 ID"""
        return f"sol_{uuid.uuid4().hex[:8]}"

    def save(self, solution: Solution) -> Result[Solution]:
        """保存方案"""
        try:
            item_path = self._item_path(solution.id)
            self._write_json(item_path, solution.to_dict())

            index = self._get_index()
            entries = index["solutions"]
            entries = [e for e in entries if e["id"] != solution.id]
            entries.append(self._to_index_entry(solution))
            index["solutions"] = entries
            self._save_index(index)

            return Result.ok(solution)
        except Exception as e:
            return Result.fail_with(
                code="S_WRITE_FAILED",
                message=f"保存方案失败: {e}",
                recoverable=False
            )

    def get(self, solution_id: str) -> Result[Solution]:
        """获取方案"""
        try:
            item_path = self._item_path(solution_id)
            data = self._read_json(item_path)
            if data is None:
                return Result.fail_with(
                    code="S_NOT_FOUND",
                    message=f"方案不存在: {solution_id}",
                    recoverable=False
                )
            return Result.ok(Solution.from_dict(data))
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"读取方案失败: {e}",
                recoverable=False
            )

    def list(
        self,
        problem_type: ProblemType = None,
        trust_level: TrustLevel = None
    ) -> Result[list[dict]]:
        """列出方案"""
        try:
            index = self._get_index()
            entries = index["solutions"]
            if problem_type:
                entries = [e for e in entries if e["problem_type"] == problem_type.value]
            if trust_level:
                entries = [e for e in entries if e["trust_level"] == trust_level.value]
            return Result.ok(entries)
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"列出方案失败: {e}",
                recoverable=False
            )

    def list_trusted(self) -> Result[list[dict]]:
        """列出可信方案"""
        return self.list(trust_level=TrustLevel.TRUSTED)

    def find_matching(
        self,
        problem_type: ProblemType,
        context: dict
    ) -> Result[Solution | None]:
        """查找匹配的方案"""
        try:
            # 获取该类型的所有可用方案（非 FAILED）
            index = self._get_index()
            candidates = [
                e for e in index["solutions"]
                if e["problem_type"] == problem_type.value
                and e["trust_level"] != TrustLevel.FAILED.value
            ]

            # 按信任等级和成功率排序
            trust_order = {
                TrustLevel.TRUSTED.value: 0,
                TrustLevel.TESTING.value: 1,
                TrustLevel.NEW.value: 2
            }
            candidates.sort(
                key=lambda x: (trust_order.get(x["trust_level"], 99), -x["success_rate"])
            )

            # 逐个检查匹配规则
            for entry in candidates:
                result = self.get(entry["id"])
                if not result.success:
                    continue

                solution = result.data
                if self._matches(solution, context):
                    return Result.ok(solution)

            return Result.ok(None)
        except Exception as e:
            return Result.fail_with(
                code="K_SOLUTION_NOT_FOUND",
                message=f"查找方案失败: {e}",
                recoverable=True
            )

    def _matches(self, solution: Solution, context: dict) -> bool:
        """检查方案是否匹配上下文"""
        rules = solution.match_rules
        if not rules:
            return True  # 无规则则匹配所有

        # URL 模式匹配
        if "url_pattern" in rules and "page_url" in context:
            pattern = rules["url_pattern"]
            if not re.search(pattern, context["page_url"]):
                return False

        # 元素选择器匹配
        if "element_pattern" in rules and "element_selector" in context:
            pattern = rules["element_pattern"]
            if not re.search(pattern, context.get("element_selector", "")):
                return False

        return True

    def record_execution(self, solution_id: str, success: bool) -> Result[Solution]:
        """记录方案执行结果"""
        result = self.get(solution_id)
        if not result.success:
            return result

        solution = result.data
        solution.record_execution(success)
        return self.save(solution)
