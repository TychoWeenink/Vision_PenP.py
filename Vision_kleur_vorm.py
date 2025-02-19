# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 10:38:43 2024

@author: tycho
"""
import cv2
import numpy as np
import time

# Kleuren en hun HSV Hue-bereiken
COLOR_RANGES = {
    "Groen": (35, 85),       # Hue bereik voor groen
    "Oranje": (10, 25),      # Hue bereik voor oranje
    "Donkerblauw": (100, 130), # Hue bereik voor donkerblauw
    "Rood": (0, 10),         # Hue bereik voor rood
    "Wit": (0, 0),           # Speciaal: gebaseerd op hoge waarde en lage saturatie
    "Geel": (25, 35),        # Hue bereik voor geel
    "Paars": (130, 160)      # Hue bereik voor paars
}

# Functie om de vorm te bepalen
def detect_shape(contour):
    approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
    vertices = len(approx)

    if vertices == 3:
        return "Driehoek"
    elif vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if 0.95 <= aspect_ratio <= 1.05:
            return "Vierkant"
        else:
            return "Parallellogram"
    else:
        return "Onbekende vorm"

# Functie om een kleurmasker te maken op basis van Hue
def get_color_mask(hsv_image, lower_hue, upper_hue):
    lower = np.array([lower_hue, 50, 50])  # Minimale Saturatie en Value om zwart te filteren
    upper = np.array([upper_hue, 255, 255])
    return cv2.inRange(hsv_image, lower, upper)

# Speciaal masker voor wit
def get_white_mask(hsv_image):
    lower = np.array([0, 0, 200])  # Lage saturatie, hoge value
    upper = np.array([180, 20, 255])
    return cv2.inRange(hsv_image, lower, upper)

# Verwerk het frame
def process_frame(frame, min_area=1000):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    output_frame = frame.copy()

    detected_piece = None

    for color_name, hue_range in COLOR_RANGES.items():
        # Speciaal masker voor wit
        if color_name == "Wit":
            mask = get_white_mask(hsv)
        else:
            lower_hue, upper_hue = hue_range
            mask = get_color_mask(hsv, lower_hue, upper_hue)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Sorteer contouren op grootte (van groot naar klein)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            # Pak de grootste contour
            largest_contour = contours[0]
            area = cv2.contourArea(largest_contour)

            if area > min_area:
                shape = detect_shape(largest_contour)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Teken contouren en label
                cv2.drawContours(output_frame, [largest_contour], -1, (0, 255, 0), 2)
                cv2.putText(output_frame, f"{color_name} {shape}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Sla de gedetecteerde kleur en vorm op
                detected_piece = (color_name, shape)
                break

    return output_frame, detected_piece

# Main-functie
def main():
    # Parameters: time delay en minimale grootte
    time_delay = 0.5  # Time delay in seconden
    min_area = 1500   # Minimale grootte van een contour in pixels

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: Kan de externe webcam niet openen!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Druk op 'q' om te stoppen.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame niet gelezen!")
            break

        processed_frame, detected_piece = process_frame(frame, min_area)

        # Toon de uitvoer
        cv2.imshow("Tangram Detectie", processed_frame)

        # Print het gedetecteerde stuk
        if detected_piece:
            color, shape = detected_piece
            print(f"Gedetecteerd: Kleur = {color}, Vorm = {shape}")

        # Wacht op een time delay
        time.sleep(time_delay)

        # Stop als 'q' wordt ingedrukt
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
