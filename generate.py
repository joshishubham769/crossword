import sys

from crossword import *
import random
import functools

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }#nahi samajh rha

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #print("OVERLAP:",self.crossword.overlaps)
        l=self.crossword.variables
        for var in l:
            flag=True
            for x in self.domains[var].copy():
                if len(x)!=var.length:
                    self.domains[var].remove(x)
                    
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        f=False
        
        t=self.crossword.overlaps[(x,y)]
        if not t is None:
            
            for solx in self.domains[x].copy():
                flag=False
                for soly in self.domains[y]:
                    if soly[t[1]]==solx[t[0]] and not soly==solx:
                        flag=True
                if not flag:
                    self.domains[x].remove(solx)
                    f=True
        
        return f
        #raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #we want queue of arcs
        q=list(self.crossword.overlaps)
        
        for n in q:
            if self.crossword.overlaps[n]==None:
                q.remove(n)
        #print(q)
        
        while not len(q)==0:
            key=q.pop(0)
            flag=self.revise(key[0],key[1])
            if flag:
                for z in self.crossword.variables:
                    if (z,key[0]) in self.crossword.overlaps:
                        q.append((z,key[0]))
            
                
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        s=set()
        for var in self.crossword.variables:
            if not var in assignment.keys():
                return False
            if not assignment[var] in s:
                s.add(assignment[var])
            else:
                return False
        
        return True
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        s=set()
        neighbors=set(self.crossword.variables)
        for var in assignment.keys():
            if not var.length==len(assignment[var]):
                return False
            #print(neighbors)
            neighbors.remove(var)
            for neighbor in neighbors:
                t=self.crossword.overlaps[(var,neighbor)]
                if t==None or (not neighbor in assignment.keys()):
                    continue
                #print(t)
                if not assignment[var][t[0]]==assignment[neighbor][t[1]]:
                    return False
                    
            neighbors.add(var)
            if var in s:
                return False
            s.add(var)
                        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def Sum(value):
            s=0
            neighbors=set(self.crossword.variables)
            neighbors.remove(var)
            for neighbor in neighbors:
                t=self.crossword.overlaps[(neighbor,var)]
                if t==None:
                    continue
                for valn in self.domains[neighbor]:
                    if value[t[1]]!=valn[t[0]]:
                        s=s+1
                        
            return s
                        
                    
        def myFunc(a,b):
            if Sum(a)>Sum(b):
                return 1
            elif Sum(a)<Sum(b):
                return -1
            else:
                return 0
        print(var)
        lst=list(self.domains[var])

        sorted(lst,key=functools.cmp_to_key(myFunc))
        return lst
        
    def numNeighbors(self,var):
        n=0
        neighbors=set(self.crossword.variables)
        neighbors.remove(var)
        for neighbor in neighbors:
            if (neighbor,var) in self.crossword.overlaps:
                n=n+1
                
        return n
        
        
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        lst=list(self.crossword.variables-assignment.keys())
        
        miN=len(self.domains[lst[0]])
        varMiN=lst[0]
        
        for var in lst:
            if miN>len(self.domains[var]):
                miN=len(self.domains[var])
                varMiN=var
            elif miN==len(self.domains[var]):
                if self.numNeighbors(varMiN)<self.numNeighbors(var):#choose with greatest neighbpur
                    miN=len(self.domains[var])
                    varMiN=var
        
        return varMiN
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var=self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var,assignment):
            assignment[var]=val
            if self.consistent(assignment):
                return self.backtrack(assignment)
            del assignment[var]
        
        return None
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    
    assignment = creator.solve()
    #print(assignment)
    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
