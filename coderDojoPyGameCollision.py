def __valueWithinScaleFromLowest(value: float, lowest: float, scale: float):
    return lowest + scale > value > lowest


def PointWithinBox(point: (float, float), boxPosition: (float, float), boxScale: (float, float)):
    return __valueWithinScaleFromLowest(point[0], boxPosition[0], boxScale[0]) and __valueWithinScaleFromLowest(point[1], boxPosition[1], boxScale[1])


def GetSideIntersectLength(intersectionPoint1: (float, float), intersectionPoint2: (float, float)) -> (float, float):
    return abs(intersectionPoint2[0] - intersectionPoint1[0]), abs(intersectionPoint2[1] - intersectionPoint1[1])


def BoxWithinBox(box1Pos: (float, float), box1Scale: (float, float), box2Pos: (float, float), box2Scale: (float, float)) -> dict:
    result = {
        "collided": False,
        "push": (0, 0)
    }

    if PointWithinBox((box1Pos[0] + box1Scale[0], box1Pos[0]), box2Pos, box2Scale):
        intersect = GetSideIntersectLength((box1Pos[0] + box1Scale[0], box1Pos[1]), (box2Pos[0], box2Pos[1] + box2Scale[1]))

        result["collided"] = True
        if intersect[1] <= intersect[0]:
            result["push"] = (0, intersect[1])
            return result

        if intersect[0] < intersect[1]:
            result["push"] = (-intersect[0], 0)
            return result

        return result

    if PointWithinBox((box1Pos[0] + box1Scale[0], box1Pos[1] + box1Scale[1]), box2Pos, box2Scale):
        intersect = GetSideIntersectLength((box1Pos[0] + box1Scale[0], box1Pos[1] + box1Scale[1]), box2Pos)

        result["collided"] = True
        if intersect[1] <= intersect[0]:
            result["push"] = (0, -intersect[1])
            return result

        if intersect[0] < intersect[1]:
            result["push"] = (-intersect[0], 0)
            return result

        return result

    if PointWithinBox(box1Pos, box2Pos, box2Scale):
        intersect = GetSideIntersectLength(box1Pos, (box2Pos[0] + box2Scale[0], box2Pos[1] + box2Scale[1]))

        result["collided"] = True
        if intersect[1] <= intersect[0]:
            result["push"] = (0, intersect[1])
            return result

        if intersect[0] < intersect[1]:
            result["push"] = (intersect[0], 0)
            return result

        return result

    if PointWithinBox((box1Pos[0], box1Pos[1] + box1Scale[1]), (box2Pos[0] + box2Scale[0], box2Pos[1]), box2Scale):
        intersect = GetSideIntersectLength((box1Pos[0], box1Pos[1] + box1Scale[1]), (box2Pos[0] + box2Scale[0], box2Pos[1]))

        result["collided"] = True
        if intersect[1] <= intersect[0]:
            result["push"] = (0, -intersect[1])
            return result

        if intersect[0] < intersect[1]:
            result["push"] = (intersect[0], 0)
            return result

    return result
