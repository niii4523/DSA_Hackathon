"""Run:  python test_maze.py        (no extra libraries needed)"""
import random, time, unittest
from collections import deque
from maze_keys import solve, generate, mark, DOOR


def G(s):
    return [list(r.replace(' ', '')) for r in s.strip().splitlines()]


def brute(g):
    """Independent checker: BFS where state = (cell, frozenset of keys)."""
    n = len(g)
    pos = {g[i][j]: (i, j) for i in range(n) for j in range(n) if g[i][j] in 'SE'}
    if 'S' not in pos or 'E' not in pos:
        return -1
    inv = {v: k for k, v in DOOR.items()}           # key index -> door char
    start = (pos['S'], frozenset())
    dist = {start: 0}
    q = deque([start])
    while q:
        (r, c), keys = q.popleft()
        if (r, c) == pos['E']:
            return dist[((r, c), keys)]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < n and 0 <= nc < n) or g[nr][nc] == '#':
                continue
            ch, nk = g[nr][nc], keys
            if ch.islower():
                nk = keys | {ord(ch) - 97}
            elif ch in DOOR and DOOR[ch] not in keys:
                continue
            st = ((nr, nc), nk)
            if st not in dist:
                dist[st] = dist[((r, c), keys)] + 1
                q.append(st)
    return -1


class Cases(unittest.TestCase):
    def L(self, s):
        return solve(G(s))[0]

    def test_no_doors(self):            self.assertEqual(self.L("S.E"), 2)
    def test_adjacent(self):            self.assertEqual(self.L("SE"), 1)
    def test_detour_for_key(self):      self.assertEqual(self.L("SAE\n.#.\n.a."), 6)
    def test_door_blocks_no_key(self):  self.assertEqual(self.L("SAE"), -1)
    def test_key_missing(self):         self.assertEqual(self.L("S.A.E\n#####"), -1)
    def test_key_behind_own_door(self): self.assertEqual(self.L("SA#\n#a.\n..E"), -1)
    def test_exit_walled(self):         self.assertEqual(self.L("S#E"), -1)
    def test_no_start(self):            self.assertEqual(self.L("..E\n..."), -1)
    def test_no_exit(self):             self.assertEqual(self.L("S..\n..."), -1)
    def test_wrong_door_key(self):      self.assertEqual(self.L("aSBE\n####"), -1)
    def test_key_not_consumed(self):    # pass the same door twice
        self.assertEqual(self.L("aSAE\n####"), 4)  # a,S,A,E in a row
    def test_backtrack_needed(self):    # key in a dead end, door on the way
        self.assertEqual(self.L("a#E\nSA.\n..."), 5)
    def test_chain_order(self):         # key b locked behind door A, key a free
        g = "SaAbBE"
        self.assertEqual(self.L(g), 5)
    def test_chain_wrong_order(self):   # needs b before a, a behind B
        self.assertEqual(self.L("SBbaAE"), -1)
    def test_door_E_symbol(self):       # key e opens '@' (E is the exit)
        self.assertEqual(self.L("Se@E"), 3)
        self.assertEqual(self.L("S@eE"), -1)
    def test_all_six(self):
        self.assertEqual(self.L("SabcdefABCD@FE"), 13)
    def test_2x2(self):                 self.assertEqual(self.L("SE\n.."), 1)
    def test_shortest_not_first(self):  # two routes, short one needs a key
        self.assertEqual(self.L("SaA..E"), 5)
    def test_long_route_when_short_locked(self):
        self.assertEqual(self.L("S.#.E\n.#A#.\n....."), 8)

    def test_mark(self):
        g = G("SAE\n.#.\n.a.")
        L, p = solve(g)
        m = mark(g, p)
        self.assertEqual(m[0][1], 'A'); self.assertEqual(m[2][1], 'a')
        self.assertEqual(m[0][0], 'S'); self.assertEqual(m[0][2], 'E')
        self.assertEqual(sum(r.count('x') for r in m), 4)    # path cells that were '.'


class Generator(unittest.TestCase):
    def test_valid_for_all_T(self):
        for T in range(1, 7):
            for seed in range(15):
                g = generate(12, T, seed)
                flat = [c for r in g for c in r]
                self.assertEqual(flat.count('S'), 1)
                self.assertEqual(flat.count('E'), 1)
                for k in range(T):
                    self.assertEqual(flat.count(chr(97 + k)), 1)
                    self.assertEqual(flat.count('@' if k == 4 else chr(65 + k)), 1)
                self.assertNotEqual(solve(g)[0], -1)

    def test_too_small(self):
        with self.assertRaises(ValueError): generate(3, 6, 1)


class CrossCheck(unittest.TestCase):
    def test_random_vs_independent(self):
        rnd = random.Random(42)
        for _ in range(400):
            n, T = rnd.randint(2, 7), rnd.randint(1, 3)
            g = [['#' if rnd.random() < .3 else '.' for _ in range(n)] for _ in range(n)]
            cells = rnd.sample([(i, j) for i in range(n) for j in range(n)], min(n * n, 2 + 2 * T))
            if len(cells) < 2 + 2 * T: continue
            g[cells[0][0]][cells[0][1]] = 'S'; g[cells[1][0]][cells[1][1]] = 'E'
            for k in range(T):
                g[cells[2 + 2 * k][0]][cells[2 + 2 * k][1]] = chr(97 + k)
                g[cells[3 + 2 * k][0]][cells[3 + 2 * k][1]] = chr(65 + k)
            self.assertEqual(solve(g)[0], brute(g), g)


def benchmark():
    print("\nTiming (T=6, random mazes):")
    for n in (10, 50, 100, 200):
        g = generate(n, 6, 1, wall_p=0.2)
        t = time.perf_counter(); L, _ = solve(g); dt = time.perf_counter() - t
        print(f"  N={n:4d}  length={L:5d}  time={dt*1000:9.2f} ms")


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1)
    if r.result.wasSuccessful():
        benchmark()
