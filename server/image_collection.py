import os
import cv2

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 45
dataset_size = 100

cap = cv2.VideoCapture(0)
for j in range(number_of_classes):
    class_dir = os.path.join(DATA_DIR, str(j))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print('Collecting data for class {}'.format(j))

    existing_images = len(os.listdir(class_dir))
    images_to_capture = dataset_size - existing_images

    if images_to_capture <= 0:
        print("Class {} already has {} images. Skipping...".format(j, dataset_size))
        continue

    done = False
    while True:
        ret, frame = cap.read()
        cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                    cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) == ord('q'):
            break

    counter = 0
    while counter < images_to_capture:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        cv2.waitKey(100)
        cv2.imwrite(os.path.join(class_dir, '{}.jpg'.format(existing_images + counter)), frame)

        counter += 1

cap.release()
cv2.destroyAllWindows()
