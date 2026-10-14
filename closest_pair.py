
import random
import math
import time
import matplotlib.pyplot as plt


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# Brute Force Algorithm: O(N^2)
def brute_force(points):
    n = len(points)

    if n < 2:
        return None, None

    min_dist = float("inf")
    closest_pair = None

    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])

            if d < min_dist:
                min_dist = d
                closest_pair = (points[i], points[j])

    return min_dist, closest_pair


# Divide and Conquer Algorithm: O(N log N)
def divide_and_conquer(points):
    if len(points) < 2:
        return None, None, None

    px = sorted(points, key=lambda p: (p[0], p[1], p[2]))
    py = sorted(points, key=lambda p: (p[1], p[0], p[2]))

    root_info = {}

    def solve(px, py, is_root=False):
        n = len(px)

        if n <= 3:
            return brute_force(px)

        mid = n // 2
        left_x = px[:mid]
        right_x = px[mid:]
        mid_x = px[mid][0]

        left_ids = {p[2] for p in left_x}
        left_y = [p for p in py if p[2] in left_ids]
        right_y = [p for p in py if p[2] not in left_ids]

        d1, pair1 = solve(left_x, left_y)
        d2, pair2 = solve(right_x, right_y)

        if d1 is None or (d2 is not None and d2 < d1):
            best_dist, best_pair = d2, pair2
        else:
            best_dist, best_pair = d1, pair1

        if is_root:
            root_info["mid_x"] = mid_x
            root_info["strip_d"] = best_dist

        strip = [
            p for p in py
            if abs(p[0] - mid_x) < best_dist
        ]

        for i in range(len(strip)):
            j = i + 1

            while (
                j < len(strip)
                and strip[j][1] - strip[i][1] < best_dist
            ):
                d = distance(strip[i], strip[j])

                if d < best_dist:
                    best_dist = d
                    best_pair = (strip[i], strip[j])

                j += 1

        return best_dist, best_pair

    min_dist, closest_pair = solve(px, py, True)
    return min_dist, closest_pair, root_info


# Display the closest pair and distance
def print_result(name, result):
    d, pair = result

    if d is None:
        print(f"{name}: No valid pair (N < 2)")
        return

    p1, p2 = pair

    print(
        f"{name}: {d:.6f} | "
        f"({p1[0]:.3f}, {p1[1]:.3f}) and "
        f"({p2[0]:.3f}, {p2[1]:.3f})"
    )


# Visualize points and closest pairs
def visualize(points, brute_result, dc_result, root_info):
    plt.figure(figsize=(9, 7))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    plt.scatter(xs, ys, color="black", label="All points")

    if brute_result[1] is not None:
        a, b = brute_result[1]
        plt.plot(
            [a[0], b[0]], [a[1], b[1]],
            "r-o", linewidth=2, label="Brute Force pair"
        )

    if dc_result[1] is not None:
        a, b = dc_result[1]
        plt.plot(
            [a[0], b[0]], [a[1], b[1]],
            "b--o", linewidth=2, label="Divide & Conquer pair"
        )

    if root_info and "mid_x" in root_info:
        mid_x = root_info["mid_x"]
        d = root_info["strip_d"]

        plt.axvline(
            mid_x, color="green", linestyle=":",
            label="Dividing line"
        )

        plt.axvspan(
            mid_x - d, mid_x + d,
            color="green", alpha=0.12,
            label="Strip (width 2d)"
        )

    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.title("Closest Pair of Points")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("closest_pair_visualization.png", dpi=150)
    plt.show()


# Compare execution times for increasing input sizes
def benchmark():
    sizes = [100, 200, 400, 800, 1600, 3200]
    brute_times = []
    dc_times = []

    random.seed(42)

    print("\nPERFORMANCE COMPARISON")

    for n in sizes:
        points = [
            (random.uniform(0, 10000),
             random.uniform(0, 10000), i)
            for i in range(n)
        ]

        start = time.perf_counter()
        d1, _ = brute_force(points)
        brute_ms = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        d2, _, _ = divide_and_conquer(points)
        dc_ms = (time.perf_counter() - start) * 1000

        assert math.isclose(
            d1, d2, rel_tol=1e-9, abs_tol=1e-9
        ), "Algorithms produced different distances!"

        brute_times.append(brute_ms)
        dc_times.append(dc_ms)

        print(
            f"N={n:4d} | "
            f"Brute Force={brute_ms:.3f} ms | "
            f"Divide & Conquer={dc_ms:.3f} ms"
        )

    plt.figure(figsize=(9, 6))
    plt.plot(
        sizes, brute_times, "r-o",
        label="Brute Force O(N^2)"
    )
    plt.plot(
        sizes, dc_times, "b-o",
        label="Divide & Conquer O(N log N)"
    )

    plt.xlabel("Number of points (N)")
    plt.ylabel("Execution time (ms)")
    plt.title("Running Time Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("running_time.png", dpi=150)
    plt.show()


# Predefined test cases
TEST_CASES = {
    "1": ("Duplicate points",
          [(1, 2), (1, 2), (4, 5), (8, 9)]),

    "2": ("Collinear points",
          [(0, 0), (2, 0), (5, 0), (6, 0)]),

    "3": ("Same x coordinate",
          [(2, 1), (2, 4), (2, 2), (7, 3)]),

    "4": ("Same y coordinate",
          [(1, 3), (4, 3), (2, 3), (8, 3)]),

    "5": ("Two points",
          [(0, 0), (3, 4)]),

    "6": ("Single point",
          [(5, 5)]),

    "7": ("No points", []),

    "8": ("Fractional coordinates",
          [(0.5, 1.2), (0.7, 1.3),
           (4.4, 6.1), (2.0, 2.0)]),

    "9": ("Negative coordinates",
          [(-3, -4), (-2, -4), (5, 7), (-8, 2)])
}


# Main program
def main():
    print("\nCLOSEST PAIR OF POINTS")
    print("1. Generate random points")
    print("2. Enter my own test case")
    print("3. Run a predefined test case")

    choice = input("Choose an option (1/2/3): ").strip()
    raw_points = []

    if choice == "1":
        try:
            n = int(input("Enter N: "))

            if n < 0:
                print("N cannot be negative.")
                return

            for _ in range(n):
                x = random.randint(-100, 100)
                y = random.randint(-100, 100)
                raw_points.append((x, y))

        except ValueError:
            print("Enter a valid integer.")
            return

    elif choice == "2":
        try:
            n = int(input("Enter N: "))

            if n < 0:
                print("N cannot be negative.")
                return

            for i in range(n):
                x, y = map(
                    float,
                    input(
                        f"Enter x y for point {i + 1}: "
                    ).split()
                )
                raw_points.append((x, y))

        except ValueError:
            print("Invalid input. Enter two numbers per point.")
            return

    elif choice == "3":
        print("\nAvailable test cases:")

        for key, (name, pts) in TEST_CASES.items():
            print(f"{key}. {name} (N={len(pts)})")

        case = input("Select test case: ").strip()

        if case not in TEST_CASES:
            print("Invalid test case.")
            return

        name, raw_points = TEST_CASES[case]
        print(f"Running: {name}")

    else:
        print("Invalid choice.")
        return

    # Assign a unique ID to every point.
    points = [
        (x, y, i)
        for i, (x, y) in enumerate(raw_points)
    ]

    n = len(points)
    print(f"\nNumber of points: {n}")

    if n < 2:
        print("Brute Force: No valid pair (N < 2)")
        print("Divide & Conquer: No valid pair (N < 2)")
        print("Execution time: Not applicable")
        return

    start = time.perf_counter()
    brute_result = brute_force(points)
    brute_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    dc_dist, dc_pair, root_info = divide_and_conquer(points)
    dc_ms = (time.perf_counter() - start) * 1000

    dc_result = (dc_dist, dc_pair)

    print()
    print_result("Brute Force", brute_result)
    print_result("Divide & Conquer", dc_result)

    print(
        f"Execution time: Brute Force = {brute_ms:.3f} ms, "
        f"Divide & Conquer = {dc_ms:.3f} ms"
    )

    if math.isclose(
        brute_result[0], dc_result[0],
        rel_tol=1e-9, abs_tol=1e-9
    ):
        print("Verification: Both algorithms agree.")
    else:
        print("Verification FAILED: Results differ!")

    visualize(points, brute_result, dc_result, root_info)

    answer = input(
        "\nRun performance benchmark? (y/n): "
    ).strip().lower()

    if answer == "y":
        benchmark()


if __name__ == "__main__":
    main()
