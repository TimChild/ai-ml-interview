from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class State:
    # shared state passed between nodes
    sim_inputs: dict[str, Any]  # e.g., {"Q_in": ..., "Q_out": ..., "m": ..., "cp": ..., "dt": ...}
    sim_outputs: dict[str, Any]  # e.g., {"dT_measured": ...}
    analysis: dict[str, Any]  # freeform fields from the "LLM"
    decision: str | None = None  # "accept" | "reject" | "retry"


def _do_calculation(**kwargs):
    # stub for complex calculation
    return {
        "Q_out": kwargs.get("Q_in", 0) * 0.98,  # assume 2% loss
        "dT_measured": 0.02,
    }


def retrieve_sim_results(state: State) -> State:
    # Stub for a real sim fetch (e.g., from CFD/ANSYS results)

    result = _do_calculation(
        q_in=state.sim_inputs.get("Q_in"),
        m=state.sim_inputs.get("m"),
        cp=state.sim_inputs.get("cp"),
        dt=state.sim_inputs.get("dt"),
        tol=state.sim_inputs.get("tol"),
    )

    state.sim_outputs["Q_out"] = result["Q_out"]  # e.g., heat outflow from sim
    state.sim_outputs["dT_measured"] = result[
        "dT_measured"
    ]  # e.g., observed temp rise from sensors
    return state


def llm_analyze(state: State) -> State:
    q_in = state.sim_inputs["Q_in"]
    q_out = state.sim_outputs["Q_out"]
    _ = state.sim_outputs["dT_measured"]

    # This is where an LLM call should be made.

    state.analysis["net"] = q_in - q_out
    state.analysis["summary"] = "System appears energy-positive; proceed."
    return state


def physics_guardrail(state: State) -> State:
    m = state.sim_inputs["m"]
    cp = state.sim_inputs["cp"]
    dt = state.sim_inputs["dt"]
    Qin = state.sim_inputs["Q_in"]
    Qout = state.sim_outputs["Q_out"]
    dT = state.sim_outputs["dT_measured"]

    # Check conservation-ish constraint: ΔE = m*cp*ΔT should match (Q_in - Q_out)*dt (very simplified).
    lhs = m * cp * dT  # observed energy change
    rhs = (Qin - Qout) * dt  # predicted by flows
    resid = lhs - rhs

    state.analysis["energy_residual"] = resid
    state.analysis["constraint_ok"] = abs(resid) < state.sim_inputs.get("tol", 1e-2)
    return state


def decide(state: State) -> State:
    if state.analysis.get("constraint_ok"):
        state.decision = "accept"
    else:
        state.decision = "retry"
    return state


GRAPH: dict[str, Callable[[State], State]] = {
    "retrieve": retrieve_sim_results,
    "analyze": llm_analyze,
    "guard": physics_guardrail,
    "decide": decide,
}


def run_graph(initial: State) -> State:
    state = initial
    for node in ["retrieve", "analyze", "guard", "decide"]:
        state = GRAPH[node](state)
    return state


if __name__ == "__main__":
    init = State(
        sim_inputs={
            "Q_in": 100.0,
            "m": 10.0,
            "cp": 4.0,
            "dt": 1.0,
            "tol": 0.5,
        },
        sim_outputs={},
        analysis={},
    )
    final = run_graph(init)
    print(final)
