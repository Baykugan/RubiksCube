"""
Defines the parent class for various Rubik's Cube configurations, setting up the basic
structure and functionalities common across different types of cubes. It handles the
general attributes like the cube's dimensions and operations like rotating layers and
simplifying sequences of moves.

Classes:
    Cube: Base class for defining general behavior of a Rubik's Cube. Includes
          functionalities like rotating layers, simplifying sequences of moves,
          scrambling, and solving the cube.
"""

import itertools
import random
import json
import re
from abc import ABC, abstractmethod

from aioconsole import ainput

from Utilities import shiftList
from piece import Piece


class Cube(ABC):
    "This is the Rubiks Cube parent class"

    ID_ITER = itertools.count()

    def __init__(self, x: int, y: int, z: int) -> None:
        self.id = next(Cube.ID_ITER)

        self.cube_type = "BaseCube"

        self.x = x
        self.y = y
        self.z = z
        self.piece_list = [
            [[[Piece()] for _ in range(self.x)] for _ in range(self.z)]
            for _ in range(self.y)
        ]
        self.id_list = [
            sub_sub_sub_list[0].id
            for sub_list in self.piece_list
            for sub_sub_list in sub_list
            for sub_sub_sub_list in sub_sub_list
        ]
        self.previous_moves = ""

        self.indent_level = 0
        self.indentation = "  "
        self.indent = lambda: self.indentation * self.indent_level

        self.layers = {}
        self.sequence_map = {}

    def __repr__(self) -> str:
        return f"Cube({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        ret_str = "["
        for sub_list in self.piece_list:
            ret_str += (
                str(
                    [
                        [sub_sub_sub_list[0] for sub_sub_sub_list in sub_sub_list]
                        for sub_sub_list in sub_list
                    ]
                )
                + ",\n "
            )
        ret_str = ret_str[:-3] + "]"
        return ret_str

    def rotate_layer(
        self, side: list[list[list[Piece]]], move: str, prime: bool = False
    ) -> None:
        for ring in side:
            if len(ring) > 1:
                if prime:
                    shifted_list = [
                        [obj[0]] for obj in shiftList(ring, -len(ring) // 4)
                    ]
                else:
                    shifted_list = [[obj[0]] for obj in shiftList(ring, len(ring) // 4)]

                for i, current_ring in enumerate(ring):
                    current_ring[0] = shifted_list[i][0]

            for obj in ring:
                obj[0].rotate(move, prime=prime)

    # Reverses sequence by position and inverts prime
    def reverse_sequence(self, moves: str) -> str:
        return " ".join(
            [
                move[:-1] if move.endswith("'") else move + "'"
                for move in moves.split()[::-1]
            ]
        )

    def simplify_sequence(self, seq: str) -> str:
        previous_sequence = ""

        # Check direction of triple turn and returns single a diametrically opposed turn
        def triple_turn(match: re.Match) -> str:
            return (
                f" {match.group('char')} {match.group('separation')}"
                if match.group("suffix") == "'"
                else f" {match.group('char')}'{match.group('separation')}"
            )

        # fmt: off
        # pylint: disable=line-too-long
        while previous_sequence != (previous_sequence := seq):
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
            seq = re.sub(r"(?:^| )(?P<char>.)(?P<suffix> |$)(?P<separation>(?<=[LRM] )[LRM '2]*?|(?<=[UED] )[UED '2]*?|(?<=[FSB] )[FSB '2]*?)\1(?:2)(?= |$)", triple_turn, seq)
            # Replaces N' N2 pairs separated by an unknown amount of same plane turns with N
            seq = re.sub(r"(?:^| )(?P<char>.)(?P<suffix>')(?P<separation>(?<=[LRM]')[LRM '2]*?|(?<=[UED]')[UED '2]*?|(?<=[FSB]')[FSB '2]*?)\1(?:2)(?= |$)", triple_turn, seq)
            # Replaces N2 N pairs separated by an unknown amount of same plane turns with N'
            seq = re.sub(r"(?:^| )(?P<char>.)2(?P<separation>(?<=[LRM]2)[LRM '2]*?|(?<=[UED]2)[UED '2]*?|(?<=[FSB]2)[FSB '2]*?)\1(?P<suffix> |$)(?= |$)", triple_turn, seq)
            # Replaces N2 N' pairs separated by an unknown amount of same plane turns with N
            seq = re.sub(r"(?:^| )(?P<char>.)2(?P<separation>(?<=[LRM]2)[LRM '2]*?|(?<=[UED]2)[UED '2]*?|(?<=[FSB]2)[FSB '2]*?)\1(?P<suffix>')(?= |$)", triple_turn, seq)
            # Cleans up extra whitespaces
            seq = re.sub(r"\s+", " ", seq)
        # pylint: enable=line-too-long
        # fmt: on
        return seq.strip()

    # Scrambles the cube
    async def scramble(self, iterations):
        key_list = [key for key in self.layers]
        suffix_list = ["' ", " "]
        scramble_str = ""
        for _ in range(iterations):
            scramble_str += random.choice(key_list) + random.choice(suffix_list)

        await self.do_sequence(scramble_str)

    # Solves the cube by reverting all moves
    async def solve(self):
        await self.do_sequence(self.reverse_sequence(self.previous_moves))

    def get_color(self, i, j, k, layer):
        return self.piece_list[i][j][k][0].get_face_color(layer)

    def get_face_from_layer(self, layer):
        layer_to_face = {"r": "X", "l": "-X", "u": "-Y", "d": "Y", "b": "Z", "f": "-Z"}
        return layer_to_face[layer]

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def pprint(self, side: str = "all") -> None:
        full_str = ""

        if side == "all":
            full_str += "Printing all sides:\n"
            padding_z = " " * ((7 * self.z) + 1)

            # Top layer
            for i in range(self.z - 1, -1, -1):
                full_str += padding_z
                for j in range(self.x):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(0, i, j, 'U')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

            # Middle layers
            for i in range(self.y):
                for j in range(self.z - 1, -1, -1):
                    # Left
                    if j == self.z - 1:
                        full_str += "["
                    full_str += f"{self.get_color(i, j, 0, 'L')}"
                    if j > 0:
                        full_str += "|"
                    else:
                        full_str += "]"

                for j in range(self.x):
                    # Front
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(i, 0, j, 'F')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]"

                for j in range(self.z):
                    # Right
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(i, j, self.x-1, 'R')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]"

                for j in range(self.x - 1, -1, -1):
                    # Back
                    if j == self.x - 1:
                        full_str += "["
                    full_str += f"{self.get_color(i, self.z-1, j, 'B')}"
                    if j > 0:
                        full_str += "|"
                    else:
                        full_str += "]"

                    if j == 0:
                        full_str += "\n"

            # Bottom layer
            for i in range(self.z):
                full_str += padding_z
                for j in range(self.x):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(self.y-1, i, j, 'D')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "up":
            # Top layer only
            full_str += "Printing up:\n"
            for i in range(self.z - 1, -1, -1):
                for j in range(self.x):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(0, i, j, 'U')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "left":
            # Left layer only
            full_str += "Printing left:\n"
            for i in range(self.y):
                for j in range(self.z - 1, -1, -1):
                    if j == self.z - 1:
                        full_str += "["
                    full_str += f"{self.get_color(i, j, 0, 'L')}"
                    if j > 0:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "front":
            # Front layer only
            full_str += "Printing front:\n"
            for i in range(self.y):
                for j in range(self.x):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(i, 0, j, 'F')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "right":
            # Right layer only
            full_str += "Printing right:\n"
            for i in range(self.y):
                for j in range(self.z):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(i, j, self.x-1, 'R')}"
                    if j < self.z - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "back":
            # Back layer only
            full_str += "Printing backs:\n"
            for i in range(self.y):
                for j in range(self.x - 1, -1, -1):
                    if j == self.x - 1:
                        full_str += "["
                    full_str += f"{self.get_color(i, self.z-1, j, 'B')}"
                    if j > 0:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        elif side == "down":
            # Bottom layer only
            full_str += "Printing down:\n"
            for i in range(self.z):
                full_str += padding_z
                for j in range(self.x):
                    if j == 0:
                        full_str += "["
                    full_str += f"{self.get_color(self.y-1, i, j, 'D')}"
                    if j < self.x - 1:
                        full_str += "|"
                    else:
                        full_str += "]\n"

        print(full_str)

    # pylint: enable=too-many-branches
    # pylint: enable=too-many-statements

    def edit_sequence_map(self) -> None:
        sequence_name = input("What is the name of the sequence? ")
        self.sequence_map[sequence_name] = input("What is the sequence? ")

    def save_sequence_map(self) -> None:
        file_name = "Sequences.json"
        with open(file_name, "r", encoding="UTF-8") as file:
            data = json.load(file)

        data[self.cube_type] = self.sequence_map

        with open(file_name, "w", encoding="UTF-8") as file:
            json.dump(data, file, indent=4)
        print("Saved sequence_map")

    def save(self) -> None:
        file_name = "Saves.json"
        save_name = input("What to save as? ")

        with open(file_name, "r", encoding="UTF-8") as file:
            data = json.load(file)

        data[self.cube_type][save_name] = self.previous_moves

        with open(file_name, "w", encoding="UTF-8") as file:
            json.dump(data, file, indent=4)

    @abstractmethod
    async def do_move(self, move: str) -> None:
        """
        Funntion that moves the cube.
        Needs to be defined in each subclass
        """

    def get_sequence(self, sequence_name: str) -> tuple[str, int]:
        """
        Retrieves a sequence and its repetition count based on the sequence name.

        Parameters:
            sequence_name (str): The name of the sequence to retrieve.

        Returns:
            tuple[str, int]: A tuple containing the sequence of moves as a string and
                             the repetition count.
        """
        # Extract repeat part
        repeat = (
            int(match.group()) if (match := re.search(r"\d+", sequence_name)) else 1
        )
        # Extract sequence part
        sequence = self.sequence_map[
            re.match(
                "|".join([r"^" + key + r"(?=[\d']|$)" for key in self.sequence_map]),
                sequence_name,
            ).group()
        ]

        # Adjust for prime move if applicable
        if sequence_name.endswith("'"):
            sequence = self.reverse_sequence(sequence)

        # Return sequence and repetitions
        return sequence, repeat

    async def do_sequence(self, moves: str) -> None:
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
                print(f"{self.indent()}Doing move: {move}")
                await self.do_move(move)

            # Named sequences of basic moves
            elif re.match(
                "|".join([r"^" + key + r"\d*[']?$" for key in self.sequence_map]), move
            ):
                print(f"{self.indent()}Doing sequence: {move}")
                self.indent_level += 1
                moves, repeat = self.get_sequence(move)
                for _ in range(repeat):
                    await self.do_sequence(move)
                self.indent_level -= 1

            # Handles invalid moves
            else:
                self.indent_level += 1
                print(f"{self.indent()}Invalid move: {move}")
                self.indent_level -= 1

    async def get_move(self) -> None:
        """
        Continuously prompts the user for moves to perform on the cube and executes
        them until an exit condition is met.

        This method uses asynchronous input to interact with the user, allowing
        for dynamic command entry and immediate cube manipulation.
        """

        while moves := await ainput("What moves to do? "):
            await self.do_sequence(moves)
            self.pprint()
            print(f"Solved = {self.is_solved()}")

            print(self.previous_moves)

    #############################################
    ########### Finds colors of sides ###########
    #############################################

    def up_layer(self) -> list[str]:
        # Top layer
        side_list = []
        for i in range(self.z - 1, -1, -1):
            for j in range(self.x):
                side_list.append(self.get_color(0, i, j, "U"))
        return side_list

    def left_layer(self) -> list[str]:
        # Left layer
        side_list = []
        for i in range(self.y):
            for j in range(self.z - 1, -1, -1):
                side_list.append(self.get_color(i, j, 0, "L"))
        return side_list

    def front_layer(self) -> list[str]:
        # Front layer
        side_list = []
        for i in range(self.y):
            for j in range(self.x):
                side_list.append(self.get_color(i, 0, j, "F"))
        return side_list

    def right_layer(self) -> list[str]:
        # Right layer
        side_list = []
        for i in range(self.y):
            for j in range(self.z):
                side_list.append(self.get_color(i, j, self.x - 1, "R"))
        return side_list

    def back_layer(self) -> list[str]:
        # Back layer
        side_list = []
        for i in range(self.y):
            for j in range(self.x - 1, -1, -1):
                side_list.append(self.get_color(i, self.z - 1, j, "B"))
        return side_list

    def down_layer(self) -> list[str]:
        # Bottom layer
        side_list = []
        for i in range(self.z):
            for j in range(self.x):
                side_list.append(self.get_color(self.y - 1, i, j, "D"))
        return side_list

    #############################################
    #############################################
    #############################################

    #############################################
    ############## Solves the cube ##############
    #############################################

    def is_side_solved(self, colors: list[str]) -> bool:
        return all(color == colors[0] for color in colors)

    def is_solved(self) -> bool:
        up = self.up_layer()
        left = self.left_layer()
        front = self.front_layer()
        right = self.right_layer()
        back = self.back_layer()
        down = self.down_layer()

        sides = [up, left, front, right, back, down]

        return all(self.is_side_solved(side) for side in sides)

    #############################################
    #############################################
    #############################################
