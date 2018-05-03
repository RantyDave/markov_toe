import random


class Board:
    line_tuples = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                   (0, 3, 6), (1, 4, 7), (2, 5, 8),
                   (0, 4, 8), (2, 4, 6))

    def __init__(self, who_move_first=0):
        self.state = bytearray(b'.........')
        self.who_move = who_move_first
        self.moves = 0

    def score(self):
        if self.moves < 3:  # can't be a line yet
            return False, False
        for line in Board.line_tuples:
            if self.state[line[0]] == ord(b'.'):
                continue
            if self.state[line[0]] == self.state[line[1]] == self.state[line[2]]:
                return (True, False) if self.state[line[0]] == ord(b'x') else (False, True)
        return False, False

    def random_move(self):
        # just finds a spare space
        skip = random.randint(1, 9 - self.moves)
        index = -1
        while skip > 0:
            index += 1  # so the first time it initialises to 0
            index %= 9  # loop over
            if self.state[index] == ord(b'.'):  # that one counts
                skip -= 1
        return index

    def make_move(self, move):
        self.state[move] = ord(b'x') if self.who_move == 0 else ord(b'o')
        self.moves += 1
        self.who_move += 1
        self.who_move %= 2

    def dump_state(self):
        for n in range(0, 3):
            print(self.state[n*3:n*3 + 3].decode())
        print()


class State:
    def __init__(self):
        self.results = {}

    def insert_result(self, move, score):
        # initialise this result
        if move not in self.results.keys():
            self.results[move] = [0, 0]
        if score[0]:
            self.results[move][0] += 1
        if score[1]:
            self.results[move][1] += 1

    def best_move(self, for_who):
        best_score_fraction = -1
        best = None
        for move, results in self.results.items():
            total = results[0] + results[1]
            if for_who == 0:
                score = results[0] - results[1]
            else:
                score = results[1] - results[0]
            if total != 0:
                score_fraction = float(score) / float(total)
            else:
                score_fraction = 0  # the only results we have on record were draws
            if score_fraction > best_score_fraction:
                best_score_fraction = score_fraction
                best = move
        return best[1] if best is not None else None

    def dump(self):
        for move, results in self.results.items():
            print("   %s plays %d = %d x-wins, %d o-wins" %
                  ('x' if move[0] == 0 else 'o', move[1], results[0], results[1]))

    @staticmethod
    def dump_all_state(db):
        for name, state in db.items():
            print()
            print(name)
            state.dump()


def one_game(global_states, x_use_history=False, dump=False):
    brd = Board(random.randint(0, 1))  # random x or o starts first
    score = brd.score()
    these_states = []
    while score == (False, False) and brd.moves < 9:
        move = None
        if x_use_history and brd.who_move == 0 and brd.state.decode() in global_states:
            move = global_states[brd.state.decode()].best_move(0)
        if move is None:
            move = brd.random_move()
        these_states.append((brd.state.decode(), (brd.who_move, move)))
        brd.make_move(move)
        if dump:
            brd.dump_state()
        score = brd.score()

    for state_string, move in these_states:  # for each state record any wins as a result of choices
        if state_string not in global_states:
            global_states[state_string] = State()
        global_states[state_string].insert_result(move, score)

    return score


state_db = {}

for _ in range(0, 100):
    # shove some random games in ...
    for _ in range(0, 1000):
        one_game(state_db)

    # see how we perform with history...
    x_score = 0
    o_score = 0
    for _ in range(0, 100):
        score = one_game(state_db, True)
        if score[0]:
            x_score += 1
        if score[1]:
            o_score += 1
    print(x_score, o_score)


# State.dump_all_state(state_db)
