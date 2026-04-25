from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.parser import parse_input_text
from solvers.forward_chaining import solve_forward_chaining
from solvers.backward_chaining import solve_backward_chaining
from solvers.a_star import solve_a_star
from solvers.brute_force import solve_brute_force
from solvers.backtracking import solve_backtracking
from utils.io import format_solution, save_text_output
from utils.tracer import Tracer


def _list_input_files() -> list[Path]:
    input_dir = Path("../input")
    if not input_dir.exists():
        return []
    return sorted(input_dir.glob("*.txt"))


def _render_sidebar() -> tuple[str | None, str | None]:
    st.sidebar.header("Input Files")
    files = _list_input_files()
    if not files:
        st.sidebar.info("No .txt file found in ./input")
        return None, None

    selected = st.sidebar.selectbox("Input file", files, format_func=lambda p: p.name)
    content = selected.read_text(encoding="utf-8")
    return selected.name, content


def main() -> None:
    st.set_page_config(page_title="Futoshiki Solver", layout="wide")
    st.markdown(
        """
        <style>
        div[data-testid="stTextArea"] textarea {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
            white-space: pre !important;
            line-height: 1.45 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Futoshiki Solver - Streamlit")
    
    # Thêm Selectbox chọn Solver
    solver_options = {
        "Forward Chaining": solve_forward_chaining,
        "Backward Chaining (SLD Resolution)": solve_backward_chaining,
        "A* Search (with AC-3)": solve_a_star,
        "Brute-Force": solve_brute_force,
        "Backtracking (with MRV)": solve_backtracking,
    }
    selected_solver_name = st.sidebar.selectbox("Select Solver Algorithm", list(solver_options.keys()))
    show_trace = st.sidebar.checkbox("Show inference steps", value=True)
    trace_cap = st.sidebar.number_input(
        "Max steps to display", min_value=100, max_value=50000, value=5000, step=500,
        disabled=not show_trace,
    )
    st.caption(f"Current solver: {selected_solver_name}")

    if "solved_text" not in st.session_state:
        st.session_state.solved_text = ""
    if "output_name" not in st.session_state:
        st.session_state.output_name = ""
    if "trace_text" not in st.session_state:
        st.session_state.trace_text = ""

    file_name, raw_input = _render_sidebar()

    solve_clicked = st.button("Solve", disabled=not raw_input)
    validate_clicked = st.button("Validate Input", disabled=not raw_input)

    if raw_input and solve_clicked:
        try:
            puzzle = parse_input_text(raw_input)
            tracer = Tracer(enabled=show_trace, cap=int(trace_cap))
            with st.spinner("Solving..."):
                import time
                start_t = time.time()
                solve_func = solver_options[selected_solver_name]
                solved = solve_func(puzzle, tracer=tracer)
                end_t = time.time()
            st.session_state.trace_text = tracer.render() if show_trace else ""
                
            if solved is None:
                st.error("No valid solution found.")
            else:
                st.success(f"Solved in {end_t - start_t:.4f} seconds!")
                rendered = format_solution(puzzle, solved)
                st.session_state.solved_text = rendered

                output_dir = Path("../output")
                output_dir.mkdir(parents=True, exist_ok=True)
                if file_name and file_name.startswith("input-"):
                    output_name = file_name.replace("input-", "output-")
                else:
                    output_name = f"output-{file_name}"
                output_path = output_dir / output_name
                save_text_output(output_path, rendered)
                st.session_state.output_name = output_name
                st.success(f"Saved to {output_path}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Cannot solve input: {exc}")

    if raw_input and validate_clicked:
        try:
            puzzle_preview = parse_input_text(raw_input)
            st.success(f"Valid format. N = {puzzle_preview.size}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Input is invalid: {exc}")

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Input")
        if raw_input:
            st.text_area("Input content", raw_input, height=420, disabled=True)
        else:
            st.info("No input file found in ./input. Please add your input files there.")

    with right_col:
        st.subheader("Output")
        st.text_area("Solved result", st.session_state.solved_text, height=420, disabled=True)

        if st.session_state.solved_text and st.session_state.output_name:
            st.download_button(
                label="Download output",
                data=st.session_state.solved_text + "\n",
                file_name=st.session_state.output_name,
                mime="text/plain",
            )

    if st.session_state.trace_text:
        with st.expander(f"Inference steps ({selected_solver_name})", expanded=False):
            st.text_area(
                "Trace",
                st.session_state.trace_text,
                height=420,
                disabled=True,
                label_visibility="collapsed",
            )
            st.download_button(
                label="Download trace",
                data=st.session_state.trace_text + "\n",
                file_name="trace.txt",
                mime="text/plain",
            )


if __name__ == "__main__":
    main()
