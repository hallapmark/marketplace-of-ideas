import sys
from .simulation import SimulationConfiguration
from .simulations import setup_sims

mill_configs = [
    SimulationConfiguration(
        agents_n=30,
        p_start_belief=0.3,
        rounds_of_play=rounds,
        mrb=3,
        tw=tw,
        atrophy_p=atrophy_p,
        output_p=output_p,
    )
    for tw in (0.05, 0.1, 0.15)
    for rounds in (20,)
    for atrophy_p in (0, 0.2)
    for output_p in (0.6, 1)
]

disinfo_configs = [
    SimulationConfiguration(
        agents_n=30,
        p_start_belief=0.3,
        rounds_of_play=rounds,
        mrb=3,
        tw=tw,
        atrophy_p=atrophy_p,
        output_p=output_p,
        disinfo_agents_n=disinfo_agents,
        disinfo_broadcast_capability=disinfo_broadcast_capability,
    )
    for tw in (0.05, 0.1)
    for rounds in (20,)
    for atrophy_p in (0,)
    for output_p in (0.6,)
    for disinfo_agents in (10,)
    for disinfo_broadcast_capability in (30,)
]


# CMDLINE
def main(argv=None):
    # if argv is None:
    #     argv = sys.argv[1:]

    # args = parse_args(argv)
    # eval_args = EvalArgs(
    # )
    # TODO: sim_n and output_path as cmdline arguments

    sim_n = 300

    # Might take a couple of hours to run
    setup_sims(mill_configs, "results/mill.csv", sim_n)
    setup_sims(disinfo_configs, "results/disinfo_mill.csv", sim_n)


if __name__ == "__main__":
    main()
