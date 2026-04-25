from __future__ import annotations

import heapq
from copy import deepcopy
from dataclasses import dataclass, field

from core.types import Puzzle
from utils.tracer import Tracer


Cell = tuple[int, int]


@dataclass(order=True)
class StateNode:
    """Nút trạng thái trong A* search với ưu tiên f(s) = g(s) + h(s)"""
    f_score: float  # f(s) = g(s) + h(s) - dùng để sắp xếp priority queue
    g_score: int = field(compare=False)  # g(s) - số ô đã gán giá trị
    h_score: float = field(compare=False)  # h(s) - ước tính còn lại
    grid: list[list[int]] = field(compare=False)  # Trạng thái grid hiện tại
    domains: dict[Cell, set[int]] = field(compare=False)  # Domains cho mỗi ô
    puzzle: Puzzle = field(compare=False)  # Tham chiếu đến puzzle gốc


class AC3:
    """Thuật toán AC-3 (Arc Consistency level 3) để kiểm tra nhất quán ràng buộc"""
    
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.n = puzzle.size
    
    def _get_neighbors(self, cell: Cell) -> list[Cell]:
        """Lấy danh sách các ô kề (cùng hàng, cùng cột)"""
        r, c = cell
        neighbors = []
        
        # Cùng hàng
        for c_other in range(self.n):
            if c_other != c:
                neighbors.append((r, c_other))
        
        # Cùng cột
        for r_other in range(self.n):
            if r_other != r:
                neighbors.append((r_other, c))
        
        return neighbors
    
    def _enforce_unary(self, domains: dict[Cell, set[int]]) -> bool:
        """Áp dụng ràng buộc unary (đã gán giá trị không thay đổi)"""
        changed = False
        for cell in domains:
            r, c = cell
            if self.puzzle.grid[r][c] != 0:
                # Ô đã gán: domain phải chỉ chứa giá trị đó
                given_value = self.puzzle.grid[r][c]
                if len(domains[cell]) > 1:
                    domains[cell] = {given_value}
                    changed = True
        return changed
    
    def _enforce_uniqueness(self, domains: dict[Cell, set[int]]) -> bool:
        """Áp dụng ràng buộc uniqueness (row/column không trùng giá trị)"""
        changed = False
        n = self.n
        
        # Row uniqueness
        for r in range(n):
            fixed_values = set()
            for c in range(n):
                if len(domains[(r, c)]) == 1:
                    fixed_values.add(next(iter(domains[(r, c)])))
            
            for c in range(n):
                if len(domains[(r, c)]) > 1:
                    old_size = len(domains[(r, c)])
                    domains[(r, c)] -= fixed_values
                    if len(domains[(r, c)]) < old_size:
                        changed = True
        
        # Column uniqueness
        for c in range(n):
            fixed_values = set()
            for r in range(n):
                if len(domains[(r, c)]) == 1:
                    fixed_values.add(next(iter(domains[(r, c)])))
            
            for r in range(n):
                if len(domains[(r, c)]) > 1:
                    old_size = len(domains[(r, c)])
                    domains[(r, c)] -= fixed_values
                    if len(domains[(r, c)]) < old_size:
                        changed = True
        
        return changed
    
    def _enforce_inequality(self, domains: dict[Cell, set[int]]) -> bool:
        """Áp dụng ràng buộc inequality (so sánh giữa các ô)"""
        changed = False
        n = self.n
        puzzle = self.puzzle
        
        # Horizontal inequalities
        for r in range(n):
            for c in range(n - 1):
                left_cell = (r, c)
                right_cell = (r, c + 1)
                sign = puzzle.horizontal[r][c]
                
                if sign == 1:  # left < right
                    changed |= self._enforce_less_than(
                        domains, left_cell, right_cell
                    )
                elif sign == -1:  # left > right
                    changed |= self._enforce_less_than(
                        domains, right_cell, left_cell
                    )
        
        # Vertical inequalities
        for r in range(n - 1):
            for c in range(n):
                top_cell = (r, c)
                bottom_cell = (r + 1, c)
                sign = puzzle.vertical[r][c]
                
                if sign == 1:  # top < bottom
                    changed |= self._enforce_less_than(
                        domains, top_cell, bottom_cell
                    )
                elif sign == -1:  # top > bottom
                    changed |= self._enforce_less_than(
                        domains, bottom_cell, top_cell
                    )
        
        return changed
    
    def _enforce_less_than(
        self,
        domains: dict[Cell, set[int]],
        less_cell: Cell,
        greater_cell: Cell
    ) -> bool:
        """Áp dụng ràng buộc: less_cell < greater_cell"""
        changed = False
        
        # Lọc less_cell: chỉ giữ giá trị < tất cả khả thi trong greater_cell
        less_domain = domains[less_cell]
        greater_domain = domains[greater_cell]
        
        new_less = {x for x in less_domain if any(x < y for y in greater_domain)}
        if new_less != less_domain:
            domains[less_cell] = new_less
            changed = True
        
        # Lọc greater_cell: chỉ giữ giá trị > tất cả khả thi trong less_cell
        less_domain = domains[less_cell]
        greater_domain = domains[greater_cell]
        new_greater = {y for y in greater_domain if any(x < y for x in less_domain)}
        if new_greater != greater_domain:
            domains[greater_cell] = new_greater
            changed = True
        
        return changed
    
    def is_consistent(self, domains: dict[Cell, set[int]]) -> bool:
        """
        Kiểm tra nhất quán toàn bộ: không có domain nào rỗng.
        Trả về True nếu vẫn khả thi, False nếu vô nghiệm.
        """
        return all(len(domain) > 0 for domain in domains.values())
    
    def propagate(self, domains: dict[Cell, set[int]]) -> bool:
        """
        Chạy AC-3 (kết hợp unary, uniqueness, inequality constraints).
        Trả về True nếu vẫn khả thi, False nếu vô nghiệm.
        """
        changed = True
        while changed:
            changed = False
            changed |= self._enforce_unary(domains)
            if not self.is_consistent(domains):
                return False
            
            changed |= self._enforce_uniqueness(domains)
            if not self.is_consistent(domains):
                return False
            
            changed |= self._enforce_inequality(domains)
            if not self.is_consistent(domains):
                return False
        
        return True


class AStarSolver:
    """A* Search solver cho Futoshiki Puzzles"""
    
    def __init__(self, puzzle: Puzzle, tracer: Tracer | None = None):
        self.puzzle = puzzle
        self.n = puzzle.size
        self.ac3 = AC3(puzzle)
        self.expanded_count = 0  # Đếm số nút được mở rộng
        self.t = tracer or Tracer(enabled=False)
    
    def _init_domains(self) -> dict[Cell, set[int]]:
        """Khởi tạo domains cho tất cả ô"""
        domains: dict[Cell, set[int]] = {}
        
        for r in range(self.n):
            for c in range(self.n):
                given = self.puzzle.grid[r][c]
                if given != 0:
                    domains[(r, c)] = {given}
                else:
                    domains[(r, c)] = set(range(1, self.n + 1))
        
        return domains
    
    def _heuristic(self, domains: dict[Cell, set[int]]) -> float:
        """
        Tính h(s): số ô chưa gán + tổng kích thước domains (ước lượng hợp lệ).
        Đảm bảo admissible (không bao giờ ước tính quá).
        
        h(s) = số ô chưa gán
        """
        # Cách 1: Đơn giản - số ô chưa gán (domain > 1)
        unassigned = sum(1 for d in domains.values() if len(d) > 1)
        return float(unassigned)
    
    def _is_goal(self, domains: dict[Cell, set[int]]) -> bool:
        """Kiểm tra đích: tất cả ô đều gán giá trị duy nhất và thỏa mãn ràng buộc"""
        return all(len(domain) == 1 for domain in domains.values())
    
    def _extract_grid(self, domains: dict[Cell, set[int]]) -> list[list[int]]:
        """Trích xuất grid từ domains"""
        grid = [[0] * self.n for _ in range(self.n)]
        for r in range(self.n):
            for c in range(self.n):
                if len(domains[(r, c)]) == 1:
                    grid[r][c] = next(iter(domains[(r, c)]))
        return grid
    
    def _select_cell(self, domains: dict[Cell, set[int]]) -> Cell | None:
        """
        Chọn ô để gán tiếp (MRV - Minimum Remaining Values).
        Ưu tiên ô có domain nhỏ nhất để cắt tìm kiếm.
        """
        min_size = float('inf')
        best_cell = None
        
        for cell, domain in domains.items():
            if 1 < len(domain) < min_size:
                min_size = len(domain)
                best_cell = cell
        
        return best_cell
    
    def solve(self) -> list[list[int]] | None:
        """
        Thực hiện A* search để giải Futoshiki puzzle.
        Trả về grid giải nếu tìm thấy, None nếu vô nghiệm.
        """
        # Khởi tạo trạng thái ban đầu
        initial_domains = self._init_domains()
        
        self.t.header("A* Search + AC-3", f"N={self.n}")
        self.t.log("[init] running AC-3 on initial state")
        if not self.ac3.propagate(initial_domains):
            self.t.log("[init] [FAIL] AC-3 found inconsistency")
            return None
        solved0 = sum(1 for d in initial_domains.values() if len(d) == 1)
        self.t.log(f"[init] AC-3 done — {solved0}/{self.n*self.n} cells fixed")
        self.t.blank()
        
        initial_grid = self._extract_grid(initial_domains)
        initial_h = self._heuristic(initial_domains)
        initial_node = StateNode(
            f_score=initial_h,
            g_score=0,
            h_score=initial_h,
            grid=initial_grid,
            domains=initial_domains,
            puzzle=self.puzzle
        )
        
        # Priority queue: sắp xếp theo f(s)
        open_set: list[StateNode] = [initial_node]
        closed_set: set[frozenset] = set()
        
        while open_set:
            # Lấy nút có f(s) nhỏ nhất
            current = heapq.heappop(open_set)

            # Kiểm tra đích
            if self._is_goal(current.domains):
                self.t.blank()
                self.t.log(
                    f"[goal] reached after {self.expanded_count} expansions "
                    f"(open={len(open_set)}, closed={len(closed_set)})"
                )
                return self._extract_grid(current.domains)

            # Đánh dấu nút đã mở rộng
            self.expanded_count += 1
            state_hash = frozenset(
                (cell, frozenset(domain))
                for cell, domain in current.domains.items()
            )

            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)

            # Chọn ô để gán (MRV heuristic)
            cell = self._select_cell(current.domains)
            if cell is None:
                continue

            r, c = cell
            domain = current.domains[cell]
            self.t.log(
                f"#{self.expanded_count:<3} pop  f={current.f_score:<3.0f} g={current.g_score:<3} "
                f"h={current.h_score:<3.0f}  MRV -> ({r},{c}) in {sorted(domain)}"
            )
            self.t.push()
            for value in sorted(domain):
                # Sao chép domains
                new_domains = {}
                for k, v in current.domains.items():
                    new_domains[k] = v.copy()
                
                # Gán giá trị
                new_domains[cell] = {value}
                
                # Áp dụng AC-3 propagation
                if not self.ac3.propagate(new_domains):
                    self.t.log(f"branch ({r},{c}) = {value}   [pruned by AC-3]")
                    continue

                # Tính g(s), h(s), f(s)
                g_score = current.g_score + 1
                h_score = self._heuristic(new_domains)
                f_score = g_score + h_score
                self.t.log(
                    f"branch ({r},{c}) = {value}   -> child f={f_score:<3.0f} g={g_score:<3} h={h_score:<3.0f}"
                )
                
                new_grid = self._extract_grid(new_domains)
                new_node = StateNode(
                    f_score=f_score,
                    g_score=g_score,
                    h_score=h_score,
                    grid=new_grid,
                    domains=new_domains,
                    puzzle=self.puzzle
                )
                
                heapq.heappush(open_set, new_node)
            self.t.pop()

        return None


def solve_a_star(puzzle: Puzzle, tracer: Tracer | None = None) -> list[list[int]] | None:
    """
    Giải Futoshiki puzzle sử dụng A* search với AC-3 propagation.
    
    Args:
        puzzle: Đối tượng Puzzle chứa grid, horizontal, vertical constraints
    
    Returns:
        Grid đã giải nếu có, None nếu puzzle vô nghiệm
    
    Chi tiết thuật toán:
    - g(s): Số ô đã được gán giá trị
    - h(s): Số ô còn chưa gán (admissible heuristic)
    - f(s): g(s) + h(s)
    - AC-3: Kiểm tra và lan truyền constraints
    - MRV: Chọn ô có ít lựa chọn nhất để gán tiếp
    """
    solver = AStarSolver(puzzle, tracer=tracer)
    result = solver.solve()
    if tracer is not None:
        tracer.blank()
        if result is None:
            tracer.log(f"[done] NO SOLUTION — open set exhausted after {solver.expanded_count} expansions")
        else:
            tracer.log(f"[done] SUCCESS — {solver.expanded_count} expansions")
    return result
