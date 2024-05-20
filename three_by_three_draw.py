"""
This module provides a graphical simulation of a 3x3 Rubik's Cube using Pygame. 
It renders a 3D Rubik's Cube that can be interactively rotated and manipulated.
It supports asynchronous operations to keep the simulation responsive.

Classes:
    RubiksCubeSimulator: Handles the graphical rendering and interaction of a 3x3 
    Rubik's Cube simulation in a 3D space.
"""

import asyncio
import pygame
import numpy as np


class RubiksCubeSimulator:
    """
       6_ _ _ _ _ _ _ _6
       /|             /|
      / |            / |
    3 _ _ _ _ _ _ _2/  |
    |   |          |   |
    |   |          |   |
    |   7_ _ _ _ _ |_ _5
    |  /           |  /
    | /            | /
    0/_ _ _ _ _ _ _1/
    """

    def __init__(self, cube) -> None:
        self.cube = cube
        self.running = False

        # Set up the display
        self.size = (640, 480)
        self.fov, self.distance = 90, 3

        self.angle_x, self.angle_y = 0, 0

        # Define colors
        self.colors = {
            "white".ljust(6): (255, 255, 255),
            "green".ljust(6): (0, 255, 0),
            "red".ljust(6): (255, 0, 0),
            "blue".ljust(6): (0, 0, 255),
            "orange".ljust(6): (255, 165, 0),
            "yellow".ljust(6): (255, 255, 0),
        }

        # fmt: off
        # Define vertices of a cube
        self.vertices = [
            # Points on the corners of the cube
            # 0 - 7
            np.array([-1, -1, -1]),
            np.array([1, -1, -1]),
            np.array([1, 1, -1]),
            np.array([-1, 1, -1]),
            np.array([-1, -1, 1]),
            np.array([1, -1, 1]),
            np.array([1, 1, 1]),
            np.array([-1, 1, 1]),
            # Points on the edges of front layer
            # 8 - 15
            np.array([-1/3, -1, -1]),
            np.array([1/3, -1, -1]),
            np.array([1, -1/3, -1]),
            np.array([1, 1/3, -1]),
            np.array([1/3, 1, -1]),
            np.array([-1/3, 1, -1]),
            np.array([-1, 1/3, -1]),
            np.array([-1, -1/3, -1]),
            # Points on the edges of back layer
            # 16 - 23
            np.array([-1/3, -1, 1]),
            np.array([1/3, -1, 1]),
            np.array([1, -1/3, 1]),
            np.array([1, 1/3, 1]),
            np.array([1/3, 1, 1]),
            np.array([-1/3, 1, 1]),
            np.array([-1, 1/3, 1]),
            np.array([-1, -1/3, 1]),
            # Points on the edges in the z direction, starting on between L and U
            # 24 - 31
            np.array([-1, -1, -1/3]),
            np.array([-1, -1, 1/3]),
            np.array([1, -1, -1/3]),
            np.array([1, -1, 1/3]),
            np.array([1, 1, -1/3]),
            np.array([1, 1, 1/3]),
            np.array([-1, 1, -1/3]),
            np.array([-1, 1, 1/3]),
            # Points on front face
            # 32 - 35
            np.array([-1/3, -1/3, -1]),
            np.array([1/3, -1/3, -1]),
            np.array([1/3, 1/3, -1]),
            np.array([-1/3, 1/3, -1]),
            # Points on back face
            # 36 - 39
            np.array([-1/3, -1/3, 1]),
            np.array([1/3, -1/3, 1]),
            np.array([1/3, 1/3, 1]),
            np.array([-1/3, 1/3, 1]),
            # Points on down face
            # 40 - 43
            np.array([-1/3, -1, -1/3]),
            np.array([1/3, -1, -1/3]),
            np.array([1/3, -1, 1/3]),
            np.array([-1/3, -1, 1/3]),
            # Points on right face
            # 44 - 47
            np.array([1, -1/3, -1/3]),
            np.array([1, 1/3, -1/3]),
            np.array([1, 1/3, 1/3]),
            np.array([1, -1/3, 1/3]),
            # Points on up face
            # 48 - 51
            np.array([1/3, 1, -1/3]),
            np.array([-1/3, 1, -1/3]),
            np.array([-1/3, 1, 1/3]),
            np.array([1/3, 1, 1/3]),
            # Points on left face
            # 52 - 55
            np.array([-1, 1/3, -1/3]),
            np.array([-1, -1/3, -1/3]),
            np.array([-1, -1/3, 1/3]),
            np.array([-1, 1/3, 1/3]),
        ]
        # fmt: on

        # fmt: off
        # Define edges between vertices
        self.edges = [
            # Edges of the cube
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
            # Edges of the squares on the front face
            (8, 13), (9, 12), (10, 15), (11, 14),
            # Edges of the squares on the back face
            (16, 21), (17, 20), (18, 23), (19, 22),
            # Edges of the squares on the down face
            (8, 16), (9, 17), (24, 26), (25, 27),
            # Edges of the squares on the right face
            (10, 18), (11, 19), (26, 28), (27, 29),
            # Edges of the squares on the up face
            (12, 20), (13, 21), (28, 30), (29, 31),
            # Edges of the squares on the left face
            (14, 22), (15, 23), (30, 24), (31, 25)

            # (32, 33), (33, 34), (34, 35), (35, 32),
            # (36, 37), (37, 38), (38, 39), (39, 36),
            # (40, 41), (41, 42), (42, 43), (43, 40),
            # (44, 45), (45, 46), (46, 47), (47, 44),
            # (48, 49), (49, 50), (50, 51), (51, 48),
            # (52, 53), (53, 54), (54, 55), (55, 52)
        ]
        # fmt: on

        # fmt: off
        # Define squares
        self.squares = [
            # Up
            (7, 21, 50, 31), (21, 20, 51, 50), (20, 6, 29, 51),
            (31, 50, 49, 30), (50, 51, 48, 49), (51, 29, 28, 48),
            (30, 49, 13, 3), (49, 48, 12, 13), (48, 28, 2, 12),
            # Left
            (7, 31, 55, 22), (31, 30, 52, 55), (30, 3, 14, 52),
            (22, 55, 54, 23), (55, 52, 53, 54), (52, 14, 15, 53),
            (23, 54, 25, 4), (54, 53, 24, 25), (53, 15, 0, 24),
            # Front
            (3, 13, 35, 14), (13, 12, 34, 35), (12, 2, 11, 34),
            (14, 35, 32, 15), (35, 34, 33, 32), (34, 11, 10, 33),
            (15, 32, 8, 0), (32, 33, 9, 8), (33, 10, 1, 9),
            # Right
            (2, 28, 45, 11), (28, 29, 46, 45), (29, 6, 19, 46),
            (11, 45, 44, 10), (45, 46, 47, 44), (46, 19, 18, 47),
            (10, 44, 26, 1), (44, 47, 27, 26), (47, 18, 5, 27),
            # Back
            (6, 20, 38, 19), (20 ,21, 39, 38), (21, 7, 22, 39),
            (19, 38, 37, 18), (38, 39, 36, 37), (39, 22, 23, 36),
            (18, 37, 17, 5), (37, 36, 16, 17), (36, 23, 4, 16),
            # Down
            (0, 8, 40, 24), (8, 9, 41, 40), (9, 1, 26, 41),
            (24, 40, 43, 25), (40, 41, 42, 43), (41, 26, 27, 42),
            (25, 43, 16, 4), (43, 42, 17, 16), (42, 27, 5, 17)
        ]
        # fmt: on

    def project_point(self, point, size, fov, viewer_distance):
        fov_rad = np.radians(fov)
        focal_length = (min(size[0], size[1]) / 2) / np.tan(fov_rad / 2)

        adjusted_z = point[2] + viewer_distance

        projected_x = (point[0] * focal_length) / adjusted_z + (size[0] / 2)
        projected_y = -(point[1] * focal_length) / adjusted_z + (size[1] / 2)

        return (int(projected_x), int(projected_y), point[2])

    def rotate_x(self, point, angle):
        """Rotate a point around the x-axis by the given angle."""
        rotation_matrix = np.array(
            [
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ]
        )
        return np.dot(point, rotation_matrix)

    def rotate_y(self, point, angle):
        """Rotate a point around the y-axis by the given angle."""
        rotation_matrix = np.array(
            [
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ]
        )
        return np.dot(point, rotation_matrix)

    async def run(self):
        # pylint: disable=no-member
        pygame.init()

        self.angle_x, self.angle_y = 0, 0

        screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        pygame.display.set_caption("3D Rubik's Cube")
        clock = pygame.time.Clock()

        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\n------------------------------------------")
                    print("Window closed, shutting down simulation...")
                    print("------------------------------------------")
                    print("Previous question continues: ", end="")
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.size = event.size
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.angle_y -= 0.01
            if keys[pygame.K_RIGHT]:
                self.angle_y += 0.01
            if keys[pygame.K_UP]:
                self.angle_x -= 0.01
            if keys[pygame.K_DOWN]:
                self.angle_x += 0.01
            if keys[pygame.K_r]:
                self.angle_x = 0
                self.angle_y = 0
            if keys[pygame.K_m]:
                self.cube.getMove()
            # pylint: enable=no-member

            # Apply rotation
            rotated_vertices = [
                self.rotate_x(self.rotate_y(vertex, self.angle_y), self.angle_x)
                for vertex in self.vertices
            ]

            screen.fill((100, 100, 100))  # Clear the screen

            # Draw each square of the cube

            drawables = []
            for index, square in enumerate(self.squares):
                points = []
                for vertex_index in square:
                    projected_point = self.project_point(
                        rotated_vertices[vertex_index],
                        self.size,
                        self.fov,
                        self.distance,
                    )
                    points.append(projected_point)
                drawables.append(DrawableSquare(self.cube, points, index, self.colors))

            drawables.sort(key=lambda obj: obj.average_z, reverse=True)
            for drawable in drawables:
                drawable.draw(screen)

            pygame.display.flip()  # Update the display
            clock.tick(144)  # Limit frames per second
            await asyncio.sleep(0)  # Yields to event loop

        pygame.quit()


class DrawableSquare:
    def __init__(self, cube, points, index, color_dict):
        self.cube = cube
        self.points = points  # Points should be a list of tuples or Vector3
        self.faces = ["U", "L", "F", "R", "B", "D"]
        self.index = index
        self.colors = color_dict

    def draw(self, surface):
        points = self.remove_z()
        piece = self.cube.faces[self.index][0]
        pygame.draw.polygon(
            surface, self.colors[piece.faces[self.faces[self.index // 9]]], points
        )
        pygame.draw.polygon(surface, (0, 0, 0), points, 3)

    def remove_z(self):
        new_points = []
        for point in self.points:
            new_points.append((point[0], point[1]))
        return new_points

    @property
    def average_z(self):
        # Calculate the average z-value of the points
        return sum(point[2] for point in self.points) / len(self.points)
