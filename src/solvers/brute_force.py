from __future__ import annotations

from core.types import Puzzle
from utils.tracer import Tracer


Cell = tuple[int, int]


class BruteForceSolver:
    """Brute-Force Backtracking solver cho Futoshiki Puzzles"""
    
    def __init__(self, puzzle: Puzzle, tracer: Tracer | None = None):
        self.puzzle = puzzle
        self.n = puzzle.size
        self.grid = [row[:] for row in puzzle.grid]  # Copy grid
        self.expanded_count = 0  # Đếm số nút được mở rộng
        self.t = tracer or Tracer(enabled=False)
    
    def find_empty_cell(self) -> Cell | None:
        """
        Tìm ô trống đầu tiên (từ trái sang phải, từ trên xuống dưới).
        
        Returns:
            Tuple (row, col) của ô trống, hoặc None nếu không có
        """
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None
    
    def is_valid(self, row: int, col: int, value: int) -> bool:
        """
        Kiểm tra xem giá trị có hợp lệ tại vị trí (row, col) không.
        
        Điều kiện kiểm tra:
        1. Tính duy nhất trong hàng: value chưa tồn tại trong hàng row
        2. Tính duy nhất trong cột: value chưa tồn tại trong cột col
        3. Ràng buộc bất đẳng thức với các ô lân cận đã được điền
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            value: Giá trị muốn kiểm tra (1 đến N)
        
        Returns:
            True nếu hợp lệ, False nếu vi phạm ràng buộc
        """
        # 1. Kiểm tra tính duy nhất trong hàng
        for c in range(self.n):
            if c != col and self.grid[row][c] == value:
                return False
        
        # 2. Kiểm tra tính duy nhất trong cột
        for r in range(self.n):
            if r != row and self.grid[r][col] == value:
                return False
        
        # 3. Kiểm tra ràng buộc bất đẳng thức với ô bên trái
        if col > 0 and self.grid[row][col - 1] != 0:
            left_value = self.grid[row][col - 1]
            sign = self.puzzle.horizontal[row][col - 1]
            
            if sign == 1 and not (left_value < value):  # left < right
                return False
            if sign == -1 and not (left_value > value):  # left > right
                return False
        
        # 4. Kiểm tra ràng buộc bất đẳng thức với ô bên phải
        if col < self.n - 1 and self.grid[row][col + 1] != 0:
            right_value = self.grid[row][col + 1]
            sign = self.puzzle.horizontal[row][col]
            
            if sign == 1 and not (value < right_value):  # left < right
                return False
            if sign == -1 and not (value > right_value):  # left > right
                return False
        
        # 5. Kiểm tra ràng buộc bất đẳng thức với ô phía trên
        if row > 0 and self.grid[row - 1][col] != 0:
            top_value = self.grid[row - 1][col]
            sign = self.puzzle.vertical[row - 1][col]
            
            if sign == 1 and not (top_value < value):  # top < bottom
                return False
            if sign == -1 and not (top_value > value):  # top > bottom
                return False
        
        # 6. Kiểm tra ràng buộc bất đẳng thức với ô phía dưới
        if row < self.n - 1 and self.grid[row + 1][col] != 0:
            bottom_value = self.grid[row + 1][col]
            sign = self.puzzle.vertical[row][col]
            
            if sign == 1 and not (value < bottom_value):  # top < bottom
                return False
            if sign == -1 and not (value > bottom_value):  # top > bottom
                return False
        
        return True
    
    def solve(self) -> bool:
        """
        Thuật toán backtracking để giải Futoshiki puzzle.
        
        Quy trình:
        1. Tìm ô trống đầu tiên
        2. Nếu không có ô trống → đã giải xong (return True)
        3. Thử giá trị 1 đến N:
           - Kiểm tra tính hợp lệ
           - Nếu hợp lệ: gán giá trị và gọi đệ quy
           - Nếu đệ quy thành công: return True
           - Nếu không: quay lui (đặt lại 0) và thử giá trị tiếp theo
        4. Nếu tất cả giá trị đều thất bại → return False
        
        Returns:
            True nếu tìm được lời giải, False nếu vô nghiệm
        """
        # Tìm ô trống đầu tiên
        cell = self.find_empty_cell()
        
        # Nếu không có ô trống → đã giải xong
        if cell is None:
            return True
        
        row, col = cell
        self.expanded_count += 1
        self.t.log(f"#{self.expanded_count:<4} first-empty -> ({row},{col})")

        self.t.push()
        for value in range(1, self.n + 1):
            if self.is_valid(row, col, value):
                self.grid[row][col] = value
                self.t.log(f"try   ({row},{col}) = {value}")
                self.t.push()
                if self.solve():
                    self.t.pop()
                    self.t.pop()
                    return True
                self.t.pop()
                self.grid[row][col] = 0
                self.t.log(f"undo  ({row},{col}) = {value}")
        self.t.pop()
        return False
    
    def get_solution(self) -> list[list[int]] | None:
        """
        Giải puzzle và trả về lưới đã giải.
        
        Returns:
            Lưới đã giải nếu tìm được lời giải, None nếu vô nghiệm
        """
        if self.solve():
            return self.grid
        return None


def solve_brute_force(puzzle: Puzzle, tracer: Tracer | None = None) -> list[list[int]] | None:
    """
    Giải Futoshiki puzzle sử dụng thuật toán Brute-Force Backtracking.
    
    Thuật toán này thử mọi tổ hợp giá trị có thể cho các ô trống,
    với kiểm tra tính hợp lệ theo các ràng buộc:
    - Không trùng giá trị trong cùng hàng/cột
    - Thỏa mãn các ràng buộc bất đẳng thức
    
    Ưu điểm:
    - Đơn giản, dễ hiểu
    - Đảm bảo tìm được lời giải nếu có
    
    Nhược điểm:
    - Chậm với puzzle lớn (độ phức tạp exponential)
    - Không có heuristic để cắt bớt search space
    
    Args:
        puzzle: Đối tượng Puzzle chứa grid, horizontal, vertical constraints
    
    Returns:
        Grid đã giải nếu có, None nếu puzzle vô nghiệm
    """
    solver = BruteForceSolver(puzzle, tracer=tracer)
    if tracer is not None:
        tracer.header("Brute-Force Backtracking", f"N={solver.n}")
        tracer.log("[init] scan empty cells left-to-right, top-to-bottom")
        tracer.blank()
    result = solver.get_solution()
    if tracer is not None:
        tracer.blank()
        if result is None:
            tracer.log(f"[done] NO SOLUTION after {solver.expanded_count} cell picks")
        else:
            tracer.log(f"[done] SUCCESS — solved with {solver.expanded_count} cell picks")
    return result
