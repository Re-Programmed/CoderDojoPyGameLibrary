import pygame
from pygame.locals import *
from abc import ABC, abstractmethod
import coderDojoPyGameCollision as collision
from typing import TypeVar

PygamePosition: type = type((float, float))
AlignedPosition: type = type((float, float))


GameClock = pygame.time.Clock()
GameDeltaTime = 0

class Renderable(ABC):
    @abstractmethod
    def Render(self, pos: AlignedPosition, scale: (float, float)):
        pass


def ToPygamePosition(position: AlignedPosition) -> PygamePosition:
    """
    Converts a position orienting everything to the bottom left to one orienting everything to the top left.
    :param position:
    :return:
    """
    return position[0], GetCurrentGameWindow().GetSize()[1] - position[1]


def ToAlignedPosition(position: PygamePosition) -> AlignedPosition:
    """
    Converts a position orienting everything to the top left to one orienting everything to the bottom left.
    :param position:
    :return:
    """
    return position[0], GetCurrentGameWindow().GetSize()[1] - position[1]


class ImageRenderable(Renderable):
    __image: pygame.image = None

    def __init__(self, imageFile: str):
        self.__image = pygame.image.load(imageFile)

    def Render(self, pos: AlignedPosition, scale: (float, float)):
        pPos = ToPygamePosition(pos)
        pygame.display.get_surface().blit(pygame.transform.scale(self.__image, scale), pPos)


class RectangleRenderable(Renderable):
    """
    Renderable for a rectangle with width, height, and color.
    """
    __color: Color = (255, 255, 255)

    def __init__(self, color: Color = (255, 255, 255)):
        self.__color = color

    def Render(self, pos: AlignedPosition, scale: (float, float)):
        pPos = ToPygamePosition(pos)
        pygame.draw.rect(pygame.display.get_surface(), self.__color, Rect(pPos[0], pPos[1] - scale[1], scale[0], scale[1]))


class TextRenderable(Renderable):
    __fontObject: pygame.sysfont.SysFont = None
    __text: str = ""
    __color: Color = (0, 0, 0)

    def SetFont(self, font: str, size: int):
        self.__fontObject = pygame.sysfont.SysFont(font, size)

    def SetText(self, text: str):
        self.__text = text

    def GetText(self) -> str:
        return self.__text

    def SetColor(self, color: Color):
        self.__color = color

    def __init__(self, text: str, font: str, size: int, color: Color):
        #'arial', 30
        self.__color = color
        self.__text = text
        self.__fontObject = pygame.sysfont.SysFont(font, size)

    def Render(self, pos: AlignedPosition, scale: (float, float)):
        surface = self.__fontObject.render(self.__text, False, self.__color)
        pygame.display.get_surface().blit(surface, ToPygamePosition(pos))


class CircleRenderable(Renderable):
    __color: Color = (255, 255, 255)

    def __init__(self, color: Color = (255, 255, 255)):
        self.__color = color

    def Render(self, pos: AlignedPosition, scale: (float, float)):
        pPos = ToPygamePosition(pos)
        pygame.draw.circle(pygame.display.get_surface(), self.__color, (pPos[0] + scale[0]/2, pPos[1] - scale[1]/2), scale[0])


class GameObject:
    """
    An object in the game with position, scale, and rendered graphics.
    """
    _position: AlignedPosition = (0, 0)
    _scale: (float, float) = (0, 0)
    _renderer: Renderable
    __canCollide: bool = True
    __enabled: bool = True

    def SetEnabled(self, enabled: bool):
        self.__enabled = enabled

    def SetPosition(self, position: AlignedPosition):
        self._position = position

    def GetPosition(self) -> (float, float):
        return self._position

    def SetScale(self, scale: (float, float)):
        self._scale = scale

    def GetScale(self) -> (float, float):
        return self._scale

    def SetAllowOtherCollisions(self, allow: bool):
        self.__canCollide = allow

    def IsAllowingOtherCollisions(self) -> bool:
        return self.__canCollide

    def Translate(self, translation: (float, float)):
        self._position = (self._position[0] + translation[0], self._position[1] + translation[1])

    def GetRenderable(self) -> Renderable:
        """
        Returns the renderable for this object containing information on how to display the object.
        :return: Renderable
        """
        return self._renderer

    def Update(self):
        """
        Called each frame to update stuff.
        :return:
        """
        if not self.__onUpdate is None:
            self.__onUpdate(self)

    def Render(self):
        """
        Draw the object.
        :return:
        """
        if not self.__enabled:
            return
        self._renderer.Render(self._position, self._scale)

    def __init__(self, position: AlignedPosition, scale: (float, float), renderable: Renderable = RectangleRenderable(), canCollide: bool = True, onUpdate = None, enabled: bool = True):
        self._scale = scale
        self._position = position
        self._renderer = renderable
        self.__canCollide = canCollide
        self.__onUpdate = onUpdate
        self.__enabled = enabled


class PhysicsGameObject(GameObject):
    __vel: (float, float) = (0, 0)
    __acc: (float, float) = (0, 0)
    __friction: float = 0
    __collisionEnabled: bool = True

    def __init__(self, position: AlignedPosition, scale: (float, float), renderable: Renderable = RectangleRenderable(),
                 initalVelocity: (float, float) = (0, 0), initalAcceleration: (float, float) = (0, 0),
                 friction: float = 0, collisionEnabled: bool = True, onCollision=None):
        # onCollision should be in the form: (GameObject (self), GameObject (other), (float, float) pushAmount) -> bool (should stop velocity)
        super().__init__(position, scale, renderable)
        self.__vel = initalVelocity
        self.__acc = initalAcceleration
        self.__friction = friction
        self.__collisionEnabled = collisionEnabled
        self.__onCollision = onCollision

    def SetVelocity(self, velocity: (float, float)):
        self.__vel = velocity

    def SetAcceleration(self, acceleration: (float, float)):
        self.__acc = acceleration

    def GetVelocity(self) -> (float, float):
        return self.__vel

    def GetAcceleration(self) -> (float, float):
        return self.__acc

    def SetFriction(self, friction: float):
        self.__friction = friction

    def GetFriction(self) -> float:
        return self.__friction

    def SetOnCollision(self, collisionFunc):
        self.__onCollision = collisionFunc

    def OnCollision(self, other: GameObject, push: (float, float)):
        shouldStopVelocity = True
        if not self.__onCollision is None:
            shouldStopVelocity = self.__onCollision(self, other, push)

        if shouldStopVelocity:
            if push[0] != 0:
                self.__vel = (0, self.__vel[1])
            if push[1] != 0:
                self.__vel = (self.__vel[0], 0)

    def Update(self):
        #dx = vt + at^2/2
        posX = self._position[0]
        posX = posX + (self.__vel[0] * GameDeltaTime) + (self.__acc[0] * (GameDeltaTime ** 2))/2
        posY = self._position[1]
        posY = posY + (self.__vel[1] * GameDeltaTime) + (self.__acc[1] * (GameDeltaTime ** 2))/2
        self.SetPosition((posX, posY))

        #dv = at
        self.__vel = (self.__vel[0] + (self.__acc[0] * GameDeltaTime), self.__vel[1] + (self.__acc[1] * GameDeltaTime))

        # Frictional acceleration is calculated separate from other accelerations.
        if self.__vel[0] > 0.1:
            self.__vel = (self.__vel[0] - (self.__friction * GameDeltaTime), self.__vel[1])
        elif self.__vel[0] < -0.1:
            self.__vel = (self.__vel[0] + (self.__friction * GameDeltaTime), self.__vel[1])
        else:
            self.__vel = (0, self.__vel[1])

        if self.__vel[1] > 0.1:
            self.__vel = (self.__vel[0], self.__vel[1] - (self.__friction * GameDeltaTime))
        elif self.__vel[1] < -0.1:
            self.__vel = (self.__vel[0], self.__vel[1] + (self.__friction * GameDeltaTime))
        else:
            self.__vel = (self.__vel[0], 0)

        if self.__collisionEnabled:
            collisions = GetAllOverlappingObjects(self)
            for result in collisions:
                # Don't collide with objects that don't allow it.
                if not result["object"].IsAllowingOtherCollisions():
                    continue

                # self.Translate(result["push"])
                self.OnCollision(result["object"], result["push"])

        super().Update()


class Window:
    """
    The window the game is running in.
    """
    __size: (int, int) = (500, 500)
    __bgColor: Color = Color(255, 255, 255)
    __title: str = "PyGame Window"

    def __init__(self, size: (int, int), color: Color, title: str = "PyGame Window"):
        self.__size = size
        pygame.display.set_mode(size)
        self.SetColor(color)
        self.SetTite(title)

    def SetColor(self, color: Color):
        """
        Sets the background color of the window.
        :param color: Color
        """
        pygame.display.get_surface().fill(color)
        self.__bgColor = color

    def SetTite(self, title: str):
        """
        Sets the title to display for the window.
        :param title: str
        :return:
        """
        pygame.display.set_caption(title)
        self.__title = title

    def GetTitle(self) -> str:
        """
        Returns the currently displayed title for the window.
        :return: str
        """
        return self.__title

    def GetColor(self) -> Color:
        """
        Returns the background color of the window.
        :return: Color
        """
        return self.__bgColor

    def Refresh(self):
        """
        Clears the screen.
        :return:
        """
        pygame.display.get_surface().fill(self.__bgColor)

    def SetSize(self, size: (int, int)):
        """
        Sets the size of the window.
        :param size: (int, int)
        """
        pygame.display.set_mode(size)
        self.__size = size

    def GetSize(self) -> (int, int):
        """
        Returns the size of the window.
        :return: (int, int)
        """
        return self.__size


__gameObjects: list[GameObject] = []
"""
    All the objects in your game.
"""

__currentGameWindow: Window | None = None
"""
    The current displayed window for your game.
"""


def InitGame():
    """
    Initilize pygame.
    Call before anything else.
    :return:
    """
    pygame.init()
    pygame.font.init()


def GetCurrentGameWindow() -> Window:
    """
        Returns the current displayed window for your game.
        :return: Window
    """
    if __currentGameWindow is None:
        print("Tried to get the current game window before creating a window.")
        return None

    return __currentGameWindow


def __updateDisplay():
    pygame.display.flip()
    pygame.display.update()


COLLISION_PADDING: (float, float) = (7, 2)


def GetAllOverlappingObjects(testObject: GameObject) -> list[dict]:
    global COLLISION_PADDING
    """
    Returns a list of dictionaries containing each overlapping object and by how much they overlap.
    :param testObject: GameObject
    :return: list[dict]
    {
        "collided" - bool
        "push" - (float, float)
        "object" - GameObject
    }
    """
    resultingCollisions: list[dict] = []
    for gObject in __gameObjects:
        if gObject is testObject:
            continue

        result = collision.BoxWithinBox(testObject.GetPosition(), testObject.GetScale(), (gObject.GetPosition()[0] + COLLISION_PADDING[0], gObject.GetPosition()[1] + COLLISION_PADDING[1]), (gObject.GetScale()[0] - COLLISION_PADDING[0], gObject.GetScale()[1] - COLLISION_PADDING[1]))
        if result["collided"]:
            result["object"] = gObject
            resultingCollisions.append(result)

    return resultingCollisions


def CreateWindow(size: (int, int), color: Color, title: str = "PyGame Window") -> Window:
    """
    Create a window with given size, color, and title.
    :param size: (int, int)
    :param color: Color
    :param title: str
    :return: Window
    """
    global __currentGameWindow
    __currentGameWindow = Window(size, color, title)
    return __currentGameWindow


def GetMousePosition() -> AlignedPosition:
    return ToAlignedPosition(pygame.mouse.get_pos())


def GetMousePressed(button: int) -> bool:
    return pygame.mouse.get_pressed()[button]


T = TypeVar('T')


def InstantiateGameObject(gObject: T) -> T:
    """
    Adds the provided object to the game and renderer to be rendered.
    :param gObject: GameObject
    :return: GameObject
    """
    global __gameObjects
    __gameObjects.append(gObject)
    return gObject


def UpdateGame() -> bool:
    global GameDeltaTime
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            return False
    __currentGameWindow.Refresh()
    __render()
    __updateDisplay()
    GameDeltaTime = GameClock.tick() / 1000
    return True


def __render():
    global __gameObjects
    for obj in __gameObjects:
        obj.Update()
        obj.Render()


def GetGameDeltaTime() -> float:
    return GameDeltaTime


def GetKey(key: int) -> bool:
    keys = pygame.key.get_pressed()
    return keys[key]
