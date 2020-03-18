import sys
import json

from search.util import print_move, print_boom, print_board
from search.board import Board

def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

    # TODO: find and print winning action sequence

    # test early implementation of Board class
    test_board = Board(data)
    test_board_dict = test_board.get_board_dict()
    print(test_board_dict)

if __name__ == '__main__':
    main()
