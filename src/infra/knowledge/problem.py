"""
问题库存储
"""
import uuid
from pathlib import Path

from src.models import Problem, ProblemType, ProblemStatus, Result
from src.infra.storage.base import BaseStorage


class ProblemStorage(BaseStorage[Problem]):
    """问题库存储"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("data/problems")
        super().__init__(data_dir)

    def _empty_index(self) -> dict:
        return {"problems": []}

    def _to_index_entry(self, problem: Problem) -> dict:
        return {
            "id": problem.id,
            "type": problem.type.value,
            "message": problem.message[:50],  # 截断
            "status": problem.status.value,
            "solution_id": problem.solution_id,
            "created_at": problem.created_at.isoformat()
        }

    def generate_id(self) -> str:
        """生成唯一 ID"""
        return f"prob_{uuid.uuid4().hex[:8]}"

    def save(self, problem: Problem) -> Result[Problem]:
        """保存问题"""
        try:
            item_path = self._item_path(problem.id)
            self._write_json(item_path, problem.to_dict())

            index = self._get_index()
            entries = index["problems"]
            entries = [e for e in entries if e["id"] != problem.id]
            entries.append(self._to_index_entry(problem))
            index["problems"] = entries
            self._save_index(index)

            return Result.ok(problem)
        except Exception as e:
            return Result.fail_with(
                code="S_WRITE_FAILED",
                message=f"保存问题失败: {e}",
                recoverable=False
            )

    def get(self, problem_id: str) -> Result[Problem]:
        """获取问题"""
        try:
            item_path = self._item_path(problem_id)
            data = self._read_json(item_path)
            if data is None:
                return Result.fail_with(
                    code="S_NOT_FOUND",
                    message=f"问题不存在: {problem_id}",
                    recoverable=False
                )
            return Result.ok(Problem.from_dict(data))
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"读取问题失败: {e}",
                recoverable=False
            )

    def list(
        self,
        status: ProblemStatus = None,
        problem_type: ProblemType = None
    ) -> Result[list[dict]]:
        """列出问题"""
        try:
            index = self._get_index()
            entries = index["problems"]
            if status:
                entries = [e for e in entries if e["status"] == status.value]
            if problem_type:
                entries = [e for e in entries if e["type"] == problem_type.value]
            return Result.ok(entries)
        except Exception as e:
            return Result.fail_with(
                code="S_READ_FAILED",
                message=f"列出问题失败: {e}",
                recoverable=False
            )

    def list_open(self) -> Result[list[dict]]:
        """列出待处理的问题"""
        return self.list(status=ProblemStatus.OPEN)

    def mark_solved(self, problem_id: str, solution_id: str) -> Result[Problem]:
        """标记问题已解决"""
        result = self.get(problem_id)
        if not result.success:
            return result

        problem = result.data
        problem.status = ProblemStatus.SOLVED
        problem.solution_id = solution_id
        from datetime import datetime
        problem.resolved_at = datetime.now()

        return self.save(problem)
