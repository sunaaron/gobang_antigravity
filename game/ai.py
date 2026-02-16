def handle_cpu_move(game):
    """The AI evaluates the board to find the best move."""
    move = game.state.get_best_move()
    if move:
        bx, by = move
        stone_img = [game.black_img, game.white_img][game.state.current_turn]
        if game.state.place_stone(bx, by, stone_img):
            if game.state.winner is not None:
                winner_name = ["BLACK", "WHITE"][game.state.winner]
                print(f"Winner: CPU ({winner_name})")
