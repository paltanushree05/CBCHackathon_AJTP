# engine/greedy_insert.py
from .sort_edf import sort_by_edf, sort_pantries_by_close
from .feasibility import is_feasible

def greedy_insert(donations, pantries, drivers, time_matrix):
    sorted_donations = sort_by_edf(donations)
    sorted_pantries  = sort_pantries_by_close(pantries)
    assignments      = []
    unroutable       = []

    n_donations = len(donations)

    for donation in sorted_donations:
        best_cost       = float("inf")
        best_assignment = None

        for driver in drivers:
            for p_idx, pantry in enumerate(sorted_pantries):
                d_idx       = donation["id"] - 1
                matrix_idx  = n_donations + p_idx  # pantries start after donations in matrix
                travel_time = time_matrix[d_idx][matrix_idx]

                if is_feasible(driver, pantry, donation, travel_time):
                    cost = travel_time
                    if cost < best_cost:
                        best_cost       = cost
                        best_assignment = {
                            "driver":          driver,
                            "pantry":          pantry,
                            "donation":        donation,
                            "travel_time_min": round(travel_time / 60, 1)
                        }

        if best_assignment:
            assignments.append(best_assignment)
            best_assignment["driver"]["current_load"] += donation["quantity"]
        else:
            unroutable.append(donation)

    return assignments, unroutable