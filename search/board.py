class Board:
    def __init__(self, board_data):
        self.board_data = board_data
        
        board_dict = {(i, j):"" for i in range(8) for j in range(8)}
        for stack in board_data['white']:
            height = stack[0]
            coords = (stack[1], stack[2])
            board_dict[coords] = f"{height}-w"
        for stack in board_data['black']:
            height = stack[0]
            coords = (stack[1], stack[2])
            board_dict[coords] = f"{height}-b"
        self.board_dict = board_dict
    
    def get_board_dict(self):
        return self.board_dict