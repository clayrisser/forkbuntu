from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest
from munch import munchify

from forkbuntu.app import App
from forkbuntu.step import Step


class RecordingStep(Step):
    cache = True

    def __init__(self, name: str, app: App) -> None:
        super().__init__(name, app)
        self.messages = munchify({"past": name + " ran", "present": name + " running"})
        self.runs = 0

    def run(self, *args: object) -> None:
        self.runs += 1


def add_step(app: App, name: str, **attrs: object) -> RecordingStep:
    step = RecordingStep(name, app)
    for key, value in attrs.items():
        setattr(step, key, value)
    app.steps[name] = step
    return step


class TestStepOrchestration:
    def test_runs_requirements_first(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        order: list[str] = []
        first = add_step(app, "first")
        second = add_step(app, "second", requires=["first"])
        first.run = lambda *a: order.append("first")  # type: ignore[method-assign]
        second.run = lambda *a: order.append("second")  # type: ignore[method-assign]
        second.start()
        assert order == ["first", "second"]

    def test_requirements_run_once(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        shared = add_step(app, "shared")
        add_step(app, "left", requires=["shared"])
        right = add_step(app, "right", requires=["shared", "left"])
        right.start()
        assert shared.runs == 1

    def test_steps_ran_registry(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        add_step(app, "first")
        second = add_step(app, "second", requires=["first"])
        second.start()
        assert set(app.steps_ran.keys()) == {"first", "second"}

    def test_checksum_caching_skips_second_run(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("original")
        step = add_step(app, "step", agnostic=True, checksum_paths=[str(tracked)])
        step.start()
        assert step.runs == 1
        app.steps_ran.clear()
        step.start()
        assert step.runs == 1

    def test_checksum_caching_reruns_on_change(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("original")
        step = add_step(app, "step", agnostic=True, checksum_paths=[str(tracked)])
        step.start()
        tracked.write_text("changed")
        app.steps_ran.clear()
        step.start()
        assert step.runs == 2

    def test_missing_has_path_forces_run(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        step = add_step(app, "step", has_paths=[str(tmp_path / "missing")])
        step.start()
        step.start()
        assert step.runs == 2

    def test_cache_false_always_runs(self, make_app: Callable[..., App]) -> None:
        app = make_app()
        step = add_step(app, "step", cache=False)
        step.start()
        app.steps_ran.clear()
        step.start()
        assert step.runs == 2

    def test_root_step_runs_when_not_finished(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        app.finished = False
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("original")
        step = add_step(app, "step", root=True, checksum_paths=[str(tracked)])
        step.start()
        app.steps_ran.clear()
        step.start()
        assert step.runs == 2

    def test_root_step_cached_when_finished(
        self, make_app: Callable[..., App], tmp_path: Path
    ) -> None:
        app = make_app()
        app.finished = True
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("original")
        step = add_step(app, "step", root=True, checksum_paths=[str(tracked)])
        step.start()
        app.steps_ran.clear()
        step.start()
        assert step.runs == 1
