"""Train the Mirror Mode BC + GAIL + masked PPO policy for mengde."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from imitation.algorithms import bc
from imitation.algorithms.adversarial.gail import GAIL
from imitation.rewards.reward_nets import BasicRewardNet
from imitation.util.networks import RunningNorm
from sb3_contrib import MaskablePPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecEnv, VecEnvWrapper

from rl.demo_data import load_transitions
from rl.mengde_env import MengdeEnv


class MixedReward(VecEnvWrapper):
    """Blend GAIL reward with the native reward retained by imitation's wrapper."""

    def __init__(self, venv: VecEnv, imitation_strength: float, extrinsic_strength: float):
        super().__init__(venv)
        self.imitation_strength = imitation_strength
        self.extrinsic_strength = extrinsic_strength

    def reset(self):
        return self.venv.reset()

    def step_wait(self):
        observations, imitation_rewards, dones, infos = self.venv.step_wait()
        extrinsic_rewards = np.asarray(
            [info["original_env_rew"] for info in infos], dtype=np.float32
        )
        rewards = (
            self.imitation_strength * imitation_rewards
            + self.extrinsic_strength * extrinsic_rewards
        )
        return observations, rewards, dones, infos


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--demonstrations", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("rl/models/mirror_mode"))
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-actions", type=int, default=2048)
    parser.add_argument("--bc-epochs", type=int, default=20)
    parser.add_argument("--steps", type=int, default=1_000_000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    demonstrations = load_transitions(args.demonstrations)
    if len(demonstrations) == 0:
        raise ValueError("demonstration file is empty")
    if int(np.max(demonstrations.acts)) >= args.max_actions:
        raise ValueError("demonstration contains an action outside --max-actions")
    demo_batch_size = min(512, len(demonstrations))
    demo_minibatch_size = math.gcd(demo_batch_size, 128)

    def make_env() -> MengdeEnv:
        return MengdeEnv(
            args.executable,
            scenario=args.scenario,
            max_actions=args.max_actions,
        )

    venv = DummyVecEnv([make_env])
    learner = MaskablePPO(
        "MlpPolicy",
        venv,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=256,
        n_epochs=3,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.001,
        policy_kwargs={"net_arch": {"pi": [256, 256], "vf": [256, 256]}},
        seed=args.seed,
        verbose=1,
        tensorboard_log=str(args.output.parent / "tensorboard"),
    )

    bc_trainer = bc.BC(
        observation_space=venv.observation_space,
        action_space=venv.action_space,
        rng=rng,
        policy=learner.policy,
        demonstrations=demonstrations,
        batch_size=demo_batch_size,
        ent_weight=0.001,
    )
    bc_trainer.train(n_epochs=args.bc_epochs)

    reward_net = BasicRewardNet(
        observation_space=venv.observation_space,
        action_space=venv.action_space,
        normalize_input_layer=RunningNorm,
        hid_sizes=(128, 128),
    )
    gail = GAIL(
        demonstrations=demonstrations,
        demo_batch_size=demo_batch_size,
        demo_minibatch_size=demo_minibatch_size,
        gen_replay_buffer_capacity=2048,
        n_disc_updates_per_round=2,
        venv=venv,
        gen_algo=learner,
        reward_net=reward_net,
        allow_variable_horizon=True,
        log_dir=args.output.parent / "gail",
    )

    mixed_env = MixedReward(
        gail.venv_train,
        imitation_strength=1.0,
        extrinsic_strength=0.5,
    )
    gail.venv_train = mixed_env
    learner.set_env(mixed_env)
    gail.train(total_timesteps=args.steps)
    learner.save(args.output)
    print(f"模型已保存到 {args.output}.zip")


if __name__ == "__main__":
    main()
