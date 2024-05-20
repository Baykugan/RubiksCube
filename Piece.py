"""
This module defines the basic components of a Rubik's Cube puzzle, including various
types of pieces such as internal, middle, edge, and corner pieces. Each piece has
unique identifiers and can undergo transformations like rotations, reflecting their
behavior in a physical Rubik's Cube.

Classes:
    Piece: Base class for a piece of the Rubik's Cube.
    InternalPiece: Represents an internal (hidden) piece that does not move.
    MiddlePiece: Represents a middle piece that can be part of two sides but doesn't
                 reach any edge.
    EdgePiece: Represents an edge piece that spans two adjacent sides.
    CornerPiece: Represents a corner piece that spans three adjacent sides.
"""

import itertools


class Piece:
    """
    Represents a piece of a Rubik's Cube. Each piece has unique properties such as type
    and face colors. Pieces can be rotated, reflecting their behavior in a physical
    Rubik's Cube.

    Attributes:
        id (int): A unique identifier for the piece, automatically generated.
        piece_type (str): A string representing the type of piece ("OP" by default).
        faces (dict): A dictionary mapping each face ('U', 'L', 'F', 'R', 'B', 'D') to
                      its color.
        rotation_map (dict): A dictionary mapping rotation directions to cube faces.

    Methods:
        rotate: Rotates the piece according to a specified rotation direction and mode
                (prime).
        do_rotation: Performs the rotation on the piece's faces based on the specified
                    axis.
        invert_axis: Inverts the axis direction for rotation.
        get_face_color: Returns the color of a specified face.
    """

    ID_ITER = itertools.count()

    def __init__(self) -> None:
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

        Parameters:
            rotation (str): The rotation directive (e.g., 'U', 'F').
            prime (bool): Indicates whether the rotation should be counter-clockwise
                          (True) or clockwise (False).
        """
        rotation = self.rotation_map[rotation]
        if rotation.startswith("-"):
            rotation = rotation[1:]
            prime = not prime

        self.do_rotation(rotation, prime=prime)

    def do_rotation(self, axis: str, prime: bool = False) -> None:
        """
        Performs the rotation on the piece's faces based on the specified axis.

        Parameters:
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

        Parameters:
            axis (str): The axis to invert ('X', 'Y', 'Z', with optional leading '-').

        Returns:
            str: The inverted axis direction.
        """
        return axis[1:] if axis.startswith("-") else "-" + axis

    def get_face_color(self, face: str) -> str:
        """
        Returns the color of the specified face of the piece.

        Parameters:
            face (str): The face identifier ('U', 'L', 'F', 'R', 'B', 'D').

        Returns:
            str: The color of the specified face.
        """
        return self.faces[face]
