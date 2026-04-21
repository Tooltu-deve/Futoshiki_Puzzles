from __future__ import annotations

from core.types import Puzzle


def solve_backward_chaining(puzzle: Puzzle) -> list[list[int]] | None:
    """
    Giả lập máy suy diễn Prolog (Backward Chaining / SLD Resolution).
    Mỗi ô (r, c) cần được truy vấn: ?- Val(r, c, V)
    Hệ thống sẽ thử Unify (khớp) V với các giá trị từ 1 đến N.
    Sau đó chứng minh (Prove) các Fact và Rule ràng buộc.
    Nếu thất bại, nó kích hoạt Backtracking (quay lui).
    """

    n = puzzle.size
    # "Môi trường" (Environment) lưu trữ các Binding của biến số trong quá trình truy vấn
    grid = [[puzzle.grid[r][c] for c in range(n)] for r in range(n)]

    def is_consistent_with_kb(r: int, c: int, v: int) -> bool:
        """
        Chứng minh các tiên đề (Axioms) không bị vi phạm nếu ta gắn Val(r, c, v).
        Tương đương với việc kiểm tra các quy luật Horn Clauses.
        """
        # 1. Rule Row Uniqueness: Không trùng số trên hàng
        for c_other in range(n):
            if c_other != c and grid[r][c_other] == v:
                return False

        # 2. Rule Column Uniqueness: Không trùng số trên cột
        for r_other in range(n):
            if r_other != r and grid[r_other][c] == v:
                return False

        # 3. Rule Horizontal Inequalities:
        # Kiểm tra ô bên trái (r, c-1)
        if c > 0 and puzzle.horizontal[r][c - 1] != 0 and grid[r][c - 1] != 0:
            left_v = grid[r][c - 1]
            sign = puzzle.horizontal[r][c - 1]
            if sign == 1 and not (left_v < v):  # Left < Right
                return False
            if sign == -1 and not (left_v > v): # Left > Right
                return False

        # Kiểm tra ô bên phải (r, c+1)
        if c < n - 1 and puzzle.horizontal[r][c] != 0 and grid[r][c + 1] != 0:
            right_v = grid[r][c + 1]
            sign = puzzle.horizontal[r][c]
            if sign == 1 and not (v < right_v):  # Left < Right
                return False
            if sign == -1 and not (v > right_v): # Left > Right
                return False

        # 4. Rule Vertical Inequalities:
        # Kiểm tra ô phía trên (r-1, c)
        if r > 0 and puzzle.vertical[r - 1][c] != 0 and grid[r - 1][c] != 0:
            top_v = grid[r - 1][c]
            sign = puzzle.vertical[r - 1][c]
            if sign == 1 and not (top_v < v):    # Top < Bottom
                return False
            if sign == -1 and not (top_v > v):   # Top > Bottom
                return False
                
        # Kiểm tra ô phía dưới (r+1, c)
        if r < n - 1 and puzzle.vertical[r][c] != 0 and grid[r + 1][c] != 0:
            bottom_v = grid[r + 1][c]
            sign = puzzle.vertical[r][c]
            if sign == 1 and not (v < bottom_v):  # Top < Bottom
                return False
            if sign == -1 and not (v > bottom_v): # Top > Bottom
                return False

        return True

    def prove_goal(index: int) -> bool:
        """
        SLD Resolution đệ quy (Recursive Backward Engine).
        Hàm này cố gắng "chứng minh" (Prove) đích đến là gán biến hoàn chỉnh.
        Index mã hóa vị trí r, c hiện tại.
        """
        if index == n * n:
            return True  # Base case: Đã duyệt và chứng minh xong toàn bộ bảng

        r = index // n
        c = index % n

        # Nếu KB đã có sẵn Fact (Given Clue):
        if puzzle.grid[r][c] != 0:
            if not is_consistent_with_kb(r, c, puzzle.grid[r][c]):
                return False  # Fact mâu thuẫn (như file test-02.txt)
            # Khớp Fact thành công, đi tiếp đến Sub-Goal kế tiếp
            return prove_goal(index + 1)

        # Nếu ô trống, thực hiện truy vấn ?- Val(r, c, V)
        for v in range(1, n + 1):
            # Thử hợp nhất (Unification) V vào Knowledge Base
            if is_consistent_with_kb(r, c, v):
                grid[r][c] = v  # Binding (Gán môi trường)
                
                # Gọi đệ quy quy nạp backward (SLD branch evaluation)
                if prove_goal(index + 1):
                    return True
                
                # Nếu nhánh thất bại -> Undo (Hủy binding) -> Backtracking tìm nhánh khác
                grid[r][c] = 0

        # Nếu tất cả các Vều thất bại, nhánh SLD này là cụt (Dead-end branch)
        return False

    # Khởi tạo truy vấn gốc (Root Goal)
    if prove_goal(0):
        return grid
    
    return None
