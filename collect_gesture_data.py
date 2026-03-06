import cv2
import mediapipe as mp
import csv

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)

cap = cv2.VideoCapture(0)

gesture_label = input("Enter gesture label: ")

data = []

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:

            features = []

            for lm in hand.landmark:
                features.extend([lm.x, lm.y, lm.z])

            features.append(gesture_label)
            data.append(features)

    cv2.imshow("Collecting", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

with open("gesture_dataset.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

print("Data saved.")