"""
This module extends the basic Rubik's Cube functionality to specifically handle a
standard 3x3 Rubik's Cube. It includes asynchronous functions for manipulating the cube
through various moves and sequences, reading user input asynchronously, and displaying
the current state of the cube.

Classes:
    ThreeByThree: Represents a 3x3 Rubik's Cube with functionalities for executing
                  moves, sequences, and solving the cube asynchronously.
"""

import re
import json
import asyncio

from aioconsole import ainput


from RubiksCube import Cube
from ThreeByThreeDraw import RubiksCubeSimulator


class ThreeByThree(Cube):
    """
    Represents a 3x3 Rubik's Cube, providing functionalities for manipulating the
    cube's state through moves and sequences, and solving the cube asynchronously. This
    class extends the Cube class by implementing specific configurations and operations
    suited for a 3x3 Rubik's Cube.

    Attributes:
        cubeType (str): Identifier for the type of cube, set to "ThreeByThree".
        indentLevel (int): Current indentation level for console output formatting.
        indentation (str): A string used for indenting console outputs.
        sequenceMap (dict): Maps sequences of moves to their corresponding cube
                            rotations.
        layers (dict): Organizes the cube's pieces in various layers and orientations.
        faces (list): List of all face pieces structured in a specific cube orientation.
    """

    def __init__(self) -> None:
        super().__init__(3, 3, 3)

        self.cubeType = "ThreeByThree"

        with open("Sequences.json", "r", encoding="UTF-8") as file:
            self.sequenceMap = json.load(file)[self.cubeType]

        # Organizes all non-internal layer elements into clockwise sequences
        # Starts from the element nearest to the origin (0, 0, 0).
        # fmt: off
        self.layers = {
            "U": [[self.pieceList[0][1][1]],
                  [self.pieceList[0][0][0], self.pieceList[0][1][0],
                   self.pieceList[0][2][0], self.pieceList[0][2][1],
                   self.pieceList[0][2][2], self.pieceList[0][1][2],
                   self.pieceList[0][0][2], self.pieceList[0][0][1]]],
            "F": [[self.pieceList[1][0][1]],
                  [self.pieceList[0][0][0], self.pieceList[0][0][1],
                   self.pieceList[0][0][2], self.pieceList[1][0][2],
                   self.pieceList[2][0][2], self.pieceList[2][0][1],
                   self.pieceList[2][0][0], self.pieceList[1][0][0]]],
            "L": [[self.pieceList[1][1][0]],
                  [self.pieceList[0][0][0], self.pieceList[1][0][0],
                   self.pieceList[2][0][0], self.pieceList[2][1][0],
                   self.pieceList[2][2][0], self.pieceList[1][2][0],
                   self.pieceList[0][2][0], self.pieceList[0][1][0]]],

            "D": [[self.pieceList[2][1][1]],
                  [self.pieceList[2][0][0], self.pieceList[2][0][1],
                   self.pieceList[2][0][2], self.pieceList[2][1][2],
                   self.pieceList[2][2][2], self.pieceList[2][2][1],
                   self.pieceList[2][2][0], self.pieceList[2][1][0]]],
            "B": [[self.pieceList[1][2][1]],
                  [self.pieceList[0][2][0], self.pieceList[1][2][0],
                   self.pieceList[2][2][0], self.pieceList[2][2][1],
                   self.pieceList[2][2][2], self.pieceList[1][2][2],
                   self.pieceList[0][2][2], self.pieceList[0][2][1]]],
            "R": [[self.pieceList[1][1][2]],
                  [self.pieceList[0][0][2], self.pieceList[0][1][2],
                   self.pieceList[0][2][2], self.pieceList[1][2][2],
                   self.pieceList[2][2][2], self.pieceList[2][1][2],
                   self.pieceList[2][0][2], self.pieceList[1][0][2]]],

            "E": [[self.pieceList[1][1][1]],
                  [self.pieceList[1][0][0], self.pieceList[1][0][1],
                   self.pieceList[1][0][2], self.pieceList[1][1][2],
                   self.pieceList[1][2][2], self.pieceList[1][2][1],
                   self.pieceList[1][2][0], self.pieceList[1][1][0]]],
            "S": [[self.pieceList[1][1][1]],
                  [self.pieceList[0][1][0], self.pieceList[0][1][1],
                   self.pieceList[0][1][2], self.pieceList[1][1][2],
                   self.pieceList[2][1][2], self.pieceList[2][1][1],
                   self.pieceList[2][1][0], self.pieceList[1][1][0]]],
            "M": [[self.pieceList[1][1][1]],
                  [self.pieceList[0][0][1], self.pieceList[1][0][1],
                   self.pieceList[2][0][1], self.pieceList[2][1][1],
                   self.pieceList[2][2][1], self.pieceList[1][2][1],
                   self.pieceList[0][2][1], self.pieceList[0][1][1]]]
        }
        # fmt: on

        #fmt: off
        self.faces = [
            # Up
            self.pieceList[0][2][0], self.pieceList[0][2][1], self.pieceList[0][2][2],
            self.pieceList[0][1][0], self.pieceList[0][1][1], self.pieceList[0][1][2],
            self.pieceList[0][0][0], self.pieceList[0][0][1], self.pieceList[0][0][2],
            # Left
            self.pieceList[0][2][0], self.pieceList[0][1][0], self.pieceList[0][0][0],
            self.pieceList[1][2][0], self.pieceList[1][1][0], self.pieceList[1][0][0],
            self.pieceList[2][2][0], self.pieceList[2][1][0], self.pieceList[2][0][0],
            # Front
            self.pieceList[0][0][0], self.pieceList[0][0][1], self.pieceList[0][0][2],
            self.pieceList[1][0][0], self.pieceList[1][0][1], self.pieceList[1][0][2],
            self.pieceList[2][0][0], self.pieceList[2][0][1], self.pieceList[2][0][2],
            # Right
            self.pieceList[0][0][2], self.pieceList[0][1][2], self.pieceList[0][2][2],
            self.pieceList[1][0][2], self.pieceList[1][1][2], self.pieceList[1][2][2],
            self.pieceList[2][0][2], self.pieceList[2][1][2], self.pieceList[2][2][2],
            # Back
            self.pieceList[0][2][2], self.pieceList[0][2][1], self.pieceList[0][2][0],
            self.pieceList[1][2][2], self.pieceList[1][2][1], self.pieceList[1][2][0],
            self.pieceList[2][2][2], self.pieceList[2][2][1], self.pieceList[2][2][0],
            # Down
            self.pieceList[2][0][0], self.pieceList[2][0][1], self.pieceList[2][0][2],
            self.pieceList[2][1][0], self.pieceList[2][1][1], self.pieceList[2][1][2],
            self.pieceList[2][2][0], self.pieceList[2][2][1], self.pieceList[2][2][2]
        ]
        # fmt: on

    async def doMove(self, move: str) -> None:
        """
        Executes a single cube move asynchronously as specified by the move notation.

        Parameters:
            move (str): The move to be executed, described in standard cube notation.

        Modifies the cube state by rotating layers according to the specified move and
        handles the updating of the move history.
        """
        # Extract repeat part
        repeat = int(match.group()) % 4 if (match := re.search(r"\d+", move)) else 1

        # Generalizes suffix
        if repeat == 0:
            return
        elif repeat == 1:
            move = move[:1] + "'" if move.endswith("'") else move[:1]
        elif repeat == 2:
            move = move[:1] + "2"
        elif repeat == 3:
            move = move[:1] if move.endswith("'") else move[:1] + "'"
            repeat = 1

        # Add to previous moves
        self.previousMoves += " " + move

        # Simplifies if possible
        self.previousMoves = self.simplifySequence(self.previousMoves)

        # Adjust for prime move if applicable
        for _ in range(repeat):
            if move.endswith("'"):
                self.rotateLayer(self.layers[move[:1]], move[:1], prime=True)
            else:
                self.rotateLayer(self.layers[move[:1]], move[:1])
            await asyncio.sleep(0.2)


async def getInput(cube, simulator):
    """
    Handles user input asynchronously in a loop, allowing the user to interact with
    the cube simulation through various commands like adding sequences, saving
    sequences, moving the cube, scrambling, solving, and managing the simulation state.

    Parameters:
        cube (ThreeByThree): The cube object to interact with.
        simulator (RubiksCubeSimulator): The cube simulator object for graphical
                                         interaction.
    """

    async def shutdown(simulator):
        await asyncShutdown.wait()
        simulator.running = False

    while inp := await ainput("What to do? "):
        if re.search(r"(?i)add seq", inp):
            cube.editSequenceMap()
        elif re.search(r"(?i)save seq", inp):
            cube.saveSequenceMap()
        elif re.search(r"(?i)move", inp):
            await cube.getMove()
        elif re.search(r"(?i)scramble", inp):
            repeat = int(match.group()) if (match := re.search(r"\d+", inp)) else 50
            await cube.scramble(repeat)
            cube.pPrint()
            print(f"Solved = {cube.isSolved()}")
            print(cube.previousMoves)
        elif re.search(r"(?i)solve", inp):
            await cube.solve()
            cube.pPrint()
            print(f"Solved = {cube.isSolved()}")
            print(cube.previousMoves)
        elif re.search(r"(?i)save", inp):
            cube.save()
        elif re.search(r"(?i)shutdown", inp):
            if simulator.running:
                print("Shutting down simulation...")
                asyncShutdown.set()
            else:
                print("No simulation running")
        elif re.search(r"(?i)simulate", inp):
            if simulator.running:
                print("Simulation alreday running")
            else:
                print("Starting simulation...")
                asyncShutdown.clear()
                asyncio.create_task(simulator.run())
                asyncio.create_task(shutdown(simulator))
        await asyncio.sleep(0)
    asyncShutdown.set()


asyncShutdown = asyncio.Event()


async def main():
    """
    Main function to initiate the cube and simulator, and start handling user input.
    Sets up an asynchronous event loop to manage cube operations and user interactions.
    """
    cube = ThreeByThree()
    simulator = RubiksCubeSimulator(cube)

    await getInput(cube, simulator)


if __name__ == "__main__":
    asyncio.run(main())
