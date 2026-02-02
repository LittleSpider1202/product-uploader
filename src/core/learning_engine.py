"""
学习引擎
"""
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from src.models import Problem, Solution, Step, StepAction, ProblemType, TrustLevel, Result
from src.infra.knowledge import KnowledgeBase
from .events import EventBus, EventTypes


@dataclass
class RecordingSession:
    """录制会话"""
    id: str
    problem: Problem | None
    target_url: str
    started_at: datetime
    process: subprocess.Popen | None = None


class LearningEngine:
    """学习引擎：Codegen 录制"""

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        event_bus: EventBus = None
    ):
        self.knowledge_base = knowledge_base
        self.event_bus = event_bus or EventBus()
        self._current_session: RecordingSession | None = None

    # === 增量学习（问题处理）===

    async def learn_from_problem(self, problem: Problem) -> Result[Solution | None]:
        """增量学习：从问题中学习解决方案"""
        # 1. 先查找现有方案
        find_result = self.knowledge_base.find_solution(problem)
        if find_result.success and find_result.data:
            return Result.ok(find_result.data)

        # 2. 没有现成方案，需要人工录制
        # 这里返回 None，让上层决定是否启动录制
        return Result.ok(None)

    # === Codegen 集成 ===

    def start_recording(
        self,
        target_url: str,
        problem: Problem = None,
        on_complete: Callable[[str], None] = None
    ) -> Result[RecordingSession]:
        """启动 codegen 录制"""
        if self._current_session:
            return Result.fail_with(
                code="L_RECORDING_IN_PROGRESS",
                message="已有录制会话进行中",
                recoverable=False
            )

        session_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 创建输出目录
        output_dir = Path("data/recordings")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{session_id}.py"

        try:
            # 启动 codegen 进程
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "playwright", "codegen",
                    target_url,
                    "--target", "python-async",
                    "-o", str(output_file)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            session = RecordingSession(
                id=session_id,
                problem=problem,
                target_url=target_url,
                started_at=datetime.now(),
                process=process
            )
            self._current_session = session

            # 发送事件
            self._emit_event(
                EventTypes.RECORDING_START,
                session_id=session_id,
                target_url=target_url
            )

            return Result.ok(session)
        except Exception as e:
            return Result.fail_with(
                code="L_CODEGEN_FAILED",
                message=f"启动 codegen 失败: {e}",
                recoverable=False
            )

    def stop_recording(self) -> Result[Solution | None]:
        """停止录制，生成方案"""
        if not self._current_session:
            return Result.fail_with(
                code="L_NO_RECORDING",
                message="没有进行中的录制会话",
                recoverable=False
            )

        session = self._current_session

        # 终止进程
        if session.process:
            session.process.terminate()
            try:
                session.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                session.process.kill()

        # 读取生成的代码
        output_file = Path("data/recordings") / f"{session.id}.py"
        if not output_file.exists():
            self._current_session = None
            return Result.ok(None)

        try:
            code = output_file.read_text(encoding="utf-8")
            steps = self._parse_codegen_output(code)

            if not steps:
                self._current_session = None
                return Result.ok(None)

            # 创建方案
            problem_type = session.problem.type if session.problem else ProblemType.UNKNOWN
            solution = Solution(
                id=self.knowledge_base.solutions.generate_id(),
                problem_type=problem_type,
                name=f"录制方案 {session.id}",
                description=f"通过 codegen 录制生成，目标 URL: {session.target_url}",
                match_rules={"url_pattern": session.target_url},
                steps=steps,
                trust_level=TrustLevel.NEW,
                created_by="codegen"
            )

            # 保存方案
            save_result = self.knowledge_base.save_solution(solution)
            if not save_result.success:
                self._current_session = None
                return save_result

            # 如果有关联问题，建立关联
            if session.problem:
                self.knowledge_base.link_solution(session.problem.id, solution.id)

            # 发送事件
            self._emit_event(
                EventTypes.RECORDING_STOP,
                session_id=session.id,
                solution_id=solution.id
            )

            self._current_session = None
            return Result.ok(solution)
        except Exception as e:
            self._current_session = None
            return Result.fail_with(
                code="L_PARSE_FAILED",
                message=f"解析录制结果失败: {e}",
                recoverable=False
            )

    def _parse_codegen_output(self, code: str) -> list[Step]:
        """解析 codegen 生成的代码"""
        steps = []
        lines = code.split("\n")

        for line in lines:
            line = line.strip()

            # 解析 click
            if ".click(" in line:
                selector = self._extract_selector(line)
                if selector:
                    steps.append(Step(
                        action=StepAction.CLICK,
                        selector=selector
                    ))

            # 解析 fill
            elif ".fill(" in line:
                selector = self._extract_selector(line)
                value = self._extract_value(line)
                if selector:
                    steps.append(Step(
                        action=StepAction.FILL,
                        selector=selector,
                        value=value
                    ))

            # 解析 select_option
            elif ".select_option(" in line:
                selector = self._extract_selector(line)
                value = self._extract_value(line)
                if selector:
                    steps.append(Step(
                        action=StepAction.SELECT,
                        selector=selector,
                        value=value
                    ))

            # 解析 hover
            elif ".hover(" in line:
                selector = self._extract_selector(line)
                if selector:
                    steps.append(Step(
                        action=StepAction.HOVER,
                        selector=selector
                    ))

            # 解析 press
            elif ".press(" in line:
                selector = self._extract_selector(line)
                value = self._extract_value(line)
                if selector:
                    steps.append(Step(
                        action=StepAction.PRESS,
                        selector=selector,
                        value=value
                    ))

        return steps

    def _extract_selector(self, line: str) -> str | None:
        """从代码行提取选择器"""
        import re
        # 匹配 .xxx("selector" 或 .xxx('selector'
        match = re.search(r'\.\w+\(["\']([^"\']+)["\']', line)
        return match.group(1) if match else None

    def _extract_value(self, line: str) -> str | None:
        """从代码行提取值"""
        import re
        # 匹配第二个字符串参数
        matches = re.findall(r'["\']([^"\']+)["\']', line)
        return matches[1] if len(matches) > 1 else None

    def promote_solution(self, solution_id: str, new_level: TrustLevel) -> Result[Solution]:
        """手动提升方案信任等级"""
        result = self.knowledge_base.solutions.get(solution_id)
        if not result.success:
            return result

        solution = result.data
        solution.trust_level = new_level
        solution.updated_at = datetime.now()

        return self.knowledge_base.solutions.save(solution)

    def _emit_event(self, event_type: str, **payload):
        """发送事件"""
        if self.event_bus:
            self.event_bus.emit(event_type, **payload)
