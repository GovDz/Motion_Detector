# By Feth-Ellah BOUDELLAL
import threading
import cv2
import imutils
import sounddevice as sd
import asyncio
import numpy as np
from telegram import Bot
from telegram import InputFile

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0

async def send_telegram_message(photo_path):
    try:
        bot_token = 'XX'
        chat_id = 'XX'
        bot = Bot(token=bot_token)

        caption = "Motion detected!"
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=InputFile(photo), caption=caption)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

async def beep_alarm(photo_path):
    global alarm
    for _ in range(5):
        if not alarm_mode:
            break
        print("Motion detected!")

        # Save the frame with detected motion to a temporary file
        cv2.imwrite('motion_detected.jpg', frame)

        # Send the photo to Telegram
        await send_telegram_message('motion_detected.jpg')

        # Replace winsound.Beep with sounddevice
        sd.play(1000 * np.sin(2 * np.pi * np.arange(44100) * 2500 / 44100), samplerate=44100, blocking=True)

    alarm = False

while True:
    _, frame = cap.read()
    frame = imutils.resize(frame, width=500)

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]

        start_frame = frame_bw

        if threshold.sum() > 1000000:
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1
    else:
        threshold = frame

    cv2.imshow("Detector", threshold)

    if alarm_counter > 20:
        if not alarm:
            alarm = True
            asyncio.run(beep_alarm('motion_detected.jpg'))

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    if key_pressed == ord("q"):
        alarm_mode = False
        break

cap.release()
cv2.destroyAllWindows()
