"""
Defines the parent class for various Rubik's Cube configurations, setting up the basic structure and functionalities
common across different types of cubes. It handles the general attributes like the cube's dimensions and operations like
rotating layers and simplifying sequences of moves.

Classes:
    Cube: Base class for defining general behavior of a Rubik's Cube. Includes functionalities like rotating layers,
          simplifying sequences of moves, scrambling, and solving the cube.
"""


import itertools
import random
import json
import re
from abc import ABC, abstractmethod

from aioconsole import ainput

from Utilities import shiftList
from Piece import Piece


class Cube(ABC):
    'This is the Rubiks Cube parent class'

    ID_ITER = itertools.count()

    def __init__(self, x: int, y: int, z:int) -> None:
        self.id = next(Cube.ID_ITER)


        self.cubeType = "BaseCube"

        self.x = x
        self.y = y
        self.z = z
        self.pieceList = [[[[Piece()] for _ in range(self.x)] for _ in range(self.z)] for _ in range(self.y)]
        self.idList = [subSubSubList[0].id for subList in self.pieceList \
                       for subSubList in subList for subSubSubList in subSubList]
        self.previousMoves = ""

        self.indentLevel = 0
        self.indentation = "  "
        self.indent = lambda : self.indentation * self.indentLevel

        self.layers = {}
        self.sequenceMap = {}


        # for (i, j, k) in itertools.product(range(self.y), range(self.z), range(self.x)):
        #     isEdge = lambda index, listLen: index in [0, listLen - 1]
        #     match sum((isEdge(i, self.y), isEdge(j, self.z), isEdge(k, self.x))):
        #         case 0:
        #             self.pieceList[i][j][k][0] = InternalPiece()
        #         case 1:
        #             self.pieceList[i][j][k][0] = MiddlePiece()
        #         case 2:
        #             self.pieceList[i][j][k][0] = EdgePiece()
        #         case 3:
        #             self.pieceList[i][j][k][0] = CornerPiece()


    def __repr__(self) -> str:
        return f'Cube({self.x}, {self.y}, {self.z})'

    def __str__(self) -> str:
        retStr = '['
        for subList in self.pieceList:
            retStr += str([[subSubSubList[0] for subSubSubList in subSubList] for subSubList in subList]) + ',\n '
        retStr = retStr[:-3] + ']'
        return retStr



    def rotateLayer(self, side:list[list[list[Piece]]], move:str, prime:bool=False) -> None:
        for ring in side:
            if  len(ring) > 1:
                if prime:
                    shiftedList = [[obj[0]] for obj in shiftList(ring, -len(ring)//4)]
                else:
                    shiftedList = [[obj[0]] for obj in shiftList(ring, len(ring)//4)]

                for i, curRing in enumerate(ring):
                    curRing[0] = shiftedList[i][0]

            for obj in ring:
                obj[0].rotate(move, prime=prime)


    # Reverses sequence by position and inverts prime
    def reverseSequence(self, moves:str) -> str:
        return " ".join([move[:-1] if move.endswith("'") else move+"'" for move in moves.split()[::-1]])


    def simplifySequence(self, seq:str) -> str:
        prevSeq = ""


        # Check direction of triple turn and returns single a diametrically opposed turn
        def tripleTurn(match:re.Match) -> str:
            return f" {match.group('char')} {match.group('separation')}" if match.group("suffix") == "'" \
                else f" {match.group('char')}'{match.group('separation')}"

        # pylint: disable=line-too-long
        while prevSeq != (prevSeq := seq):
            # Removes N' N pairs separated by an unknown amount of same plane turns
            seq = re.sub(r"(?:^| )(.)'(?P<separation>(?<=[LRM]')[LRM '2]*?|(?<=[UED]')[UED '2]*?|(?<=[FSB]')[FSB '2]*?)\1(?= |$)", r" \g<separation>", seq)
            # Removes N N' pairs separated by an unknown amount of same plane turns
            seq = re.sub(r"(?:^| )(.) (?P<separation>(?<=[LRM] )[LRM '2]*?|(?<=[UED] )[UED '2]*?|(?<=[FSB] )[FSB '2]*?)\1'(?= |$)", r" \g<separation>", seq)
            # Removes N2 N2 pairs separated by an unknown amount of same plane turns
            seq = re.sub(r"(?:^| )(.2)(?P<separation>(?<=[LRM]2)[LRM '2]*?|(?<=[UED]2)[UED '2]*?|(?<=[FSB]2)[FSB '2]*?)\1(?= |$)", r" \g<separation>", seq)
            # Replaces N N pairs separated by an unknown amount of same plane turns with N2
            seq = re.sub(r"(?:^| )(?P<char>.) (?P<separation>(?<=[LRM] )[LRM '2]*?|(?<=[UED] )[UED '2]*?|(?<=[FSB] )[FSB '2]*?)\1(?= |$)", r" \g<char>2 \g<separation>", seq)
            # Replaces N' N' pairs separated by an unknown amount of same plane turns with N2
            seq = re.sub(r"(?:^| )(?P<char>.)'(?P<separation>(?<=[LRM]')[LRM '2]*?|(?<=[UED]')[UED '2]*?|(?<=[FSB]')[FSB '2]*?)\1'(?= |$)", r" \g<char>2 \g<separation>", seq)
            # Replaces N N2 pairs separated by an unknown amount of same plane turns with N'
            seq = re.sub(r"(?:^| )(?P<char>.)(?P<suffix> |$)(?P<separation>(?<=[LRM] )[LRM '2]*?|(?<=[UED] )[UED '2]*?|(?<=[FSB] )[FSB '2]*?)\1(?:2)(?= |$)", tripleTurn, seq)
            # Replaces N' N2 pairs separated by an unknown amount of same plane turns with N
            seq = re.sub(r"(?:^| )(?P<char>.)(?P<suffix>')(?P<separation>(?<=[LRM]')[LRM '2]*?|(?<=[UED]')[UED '2]*?|(?<=[FSB]')[FSB '2]*?)\1(?:2)(?= |$)", tripleTurn, seq)
            # Replaces N2 N pairs separated by an unknown amount of same plane turns with N'
            seq = re.sub(r"(?:^| )(?P<char>.)2(?P<separation>(?<=[LRM]2)[LRM '2]*?|(?<=[UED]2)[UED '2]*?|(?<=[FSB]2)[FSB '2]*?)\1(?P<suffix> |$)(?= |$)", tripleTurn, seq)
            # Replaces N2 N' pairs separated by an unknown amount of same plane turns with N
            seq = re.sub(r"(?:^| )(?P<char>.)2(?P<separation>(?<=[LRM]2)[LRM '2]*?|(?<=[UED]2)[UED '2]*?|(?<=[FSB]2)[FSB '2]*?)\1(?P<suffix>')(?= |$)", tripleTurn, seq)
            # Cleans up extra whitespaces
            seq = re.sub(r"\s+", " ", seq)
        # pylint: enable=line-too-long
        return seq.strip()


    # Scrambles the cube
    async def scramble(self, iterations):
        keyList = [key for key in self.layers]
        suffixList = ["' ", " "]
        scrambleStr = ""
        for _ in range(iterations):
            scrambleStr += random.choice(keyList) + random.choice(suffixList)

        await self.doSequence(scrambleStr)


    # Solves the cube by reverting all moves
    async def solve(self):
        await self.doSequence(self.reverseSequence(self.previousMoves))



    def getColor(self, i, j, k, layer):
        return self.pieceList[i][j][k][0].getFaceColor(layer)


    def getFaceFromLayer(self, layer):
        layerToFace = {
            "r": "X",
            "l": "-X",
            "u": "-Y",
            "d": "Y",
            "b": "Z",
            "f": "-Z"
        }
        return layerToFace[layer]


    def pPrint(self, side:str="all") -> None:
        fullStr = ""

        if side == "all":
            fullStr += "Printing all sides:\n"
            paddingZ = " " * ((7 * self.z) + 1)   # Adjust spacing based on your layout needs

            # Top layer
            for i in range(self.z-1, -1, -1):
                fullStr += paddingZ
                for j in range(self.x):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(0, i, j, 'U')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else: fullStr += "]\n"

            # Middle layers
            for i in range(self.y):
                for j in range(self.z-1, -1, -1):
                    # Left
                    if j == self.z - 1:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, j, 0, 'L')}"
                    if j > 0:
                        fullStr += "|"
                    else:
                        fullStr += "]"

                for j in range(self.x):
                    # Front
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, 0, j, 'F')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else: fullStr += "]"

                for j in range(self.z):
                    # Right
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, j, self.x-1, 'R')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else: fullStr += "]"

                for j in range(self.x-1, -1, -1):
                    # Back
                    if j == self.x - 1:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, self.z-1, j, 'B')}"
                    if j > 0:
                        fullStr += "|"
                    else:
                        fullStr += "]"

                    if j == 0:
                        fullStr += "\n"

            # Bottom layer
            for i in range(self.z):
                fullStr += paddingZ
                for j in range(self.x):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(self.y-1, i, j, 'D')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else: fullStr += "]\n"


        elif side == "up":
            # Top layer only
            fullStr += "Printing up:\n"
            for i in range(self.z-1, -1, -1):
                for j in range(self.x):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(0, i, j, 'U')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        elif side == "left":
            # Left layer only
            fullStr += "Printing left:\n"
            for i in range(self.y):
                for j in range(self.z-1, -1, -1):
                    if j == self.z - 1:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, j, 0, 'L')}"
                    if j > 0:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        elif side == "front":
            # Front layer only
            fullStr += "Printing front:\n"
            for i in range(self.y):
                for j in range(self.x):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, 0, j, 'F')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        elif side == "right":
            # Right layer only
            fullStr += "Printing right:\n"
            for i in range(self.y):
                for j in range(self.z):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, j, self.x-1, 'R')}"
                    if j < self.z - 1:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        elif side == "back":
            # Back layer only
            fullStr += "Printing backs:\n"
            for i in range(self.y):
                for j in range(self.x-1, -1, -1):
                    if j == self.x - 1:
                        fullStr += "["
                    fullStr += f"{self.getColor(i, self.z-1, j, 'B')}"
                    if j > 0:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        elif side == "down":
            # Bottom layer only
            fullStr += "Printing down:\n"
            for i in range(self.z):
                fullStr += paddingZ
                for j in range(self.x):
                    if j == 0:
                        fullStr += "["
                    fullStr += f"{self.getColor(self.y-1, i, j, 'D')}"
                    if j < self.x - 1:
                        fullStr += "|"
                    else:
                        fullStr += "]\n"

        print(fullStr)


    def editSequenceMap(self) -> None:
        sequenceName = input("What is the name of the sequence? ")
        self.sequenceMap[sequenceName] = input("What is the sequence? ")


    def saveSequenceMap(self) -> None:
        fileName = "Sequences.json"
        with open(fileName, "r", encoding="UTF-8") as file:
            data = json.load(file)

        data[self.cubeType] = self.sequenceMap

        with open(fileName, "w", encoding="UTF-8") as file:
            json.dump(data, file, indent=4)
        print("Saved sequenceMap")


    def save(self) -> None:
        fileName = "Saves.json"
        saveName = input("What to save as? ")

        with open(fileName , "r", encoding="UTF-8") as file:
            data = json.load(file)

        data[self.cubeType][saveName] = self.previousMoves

        with open(fileName , "w", encoding="UTF-8") as file:
            json.dump(data, file, indent=4)


    @abstractmethod
    async def doMove(self, move:str) -> None:
        """
        Funntion that moves the cube.
        Needs to be defined in each subclass"""


    def getSequence(self, sequenceName:str) -> tuple[str, int]:
        """
        Retrieves a sequence and its repetition count based on the sequence name.

        Parameters:
            sequenceName (str): The name of the sequence to retrieve.

        Returns:
            tuple[str, int]: A tuple containing the sequence of moves as a string and the repetition count.
        """
        # Extract repeat part
        repeat = int(match.group()) if (match := re.search(r"\d+", sequenceName)) else 1
        # Extract sequence part
        sequence = self.sequenceMap[re.match("|".join([r"^" + key + r"(?=[\d']|$)" \
                                                       for key in self.sequenceMap]), sequenceName).group()]

        # Adjust for prime move if applicable
        if sequenceName.endswith("'"):
            sequence = self.reverseSequence(sequence)

        # Return sequence and repetitions
        return sequence, repeat


    async def doSequence(self, moves:str) -> None:
        """
        Asynchronously executes a sequence of moves on the Rubik's Cube.

        Parameters:
            moves (str): A string containing a sequence of moves separated by spaces.

        This method processes each move in the sequence, handling both basic moves
        and complex sequences that involve multiple layers and rotations.
        """
        for move in moves.split():
            # Basic moves
            if re.match(r"^[LMRUEDFSB]\d*[']?$", move):
                print(F"{self.indent()}Doing move: {move}")
                await self.doMove(move)

            # Named sequences of basic moves
            elif re.match("|".join([r"^" + key + r"\d*[']?$" for key in self.sequenceMap]), move):
                print(f"{self.indent()}Doing sequence: {move}")
                self.indentLevel += 1
                moves, repeat = self.getSequence(move)
                for _ in range(repeat):
                    await self.doSequence(move)
                self.indentLevel -=1

            # Handles invalid moves
            else:
                self.indentLevel += 1
                print(f"{self.indent()}Invalid move: {move}")
                self.indentLevel -= 1


    async def getMove(self) -> None:
        """
        Continuously prompts the user for moves to perform on the cube and executes them until an exit condition is met.

        This method uses asynchronous input to interact with the user, allowing
        for dynamic command entry and immediate cube manipulation.
        """

        while (moves := await ainput("What moves to do? ")):
            await self.doSequence(moves)
            self.pPrint()
            print(f"Solved = {self.isSolved()}")

            print(self.previousMoves)





#############################################
########### Finds colors of sides ###########
#############################################

    def upLayer(self) -> list[str]:
        # Top layer
        sideList = []
        for i in range(self.z-1, -1, -1):
            for j in range(self.x):
                sideList.append(self.getColor(0, i, j, 'U'))
        return sideList

    def leftLayer(self) -> list[str]:
        # Left layer
        sideList = []
        for i in range(self.y):
            for j in range(self.z-1, -1, -1):
                sideList.append(self.getColor(i, j, 0, 'L'))
        return sideList

    def frontLayer(self) -> list[str]:
        # Front layer
        sideList = []
        for i in range(self.y):
            for j in range(self.x):
                sideList.append(self.getColor(i, 0, j, 'F'))
        return sideList

    def rightLayer(self) -> list[str]:
        # Right layer
        sideList = []
        for i in range(self.y):
            for j in range(self.z):
                sideList.append(self.getColor(i, j, self.x-1, 'R'))
        return sideList

    def backLayer(self) -> list[str]:
        # Back layer
        sideList = []
        for i in range(self.y):
            for j in range(self.x-1, -1, -1):
                sideList.append(self.getColor(i, self.z-1, j, 'B'))
        return sideList

    def downLayer(self) -> list[str]:
        # Bottom layer
        sideList = []
        for i in range(self.z):
            for j in range(self.x):
                sideList.append(self.getColor(self.y-1, i, j, 'D'))
        return sideList

#############################################
#############################################
#############################################


#############################################
############## Solves the cube ##############
#############################################

    def isSideSolved(self, colors:list[str]) -> bool:
        return all(color == colors[0] for color in colors)

    def isSolved(self) -> bool:
        up = self.upLayer()
        left = self.leftLayer()
        front = self.frontLayer()
        right = self.rightLayer()
        back = self.backLayer()
        down = self.downLayer()

        sides = [up, left, front, right, back, down]

        return all(side for side in sides)



#############################################
#############################################
#############################################
