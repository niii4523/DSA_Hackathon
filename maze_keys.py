"""Maze with Keys and Doors - BFS over states (row, col, key_bitmask).
Usage:
  python maze_keys.py T --csv maze.csv [--out solved.csv]
  python maze_keys.py T --gen N [--seed 7] [--out solved.csv]
  add  --viz            to open the animated visualization window
  add  --save f.gif|f.png  to save the animation / final frame (use with or without --viz)
  add  --speed MS       milliseconds per step (default 300)
"""
import sys, csv, random
from collections import deque

# 'E' is the exit, so the door for key 'e' is written '@' (A,B,C,D,@,F)
DOOR = {'A': 0, 'B': 1, 'C': 2, 'D': 3, '@': 4, 'F': 5}
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def solve(g):
    """Return (length, path[(r,c)...]) or (-1, [])."""
    n = len(g)
    s = e = None
    for i in range(n):
        for j in range(len(g[i])):
            if g[i][j] == 'S': s = (i, j)
            elif g[i][j] == 'E': e = (i, j)
    if s is None or e is None:
        return -1, []
    start = (s[0], s[1], 0)
    par = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        r, c, m = cur
        if (r, c) == e:                       # first arrival at E is shortest (BFS)
            path = []
            while cur:
                path.append(cur[:2]); cur = par[cur]
            return len(path) - 1, path[::-1]
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < n and 0 <= nc < len(g[nr])):
                continue
            ch = g[nr][nc]
            if ch == '#':
                continue
            nm = m
            if 'a' <= ch <= 'f':
                nm |= 1 << (ord(ch) - 97)     # pick up key
            elif ch in DOOR and not (m >> DOOR[ch]) & 1:
                continue                      # locked door
            st = (nr, nc, nm)
            if st not in par:
                par[st] = cur
                q.append(st)
    return -1, []


def generate(n, T, seed=None, wall_p=0.25):
    rnd = random.Random(seed)
    while True:
        g = [['#' if rnd.random() < wall_p else '.' for _ in range(n)] for _ in range(n)]
        cells = [(i, j) for i in range(n) for j in range(n)]
        if len(cells) < 2 + 2 * T:
            raise ValueError("grid too small for T keys + T doors")
        pick = rnd.sample(cells, 2 + 2 * T)
        g[pick[0][0]][pick[0][1]] = 'S'
        g[pick[1][0]][pick[1][1]] = 'E'
        for k in range(T):
            kr, kc = pick[2 + 2 * k]; dr, dc = pick[3 + 2 * k]
            g[kr][kc] = chr(97 + k); g[dr][dc] = '@' if k == 4 else chr(65 + k)
        if solve(g)[0] != -1:                 # guarantee solvable
            return g
        wall_p = max(0.05, wall_p - 0.005)    # relax walls slowly so we always terminate


def mark(g, path):
    out = [row[:] for row in g]
    for r, c in path:
        if out[r][c] == '.':                  # keep S, E, keys, doors visible
            out[r][c] = 'x'
    return out


KEY_COLORS = ['#1f77b4', '#ff7f0e', '#9467bd', '#17becf', '#e377c2', '#8c564b']


def visualize(g, path, length, save=None, show=True, interval=300):
    """Animated matplotlib view: path highlight, key pick-ups with inventory
    panel, doors turning white with an open-padlock mark."""
    import matplotlib
    if save and not show:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.patches import Rectangle, Circle, Arc

    n = len(g)
    types = sorted({ord(c) - 97 for row in g for c in row if 'a' <= c <= 'f'})
    fig, (ax, inv) = plt.subplots(1, 2, figsize=(10, 6), gridspec_kw={'width_ratios': [4, 1]})

    def state(k):
        picked, opened = set(), set()
        for r, c in path[:k + 1]:
            ch = g[r][c]
            if 'a' <= ch <= 'f': picked.add(ord(ch) - 97)
            elif ch in DOOR: opened.add(DOOR[ch])
        return picked, opened

    def draw(k):
        ax.clear(); inv.clear()
        picked, opened = state(k)
        ax.set_xlim(0, max(len(r) for r in g)); ax.set_ylim(n, 0)
        ax.set_aspect('equal'); ax.axis('off')
        for r in range(n):
            for c, ch in enumerate(g[r]):
                face = 'white'
                if ch == '#': face = 'black'
                elif ch == 'S': face = '#2ca02c'
                elif ch == 'E': face = '#d62728'
                elif ch in DOOR and DOOR[ch] not in opened: face = KEY_COLORS[DOOR[ch]]
                ax.add_patch(Rectangle((c, r), 1, 1, fc=face, ec='#bbbbbb', lw=.5))
                if ch in 'SE':
                    ax.text(c + .5, r + .5, ch, ha='center', va='center', color='white', weight='bold')
                elif 'a' <= ch <= 'f' and ord(ch) - 97 not in picked:      # key still on the floor
                    ax.add_patch(Circle((c + .5, r + .5), .3, fc=KEY_COLORS[ord(ch) - 97], ec='k'))
                    ax.text(c + .5, r + .5, ch, ha='center', va='center', color='white', weight='bold')
                elif ch in DOOR:
                    if DOOR[ch] in opened:                                  # unlocked: padlock with open shackle
                        ax.add_patch(Rectangle((c + .3, r + .5), .4, .3, fc='#2ca02c', ec='k'))
                        ax.add_patch(Arc((c + .4, r + .5), .2, .3, theta1=180, theta2=360, lw=2))
                    else:
                        ax.text(c + .5, r + .5, ch, ha='center', va='center', color='white', weight='bold')
        if path:
            ys = [r + .5 for r, _ in path[:k + 1]]; xs = [c + .5 for _, c in path[:k + 1]]
            ax.plot(xs, ys, color='royalblue', lw=3, alpha=.7)
            ax.plot(xs[-1], ys[-1], 'o', color='gold', mec='k', ms=10)
        ax.set_title(f"Step {k}/{length}" if path else "No path (-1)")
        inv.set_xlim(0, 1.2); inv.set_ylim(len(types) + 1, 0); inv.set_aspect('equal'); inv.axis('off')
        inv.set_title("Key inventory")
        for i, t in enumerate(types):
            have = t in picked
            inv.add_patch(Circle((.25, i + .8), .3, fc=KEY_COLORS[t] if have else 'white', ec=KEY_COLORS[t], lw=2))
            inv.text(.25, i + .8, chr(97 + t), ha='center', va='center', weight='bold', color='white' if have else KEY_COLORS[t])
            inv.text(.65, i + .8, 'held' if have else '-', va='center')

    frames = max(len(path), 1)
    if save and save.lower().endswith('.png'):
        draw(frames - 1); fig.savefig(save, dpi=120); print("saved", save)
    elif save or show:
        ani = FuncAnimation(fig, draw, frames=frames, interval=interval, repeat=False)
        if save:
            ani.save(save, writer='pillow', fps=max(1, 1000 // interval)); print("saved", save)
        if show:
            plt.show()
    plt.close(fig)


def main(a):
    T = int(a[0])
    opt = lambda f: a[a.index(f) + 1] if f in a else None
    if opt('--csv'):
        with open(opt('--csv'), newline='') as f:
            g = [[x.strip() for x in row] for row in csv.reader(f) if row]
    else:
        g = generate(int(opt('--gen') or 10), T, int(opt('--seed')) if opt('--seed') else None)
        with open('maze.csv', 'w', newline='') as f:
            csv.writer(f).writerows(g)
    L, path = solve(g)
    print(L)
    if '--viz' in a or opt('--save'):
        visualize(g, path, L, save=opt('--save'), show='--viz' in a,
                  interval=int(opt('--speed') or 300))
    if L != -1:
        with open(opt('--out') or 'solved.csv', 'w', newline='') as f:
            csv.writer(f).writerows(mark(g, path))


if __name__ == '__main__':
    main(sys.argv[1:])