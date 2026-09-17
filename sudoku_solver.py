from __future__ import annotations
from time import perf_counter

logging:bool = False


class Blank(object):

    def __init__(self) -> None:
        self.candidates = list(range(1, 10))
    
    def __repr__(self) -> str:
        return "_"


class Puzzle(object):

    def __init__(self, cells:list[list[int | Blank]]) -> None:
        self.cells = cells
        self.technique_sequence:list[str] = []
        self.technique_states:list[tuple] = []
        self.initial_state:tuple = self.get_state()

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, index) -> list[int | Blank]:
        return self.cells[index]
    
    def __len__(self) -> int:
        return len(self.cells)
    
    def __repr__(self) -> str:
        return f"{self.cells[0]}\n{self.cells[1]}\n{self.cells[2]}\n{self.cells[3]}\n{self.cells[4]}\n{self.cells[5]}\n{self.cells[6]}\n{self.cells[7]}\n{self.cells[8]}"
    
    def log(self, move:function, blank:Blank) -> None:
        doc:str = move.__doc__
        print(f"{doc[doc.index("(Solve ")+7:doc.index(')')]} altered {self.coords(blank)}")

    def get_indices(self, blank:Blank) -> tuple[int]:
        for i in range(len(self)):
            for j in range(len(self[i])):
                if self.cells[i][j] == blank:
                    return (i, j)

    def get_rowdex(self, i:int) -> list[int | Blank]:
        return self.cells[i]
    
    def get_row(self, blank:Blank) -> list[int | Blank]:
        return self.cells[self.get_indices(blank)[0]]
    
    def get_coldex(self, j:int) -> list[int | Blank]:
        return [self.cells[i][j] for i in range(9)]

    def get_column(self, blank:Blank) -> list[int | Blank]:
        return [self.cells[i][self.get_indices(blank)[1]] for i in range(9)]

    def get_nondex(self, i:int, j:int) -> list[int | Blank]:
        row_base = (i // 3) * 3
        col_base = (j // 3) * 3
        return [self.cells[row][col] for row in range(row_base, row_base + 3) for col in range(col_base, col_base + 3)]

    def get_nonet(self, blank:Blank) -> list[int | Blank]:
        row_base = (self.get_indices(blank)[0] // 3) * 3
        col_base = (self.get_indices(blank)[1] // 3) * 3
        return [self.cells[row][col] for row in range(row_base, row_base + 3) for col in range(col_base, col_base + 3)]
    
    def same_row(self, *blanks:tuple[Blank], ret:bool=False) -> bool | list[int | Blank]:
        '''Returns whether the blanks reside on the same row'''
        for i in range(1, len(blanks)):
            cur_row:list[int | Blank] = self.get_row(blanks[i])
            prev_row:list[int | Blank] = self.get_row(blanks[i-1])
            if cur_row != prev_row:
                return False
        if ret:
            return self.get_row(blanks[0])
        return True
    
    def same_col(self, *blanks:tuple[Blank], ret:bool=False) -> bool | list[int | Blank]:
        '''Returns whether the blanks reside on the same column'''
        for i in range(1, len(blanks)):
            cur_col:list[int | Blank] = self.get_column(blanks[i])
            prev_col:list[int | Blank] = self.get_column(blanks[i-1])
            if cur_col != prev_col:
                return False
        if ret:
            return self.get_column(blanks[0])
        return True

    def same_nonet(self, *blanks:tuple[Blank], ret:bool=False) -> bool | list[int | Blank]:
        '''Returns whether the blanks reside in the same nonet'''
        for i in range(1, len(blanks)):
            cur_nonet:list[int | Blank] = self.get_nonet(blanks[i])
            prev_nonet:list[int | Blank] = self.get_nonet(blanks[i-1])
            if cur_nonet != prev_nonet:
                return False
        if ret:
            return self.get_nonet(blanks[0])
        return True
    
    def same_group(self, *blanks:tuple[Blank], ret:bool=False) -> bool | list[int | Blank]:
        '''Returns whether the blanks reside in any of the same groups'''
        if self.same_row(*blanks):
            if ret:
                return self.get_row(blanks[0])
            return True
        if self.same_col(*blanks):
            if ret:
                return self.get_column(blanks[0])
            return True
        if self.same_nonet(*blanks):
            if ret:
                return self.get_nonet(blanks[0])
            return True
        
        if ret:
            return []
        return False

    def candidate_count_group(self, candidate:int, group:list[int | Blank]) -> int:
        count:int = 0
        for cell in group:
            if isinstance(cell, Blank) and candidate in cell.candidates:
                count += 1
        return count
    
    def columns(self) -> list[list[int | Blank]]:
        return [self.get_coldex(i) for i in range(9)]
    
    def nonets(self) -> list[list[int | Blank]]:
        return [self.get_nondex(i, j) for i in range(0, 9, 3) for j in range(0, 9, 3)]
    
    def coords(self, blank:Blank) -> str:
        i, j = self.get_indices(blank)
        return f"R{i+1}C{j+1}"

    def blanks(self) -> list[Blank]:
        return [b for a in self for b in a if isinstance(b, Blank)]
    
    def is_solved(self) -> bool:
        for row in self:
            for cell in row:
                if isinstance(cell, Blank):
                    return False
        return True

    def is_valid(self) -> bool:
        for row in self:
            numbers = [cell for cell in row if isinstance(cell, int)]
            if len(numbers) != len(set(numbers)):
                return False

        for column in self.columns():
            numbers = [cell for cell in column if isinstance(cell, int)]
            if len(numbers) != len(set(numbers)):
                return False

        for nonet in self.nonets():
            numbers = [cell for cell in nonet if isinstance(cell, int)]
            if len(numbers) != len(set(numbers)):
                return False

        return True

    def get_state(self) -> tuple:
        state:list = []

        for row in self:
            row_state:list = []

            for cell in row:
                if isinstance(cell, Blank):
                    row_state.append(("blank", tuple(cell.candidates)))
                else:
                    row_state.append(("number", cell))

            state.append(tuple(row_state))

        return tuple(state)

    def record_technique(self, technique:str) -> None:
        self.technique_sequence.append(technique)
        self.technique_states.append(self.get_state())

    def update(self) -> None:
        '''
        (Solve Basic Elimination)
        
        Removes candidates based on numbers
        '''
        for row in self:
            for cell in row:
                if isinstance(cell, Blank):
                    i, j = self.get_indices(cell)

                    for cell2 in row:
                        if isinstance(cell2, int) and cell2 in cell.candidates:
                            self[i][j].candidates.remove(cell2)
                            if logging:
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by row")

                    for cell2 in self.get_column(cell):
                        if isinstance(cell2, int) and cell2 in cell.candidates:
                            self[i][j].candidates.remove(cell2)
                            if logging:
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by column")

                    for cell2 in self.get_nonet(cell):
                        if isinstance(cell2, int) and cell2 in cell.candidates:
                            self[i][j].candidates.remove(cell2)
                            if logging:
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by nonet")
    
    def solve_os(self) -> None:
        '''
        (Solve Obvious Singles)

        If a blank has only one remaining candidate, replace it 
        with that candidate
        '''
        for row in self:
            for cell in row:
                if isinstance(cell, Blank):
                    i, j = self.get_indices(cell)

                    if len(self[i][j].candidates) == 1:
                        if logging:
                            print(f"{self[i][j].candidates[0]} is R{i+1}C{j+1}'s last candidate")
                        self[i][j] = self[i][j].candidates[0]

                    elif isinstance(cell, Blank) and len(self[i][j].candidates) == 0:
                        raise BaseException(f"Something went wrong :( --> {self.coords(cell)} \n\n{self}")
    
    def solve_op(self) -> None:
        '''
        (Solve Obvious Pairs)

        If two blanks belonging to the same row, column, or nonet 
        possess the same two only remaining candidates, remove those
        candidates from all other blanks on which those two blanks reside
        '''
        two_candidate_blanks:list[Blank] = [blank for blank in self.blanks() if len(blank.candidates) == 2]

        for i in range(len(two_candidate_blanks)):
            for j in range(1+i, len(two_candidate_blanks)):
                if two_candidate_blanks[i].candidates == two_candidate_blanks[j].candidates:

                    if self.same_row(two_candidate_blanks[i], two_candidate_blanks[j]):
                        obv_pair:list[Blank] = [two_candidate_blanks[i], two_candidate_blanks[j]]

                        for cell in self.get_row(two_candidate_blanks[i]):
                            if isinstance(cell, Blank) and cell not in obv_pair:
                                k, l = self.get_indices(cell)

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[0])
                                    if logging:
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[0]}")
                                except ValueError:
                                    pass

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[1])
                                    if logging:
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[1]}")
                                except ValueError:
                                    pass

                    if self.same_col(two_candidate_blanks[i], two_candidate_blanks[j]):
                        obv_pair:list[Blank] = [two_candidate_blanks[i], two_candidate_blanks[j]]

                        for cell in self.get_column(two_candidate_blanks[i]):
                            if isinstance(cell, Blank) and cell not in obv_pair:
                                k, l = self.get_indices(cell)

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[0])
                                    if logging:
                                        print(f"(Column) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[0]}")
                                except ValueError:
                                    pass

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[1])
                                    if logging:
                                        print(f"(Column) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[1]}")
                                except ValueError:
                                    pass

                    if self.same_nonet(two_candidate_blanks[i], two_candidate_blanks[j]):
                        obv_pair:list[Blank] = [two_candidate_blanks[i], two_candidate_blanks[j]]

                        for cell in self.get_nonet(two_candidate_blanks[i]):
                            if isinstance(cell, Blank) and cell not in obv_pair:
                                k, l = self.get_indices(cell)

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[0])
                                    if logging:
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[0]}")
                                except ValueError:
                                    pass

                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[1])
                                    if logging:
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[1]}")
                                except ValueError:
                                    pass
    
    def solve_ot(self) -> None:
        '''
        (Solve Obvious Triples)
        '''
        for i in range(len(self.blanks())):
            for j in range(1+i, len(self.blanks())):
                for k in range(1+j, len(self.blanks())):
                    combined:list[int] = self.blanks()[i].candidates + self.blanks()[j].candidates + self.blanks()[k].candidates

                    if self.same_group(self.blanks()[i], self.blanks()[j], self.blanks()[k]) and len(set(combined)) == 3 and len(combined) > 5:
                        for cell in self.same_group(self.blanks()[i], self.blanks()[j], self.blanks()[k], ret=True):
                            if isinstance(cell, Blank) and cell not in [self.blanks()[i], self.blanks()[j], self.blanks()[k]]:
                                try:
                                    l, m = self.get_indices(cell)
                                    self[l][m].candidates.remove(combined[0])

                                    if logging:
                                        self.log(self.solve_ot, cell)
                                        print(f"  -= {combined[0]}")

                                    self[l][m].candidates.remove(combined[1])

                                    if logging:
                                        self.log(self.solve_ot, cell)
                                        print(f"  -= {combined[1]}")

                                    self[l][m].candidates.remove(combined[2])

                                    if logging:
                                        self.log(self.solve_ot, cell)
                                        print(f"  -= {combined[2]}")

                                except ValueError:
                                    pass

    def solve_oq(self) -> None:
        '''
        (Solve Obvious Quads)
        '''
        for i in range(len(self.blanks())): 
            for j in range(1+i, len(self.blanks())):
                for k in range(1+j, len(self.blanks())):
                    for l in range(1+k, len(self.blanks())):
                        combined:list[int] = self.blanks()[i].candidates + self.blanks()[j].candidates + self.blanks()[k].candidates + self.blanks()[l].candidates

                        if self.same_group(self.blanks()[i], self.blanks()[j], self.blanks()[k]) and len(set(combined)) == 4 and len(combined) > 7:
                            for cell in self.same_group(self.blanks()[i], self.blanks()[j], self.blanks()[k], self.blanks()[l], ret=True):
                                if isinstance(cell, Blank) and cell not in [self.blanks()[i], self.blanks()[j], self.blanks()[k], self.blanks()[l]]:
                                    try:
                                        m, n = self.get_indices(cell)
                                        self[m][n].candidates.remove(combined[0])

                                        if logging:
                                            self.log(self.solve_oq, cell)
                                            print(f"  -= {combined[0]}")

                                        self[m][n].candidates.remove(combined[1])

                                        if logging:
                                            self.log(self.solve_oq, cell)
                                            print(f"  -= {combined[1]}")

                                        self[m][n].candidates.remove(combined[2])

                                        if logging:
                                            self.log(self.solve_oq, cell)
                                            print(f"  -= {combined[2]}")

                                        self[m][n].candidates.remove(combined[3])

                                        if logging:
                                            self.log(self.solve_oq, cell)
                                            print(f"  -= {combined[3]}")

                                    except ValueError:
                                        pass
    
    def solve_hs(self) -> None:
        '''
        (Solve Hidden Singles)
        
        If a candidate is exclusive to a blank among any of its 
        groups, replace that blank with that candidate
        '''
        for blank in self.blanks():
            for candidate in blank.candidates:
                if self.candidate_count_group(candidate, self.get_nonet(blank)) == 1:
                    i, j = self.get_indices(blank)

                    if logging:
                        print(f"{candidate} is exclusive to R{i+1}C{j+1} in its nonet")

                    self[i][j] = candidate
                    break

                if self.candidate_count_group(candidate, self.get_row(blank)) == 1:
                    i, j = self.get_indices(blank)

                    if logging:
                        print(f"{candidate} is exclusive to R{i+1}C{j+1} in its row")

                    self[i][j] = candidate
                    break

                if self.candidate_count_group(candidate, self.get_column(blank)) == 1:
                    i, j = self.get_indices(blank)

                    if logging:
                        print(f"{candidate} is exclusive to R{i+1}C{j+1} in its column")

                    self[i][j] = candidate
                    break

            self.update()

    def solve_hp(self) -> None:
        '''
        (Solve Hidden Pairs)

        If two blanks belonging to the same row, column, or nonet 
        possess the same two candidates exclusive among the same group, 
        remove any other candidates from the blank
        '''
        for row in self:
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in row:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]:
                        i, j = self.get_indices(candidate_key[key][0])
                        k, l = self.get_indices(candidate_key[key][1])

                        if logging:
                            print(f"(Hidden Pairs) (Row) R{i+1}C{j+1} -> {[key, key2]}")
                            print(f"(Hidden Pairs) (Row) R{k+1}C{l+1} -> {[key, key2]}")

                        self[i][j].candidates = [key, key2]
                        self[k][l].candidates = [key, key2]

        for column in self.columns():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in column:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]:
                        i, j = self.get_indices(candidate_key[key][0])
                        k, l = self.get_indices(candidate_key[key][1])

                        if logging:
                            print(f"(Hidden Pairs) (Column) R{i+1}C{j+1} -> {[key, key2]}")
                            print(f"(Hidden Pairs) (Column) R{k+1}C{l+1} -> {[key, key2]}")

                        self[i][j].candidates = [key, key2]
                        self[k][l].candidates = [key, key2]

        for nonet in self.nonets():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in nonet:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]:
                        i, j = self.get_indices(candidate_key[key][0])
                        k, l = self.get_indices(candidate_key[key][1])

                        if logging:
                            print(f"(Hidden Pairs) (Nonet) R{i+1}C{j+1} -> {[key, key2]}")
                            print(f"(Hidden Pairs) (Nonet) R{k+1}C{l+1} -> {[key, key2]}")

                        self[i][j].candidates = [key, key2]
                        self[k][l].candidates = [key, key2]

    def solve_ht(self) -> None:
        '''
        (Solve Hidden Triples)

        If three blanks belonging to the same row, column, or nonet 
        possess the same three candidates exclusive among the same group, 
        remove all other candidates from the blank
        '''
        for row in self:
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in row:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4):
                            blanks:list[Blank] = []

                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)

                            if len(blanks) == 3:
                                keys:list[int] = [key, key2, key3]

                                for blank in blanks:
                                    i, j = self.get_indices(blank)
                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

        for column in self.columns():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in column:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4):
                            blanks:list[Blank] = []

                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)

                            if len(blanks) == 3:
                                keys:list[int] = [key, key2, key3]

                                for blank in blanks:
                                    i, j = self.get_indices(blank)
                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

        for nonet in self.nonets():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in nonet:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4):
                            blanks:list[Blank] = []

                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)

                            if len(blanks) == 3:
                                keys:list[int] = [key, key2, key3]

                                for blank in blanks:
                                    i, j = self.get_indices(blank)
                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

    def solve_hq(self) -> None:
        '''
        (Solve Hidden Quads)
        '''
        for row in self:
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in row:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        for key4 in range(1+key3, 10):
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5):
                                blanks:list[Blank] = []

                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)

                                if len(blanks) == 4:
                                    keys:list[int] = [key, key2, key3, key4]

                                    for blank in blanks:
                                        i, j = self.get_indices(blank)
                                        self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

        for column in self.columns():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in column:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        for key4 in range(1+key3, 10):
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5):
                                blanks:list[Blank] = []

                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)

                                if len(blanks) == 4:
                                    keys:list[int] = [key, key2, key3, key4]

                                    for blank in blanks:
                                        i, j = self.get_indices(blank)
                                        self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

        for nonet in self.nonets():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}

            for cell in nonet:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)

            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        for key4 in range(1+key3, 10):
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5):
                                blanks:list[Blank] = []

                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)

                                if len(blanks) == 4:
                                    keys:list[int] = [key, key2, key3, key4]

                                    for blank in blanks:
                                        i, j = self.get_indices(blank)
                                        self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]

    def solve_pp(self) -> None:
        '''
        (Solve Pointing Pairs)
        
        If there are only two blanks with a certain candidate in any
        group and those blanks also reside on a different group than on
        the one which they exclusively host said candidate, remove 
        that candidate from all other blanks on that other group
        '''
        for row in self:
            for n in range(1, 10):
                if self.candidate_count_group(n, row) == 2:
                    pair:list[Blank] = [cell for cell in row if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_nonet(*pair):
                        for cell in self.get_nonet(pair[0]):
                            if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

        for column in self.columns():
            for n in range(1, 10):
                if self.candidate_count_group(n, column) == 2:
                    pair:list[Blank] = [cell for cell in column if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_nonet(*pair):
                        for cell in self.get_nonet(pair[0]):
                            if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

        for nonet in self.nonets():
            for n in range(1, 10):
                if self.candidate_count_group(n, nonet) == 2:
                    pair:list[Blank] = [cell for cell in nonet if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_row(*pair):
                        for cell in self.get_row(pair[0]):
                            if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

                    elif self.same_col(*pair):
                        for cell in self.get_column(pair[0]):
                            if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

    def solve_pt(self) -> None:
        '''
        (Solve Pointing Triples)

        If there are only three blanks with a certain candidate in any
        group and those blanks also reside on a different group than on
        the one which they exclusively host said candidate, remove 
        that candidate from all other blanks on that other group
        '''
        for row in self:
            for n in range(1, 10):
                if self.candidate_count_group(n, row) == 3:
                    triple:list[Blank] = [cell for cell in row if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_nonet(*triple):
                        for cell in self.get_nonet(triple[0]):
                            if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

        for column in self.columns():
            for n in range(1, 10):
                if self.candidate_count_group(n, column) == 3:
                    triple:list[Blank] = [cell for cell in column if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_nonet(*triple):
                        for cell in self.get_nonet(triple[0]):
                            if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

        for nonet in self.nonets():
            for n in range(1, 10):
                if self.candidate_count_group(n, nonet) == 3:
                    triple:list[Blank] = [cell for cell in nonet if isinstance(cell, Blank) and n in cell.candidates]

                    if self.same_row(*triple):
                        for cell in self.get_row(triple[0]):
                            if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

                    elif self.same_col(*triple):
                        for cell in self.get_column(triple[0]):
                            if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                                i, j = self.get_indices(cell)
                                self[i][j].candidates.remove(n)

    def solve_xw(self) -> None:
        '''
        (Solve X-Wings)

        If four blanks in rectangular alignment share a certain common
        candidate and that candidate is either exclusive to the cells 
        of the rectangle on its rows or to its columns, remove that 
        candidate from the axis on which it is not exclusive
        '''
        blanks:list[Blank] = self.blanks()

        for i in range(len(blanks)):
            for j in range(1+i, len(blanks)):
                for k in range(1+j, len(blanks)):
                    for l in range(1+k, len(blanks)):
                        if self.same_row(blanks[i], blanks[j]) and self.same_row(blanks[k], blanks[l]) and self.same_col(blanks[i], blanks[k]) and self.same_col(blanks[j], blanks[l]):
                            for num in range(1, 10):
                                if num in blanks[i].candidates and num in blanks[j].candidates and num in blanks[k].candidates and num in blanks[l].candidates:

                                    if self.candidate_count_group(num, self.get_row(blanks[i])) == 2 and self.candidate_count_group(num, self.get_row(blanks[k])) == 2:
                                        for cell in self.get_column(blanks[i]):
                                            if isinstance(cell, Blank) and cell not in [blanks[i], blanks[k]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)

                                        for cell in self.get_column(blanks[j]):
                                            if isinstance(cell, Blank) and cell not in [blanks[j], blanks[l]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)

                                    if self.candidate_count_group(num, self.get_column(blanks[i])) == 2 and self.candidate_count_group(num, self.get_column(blanks[j])) == 2:
                                        for cell in self.get_row(blanks[i]):
                                            if isinstance(cell, Blank) and cell not in [blanks[i], blanks[j]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)

                                        for cell in self.get_row(blanks[k]):
                                            if isinstance(cell, Blank) and cell not in [blanks[k], blanks[l]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)

    def solve_xyw(self) -> None:
        '''
        (Solve XY-Wing)

        If a bi-candidate blank (pivot) is found with two other 
        bi-candidate blanks (wings) that are in any of the same groups
        as our pivot where each of the two wings possess one of 
        the pivot's candidates along with one that is shared by both, 
        remove that shared candidate from all other blanks that reside
        in the same groups as both wings
        '''
        blanks:list[Blank] = self.blanks()

        for i in range(len(blanks)):
            for j in range(1+i, len(blanks)):
                for k in range(1+j, len(blanks)):
                    combined:list[int] = blanks[i].candidates + blanks[j].candidates + blanks[k].candidates

                    if self.same_group(blanks[j], blanks[i]) and self.same_group(blanks[j], blanks[k]) and len(set(combined)) == 3 and len(blanks[i].candidates) == 2 and len(blanks[j].candidates) == 2 and len(blanks[k].candidates) == 2 and combined.count(list(set(combined))[0]) == combined.count(list(set(combined))[1]) == combined.count(list(set(combined))[2]):
                        z:int = blanks[i].candidates[0] if blanks[i].candidates[0] in blanks[k].candidates else blanks[i].candidates[1]

                        for blank in blanks:
                            if blank not in [blanks[i], blanks[j], blanks[k]] and self.same_group(blank, blanks[i]) and self.same_group(blank, blanks[k]) and z in blank.candidates:
                                l, m = self.get_indices(blank)
                                self[l][m].candidates.remove(z)

    def solve_xyzw(self) -> None:
        '''
        (Solve XYZ-Wing)
        '''
        blanks:list[Blank] = self.blanks()

        for i in range(len(blanks)):
            for j in range(1+i, len(blanks)):
                for k in range(1+j, len(blanks)):
                    combined:list[int] = blanks[i].candidates + blanks[j].candidates + blanks[k].candidates

                    if len(combined) == 7 and len(set(combined)) == 3 and len(blanks[i].candidates) in [2, 3] and len(blanks[j].candidates) in [2, 3] and len(blanks[k].candidates) in [2, 3] and len([num for num in set(combined) if combined.count(num) == 3]) == 1:
                        pivot:Blank = [blank for blank in [blanks[i], blanks[j], blanks[k]] if len(blank.candidates) == 3][0]
                        wings:list[Blank] = [blank for blank in [blanks[i], blanks[j], blanks[k]] if len(blank.candidates) == 2]
                        y:int = [num for num in set(combined) if combined.count(num) == 3][0]

                        if wings[0].candidates != wings[1].candidates and self.same_group(pivot, wings[0]) and self.same_group(pivot, wings[1]):
                            for blank in blanks:
                                if self.same_group(blank, pivot) and self.same_group(blank, wings[0]) and self.same_group(blank, wings[1]) and y in blank.candidates and blank not in [pivot] + wings:
                                    l, m = self.get_indices(blank)
                                    self[l][m].candidates.remove(y)

    def solve_sf(self) -> None:
        '''
        (Solve Swordfish)

        If three rows exist that share a certain candidate which only 
        appears across three different columns in those rows, remove the 
        candidate from the blanks co-columnar with the row blanks, and 
        vice versa applies with columns and rows swapped
        '''
        for n in range(1, 10):
            nrows:list[list[Blank]] = [row for row in self if self.candidate_count_group(n, row) in range(1, 4)]

            if len(nrows) >= 3:
                for i in range(len(nrows)):
                    for j in range(1+i, len(nrows)):
                        for k in range(1+j, len(nrows)):
                            rows:list[list[Blank]] = [nrows[i], nrows[j], nrows[k]]
                            nblanks:list[Blank] = []

                            for row in rows:
                                for cell in row:
                                    if isinstance(cell, Blank) and n in cell.candidates:
                                        nblanks.append(cell)

                            diff_cols:list[list[int | Blank]] = []

                            for blank in nblanks:
                                column:list[int | Blank] = self.get_column(blank)

                                if column not in diff_cols:
                                    diff_cols.append(column)

                            if len(diff_cols) == 3:
                                for blank in self.blanks():
                                    if self.get_column(blank) in diff_cols and blank not in nblanks and n in blank.candidates:
                                        i2, j2 = self.get_indices(blank)
                                        self[i2][j2].candidates.remove(n)

            ncols:list[list[int | Blank]] = [column for column in self.columns() if self.candidate_count_group(n, column) in range(1, 4)]

            if len(ncols) >= 3:
                for i in range(len(ncols)):
                    for j in range(1+i, len(ncols)):
                        for k in range(1+j, len(ncols)):
                            cols:list[list[int | Blank]] = [ncols[i], ncols[j], ncols[k]]
                            nblanks:list[Blank] = []

                            for column in cols:
                                for cell in column:
                                    if isinstance(cell, Blank) and n in cell.candidates:
                                        nblanks.append(cell)

                            diff_rows:list[list[int | Blank]] = []

                            for blank in nblanks:
                                row:list[int | Blank] = self.get_row(blank)

                                if row not in diff_rows:
                                    diff_rows.append(row)

                            if len(diff_rows) == 3:
                                for blank in self.blanks():
                                    if self.get_row(blank) in diff_rows and blank not in nblanks and n in blank.candidates:
                                        i2, j2 = self.get_indices(blank)
                                        self[i2][j2].candidates.remove(n)

    def solve_jf(self) -> None:
        '''
        (Solve Jellyfish)

        If four rows exist that share a certain candidate which only 
        appears across four different columns in those rows, remove the 
        candidate from the blanks co-columnar with the row blanks, and 
        vice versa applies with columns and rows swapped
        '''
        for n in range(1, 10):
            nrows:list[list[int | Blank]] = [row for row in self if self.candidate_count_group(n, row) in range(1, 5)]

            if len(nrows) >= 4:
                for i in range(len(nrows)):
                    for j in range(1+i, len(nrows)):
                        for k in range(1+j, len(nrows)):
                            for l in range(1+k, len(nrows)):
                                rows:list[list[int | Blank]] = [nrows[i], nrows[j], nrows[k], nrows[l]]
                                nblanks:list[Blank] = []

                                for row in rows:
                                    for cell in row:
                                        if isinstance(cell, Blank) and n in cell.candidates:
                                            nblanks.append(cell)

                                diff_cols:list[list[int | Blank]] = []

                                for blank in nblanks:
                                    column:list[int | Blank] = self.get_column(blank)

                                    if column not in diff_cols:
                                        diff_cols.append(column)

                                if len(diff_cols) == 4:
                                    for blank in self.blanks():
                                        if self.get_column(blank) in diff_cols and blank not in nblanks and n in blank.candidates:
                                            i2, j2 = self.get_indices(blank)
                                            self[i2][j2].candidates.remove(n)

            ncols:list[list[int | Blank]] = [column for column in self.columns() if self.candidate_count_group(n, column) in range(1, 5)]

            if len(ncols) >= 4:
                for i in range(len(ncols)):
                    for j in range(1+i, len(ncols)):
                        for k in range(1+j, len(ncols)):
                            for l in range(1+k, len(ncols)):
                                cols:list[list[int | Blank]] = [ncols[i], ncols[j], ncols[k], ncols[l]]
                                nblanks:list[Blank] = []

                                for column in cols:
                                    for cell in column:
                                        if isinstance(cell, Blank) and n in cell.candidates:
                                            nblanks.append(cell)

                                diff_rows:list[list[int | Blank]] = []

                                for blank in nblanks:
                                    row:list[int | Blank] = self.get_row(blank)

                                    if row not in diff_rows:
                                        diff_rows.append(row)

                                if len(diff_rows) == 4:
                                    for blank in self.blanks():
                                        if self.get_row(blank) in diff_rows and blank not in nblanks and n in blank.candidates:
                                            i2, j2 = self.get_indices(blank)
                                            self[i2][j2].candidates.remove(n)

    def solve(self) -> None:
        '''
        (Solve)
        '''

        methods:list[tuple[str, function]] = [
            ("Basic Elimination", self.update),
            ("Obvious Singles", self.solve_os),
            ("Hidden Singles", self.solve_hs),
            ("Obvious Pairs", self.solve_op),
            ("Obvious Triples", self.solve_ot),
            ("Obvious Quads", self.solve_oq),
            ("Hidden Pairs", self.solve_hp),
            ("Hidden Triples", self.solve_ht),
            ("Hidden Quads", self.solve_hq),
            ("Pointing Pairs", self.solve_pp),
            ("Pointing Triples", self.solve_pt),
            ("X-Wings", self.solve_xw),
            ("XY-Wing", self.solve_xyw),
            ("XYZ-Wing", self.solve_xyzw),
            ("Swordfish", self.solve_sf),
            ("Jellyfish", self.solve_jf)
        ]

        self.technique_sequence = []
        self.technique_states = []
        self.initial_state = self.get_state()

        while not self.is_solved():
            progress:bool = False

            for technique, method in methods:
                before:tuple = self.get_state()
                method()
                after:tuple = self.get_state()

                if not self.is_valid():
                    raise BaseException(f"Technique '{technique}' created an invalid puzzle:\n\n{self}")

                if before != after:
                    self.record_technique(technique)
                    progress = True
                    break

                if self.is_solved():
                    return

            if not progress:
                return