"""
This module provides a graphical simulation of a 3x3 Rubik's Cube using Pygame. It renders a 3D Rubik's Cube that can be
interactively rotated and manipulated. It supports asynchronous operations to keep the simulation responsive.

Classes:
    RubiksCubeSimulator: Handles the graphical rendering and interaction of a 3x3 Rubik's Cube simulation in a 3D space.
"""

import asyncio
import pygame
import numpy as np


class RubiksCubeSimulator:
    '''
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
    '''
    def __init__(self, cube) -> None:
        self.cube = cube
        self.running = False

        # Set up the display
        self.width, self.height = 640, 480
        self.fov, self.distance = 90, 3.5


        self.angleX, self.angleY = 0, 0

        # Define colors
        self.colors = {
            'white'.ljust(6): (255, 255, 255),
            'green'.ljust(6): (0, 255, 0),
            'red'.ljust(6): (255, 0, 0),
            'blue'.ljust(6): (0, 0, 255),
            'orange'.ljust(6): (255, 165, 0),
            'yellow'.ljust(6): (255, 255, 0)
        }

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

    def projectPoint(self, point, screenWidth, screenHeight, fov, viewerDistance):
        fovRad = np.radians(fov)
        focalLength = (screenWidth / 2) / np.tan(fovRad / 2)

        adjustedZ = point[2] + viewerDistance

        projectedX = (point[0] * focalLength) / adjustedZ + (screenWidth / 2)
        projectedY = -(point[1] * focalLength) / adjustedZ + (screenHeight / 2)

        return (int(projectedX), int(projectedY ), point[2])


    def rotateX(self, point, angle):
        """ Rotate a point around the x-axis by the given angle. """
        rotationMatrix = np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
        ])
        return np.dot(point, rotationMatrix)


    def rotateY(self, point, angle):
        """ Rotate a point around the y-axis by the given angle. """
        rotationMatrix = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
        ])
        return np.dot(point, rotationMatrix)

    async def run(self):
        # Initialize Pygame
        # pylint: disable=no-member
        pygame.init()
        # pylint: enable=no-member

        self.angleX, self.angleY = 0, 0

        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3D Rubik's Cube")
        clock = pygame.time.Clock()

        self.running = True

        # pylint: disable=no-member
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\n------------------------------------------")
                    print("Window closed, shutting down simulation...")
                    print("------------------------------------------")
                    print("Previous question continues: ", end="")
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.angleY -= 0.01
            if keys[pygame.K_RIGHT]:
                self.angleY += 0.01
            if keys[pygame.K_UP]:
                self.angleX -= 0.01
            if keys[pygame.K_DOWN]:
                self.angleX += 0.01
            if keys[pygame.K_r]:
                self.angleX = 0
                self.angleY = 0
            if keys[pygame.K_m]:
                self.cube.getMove()
            # pylint: enable=no-member

            # Apply rotation
            rotatedVertices = [self.rotateX(self.rotateY(vertex, self.angleY), self.angleX) for vertex in self.vertices]

            screen.fill((100, 100, 100))  # Clear the screen

            # Draw each square of the cube

            drawables = []
            for index, square in enumerate(self.squares):
                points = []
                for vertexIndex in square:
                    projectedPoint = self.projectPoint(rotatedVertices[vertexIndex], \
                                                       self.width, self.height, self.fov, self.distance)
                    points.append(projectedPoint)
                drawables.append(DrawableSquare(self.cube, points, index, self.colors))


            drawables.sort(key=lambda obj: obj.averageZ, reverse=True)
            for drawable in drawables:
                drawable.draw(screen)


            pygame.display.flip()  # Update the display
            clock.tick(144)  # Limit frames per second
            await asyncio.sleep(0) # Yields to event loop

        pygame.quit()








class DrawableSquare:
    def __init__(self, cube, points, index, colorDict):
        self.cube = cube
        self.points = points  # Points should be a list of tuples or Vector3
        self.faces = ["U", "L", "F", "R", "B", "D"]
        self.index = index
        self.colors = colorDict

    def draw(self, surface):
        points = self.removeZ()
        piece = self.cube.faces[self.index][0]
        pygame.draw.polygon(surface, self.colors[piece.faces[self.faces[self.index//9]]], points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 3)

    def removeZ(self,):
        newPoints = []
        for point in self.points:
            newPoints.append((point[0], point[1]))
        return newPoints

    @property
    def averageZ(self):
        # Calculate the average z-value of the points
        return sum(point[2] for point in self.points) / len(self.points)
