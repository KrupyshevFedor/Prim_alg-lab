import heapq
import itertools
import random
from collections import deque


def build_graph(edges, vertices=None):
    graph = {}
    for v in vertices or []:
        graph[v] = []
    for u, v, w in edges:
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, []).append((u, w))
    return graph


def prim_mst(graph, start=None):
    if not graph:
        return [], 0

    if start is None:
        start = next(iter(graph))

    visited = {start}
    mst_edges = []
    total = 0

    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)

    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)

        if v in visited:
            continue

        visited.add(v)
        mst_edges.append((u, v, w))
        total += w

        for to, weight in graph[v]:
            if to not in visited:
                heapq.heappush(heap, (weight, v, to))

    if len(visited) != len(graph):
        raise ValueError("Граф несвязный: остовного дерева не существует")

    return mst_edges, total


def has_cycle(vertices, edges):
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v, _ in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return True
        parent[ru] = rv
    return False


def is_connected(vertices, edges):
    vertices = list(vertices)
    if not vertices:
        return True

    adj = {v: [] for v in vertices}
    for u, v, _ in edges:
        adj[u].append(v)
        adj[v].append(u)

    seen = {vertices[0]}
    queue = deque([vertices[0]])
    while queue:
        cur = queue.popleft()
        for nxt in adj[cur]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    return len(seen) == len(vertices)


def brute_force_min_weight(vertices, edges):
    n = len(vertices)
    if n <= 1:
        return 0
    best = None
    for combo in itertools.combinations(edges, n - 1):
        if not has_cycle(vertices, combo) and is_connected(vertices, combo):
            weight = sum(w for _, _, w in combo)
            if best is None or weight < best:
                best = weight
    return best


def check_mst(vertices, edges, graph, mst_edges, total):
    assert sum(w for _, _, w in mst_edges) == total, "неверная сумма весов"

    for u, v, w in mst_edges:
        assert (v, w) in graph[u], f"ребра {(u, v, w)} нет в графе"

    assert len(mst_edges) == len(vertices) - 1, "число рёбер != V-1"
    assert not has_cycle(vertices, mst_edges), "в MST есть цикл"
    assert is_connected(vertices, mst_edges), "MST не связно"
    assert total == brute_force_min_weight(vertices, edges), "вес не минимален"


def test_connected_graph():
    edges = [
        ("A", "B", 4), ("A", "C", 3), ("B", "C", 1),
        ("B", "D", 2), ("C", "D", 4), ("D", "E", 2), ("E", "F", 6),
    ]
    graph = build_graph(edges)
    mst_edges, total = prim_mst(graph)

    assert total == 14
    check_mst(list(graph), edges, graph, mst_edges, total)

    for s in graph:
        assert prim_mst(graph, start=s)[1] == 14
    print("OK: связный граф")


def test_equal_weights():
    k4 = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (1, 3, 1), (2, 3, 1)]
    graph = build_graph(k4)
    mst_edges, total = prim_mst(graph)
    assert total == 3 and len(mst_edges) == 3
    check_mst(list(graph), k4, graph, mst_edges, total)

    cycle = [(0, 1, 7), (1, 2, 7), (2, 3, 7), (3, 4, 7), (4, 0, 7)]
    graph = build_graph(cycle)
    mst_edges, total = prim_mst(graph)
    assert total == 28 and len(mst_edges) == 4
    check_mst(list(graph), cycle, graph, mst_edges, total)
    print("OK: одинаковые веса")


def test_edge_cases():
    assert prim_mst({}) == ([], 0)
    assert prim_mst({"X": []}) == ([], 0)

    graph = build_graph([(0, 1, 1), (2, 3, 1)])
    try:
        prim_mst(graph)
    except ValueError:
        pass
    else:
        raise AssertionError("для несвязного графа ожидался ValueError")
    print("OK: граничные случаи")


def random_connected_graph(n, extra, max_w):
    edges, used = [], set()
    for v in range(1, n):
        u = random.randrange(v)
        edges.append((u, v, random.randint(1, max_w)))
        used.add((u, v))
    for _ in range(extra):
        u, v = random.sample(range(n), 2)
        a, b = min(u, v), max(u, v)
        if (a, b) not in used:
            used.add((a, b))
            edges.append((a, b, random.randint(1, max_w)))
    return edges


def test_random_against_brute_force():
    random.seed(42)
    for _ in range(300):
        n = random.randint(2, 7)
        edges = random_connected_graph(n, extra=random.randint(0, 6), max_w=5)
        graph = build_graph(edges)
        mst_edges, total = prim_mst(graph)
        check_mst(list(graph), edges, graph, mst_edges, total)
    print("OK: 300 случайных графов")


if __name__ == "__main__":
    test_connected_graph()
    test_equal_weights()
    test_edge_cases()
    test_random_against_brute_force()
    print("Все тесты пройдены")
