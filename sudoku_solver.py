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
        print(f"{doc[doc.index("(Solve ")+7:doc.index(')')]} altered {self.coords(blank)}") # holy unreadable
    
    def get_indices(self, blank:Blank) -> tuple[int]:
        for i in range(len(self)):
            for j in range(len(self[i])):
                if self[i][j] == blank:
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
    
    def update(self) -> None:
        '''
        (Solve Basic Elimination)
        
        Removes candidates based on numbers
        '''
        for row in self: # traverse rows
            for cell in row: # traverse cells in search of blanks
                if isinstance(cell, Blank): # if current cell is a blank
                    i, j = self.get_indices(cell) # get indices of the blank to reference/modify directly 

                    # OBVIOUS CANDIDATE REMOVAL
                    # --------------------------------------------------------------------------------
                    for cell2 in row: # traverse the row of the blank (the same row again)
                        if isinstance(cell2, int) and cell2 in cell.candidates: # if 2nd traversal cell is a number
                            self[i][j].candidates.remove(cell2) # remove the number from the initial blank's candidates
                            if logging:
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by row")
                    for cell2 in self.get_column(cell): # traverse the column of the blank
                        if isinstance(cell2, int) and cell2 in cell.candidates: # if column traversal cell is a number
                            self[i][j].candidates.remove(cell2) # remove the number from the initial blank's candidates
                            if logging:    
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by column")
                    for cell2 in self.get_nonet(cell): # traverse the nonet of the blank
                        if isinstance(cell2, int) and cell2 in cell.candidates: # if nonet traversal cell is a number
                            self[i][j].candidates.remove(cell2) # remove the number from the initial blank's candidates
                            if logging:
                                self.log(self.update, cell)
                                print(f"{cell2} removed from R{i+1}C{j+1} by nonet")
                    # --------------------------------------------------------------------------------
                                 
    def solve_os(self) -> None:
        '''
        (Solve Obvious Singles)

        If a blank has only one remaining candidate, replace it 
        with that candidate
        '''
        for row in self: # traverse rows
            for cell in row: # traverse cells in search of blanks
                if isinstance(cell, Blank): # if current cell is a blank
                    i, j = self.get_indices(cell) # get indices of the blank to reference/modify directly 
                    if len(self[i][j].candidates) == 1: # if the blank has only one candidate left
                        if logging:
                            print(f"{self[i][j].candidates[0]} is R{i+1}C{j+1}'s last candidate")
                        self[i][j] = self[i][j].candidates[0] # replace it with that candidate
                    elif isinstance(cell, Blank) and len(self[i][j].candidates) == 0: # if the blank has no remaining candidates, 
                        raise BaseException(f"Something went wrong :( --> {self.coords(cell)} \n\n{self}") # cease execution immediately and report cell coordinates
    
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
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[0]}")
                                except ValueError:
                                    pass
                                try:
                                    self[k][l].candidates.remove(two_candidate_blanks[i].candidates[1])
                                    if logging:
                                        print(f"(Row) R{k+1}C{l+1} : {two_candidate_blanks[i].candidates[1]}")
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
        for i in range(len(self.blanks())): # icl idec abt efficiency atp js put the fries in the bag vro /{wilting rose} /{broken heart} /{low battery}
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

                




    def solve_oq(self) -> None: # Built based off obvious triples but is completely untested ToT
        '''
        (Solve Obvious Quads)
        
        
        '''
        # The final one... (for a while)
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
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]: # if there are only two blanks in the row with candidate
                        for cell in row:
                            if isinstance(cell, Blank) and cell not in candidate_key[key]:
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
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]: # if there are only two blanks in the row with candidate
                        for cell in column:
                            if isinstance(cell, Blank) and cell not in candidate_key[key]:
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
                    if len(candidate_key[key]) == 2 and candidate_key[key] == candidate_key[key2]: # if there are only two blanks in the nonet with candidate
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
        remove all other candidates from the group on which those three 
        blanks reside
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
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4): # do three candidates appear between 1 - 3 times
                            blanks:list[Blank] = []
                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)
                            if len(blanks) == 3:
                                i, j = self.get_indices(blanks[0])
                                k, l = self.get_indices(blanks[1])
                                m, n = self.get_indices(blanks[2])
                                keys:list[int] = [key, key2, key3]
                                
                                self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                
                                if logging:
                                    print(f"(Row) R{i+1}C{j+1}, R{k+1}C{l+1}, R{m+1}C{n+1} -> {[c for c in self[i][j].candidates if c in keys]}, {[c for c in self[k][l].candidates if c in keys]}, {[c for c in self[m][n].candidates if c in keys]}")
                                

        for column in self.columns():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}
            for cell in column:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)
            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4): # do three candidates appear between 1 - 3 times
                            blanks:list[Blank] = []
                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)
                            if len(blanks) == 3:
                                i, j = self.get_indices(blanks[0])
                                k, l = self.get_indices(blanks[1])
                                m, n = self.get_indices(blanks[2])
                                keys:list[int] = [key, key2, key3]
                                self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                
                                if logging:
                                    print(f"(Column) R{i+1}C{j+1}, R{k+1}C{l+1}, R{m+1}C{n+1} -> {[c for c in self[i][j].candidates if c in keys]}, {[c for c in self[k][l].candidates if c in keys]}, {[c for c in self[m][n].candidates if c in keys]}")

        for nonet in self.nonets():
            candidate_key:dict[int, list[Blank]] = {n : [] for n in range(1, 10)}
            for cell in nonet:
                if isinstance(cell, Blank):
                    for candidate in cell.candidates:
                        candidate_key[candidate].append(cell)
            for key in range(1, 10):
                for key2 in range(1+key, 10):
                    for key3 in range(1+key2, 10):
                        if len(candidate_key[key]) in range(1, 4) and len(candidate_key[key2]) in range(1, 4) and len(candidate_key[key3]) in range(1, 4): # do three candidates appear between 1 - 3 times
                            blanks:list[Blank] = []
                            for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3]:
                                if blank not in blanks:
                                    blanks.append(blank)
                            if len(blanks) == 3:
                                i, j = self.get_indices(blanks[0])
                                k, l = self.get_indices(blanks[1])
                                m, n = self.get_indices(blanks[2])
                                keys:list[int] = [key, key2, key3]
                                self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                
                                if logging:
                                    print(f"(Nonet) R{i+1}C{j+1}, R{k+1}C{l+1}, R{m+1}C{n+1} -> {[c for c in self[i][j].candidates if c in keys]}, {[c for c in self[k][l].candidates if c in keys]}, {[c for c in self[m][n].candidates if c in keys]}")
    
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
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5): # do three candidates appear between 1 - 3 times
                                blanks:list[Blank] = []
                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)
                                if len(blanks) == 4:
                                    i, j = self.get_indices(blanks[0])
                                    k, l = self.get_indices(blanks[1])
                                    m, n = self.get_indices(blanks[2])
                                    o, p = self.get_indices(blanks[3])
                                    keys:list[int] = [key, key2, key3, key4]
                                    
                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                    self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                    self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                    self[o][p].candidates = [c for c in self[o][p].candidates if c in keys]
                                
                                    if logging:
                                        print(f"R{i+1}C{j+1} R{k+1}C{l+1} R{m+1}C{n+1} R{o+1}C{p+1} =", *keys, *[blank.candidates for blank in blanks])
                                

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
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5): # do three candidates appear between 1 - 3 times
                                blanks:list[Blank] = []
                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)
                                if len(blanks) == 4:
                                    i, j = self.get_indices(blanks[0])
                                    k, l = self.get_indices(blanks[1])
                                    m, n = self.get_indices(blanks[2])
                                    o, p = self.get_indices(blanks[3])
                                    keys:list[int] = [key, key2, key3, key4]
                                    
                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                    self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                    self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                    self[o][p].candidates = [c for c in self[o][p].candidates if c in keys]

                                    if logging:
                                        print(f"R{i+1}C{j+1} R{k+1}C{l+1} R{m+1}C{n+1} R{o+1}C{p+1} =", *keys, *[blank.candidates for blank in blanks])
                                

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
                            if len(candidate_key[key]) in range(1, 5) and len(candidate_key[key2]) in range(1, 5) and len(candidate_key[key3]) in range(1, 5) and len(candidate_key[key4]) in range(1, 5): # do three candidates appear between 1 - 3 times
                                blanks:list[Blank] = []
                                for blank in candidate_key[key] + candidate_key[key2] + candidate_key[key3] + candidate_key[key4]:
                                    if blank not in blanks:
                                        blanks.append(blank)
                                if len(blanks) == 4:
                                    i, j = self.get_indices(blanks[0])
                                    k, l = self.get_indices(blanks[1])
                                    m, n = self.get_indices(blanks[2])
                                    o, p = self.get_indices(blanks[3])
                                    keys:list[int] = [key, key2, key3, key4]

                                    self[i][j].candidates = [c for c in self[i][j].candidates if c in keys]
                                    self[k][l].candidates = [c for c in self[k][l].candidates if c in keys]
                                    self[m][n].candidates = [c for c in self[m][n].candidates if c in keys]
                                    self[o][p].candidates = [c for c in self[o][p].candidates if c in keys]

                                    if logging:
                                        print(f"R{i+1}C{j+1} R{k+1}C{l+1} R{m+1}C{n+1} R{o+1}C{p+1} =", *keys, *[blank.candidates for blank in blanks])
                                    
        
    
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
                    for cell in self.same_nonet(*pair, ret=True) if self.same_nonet(*pair) else []:
                        if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pp, cell)
                                print(f"  -= {n} ")
                                print("Row")
                                print([self.coords(blank) for blank in pair])
                
        for column in self.columns(): 
            for n in range(1, 10):
                if self.candidate_count_group(n, column) == 2:  
                    pair:list[Blank] = [cell for cell in column if isinstance(cell, Blank) and n in cell.candidates]
                    for cell in self.same_nonet(*pair, ret=True) if self.same_nonet(*pair) else []:
                        if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pp, cell)
                                print(f"  -= {n} ")
                                print("Column")
                                print([self.coords(blank) for blank in pair])

        for nonet in self.nonets(): 
            for n in range(1, 10):
                if self.candidate_count_group(n, nonet) == 2:  
                    pair:list[Blank] = [cell for cell in nonet if isinstance(cell, Blank) and n in cell.candidates]
                    for cell in self.same_group(*pair, ret=True) if self.same_group(*pair) and self.same_group(*pair, ret=True) != nonet else []:
                        if isinstance(cell, Blank) and cell not in pair and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pp, cell)
                                print(f"  -= {n} ")
                                print("Nonet")
                                print([self.coords(blank) for blank in pair])



    def solve_pt(self) -> None: # Not thoroughly tested
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
                    for cell in self.same_nonet(*triple, ret=True) if self.same_nonet(*triple) else []:
                        if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pt, cell)
                                print(f"  -= {n} ")
                
        for column in self.columns(): 
            for n in range(1, 10):
                if self.candidate_count_group(n, column) == 3:  
                    triple:list[Blank] = [cell for cell in column if isinstance(cell, Blank) and n in cell.candidates]
                    for cell in self.same_nonet(*triple, ret=True) if self.same_nonet(*triple) else []:
                        if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pt, cell)
                                print(f"  -= {n} ")

        for nonet in self.nonets(): 
            for n in range(1, 10):
                if self.candidate_count_group(n, nonet) == 3:  
                    triple:list[Blank] = [cell for cell in nonet if isinstance(cell, Blank) and n in cell.candidates]
                    for cell in self.same_group(*triple, ret=True) if self.same_group(*triple) and self.same_group(*triple, ret=True) != nonet else []:
                        if isinstance(cell, Blank) and cell not in triple and n in cell.candidates:
                            i, j = self.get_indices(cell)
                            self[i][j].candidates.remove(n)
                            if logging:
                                self.log(self.solve_pt, cell)
                                print(f"  -= {n} ")
                            


    def solve_xw(self) -> None: # <-- THIS BOI NEED OPTIMIZATION
        '''
        (Solve X-Wings)

        If four blanks in rectangular alignment share a certain common
        candidate and that candidate is either exclusive to the cells 
        of the rectangle on its rows or to its columns, remove that 
        candidate from the axis on which it is not exclusive
        '''
        for i in range(len(self.blanks())):
            for j in range(1+i, len(self.blanks())):
                for k in range(1+j, len(self.blanks())): # HOLY NEST
                    for l in range(1+k, len(self.blanks())):
                        if self.same_row(self.blanks()[i], self.blanks()[j]) and self.same_row(self.blanks()[k], self.blanks()[l]) and self.same_col(self.blanks()[i], self.blanks()[k]) and self.same_col(self.blanks()[j], self.blanks()[l]):
                            for num in range(1, 10):
                                if num in self.blanks()[i].candidates and num in self.blanks()[j].candidates and num in self.blanks()[k].candidates and num in self.blanks()[l].candidates:
                                    if self.candidate_count_group(num, self.get_row(self.blanks()[i])) == 2 and self.candidate_count_group(num, self.get_row(self.blanks()[k])) == 2:
                                        for cell in self.get_column(self.blanks()[i]):   # IT'S STILL GOING??
                                            if isinstance(cell, Blank) and cell not in [self.blanks()[i], self.blanks()[k]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)
                                        for cell in self.get_column(self.blanks()[j]): 
                                            if isinstance(cell, Blank) and cell not in [self.blanks()[j], self.blanks()[l]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)
                                    if self.candidate_count_group(num, self.get_column(self.blanks()[i])) == 2 and self.candidate_count_group(num, self.get_column(self.blanks()[j])) == 2:
                                        for cell in self.get_row(self.blanks()[i]):  
                                            if isinstance(cell, Blank) and cell not in [self.blanks()[i], self.blanks()[j]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)
                                        for cell in self.get_row(self.blanks()[k]):  
                                            if isinstance(cell, Blank) and cell not in [self.blanks()[k], self.blanks()[l]] and num in cell.candidates:
                                                m, n = self.get_indices(cell)
                                                self[m][n].candidates.remove(num)
                                    

    def solve_xyw(self) -> None: # <-- THIS BOI NEED IT TOO
        '''
        (Solve XY-Wing)

        If a bi-candidate blank (pivot) is found with two other 
        bi-candidate blanks (wings) that are in any of the same groups
        as our pivot where each of the two wings possess one of 
        the pivot's candidates along with one that is shared by both, 
        remove that shared candidate from all other blanks that reside
        in the same groups as both wings 
        '''  

        for i in range(len(self.blanks())):
            for j in range(1+i, len(self.blanks())):
                for k in range(1+j, len(self.blanks())):
                    combined:list[int] = self.blanks()[i].candidates + self.blanks()[j].candidates + self.blanks()[k].candidates
                    if (self.same_group(self.blanks()[j], self.blanks()[i])) and (self.same_group(self.blanks()[j], self.blanks()[k])) and len(set(combined)) == 3 and len(self.blanks()[i].candidates) == 2 and len(self.blanks()[j].candidates) == 2 and len(self.blanks()[k].candidates) == 2 and combined.count(list(set(combined))[0]) == combined.count(list(set(combined))[1]) == combined.count(list(set(combined))[2]): 
                        #print(f"Wing1={self.coords(self.blanks()[i])}{self.blanks()[i].candidates}, Wing2={self.coords(self.blanks()[k])}{self.blanks()[k].candidates}, Pivot={self.coords(self.blanks()[j])}{self.blanks()[j].candidates}")
                        z:int = self.blanks()[i].candidates[0] if self.blanks()[i].candidates[0] in self.blanks()[k].candidates else self.blanks()[i].candidates[1]
                        for blank in self.blanks():
                            if blank not in [self.blanks()[i], self.blanks()[j], self.blanks()[k]] and self.same_group(blank, self.blanks()[i]) and self.same_group(blank, self.blanks()[k]) and z in blank.candidates:
                                l, m = self.get_indices(blank)
                                if logging:
                                    print(f"{self.coords(blank)} -> {self[l][m].candidates} -= {z}")
                                self[l][m].candidates.remove(z)
                
    def solve_xyzw(self) -> None: # DONT FORGET THIS ONE
        '''
        (Solve XYZ-Wing)

        
        '''             
        for i in range(len(self.blanks())):
            for j in range(1+i, len(self.blanks())):
                for k in range(1+j, len(self.blanks())):
                    combined:list[int] = self.blanks()[i].candidates + self.blanks()[j].candidates + self.blanks()[k].candidates

                    if len(combined) == 7 and len(set(combined)) == 3 and len(self.blanks()[i].candidates) in [2, 3] and len(self.blanks()[j].candidates) in [2, 3] and len(self.blanks()[k].candidates) in [2, 3] and len([num for num in set(combined) if combined.count(num) == 3]) == 1:
                        pivot:Blank = [blank for blank in [self.blanks()[i], self.blanks()[j], self.blanks()[k]] if len(blank.candidates) == 3][0]
                        wings:list[Blank] = [blank for blank in [self.blanks()[i], self.blanks()[j], self.blanks()[k]] if len(blank.candidates) == 2]
                        y:int = [num for num in set(combined) if combined.count(num) == 3][0]
                        if wings[0].candidates != wings[1].candidates and self.same_group(pivot, wings[0]) and self.same_group(pivot, wings[1]):
                            for blank in self.blanks():
                                if self.same_group(blank, pivot) and self.same_group(blank, wings[0]) and self.same_group(blank, wings[1]) and y in blank.candidates and blank not in [pivot] + wings:
                                    l, m = self.get_indices(blank)
                                    self[l][m].candidates.remove(y)
                                    if logging:
                                        print(f"{self.coords(blank)} -=  {y}")
    
    def solve_sf(self) -> None: # Has not been thoroughly tested, but seems to work..? [Some jellyfish parity adjustments made >> Still not properly tested]
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
                for x in range(len(nrows)-2):
                    rows:list[list[Blank]] = nrows[x:x+3]
                    nblanks:list[Blank] = []

                    for i in range(9):
                        if isinstance(rows[0][i], Blank) and n in rows[0][i].candidates:
                            nblanks.append(rows[0][i])
                        if isinstance(rows[1][i], Blank) and n in rows[1][i].candidates:
                            nblanks.append(rows[1][i])
                        if isinstance(rows[2][i], Blank) and n in rows[2][i].candidates:
                            nblanks.append(rows[2][i])

                    diff_cols:list[list[Blank]] = []
                    for i in range(len(nblanks)):
                        if self.get_column(nblanks[i]) not in diff_cols:
                            diff_cols.append(self.get_column(nblanks[i]))
                            
                    if len(diff_cols) == 3: 
                        for blank in self.blanks():
                            if self.get_column(blank) in diff_cols and blank not in nblanks and n in blank.candidates:
                                i, j = self.get_indices(blank)
                                if logging:
                                    self.log(self.solve_sf, blank)
                                    print(f"-= {n}")
                                self[i][j].candidates.remove(n)

            ncols:list[list[Blank]] = [col for col in self.columns() if self.candidate_count_group(n, col) in range(1, 4)]
            if len(ncols) >= 3:
                for x in range(len(ncols)-2):
                    cols:list[list[Blank]] = ncols[x:x+3]
                    nblanks:list[Blank] = []

                    for i in range(9):
                        if isinstance(cols[0][i], Blank) and n in cols[0][i].candidates:
                            nblanks.append(cols[0][i])
                        if isinstance(cols[1][i], Blank) and n in cols[1][i].candidates:
                            nblanks.append(cols[1][i])
                        if isinstance(cols[2][i], Blank) and n in cols[2][i].candidates:
                            nblanks.append(cols[2][i])

                    diff_rows:list[list[Blank]] = []
                    for i in range(len(nblanks)):
                        if self.get_row(nblanks[i]) not in diff_rows:
                            diff_rows.append(self.get_row(nblanks[i]))
                            
                        
                    if len(diff_rows) == 3: 
                        for blank in self.blanks():
                            if self.get_row(blank) in diff_rows and blank not in nblanks and n in blank.candidates:
                                i, j = self.get_indices(blank)
                                if logging:
                                    self.log(self.solve_sf, blank)
                                    print(f"-= {n}")
                                self[i][j].candidates.remove(n)
                            


    def solve_jf(self) -> None:
        '''
        (Solve Jellyfish)

        If four rows exist that share a certain candidate which only 
        appears across four different columns in those rows, remove the 
        candidate from the blanks co-columnar with the row blanks, and 
        vice versa applies with columns and rows swapped
        '''

        for n in range(1, 10):
            nrows:list[list[Blank]] = [row for row in self if self.candidate_count_group(n, row) in range(1, 5)]
                            
            if len(nrows) >= 4: 
                effective:bool = False
                for w in range(len(nrows)):
                    for x in range(1+w, len(nrows)):
                        for y in range(1+x, len(nrows)):
                            for z in range(1+y, len(nrows)):
                                rows:list[list[Blank]] = [nrows[letter] for letter in [w, x, y, z]]
                                nblanks:list[Blank] = []
                                for i in range(9):
                                    if isinstance(rows[0][i], Blank) and n in rows[0][i].candidates:
                                        nblanks.append(rows[0][i])
                                    if isinstance(rows[1][i], Blank) and n in rows[1][i].candidates:
                                        nblanks.append(rows[1][i])
                                    if isinstance(rows[2][i], Blank) and n in rows[2][i].candidates:
                                        nblanks.append(rows[2][i])
                                    if isinstance(rows[3][i], Blank) and n in rows[3][i].candidates:
                                        nblanks.append(rows[3][i])

                                diff_cols:list[list[Blank]] = []
                                for i in range(len(nblanks)):
                                    if self.get_column(nblanks[i]) not in diff_cols:
                                        diff_cols.append(self.get_column(nblanks[i]))
                                        
                                if len(diff_cols) == 4: 
                                    for blank in self.blanks():
                                        if self.get_column(blank) in diff_cols and blank not in nblanks and n in blank.candidates:
                                            i, j = self.get_indices(blank)
                                            if logging:
                                                self.log(self.solve_jf, blank)
                                                print(f"-= {n}")
                                            self[i][j].candidates.remove(n)
                                            effective = True
                if effective: # a hidden single had to occur in between these two in the intial test sample, so we break out of the function and wait for the next rep to apply any further jellyfish
                    return 

            ncols:list[list[Blank]] = [col for col in self if self.candidate_count_group(n, col) in range(1, 5)]
            if len(ncols) >= 4: 
                effective:bool = False
                for w in range(len(ncols)): 
                    for x in range(1+w, len(ncols)):
                        for y in range(1+x, len(ncols)):
                            for z in range(1+y, len(ncols)):
                                cols:list[list[Blank]] = [ncols[letter] for letter in [w, x, y, z]]
                                nblanks:list[Blank] = []
                                for i in range(9):
                                    if isinstance(cols[0][i], Blank) and n in cols[0][i].candidates:
                                        nblanks.append(cols[0][i])
                                    if isinstance(cols[1][i], Blank) and n in cols[1][i].candidates:
                                        nblanks.append(cols[1][i])
                                    if isinstance(cols[2][i], Blank) and n in cols[2][i].candidates:
                                        nblanks.append(cols[2][i])
                                    if isinstance(cols[3][i], Blank) and n in cols[3][i].candidates:
                                        nblanks.append(cols[3][i])

                                diff_rows:list[list[Blank]] = []
                                for i in range(len(nblanks)):
                                    if self.get_column(nblanks[i]) not in diff_rows:
                                        diff_rows.append(self.get_row(nblanks[i]))
                                
                                if len(diff_rows) == 4: 
                                    for blank in self.blanks():
                                        if self.get_column(blank) in diff_rows and blank not in nblanks and n in blank.candidates:
                                            i, j = self.get_indices(blank)
                                            if logging:
                                                self.log(self.solve_jf, blank)
                                                print(f"-= {n}")
                                            self[i][j].candidates.remove(n)
                                            effective = True
                
                if effective:
                    return
        

    def solve(self) -> None:
        '''
        (Solve)


        '''

        # Future algorithm: 
        '''
        Try most basic technique
        If effective
        True -> return to most basic technique
        False -> Try next most basic technique
        If we have reached the most advanced technique and it is ineffective
        output "Unable to solve with logic"
        # Maybe add a brute forcer
        
        '''
        for method in [
            self.solve_os,
            self.solve_hs,
            self.solve_op,
            self.solve_ot,
            self.solve_oq,
            self.solve_hp,
            self.solve_ht,
            self.solve_hq,
            self.solve_pp,
            self.solve_pt,
            self.solve_xw,
            self.solve_xyw,
            self.solve_xyzw,
            self.solve_sf,
            self.solve_jf
        ]:
            method()
            self.update()