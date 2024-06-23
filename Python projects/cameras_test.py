import cv2

def check_cameras(max_cameras=10):
    cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            print("Camera not detected.")
	    print(i)
        else:
            print("Camera detected.")
	    print(i)
            cameras.append(cap)
    return cameras

def main():
    cameras = check_cameras()

    while True:
        for idx, cap in enumerate(cameras):
            ret, frame = cap.read()
            if ret:
                cv2.imshow(str(idx) , frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in cameras:
        cap.release()
    cv2.destroyAllWindows()


main()

