import streamlit as st
import random
from sympy import factorint
import pandas as pd
from gmpy2 import fib

st.title("Gibonacci period calculators")

# User input for modulus
max_mod = 100
m = st.number_input(f"Enter modulus (max {max_mod}):", min_value=2, max_value=max_mod)

facs = factorint(m)
fac_str = " \\times ".join(f"{p}^{e}" for p, e in facs.items())

st.markdown(f"${m} = {fac_str}$")


# Function to generate a random color
def random_color(seed):
    random.seed(seed)
    return "#{:06x}aa".format(random.randint(0, 0xFFFFFF))


class Cell:
    def __init__(self, a, b, color):
        self.a = a
        self.b = b
        self.color = color

    def __eq__(self, lhs):
        return self.a == lhs.a and self.b == lhs.b


# Function to create a grid of colored squares
cells = []
for i in range(m):
    for j in range(m):
        color = random_color(pow(2, i) * pow(3, j))
        if i == 0 and j == 0:
            color = "#000000"
        c = Cell(i, j, color)
        if c not in cells:
            cells.append(c)
            seq = [i, j]
            while True:
                next = (seq[-1] + seq[-2]) % m
                c_next = Cell(seq[-1], next, color)
                if c_next in cells:
                    break
                seq.append(next)
                cells.append(c_next)


st.markdown(f"#### $G_0, G_1$ state pairs mod ${m}$ colored by sequence")
# for index, g in enumerate(cells):
col_count = 15
rows = int(len(cells) / col_count) + (len(cells) % col_count > 0)
for i in range(rows):
    cols_list = st.columns(col_count)
    for j in range(col_count):
        cell = i * col_count + j
        if cell >= len(cells):
            break
        c = cells[cell]
        cols_list[j].markdown(
            f"<div style='width: 49px; height: 50px; background-color: {c.color}; border: 1px solid black; display: flex; align-items: center; justify-content: center; margin: 1px;'>{c.a},{c.b}</div>",
            unsafe_allow_html=True,
        )


def find_cycle(a: int, b: int, m: int) -> tuple[int, ...]:
    sequence = [a, b]
    while True:
        next_value = (sequence[-1] + sequence[-2]) % m
        if sequence[-1] == a and next_value == b:
            break
        sequence.append(next_value)
    sequence.pop()
    n: int = len(sequence)
    return min(tuple(sequence[i:] + sequence[:i]) for i in range(n))


cycles = set()
for i in range(m):
    for j in range(m):
        c = find_cycle(i, j, m)
        cycles.add(c)

# Example computed results
data = {
    "Value": list(len(c) for c in cycles),
    "Cycle": list(cycles),
}
df = pd.DataFrame(data)


# Define a function to apply conditional formatting
def highlight_fibonacci_lucas(row):
    cycle: list = row["Cycle"]
    if len(cycle) < 2:
        return [""] * len(row)

    a, b = row["Cycle"][:2]
    clr = random_color(pow(2, a) * pow(3, b))
    return [f"background-color: {clr}"] * len(row)


# Apply the conditional formatting
styled_df = df.style.apply(highlight_fibonacci_lucas, axis=1)

st.write(f"#### Cycle lengths for {m}")
st.dataframe(styled_df)

st.write("#### Frequencies")
st.bar_chart(df.set_index("Value"))


def solve_modular_equations(a, b, p):
    # Calculate Fibonacci numbers
    F_n = fib(p)
    F_n_minus_1 = fib(p - 1)
    solutions = []
    for m in range(3, 3000):
        # Check the first equation
        G_n = (b * F_n + a * F_n_minus_1) % m
        if G_n != a:
            continue

        # Check the second equation
        G_n_plus_1 = ((b + a) * F_n + b * F_n_minus_1) % m
        if G_n_plus_1 == b:
            solutions.append(m)

    return solutions


### Modular equasion solver
st.markdown("$G_n = b\\cdot F_n + a\\cdot F_{n-2} \\equiv a \\pmod{m}$")
st.markdown("$G_{n+1} = (b+ a)\\cdot F_n + b\\cdot F_{n-1} \\equiv b \\pmod{m}$")

a = st.number_input("a =", min_value=0, max_value=30)
b = st.number_input("b =", min_value=0, max_value=30, value=1)
p = st.number_input("n =", min_value=0, max_value=300, value=24)

if st.button("Solve"):
    st.markdown(
        f"Moduli with period $p\\cdot k={p}$ for Gibonacci sequence $G_0={a},G_1={b}$"
    )
    solutions = solve_modular_equations(a, b, p)
    if solutions:
        st.write(f"Solutions for m: {solutions}")
    else:
        st.write("No solutions found.")
