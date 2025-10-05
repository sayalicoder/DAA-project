from flask import Flask, render_template, request, flash, redirect, url_for
import math

app = Flask(__name__)
app.secret_key = "tsp_secret_key"

# ------------------------------
# Held–Karp Algorithm (DP + bitmask)
# ------------------------------
def tsp_dynamic_programming(dist):
    n = len(dist)
    ALL = 1 << n
    INF = float('inf')

    dp = [[INF] * n for _ in range(ALL)]
    parent = [[-1] * n for _ in range(ALL)]

    dp[1][0] = 0  # Start from city 0

    for mask in range(ALL):
        for u in range(n):
            if not (mask & (1 << u)):
                continue
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                if mask & (1 << v):
                    continue
                new_mask = mask | (1 << v)
                new_cost = dp[mask][u] + dist[u][v]
                if new_cost < dp[new_mask][v]:
                    dp[new_mask][v] = new_cost
                    parent[new_mask][v] = u

    full_mask = ALL - 1
    min_cost = INF
    last_city = -1

    if n == 1:
        return 0, [0, 0]

    for i in range(1, n):
        if dp[full_mask][i] == INF:
            continue
        cost = dp[full_mask][i] + dist[i][0]
        if cost < min_cost:
            min_cost = cost
            last_city = i

    if last_city == -1:
        return None, []

    path = []
    mask = full_mask
    city = last_city

    while city != -1:
        path.append(city)
        next_city = parent[mask][city]
        mask ^= (1 << city)
        city = next_city

    path.append(0)
    path.reverse()

    return min_cost, path


# ------------------------------
# Helpers
# ------------------------------
def parse_matrix(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    matrix = []
    for ln in lines:
        parts = [p.strip() for p in ln.split(',') if p.strip()]
        row = []
        for p in parts:
            try:
                row.append(float(p) if '.' in p else int(p))
            except ValueError:
                raise ValueError(f"Invalid number: {p}")
        matrix.append(row)
    if any(len(r) != len(matrix) for r in matrix):
        raise ValueError("Matrix must be square")
    return matrix


# ------------------------------
# Routes
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    result_cost, result_path, matrix_table = None, None, None
    example = "0,10,15,20\n10,0,35,25\n15,35,0,30\n20,25,30,0"

    if request.method == 'POST':
        text = request.form.get('matrix', '')
        try:
            matrix = parse_matrix(text)
            n = len(matrix)

            if n > 14:
                flash("Warning: n > 14 may be very slow!", "error")

            result_cost, result_path = tsp_dynamic_programming(matrix)
            matrix_table = [[str(x) for x in row] for row in matrix]
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('index'))

        return render_template(
            "index.html",
            example=text,
            matrix_table=matrix_table,
            n=len(matrix),
            result_cost=result_cost,
            result_path=result_path
        )

    return render_template("index.html", example=example)


if __name__ == '__main__':
    app.run(debug=True)
