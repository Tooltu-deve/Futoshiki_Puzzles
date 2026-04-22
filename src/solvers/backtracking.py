from __future__ import annotations

from core.types import Puzzle


Cell = tuple[int, int]


class BacktrackingSolver:
    """Backtracking solver với constraint checking và MRV heuristic"""
    
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.n = puzzle.size
        self.grid = [row[:] for row in puzzle.grid]
        self.expanded_count = 0
    
    def get_candidates(self, row: int, col: int) -> set[int]:
        """
        Lấy tập các giá trị khả thi cho ô (row, col).
        
        Sử dụng constraint propagation để giảm domain.
        
        Returns:
            Tập giá trị hợp lệ (1 đến N)
        """
        candidates = set(range(1, self.n + 1))
        
        # Loại bỏ giá trị đã có trong hàng
        for c in range(self.n):
            if self.grid[row][c] != 0:
                candidates.discard(self.grid[row][c])
        
        # Loại bỏ giá trị đã có trong cột
        for r in range(self.n):
            if self.grid[r][col] != 0:
                candidates.discard(self.grid[r][col])
        
        # Lọc theo ràng buộc bất đẳng thức
        # Ô bên trái
        if col > 0 and self.grid[row][col - 1] != 0:
            left_val = self.grid[row][col - 1]
            sign = self.puzzle.horizontal[row][col - 1]
            if sign == 1:  # left < right
                candidates = {v for v in candidates if left_val < v}
            elif sign == -1:  # left > right
                candidates = {v for v in candidates if left_val > v}
        
        # Ô bên phải
        if col < self.n - 1 and self.grid[row][col + 1] != 0:
            right_val = self.grid[row][col + 1]
            sign = self.puzzle.horizontal[row][col]
            if sign == 1:  # left < right
                candidates = {v for v in candidates if v < right_val}
            elif sign == -1:  # left > right
                candidates = {v for v in candidates if v > right_val}
        
        # Ô phía trên
        if row > 0 and self.grid[row - 1][col] != 0:
            top_val = self.grid[row - 1][col]
            sign = self.puzzle.vertical[row - 1][col]
            if sign == 1:  # top < bottom
                candidates = {v for v in candidates if top_val < v}
            elif sign == -1:  # top > bottom
                candidates = {v for v in candidates if top_val > v}
        
        # Ô phía dưới
        if row < self.n - 1 and self.grid[row + 1][col] != 0:
            bottom_val = self.grid[row + 1][col]
            sign = self.puzzle.vertical[row][col]
            if sign == 1:  # top < bottom
                candidates = {v for v in candidates if v < bottom_val}
            elif sign == -1:  # top > bottom
                candidates = {v for v in candidates if v > bottom_val}
        
        return candidates
    
    def select_cell_mrv(self) -> tuple[Cell | None, bool]:
        """
        Chọn ô trống có ít lựa chọn nhất (Minimum Remaining Values heuristic).
        
        Này giúp cắt bỏ search space nhanh hơn vì:
        - Ô có ít candidate dễ dàng phát hiện mâu thuẫn sớm
        - Giảm branching factor
        
        Returns:
            Tuple (cell, is_unsolvable):
            - cell: Tuple (row, col) của ô trống, hoặc None nếu không có
            - is_unsolvable: True nếu phát hiện ô không có candidate (vô nghiệm)
        """
        min_candidates = float('inf')
        best_cell = None
        
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == 0:
                    candidates = self.get_candidates(r, c)
                    
                    # Fail-fast: nếu không có candidate → vô nghiệm
                    if len(candidates) == 0:
                        return None, True  # Vô nghiệm
                    
                    # MRV: chọn ô có ít candidate nhất
                    if len(candidates) < min_candidates:
                        min_candidates = len(candidates)
                        best_cell = (r, c)
        
        # Nếu best_cell is None: không có ô trống → đã giải xong
        # Nếu best_cell is not None: còn ô trống → tiếp tục
        return best_cell, False
    
    def solve(self) -> bool:
        """
        Thuật toán Backtracking với:
        1. MRV heuristic để chọn ô
        2. Constraint checking để cắt tỉa ngay lập tức
        3. Early termination nếu phát hiện mâu thuẫn
        
        Quy trình:
        1. Chọn ô có ít candidate nhất (MRV)
        2. Nếu không có ô trống → đã giải xong
        3. Nếu ô được chọn không có candidate → vô nghiệm
        4. Thử từng candidate:
           - Gán giá trị
           - Gọi đệ quy
           - Nếu thành công: return True
           - Nếu thất bại: quay lui
        5. Nếu tất cả candidate đều thất bại → return False
        
        Returns:
            True nếu tìm được lời giải, False nếu vô nghiệm
        """
        # Chọn ô tiếp theo bằng MRV heuristic
        cell, is_unsolvable = self.select_cell_mrv()
        
        # Nếu phát hiện ô không có candidate → vô nghiệm
        if is_unsolvable:
            return False
        
        # Nếu không có ô trống → đã giải xong
        if cell is None:
            return True
        
        row, col = cell
        candidates = self.get_candidates(row, col)
        
        if not candidates:
            return False
        
        self.expanded_count += 1
        
        # Thử từng candidate (đã sắp xếp giúp tìm lời giải nhanh hơn)
        for value in sorted(candidates):
            self.grid[row][col] = value
            
            # Đệ quy
            if self.solve():
                return True
            
            # Quay lui
            self.grid[row][col] = 0
        
        return False
    
    def get_solution(self) -> list[list[int]] | None:
        """
        Giải puzzle và trả về lưới đã giải.
        
        Returns:
            Lưới đã giải nếu tìm được lời giải hợp lệ (không có 0),
            None nếu vô nghiệm hoặc không thể giải hoàn toàn
        """
        if self.solve():
            # Kiểm tra cuối cùng: solution không được chứa 0
            # Nếu có 0 → bug hoặc puzzle vô nghiệm → return None
            zero_count = sum(1 for row in self.grid for v in row if v == 0)
            if zero_count == 0:
                return self.grid
        
        return None


def solve_backtracking(puzzle: Puzzle) -> list[list[int]] | None:
    """
    Giải Futoshiki puzzle sử dụng thuật toán Backtracking.
    
    So sánh với Brute-Force:
    - Brute-Force: Không kiểm tra ràng buộc → thử tất cả hoán vị
    - Backtracking: Kiểm tra ràng buộc sớm → cắt bỏ nhánh không khả thi ngay
    
    Tối ưu hóa:
    1. **Constraint Checking (Early Pruning)**:
       - Kiểm tra ràng buộc mỗi khi gán giá trị
       - Loại bỏ các nhánh vô nghiệm sớm
    
    2. **MRV Heuristic (Minimum Remaining Values)**:
       - Chọn ô có ít lựa chọn nhất tiếp theo
       - Giảm branching factor
       - Phát hiện mâu thuẫn sớm
    
    3. **Constraint Propagation**:
       - Tính domain khả thi cho mỗi ô
       - Loại bỏ giá trị vi phạm ràng buộc
    
    Ưu điểm:
    - Nhanh hơn Brute-Force nhờ early pruning
    - MRV giúp tìm lời giải nhanh hơn
    - Có cơ chế early termination khi phát hiện mâu thuẫn
    
    Nhược điểm:
    - Chậm hơn A* (không có global heuristic)
    - Không tối ưu như Forward Chaining
    
    Args:
        puzzle: Đối tượng Puzzle chứa grid, horizontal, vertical constraints
    
    Returns:
        Grid đã giải nếu có, None nếu puzzle vô nghiệm
    """
    solver = BacktrackingSolver(puzzle)
    return solver.get_solution()
