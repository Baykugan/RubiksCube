"""
This module defines the basic components of a Rubik's Cube puzzle, including various
types of pieces such as internal, middle, edge, and corner pieces. Each piece has
unique identifiers and can undergo transformations like rotations, reflecting their
behavior in a physical Rubik's Cube.

Classes:
    Piece: Base class for a piece of the Rubik's Cube.
"""

import itertools


class Piece:
    """
    Base class for a piece of the Rubik's Cube.

    Attributes:
        ID_ITER (itertools.count): An iterator for generating unique piece identifiers.
        id (int): The unique identifier of the piece.
        faces (dict): A dictionary of the piece's faces and their corresponding colors.
        rotation_map (dict): A dictionary mapping rotation directives to axis of
            rotation.

    Methods:
        rotate(): Rotates the piece according to a given rotation directive and mode.
        do_rotation(): Performs the rotation on the piece's faces based on the
            specified axis.
        invert_axis(): Inverts the specified axis direction.
        get_face_color(): Returns the color of the specified face of the piece.
    """

    ID_ITER = itertools.count()

    def __init__(self) -> None:
        """
        Initializes a new instance of the Piece class.
        """

        self.id = next(Piece.ID_ITER)

        self.faces = {
            "U": "white".ljust(6),
            "L": "orange".ljust(6),
            "F": "green".ljust(6),
            "R": "red".ljust(6),
            "B": "blue".ljust(6),
            "D": "yellow".ljust(6),
        }

        self.rotation_map = {
            "U": "Y",
            "F": "Z",
            "L": "-X",
            "D": "-Y",
            "B": "-Z",
            "R": "X",
            "E": "-Y",
            "S": "Z",
            "M": "-X",
        }

    def __repr__(self) -> str:
        return self.id

    def rotate(self, rotation: str, prime: bool = False) -> None:
        """
        Rotates the piece according to a given rotation directive and mode.

        Args:
            rotation (str): The rotation directive (e.g., 'U', 'F').
            prime (bool): Indicates if the rotation should be counter-clockwise (True)
                          or clockwise (False).
        """

        rotation = self.rotation_map[rotation]
        if rotation.startswith("-"):
            rotation = rotation[1:]
            prime = not prime

        self.do_rotation(rotation, prime=prime)

    def do_rotation(self, axis: str, prime: bool = False) -> None:
        """
        Performs the rotation on the piece's faces based on the specified axis.

        Args:
            axis (str): The axis of rotation ('X', 'Y', 'Z').
            prime (bool): Indicates if the rotation should be counter-clockwise (True)
                          or clockwise (False).
        """

        # fmt: off
        if axis == "X":
            self.faces["F"], self.faces["U"], self.faces["B"], self.faces["D"] = (
                self.faces["D"], self.faces["F"], self.faces["U"], self.faces["B"]
            )
        elif axis == "Y":
            self.faces["L"], self.faces["F"], self.faces["R"], self.faces["B"] = (
                self.faces["F"], self.faces["R"], self.faces["B"], self.faces["L"]
            )
        elif axis == "Z":
            self.faces["L"], self.faces["U"], self.faces["R"], self.faces["D"] = (
                self.faces["D"], self.faces["L"], self.faces["U"], self.faces["R"]
            )
        # fmt: on

        if prime:
            self.do_rotation(axis, False)
            self.do_rotation(axis, False)

    def invert_axis(self, axis: str) -> str:
        """
        Inverts the specified axis direction.

        Args:
            axis (str): The axis of rotation ('X', 'Y', 'Z').

        Returns:
            str: The inverted axis direction.
        """

        return axis[1:] if axis.startswith("-") else "-" + axis

    def get_face_color(self, face: str) -> str:
        """
        Returns the color of the specified face of the piece.

        Args:
            face (str): The face of the piece ('U', 'L', 'F', 'R', 'B', 'D').

        Returns:
            str: The color of the specified face.
        """

        return self.faces[face]
