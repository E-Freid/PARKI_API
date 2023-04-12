from threading import Thread
import requests
from bs4 import BeautifulSoup as BS

URL = "https://www.ahuzot.co.il/Parking/ParkingDetails/"
SRC_URL = "/pics/ParkingIcons/"
STATUSES = ["pail", "panui", "male", "meat"]
MESSAGES = ["פעיל", "פנוי", "מלא", "יש מעט מקומות"]


class GetStatusThread(Thread):
    def __init__(self, parking_id):
        super().__init__()
        self.parking_id = parking_id
        self.result = None

    def run(self):
        response = requests.get(URL, params={"ID": self.parking_id})
        soup = BS(response.content, "html.parser")
        parking_status = "אין מידע"

        for i in range(4):
            img = soup.find("img", {"src": SRC_URL + STATUSES[i] + ".png"})
            if img:
                parking_status = MESSAGES[i]
                break

        self.result = parking_status
