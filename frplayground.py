import cv2


def get_x_y_lower_left(image, window_size=1500):
    def odd_int(val):
        val = int(val)
        if val % 2 == 0:
            return val + 1
        return val

    image = cv2.imread(image)
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (odd_int(window_size/10), odd_int(window_size/10)), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

    x, y = (maxLoc)
    x -= int(window_size/2)
    y -= int(window_size/2)

    return (x, y)


if __name__=="__main__":
    r =   get_x_y_lower_left("_FINDROI_1.png", 1500)
    print(r)
