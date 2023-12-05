#!/usr/bin/env python3

import os
import cv2
import numpy as np
import robomodules as rm
from messages import MsgType, message_buffers, RotationCommand, TiltCommand
from camera_reader import CameraFeed
from laser_module import LaserModule


# Retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS", "localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2
START_POS = -1

cf = CameraFeed(0)
msg3 = TiltCommand()


class ShapeHandling(rm.ProtoModule):
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)

    def tick(self):
        pass

    def find_color(self, image, lower_bound, upper_bound):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        segmented_img = cv2.bitwise_and(image, image, mask=mask)
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
        return output

    def find_shapes(self, image, shape_name, START_POS, msg3, target_count, msg_type):
        edges = cv2.Canny(image, 30, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        output_image = image.copy()
        count = 0

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 1.95, True)

            if len(approx) == target_count:
                count += 1
                e.send_pulse()

                cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

            if count == 0 and msg3.position == 1:
                print(f"No {shape_name.lower()} found")
                msg = RotationCommand()
                START_POS += 0.1
                msg.position = START_POS
                msg.max_speed = 1
                self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)
                msg3.position = -1
                self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)

        return output_image, count

    def find_triangles(self, image, START_POS, msg3):
        print("Finding triangles")
        return self.find_shapes(image, "Triangles", START_POS, msg3, 3, MsgType.TRIANGLE)

    def find_squares(self, image, START_POS, msg3):
        print("Finding squares")
        return self.find_shapes(image, "Squares", START_POS, msg3, 4, MsgType.SQUARE)

    def find_octagons(self, image, START_POS, msg3):
        print("Finding octagons")
        return self.find_shapes(image, "Octagons", START_POS, msg3, 8, MsgType.OCTAGON)

    def find_circles(self, image, START_POS, msg3):
        print("Finding circles")
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise and improve circle detection
        gray = cv2.GaussianBlur(gray, (9, 9), 2)

        # Use Hough Circle Transform to detect circles
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=30,
        )

        output_image = image.copy()
        circle_count = 0

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                circle_count += 1
                e.send_pulse()
                # Draw the outer circle
                cv2.circle(output_image, (i[0], i[1]), i[2], (255, 0, 0), 3)

        if circle_count == 0 and msg3.position == 1:
            print("No circles found")
            msg_motor = RotationCommand()
            START_POS += 0.1
            msg_motor.position = START_POS
            msg_motor.max_speed = 1
            self.write(msg_motor.SerializeToString(), MsgType.ROTATION_COMMAND)
            msg3.position = -1
            self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)

        return output_image, circle_count


    def msg_received(self, msg, msg_type):
        msg2 = RotationCommand()
        msg2.position = START_POS
        msg2.max_speed = 1
        self.write(msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

        msg3.position = START_POS
        self.write(msg3.SerializeToString(), MsgType.ROTATION_COMMAND)


        if (msg_type == MsgType.TARGET):
          # print ("target message was found")
          # control logic for detecting colors
            if msg.color == 0:
                # Red
                cf2 = self.find_color(cf.read(), np.array([110, 155, 0]), np.array([128, 255, 255]))
            elif msg.color == 1:
                # Yellow
                cf2 = self.find_color(cf.read(), np.array([86, 132, 0]), np.array([98, 255, 255]))
            elif msg.color == 2:
                # Blue
                cf2 = self.find_color(cf.read(), np.array([0, 153, 2]), np.array([23, 255, 255]))
            elif msg.color == 3:
                # Green
                cf2 = self.find_color(cf.read(), np.array([41, 130, 0]), np.array([67, 255, 255]))


            while msg3.position != 1:
                if msg.shape == 0:
                    output, count = self.find_squares(cf2, START_POS, msg3)
                elif msg.shape == 1:
                    output, count = self.find_circles(cf2, START_POS, msg3)
                elif msg.shape == 2:
                    output, count = self.find_triangles(cf2, START_POS, msg3)
                elif msg.shape == 3:
                    output, count = self.find_octagons(cf2, START_POS, msg3)

                cv2.imshow("Testing", output)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                msg3.position += 0.1
                self.write(msg3.SerializeToString(), MsgType.ROTATION_COMMAND)

            cv2.destroyAllWindows()


def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()
