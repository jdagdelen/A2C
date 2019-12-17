from gym.envs.registration import register

register(
    id='Open-Pit-Mine-v0',
    entry_point='envs.opm_env:OpenPitEnv',
)