def point_in_rectangle(point, rectangle):

    left_sides = 0
    for i in range(0,4):

        corner_1 = rectangle[i%4]
        corner_2 = rectangle[(i+1)%4]

        dot = (corner_2[0] - corner_1[0]) * (point[1] - corner_1[1]) - (point[0] - corner_1[0]) * (corner_2[1] - corner_1[1])
        #print("point",point,"rect",rectangle,"dot",dot)
        if dot < 0:
            left_sides += 1
        else:
            return False

    if left_sides == 4:
        return True
    else:
        return False

def rectangle_collison(rect1, rect2):

    for point in rect1:

        result = point_in_rectangle(point, rect2)
        #print("point:",point,"rect",rect2,"result",result)
        if result:
            return True

    for point in rect2:

        result = point_in_rectangle(point,rect1)
        #print("point:",point,"rect",rect1,"result",result)
        if result:
            return True

    return False


if __name__ == "__main__":

    #rect1 = [(2,10),(2,5),(7,5),(7,10)]
    rect1 = [(755.0, 300.0), (655.0, 300.0), (655.0, 350.0), (755.0, 350.0)]
    #rect2 = [(9,15),(6.9,12),(12,4),(14,7)]
    rect2 = [(800.0, 550.0), (800.0, 650.0), (850.0, 650.0), (850.0, 550.0)]
    rect3 = [(800.0, 280.0), (700.0, 280.0), (700.0, 330.0), (800.0, 330.0)]
    rect4 = [(800.0, 460.0), (700.0, 460.0), (700.0, 510.0), (800.0, 510.0)]

    print(point_in_rectangle((755.0, 300.0),rect3))
    print(point_in_rectangle((700.0, 330.0),rect1))
    print(rectangle_collison(rect1,rect2))
    print(rectangle_collison(rect1,rect3))
    print(rectangle_collison(rect1,rect4))
