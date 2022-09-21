import cv2
import pickle
import cvzone
import numpy as np
import psycopg2

con = psycopg2.connect(
    database="test", user='postgres', password='1234', host='localhost'
)

cur = con.cursor()


# Video feed
cap = cv2.VideoCapture('./1218.mp4')

with open('./CarParkPosition', 'rb') as f:
    posList = pickle.load(f)

width, height = 54, 31
y1, y2, x1, x2 = (663, 78, 717, 109)


def checkParkingSpace1(imgPro):
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]

        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

        if count < 200:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 1
            # spaceCounter -= 1

        cv2.rectangle(img, pos, (pos[0] + width,
                      pos[1] + height), color, thickness)

        # cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
        #                    thickness=2, offset=0, colorR=color)
    cvzone.putTextRect(img, f'Status: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))

    ss = (f'{spaceCounter}/{len(posList)}')
    sql = f"update park_st set total={spaceCounter}, blank={len(posList)}, ts=now() where id = 1;"
    print(sql)

    cur.execute(sql)
    con.commit()
    # con.close()


while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace1(imgDilate)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    # cv2.waitKey(1)
    if cv2.waitKey(24) == 27:
        break
cap.release()
cv2.destroyAllWindows()
