from __future__ import annotations

import operator
from collections.abc import Callable

import streamlit as st


OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "−": operator.sub,
    "×": operator.mul,
    "÷": operator.truediv,
}


def calculate(first: float, second: float, operation: str) -> float:
    if operation not in OPERATIONS:
        raise ValueError(f"Unsupported operation: {operation}")
    if operation == "÷" and second == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return OPERATIONS[operation](first, second)


def format_number(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.12g}"


def reset_calculator() -> None:
    st.session_state.display = "0"
    st.session_state.stored_value = None
    st.session_state.pending_operation = None
    st.session_state.start_new_number = True


def input_digit(digit: str) -> None:
    if st.session_state.display == "Error":
        reset_calculator()
    if st.session_state.start_new_number:
        st.session_state.display = digit
        st.session_state.start_new_number = False
    elif st.session_state.display == "0":
        st.session_state.display = digit
    elif len(st.session_state.display) < 16:
        st.session_state.display += digit


def input_decimal() -> None:
    if st.session_state.display == "Error":
        reset_calculator()
    if st.session_state.start_new_number:
        st.session_state.display = "0."
        st.session_state.start_new_number = False
    elif "." not in st.session_state.display:
        st.session_state.display += "."


def choose_operation(operation: str) -> None:
    if st.session_state.display == "Error":
        reset_calculator()
        return

    current = float(st.session_state.display)
    stored = st.session_state.stored_value
    pending = st.session_state.pending_operation

    if stored is not None and pending and not st.session_state.start_new_number:
        try:
            stored = calculate(stored, current, pending)
            st.session_state.display = format_number(stored)
        except (ZeroDivisionError, OverflowError):
            st.session_state.display = "Error"
            st.session_state.stored_value = None
            st.session_state.pending_operation = None
            st.session_state.start_new_number = True
            return
    else:
        stored = current

    st.session_state.stored_value = stored
    st.session_state.pending_operation = operation
    st.session_state.start_new_number = True


def show_result() -> None:
    stored = st.session_state.stored_value
    pending = st.session_state.pending_operation
    if stored is None or not pending or st.session_state.display == "Error":
        return

    try:
        result = calculate(stored, float(st.session_state.display), pending)
        st.session_state.display = format_number(result)
    except (ZeroDivisionError, OverflowError):
        st.session_state.display = "Error"

    st.session_state.stored_value = None
    st.session_state.pending_operation = None
    st.session_state.start_new_number = True


def backspace() -> None:
    if st.session_state.display == "Error" or st.session_state.start_new_number:
        st.session_state.display = "0"
        return
    st.session_state.display = st.session_state.display[:-1] or "0"


def toggle_sign() -> None:
    if st.session_state.display not in {"0", "Error"}:
        st.session_state.display = (
            st.session_state.display[1:]
            if st.session_state.display.startswith("-")
            else f"-{st.session_state.display}"
        )


def percent() -> None:
    if st.session_state.display != "Error":
        st.session_state.display = format_number(float(st.session_state.display) / 100)


st.set_page_config(page_title="Basic Calculator", page_icon="🧮", layout="centered")

for key, default in {
    "display": "0",
    "stored_value": None,
    "pending_operation": None,
    "start_new_number": True,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(145deg, #eef2ff 0%, #f8fafc 55%, #e0f2fe 100%);
        }
        .block-container {
            max-width: 430px;
            padding-top: 3rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #111827;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1.5rem;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
            padding: 0.4rem 0.55rem 0.7rem;
        }
        .calculator-name {
            color: #94a3b8;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            margin-bottom: 0.6rem;
            text-transform: uppercase;
        }
        .calculator-display {
            color: #334155;
            font-size: clamp(2.6rem, 12vw, 4rem);
            font-weight: 500;
            line-height: 1.15;
            min-height: 4.7rem;
            overflow: hidden;
            text-align: right;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .operation-indicator {
            color: #38bdf8;
            font-size: 1rem;
            min-height: 1.5rem;
            text-align: right;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.55rem;
        }
        div.stButton > button {
            background: #273449;
            border: 0;
            border-radius: 1rem;
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 650;
            height: 3.8rem;
            transition: transform 100ms ease, background 100ms ease;
            width: 100%;
        }
        div.stButton > button:hover {
            background: #334155;
            border: 0;
            color: white;
            transform: translateY(-1px);
        }
        div.stButton > button:active {
            transform: translateY(1px);
        }
        div[data-testid="stColumn"]:last-child div.stButton > button {
            background: #0284c7;
        }
        div[data-testid="stColumn"]:last-child div.stButton > button:hover {
            background: #0ea5e9;
        }
        .helper-text {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 1rem;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

button_rows = [
    [("C", reset_calculator, None), ("⌫", backspace, None), ("%", percent, None), ("÷", choose_operation, "÷")],
    [("7", input_digit, "7"), ("8", input_digit, "8"), ("9", input_digit, "9"), ("×", choose_operation, "×")],
    [("4", input_digit, "4"), ("5", input_digit, "5"), ("6", input_digit, "6"), ("−", choose_operation, "−")],
    [("1", input_digit, "1"), ("2", input_digit, "2"), ("3", input_digit, "3"), ("+", choose_operation, "+")],
    [("±", toggle_sign, None), ("0", input_digit, "0"), (".", input_decimal, None), ("=", show_result, None)],
]

with st.container(border=True):
    st.markdown('<div class="calculator-name">Basic calculator</div>', unsafe_allow_html=True)
    indicator = st.session_state.pending_operation or "&nbsp;"
    st.markdown(
        f'<div class="operation-indicator">{indicator}</div>'
        f'<div class="calculator-display">{st.session_state.display}</div>',
        unsafe_allow_html=True,
    )

    for row_index, row in enumerate(button_rows):
        columns = st.columns(4)
        for column, (label, callback, argument) in zip(columns, row):
            with column:
                kwargs = {"on_click": callback, "use_container_width": True}
                if argument is not None:
                    kwargs["args"] = (argument,)
                st.button(label, key=f"key-{row_index}-{label}", **kwargs)

st.markdown(
    '<div class="helper-text">Use the buttons to enter a calculation.</div>',
    unsafe_allow_html=True,
)
