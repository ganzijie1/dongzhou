"""Gymnasium adapter for the native mengde headless RL process."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class MengdeProtocolError(RuntimeError):
    """Raised when the native process returns an invalid protocol response."""


class MengdeEnv(gym.Env[np.ndarray, int]):
    metadata = {"render_modes": []}

    def __init__(
        self,
        executable: str | Path,
        scenario: str = "example",
        game_path: str | Path | None = None,
        max_units: int = 32,
        max_actions: int = 2048,
        max_episode_actions: int = 20,
        interactive: bool = False,
    ) -> None:
        super().__init__()
        self.executable = Path(executable).resolve()
        if not self.executable.is_file():
            raise FileNotFoundError(f"mengde_rl executable not found: {self.executable}")
        if max_actions <= 0:
            raise ValueError("max_actions must be positive")

        self.max_units = max_units
        self.max_actions = max_actions
        self.max_episode_actions = max_episode_actions
        if game_path is None:
            game_path = Path(__file__).resolve().parents[1] / "game"
        game_path = Path(game_path).resolve()
        if not (game_path / "sce").is_dir():
            raise FileNotFoundError(f"mengde game data directory not found: {game_path}")
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(4 + max_units * 16,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(max_actions)
        process_environment = os.environ.copy()
        process_environment["MENGDE_GAME_PATH"] = str(game_path)
        self._process_args = [
            str(self.executable),
            scenario,
            str(max_units),
            str(max_episode_actions),
            "interactive" if interactive else "training",
        ]
        self._process_environment = process_environment
        self._creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self._process = self._spawn_process()
        self._initial_state: dict[str, Any] | None = self._read_response()
        self._action_count = 0
        self._closed = False

    def _spawn_process(self, stage_index: int = 0) -> subprocess.Popen[str]:
        return subprocess.Popen(
            [*self._process_args, str(stage_index)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=self._process_environment,
            creationflags=self._creation_flags,
        )

    def _restart_process(self, stage_index: int = 0) -> None:
        if self._process.poll() is None:
            try:
                self._write("QUIT")
                self._process.wait(timeout=3)
            except (BrokenPipeError, OSError, subprocess.TimeoutExpired):
                self._process.terminate()
                try:
                    self._process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self._process.kill()
        self._process = self._spawn_process(stage_index)
        self._initial_state = self._read_response()
        self._initial_state = None
        self._action_count = 0
        self._closed = False

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        del options
        if seed is not None:
            self._request(f"SEED {int(seed)}")
            self._initial_state = None
            state = self._request("RESET")
        elif self._initial_state is not None:
            state = self._initial_state
            self._initial_state = None
        else:
            state = self._request("RESET")
        return self._state_result(state)

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        action = int(action)
        if action < 0 or action >= self._action_count:
            raise ValueError(f"action {action} is masked; valid range is [0, {self._action_count})")
        state = self._request(f"STEP {action}")
        observation, info = self._state_result(state)
        return (
            observation,
            float(state["reward"]),
            bool(state["terminated"]),
            bool(state["truncated"]),
            info,
        )

    def next_stage(self) -> tuple[np.ndarray, dict[str, Any]] | None:
        """Advance within the current scenario, returning None after its final stage."""
        state = self._request("NEXT")
        if bool(state.get("complete")):
            return None
        return self._state_result(state)

    def action_masks(self) -> np.ndarray:
        """Return the mask expected by sb3-contrib MaskablePPO."""
        mask = np.zeros(self.max_actions, dtype=np.bool_)
        mask[: self._action_count] = True
        return mask

    def list_actions(self) -> list[dict[str, Any]]:
        """Describe current legal actions for the human demonstration recorder."""
        response = self._request("ACTIONS")
        return list(response["actions"])

    def map_info(self) -> dict[str, Any]:
        """Return the native terrain grid used by movement and combat rules."""
        return self._request("MAP")

    def movement_path(self, unit_id: int, x: int, y: int) -> list[tuple[int, int]]:
        """Return the engine's terrain-weighted path for a legal destination."""
        response = self._request(f"PATH {int(unit_id)} {int(x)} {int(y)}")
        return [(int(cell[0]), int(cell[1])) for cell in response["path"]]

    def movement_range(self, unit_id: int) -> set[tuple[int, int]]:
        """Return terrain-weighted reachable cells for inspection, regardless of turn."""
        response = self._request(f"MOVES {int(unit_id)}")
        return {(int(cell[0]), int(cell[1])) for cell in response["moves"]}

    def movement_costs(self, unit_id: int) -> list[int]:
        """Return the unit class's movement cost for every map cell."""
        response = self._request(f"COSTS {int(unit_id)}")
        return [int(cost) for cost in response["costs"]]
    def supply_info(self) -> dict[str, Any]:
        """Return shared consumables and restorative map sites."""
        return self._request("SUPPLIES")

    def buy_item(self, item_id: str) -> dict[str, Any]:
        """Purchase one item and return the updated shop and inventory state."""
        return self._request(f"BUY {item_id}")

    def training_options(self) -> list[dict[str, Any]]:
        """Return long-absent commanders eligible for optional level catch-up."""
        return list(self._request("TRAINING")["candidates"])

    def train_commander(self, hero_id: str) -> dict[str, Any]:
        """Catch up one eligible commander with a permanent stat penalty."""
        return self._request(f"TRAIN {hero_id}")

    def resolve_duel(
        self, attacker_id: int, defender_id: int
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Resolve a configured historical duel between adjacent named units."""
        state = self._request(f"DUEL {int(attacker_id)} {int(defender_id)}")
        observation, info = self._state_result(state)
        return (
            observation,
            float(state["reward"]),
            bool(state["terminated"]),
            bool(state["truncated"]),
            info,
        )

    def notices(self) -> list[str]:
        """Drain gameplay notices such as site rewards and recovery."""
        return [str(message) for message in self._request("NOTICES")["notices"]]

    def battle_events(self, drain: bool = True) -> dict[str, Any]:
        """Read typed battle events; draining keeps the bounded pending queue small."""
        return self._request("DRAIN_EVENTS" if drain else "EVENTS")

    def use_item(self, unit_id: int, item_id: str) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Use one shared consumable and end the selected unit's action."""
        state = self._request(f"USE_ITEM {int(unit_id)} {item_id}")
        observation, info = self._state_result(state)
        return observation, float(state["reward"]), bool(state["terminated"]), bool(state["truncated"]), info

    def snapshot(self) -> dict[str, Any]:
        """Capture an exact, version-independent native battle snapshot."""
        snapshot = self._request("SNAPSHOT")
        details = {int(unit["id"]): unit for unit in self.unit_info()}
        for unit in snapshot["units"]:
            detail = details[int(unit["id"])]
            unit["name"] = str(detail["name"])
            unit["force"] = int(detail["force"])
        return snapshot

    def restore(
        self, snapshot: dict[str, Any], *, restart_process: bool = True
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Restore a previously captured native battle snapshot."""
        # Scenario assets retain unit pointers across stage loads, so title-screen
        # loads must start from a clean native process. Search rollouts within the
        # already loaded battle can opt into the faster in-process restore path.
        stage_index = int(snapshot["stage_index"])
        if restart_process:
            self._restart_process(stage_index)
        if snapshot.get("_restart_merged_stage"):
            self._request(f"RESTORE_MONEY {int(snapshot.get('money', 500))}")
            for hero_id, progress in snapshot.get("commander_progress", {}).items():
                self._request(
                    f"RESTORE_PROGRESS {hero_id} {int(progress['level'])} "
                    f"{int(progress.get('exp', 0))} {int(progress.get('training_penalty', 0))} "
                    f"{int(progress.get('last_stage', progress.get('last_chapter', 0)))}"
                )
            for item_id, count in snapshot.get("inventory", {}).items():
                self._request(f"RESTORE_ITEM {item_id} {int(count)}")
            return self._state_result(self._request("RESTORE_DONE"))
        current_units = {int(unit["id"]): unit for unit in self.unit_info()}
        saved_units = [dict(unit) for unit in snapshot["units"]]
        legacy_without_names = bool(saved_units) and all(
            not unit.get("name") for unit in saved_units
        )
        if legacy_without_names:
            # Stage 10a formerly deployed the hunters before the Chen army. Preserve
            # those saves after the hunters were converted to a scripted ambush.
            if stage_index == 13 and len(saved_units) == 10 and len(current_units) == 6:
                legacy_by_id = {int(unit["id"]): unit for unit in saved_units}
                legacy_order = (
                    (0, 0, "CaiJi101", 1),
                    (1, 5, "ChenGongZiTuo101", 4),
                    (2, 6, "ChenEscort101", 4),
                    (3, 7, "ChenEscort101", 4),
                    (4, 8, "ChenEscort101", 4),
                    (5, 9, "ChenArcher101", 4),
                    (6, 1, "CaiHunter101", 1),
                    (7, 2, "CaiHunter102", 1),
                    (8, 3, "CaiHunterArcher101", 1),
                    (9, 4, "CaiHunter103", 1),
                )
                saved_units = []
                for new_id, old_id, name, force in legacy_order:
                    unit = dict(legacy_by_id[old_id])
                    unit.update(id=new_id, name=name, force=force)
                    saved_units.append(unit)
            else:
                for unit in saved_units:
                    current = current_units.get(int(unit["id"]))
                    if current is not None:
                        unit["name"] = str(current["name"])
                        unit["force"] = int(current["force"])
        if legacy_without_names:
            corrections = {
                (0, 8, 11, 1): (17, 3),
                (0, 8, 14, 4): (17, 3),
                (0, 2, 17, 1): (16, 1),
                (0, 3, 14, 1): (15, 1),
                (0, 4, 16, 1): (17, 1),
                (0, 6, 18, 1): (15, 2),
                (12, 0, 3, 10): (3, 9),
            }
            for unit in saved_units:
                key = (stage_index, int(unit["id"]), int(unit["x"]), int(unit["y"]))
                if key in corrections:
                    unit["x"], unit["y"] = corrections[key]
        # Stage 07 changed from the old field map to a walled Dai city. Migrate
        # exact legacy deployment coordinates so old saves remain playable.
        dai_city_positions = {
            ("ZhengZhuangGong7", 4, 8): (9, 1),
            ("YingKaoShu7", 5, 9): (7, 2),
            ("GaoQuMi7", 4, 7): (11, 2),
            ("GongSunE7", 3, 8): (9, 3),
            ("YouZaiChou7", 15, 4): (14, 12),
            ("SongGuard7", 14, 2): (8, 10),
            ("SongGuard7", 12, 10): (10, 10),
            ("WeiGuard7", 15, 7): (13, 11),
            ("WeiGuard7", 16, 7): (15, 11),
            ("CaiArcher7", 14, 11): (4, 12),
        }
        if stage_index == 8:
            for unit in saved_units:
                key = (str(unit.get("name", "")), int(unit["x"]), int(unit["y"]))
                if key in dai_city_positions:
                    unit["x"], unit["y"] = dai_city_positions[key]
        # Stage 08 Queshan was rebuilt on a native 30x22 canvas. Match exact
        # legacy name/coordinate pairs so slot 1 keeps HP, EXP and turn state.
        queshan_positions = {
            ("ZhengShiZiHu8", 9, 12): (15, 19),
            ("GaoQuMi8", 8, 12): (14, 19),
            ("ZhuDan8", 10, 12): (16, 19),
            ("GongZiYuan8", 8, 11): (14, 18),
            ("GongSunDaiZhong8", 10, 11): (16, 18),
            ("DaLiang8", 16, 7): (25, 10),
            ("BeiRongWarrior8", 14, 8): (24, 11),
            ("BeiRongWarrior8", 18, 8): (26, 11),
            ("BeiRongArcher8", 16, 8): (25, 11),
            ("XiaoLiang8", 9, 3): (20, 4),
            ("BeiRongWarrior8", 8, 4): (19, 5),
            ("BeiRongWarrior8", 10, 4): (21, 5),
            ("BeiRongArcher8", 9, 4): (20, 5),
        }
        if stage_index == 11:
            for unit in saved_units:
                key = (str(unit.get("name", "")), int(unit["x"]), int(unit["y"]))
                if key in queshan_positions:
                    unit["x"], unit["y"] = queshan_positions[key]
        for saved in saved_units:
            current = current_units.get(int(saved["id"]))
            saved_name = saved.get("name")
            if current is None and not saved_name:
                raise ValueError("存档与当前关卡版本不兼容，请重新保存")
            if current is not None and saved_name and str(current["name"]) != str(saved_name):
                raise ValueError("存档单位结构与当前关卡不兼容，请重新保存")
        self._request(f"RESTORE_MONEY {int(snapshot.get('money', 500))}")
        for hero_id, progress in snapshot.get("commander_progress", {}).items():
            self._request(
                f"RESTORE_PROGRESS {hero_id} "
                f"{int(progress['level'])} {int(progress.get('exp', 0))} "
                f"{int(progress.get('training_penalty', 0))} "
                f"{int(progress.get('last_stage', progress.get('last_chapter', 0)))}"
            )
        self._request(
            "RESTORE_BEGIN "
            f"{int(snapshot['turn_current'])} {int(snapshot['current_force'])} "
            f"{int(snapshot.get('agent_actions', 0))} {int(bool(snapshot.get('truncated', False)))}"
        )
        for unit in saved_units:
            unit_id = int(unit["id"])
            state = (
                f"{int(unit['level'])} {int(unit.get('exp', 0))} "
                f"{int(unit['hp'])} {int(unit['mp'])} {int(unit['x'])} {int(unit['y'])} "
                f"{int(unit.get('direction', 4))} {int(bool(unit['done']))}"
            )
            invulnerable = int(bool(unit.get("invulnerable", False)))
            if unit_id in current_units:
                self._request(f"RESTORE_UNIT {unit_id} {state} {invulnerable}")
            elif int(unit["hp"]) > 0:
                self._request(
                    f"RESTORE_SPAWN {unit['name']} {state} {int(unit['force'])} {invulnerable}"
                )
        for item_id, count in snapshot.get("inventory", {}).items():
            self._request(f"RESTORE_ITEM {item_id} {int(count)}")
        for site_id in snapshot.get("visited_sites", []):
            self._request(f"RESTORE_VISITED {site_id}")
        state = self._request("RESTORE_DONE")
        return self._state_result(state)

    def unit_info(self) -> list[dict[str, Any]]:
        """Return native names, exact stats, terrain modifiers, and learned skills."""
        return list(self._request("UNITS")["units"])

    def story_info(self) -> dict[str, Any]:
        """Return scenario-owned cutscenes and battle presentation metadata."""
        return self._request("STORY")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._process.poll() is None:
            try:
                self._write("QUIT")
                self._process.wait(timeout=3)
            except (BrokenPipeError, OSError, subprocess.TimeoutExpired):
                self._process.terminate()
                try:
                    self._process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self._process.kill()
        super().close()

    def _state_result(self, state: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
        observation = np.asarray(state["observation"], dtype=np.float32)
        if observation.shape != self.observation_space.shape:
            raise MengdeProtocolError(
                f"observation shape {observation.shape} != {self.observation_space.shape}"
            )
        self._action_count = int(state["action_count"])
        if not 0 <= self._action_count <= self.max_actions:
            raise MengdeProtocolError(
                f"native action count {self._action_count} exceeds configured maximum {self.max_actions}"
            )
        return observation, {
            "action_count": self._action_count,
            "current_force": int(state.get("current_force", 1)),
            "turn_current": int(state.get("turn_current", 1)),
            "turn_limit": int(state.get("turn_limit", 20)),
            "status": int(state.get("status", 2)),
        }

    def _request(self, command: str) -> dict[str, Any]:
        self._write(command)
        return self._read_response()

    def _write(self, command: str) -> None:
        if self._process.stdin is None or self._process.poll() is not None:
            raise MengdeProtocolError("native mengde process is not running")
        self._process.stdin.write(command + "\n")
        self._process.stdin.flush()

    def _read_response(self) -> dict[str, Any]:
        if self._process.stdout is None:
            raise MengdeProtocolError("native process stdout is unavailable")
        while True:
            line = self._process.stdout.readline()
            if line == "":
                raise MengdeProtocolError(
                    f"native process exited unexpectedly with code {self._process.poll()}"
                )
            if not line.startswith("RL\t"):
                continue
            try:
                response = json.loads(line[3:])
            except json.JSONDecodeError as error:
                raise MengdeProtocolError(f"invalid native JSON: {error}") from error
            if "error" in response:
                raise MengdeProtocolError(str(response["error"]))
            return response

    def __enter__(self) -> "MengdeEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
