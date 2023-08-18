import itertools
import random
from copy import deepcopy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells) and self.count > 0:
            return self.cells
        else:
            return None

        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 and len(self.cells)>0:
            return self.cells
        else:
            return None
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.discard(cell)
        return
        raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # if cell in self.cells:
        self.cells.discard(cell)
        return
        raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        def sentenceOfSurroundings(cell, count):
            to_height = cell[0] + 2
            to_width = cell[1] + 2
            from_height = cell[0] - 1
            from_width = cell[1] - 1
            if from_height < 0:
                from_height = 0
            if from_width < 0:
                from_width = 0
            if to_height > self.height:
                to_height = self.height
            if to_width > self.width:
                to_width = self.width
            count2 = deepcopy(count)
            cells = set()
            for i in range(from_height, to_height):
                for j in range(from_width, to_width):
                    if (i, j) in self.mines:
                        count2 -= 1
                    elif (i, j) not in self.safes: # here cell itself will not pass as it would have been mark_safe before this function call
                        cells.add((i, j))
            # cells.discard(cell)
            if len(cells) > 0:
                return Sentence(cells, count2)
            return None

        #1
        self.moves_made.add(cell)

        #2
        self.mark_safe(cell)

         #3
        sent = sentenceOfSurroundings(cell, count)
        if sent:
            self.knowledge.append(sent)
        #4
        self.additional_check()
        #5
        self.inference()

        return

    def additional_check(self):
        knowledge_copy = deepcopy(self.knowledge)
        for sentence in knowledge_copy:
            if len(sentence.cells) <= 0:
                try:
                    self.knowledge.remove(sentence)
                except ValueError:
                    pass
            cells = sentence.known_mines()
            if cells:
                for mine in cells:
                    self.mark_mine(mine)
                    self.additional_check()
            else:
                cells = sentence.known_safes()
                if cells:
                    for safe in cells:
                        self.mark_safe(safe)
                        self.additional_check()

        return

    def inference(self):
        checkNeed = False
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1.cells.issubset(s2.cells):
                    s3 = Sentence((s2.cells - s1.cells), s2.count - s1.count)
                    if len(s3.cells)>0 and s3 not in self.knowledge:
                        cells = s3.known_mines()
                        if cells:
                            checkNeed = True
                            for mine in cells:
                                self.mark_mine(mine)
                        else:
                            cells = s3.known_safes()
                            if cells:
                                checkNeed = True
                                for safe in cells:
                                    self.mark_safe(safe)
                            else:
                                self.knowledge.append(s3)
        if checkNeed:
            self.additional_check()
            # m, n = cell
            # cellss = set()
            # count2 = deepcopy(count)
            # i = (m-1)>0?(m-1):0
            # j = (n-1)>0?(n-1):0
            # to_i = (m+1)<(height-1)?(m+1):(height-1)
            # to_j = (n+1)<(width-1)?(n+1):(width-1)
            # while i <= to_i:
            #     while j <= to_j:
            #         if (i, j) in self.mines:
            #             counn2 -= 1
            #         elif (i, j) not in self.safes:
            #             cellss.add((i, j))
            #         j += 1
            #     i += 1
            # cellss.discard(cell)
            # sss = Sentence(cellss, count)
            # self.knowledge.add(sss)
        #4
        # for s1 in self.knowledge:
        #     if sss != s1:
        #         if sss.issubst(s1):
        #             s2 = Sentence((s1.cells - sss.cells), s1.count - sss.count)
        #             if s2 not in self.knowledge:
        #                 self.knowledge.add(s2)
        #         elif sss.issuperset(s1):


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes - self.moves_made:
                return cell
        return None
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.moves_made)+len(self.mines) < self.height*self.width:
            while True:
                i = random.randrange(self.height)
                j = random.randrange(self.width)
                if (i, j) not in self.moves_made | self.mines:
                    return (i, j)
        return None
        raise NotImplementedError
