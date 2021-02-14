import math
import googlemaps
import datetime
"""
    HYPERPARAMETERS
    """
AGE_WEIGHT = 7
b = 100
k = 0.4

DEVELOP_DIS_WEIGHT = 3.06
LUNG_CANCER_WEIGHT = 2.89
INTELLECTUAL_DIS_WEIGHT = 2.75
NSA_WEIGHT = 2.48
LEUK_WEIGHT = 2.2
CKD_WEIGHT = 1.85
ALZ_WEIGHT = 1.77
ENDO_WEIGHT = 1.73
HEART_WEIGHT = 1.58
EPILEP_WEIGHT = 1.59
COLORECTAL_WEIGHT = 1.73
MOBILITY_WEIGHT = 1.62
REL_WEIGHT = 1.45
LIVER_WEIGHT = 1.44

WEIGHT_LIST = [DEVELOP_DIS_WEIGHT, LUNG_CANCER_WEIGHT, INTELLECTUAL_DIS_WEIGHT,
                   NSA_WEIGHT, LEUK_WEIGHT, CKD_WEIGHT, ALZ_WEIGHT, ENDO_WEIGHT,
                   HEART_WEIGHT, EPILEP_WEIGHT, COLORECTAL_WEIGHT, MOBILITY_WEIGHT,
                   REL_WEIGHT, LIVER_WEIGHT]

gmaps = googlemaps.Client(key="AIzaSyBlSPDqzqzjS-5wi4KJ4ILMK4kDY5skydw")

class Person:

    def __init__(self):
        pass

    def __init__(self, first, last, age, address, number, travel_distance, times, front_line, vulnerabilities):
        #save in case of refactor back to og parameters - developmental_dis, lung_cancer, intellectual_dis, nsa, leuk, ckd, alz, endometrial, heart, colorectal, breast, mobility, rel, epilep, ulcers, liver
        #personal information
        self.first = first
        self.last = last
        self.age = age
        self.address = address
        # google maps
        self.number = number
        travel_ranges = {"Less than 10 miles": (0, 10), "Less than 25 miles": (0, 25), "Less than 50 miles": (0, 50), "50+ miles": (0, 75)}
        self.travel_distance = travel_ranges.get(travel_distance)
        self.health_care_providers = self.healthCareProvs()
        self.times = times
        self.appointment_time = 0
        self.calculateBestTime()
        self.front_line = front_line
        vulnerable_keywords = ["Developmental disorders", "Lung Cancer", "Intellectual Disabilities", "Nervous System Anomalies", "Leukemia", "Alzheimers", "Endometrial Cancer", "Chronic Kidney", "Heart Failure", "Colorectal Cancer", "Mobility Impairments", "Rel Disorders or", "Epilepsy", "Liver Disease"]
        self.vulnerabilities = vulnerabilities
        self.vul_list = []
        for x in vulnerable_keywords:
            if x in self.vulnerabilities:
                # set variable equal to zero
                self.vul_list.append(1)
            else:
                self.vul_list.append(0)
        for addresses in self.health_care_providers:
            pass
            # print(addresses)
        self.assignment = ""
        days = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        self.true_vaccine_assignment = self.next_weekday(datetime.date.today(), days.get(self.appointment_day))

    def healthCareProvs(self):
        # print("Name: {}".format(self.first))
        # print("Address: {}".format(self.address))
        local = gmaps.places(query="CVS near " + self.address, radius=self.travel_distance[1])
        temp_list = []
        for x in range(len(local["results"])):
            temp_list.append((local["results"][x]["formatted_address"]))
        # print(temp_list)
        return temp_list

    def calculateBestTime(self):
        for x in range(len(self.times)):
            if self.times[x] != "":
                self.appointment_day = self.times[x].split(",")[0]
                self.appointment_time = (8 + 2*x , 10 + 2*x)
        # time_dict = {"8:00-10:00": "...", "10:00-12:00": "...", "12:00-14:00": "...", "14:00-16:00": "...", "16:00-18:00": "...", "18:00-20:00": "...", "20:00-22:00": "..."}
        # print(self.appointment_time)
        pass

    def __str__(self):
        return self.first + " " + self.last + ": " + str(calculatePriority(self)) + "\n" + "Address: " + self.address + "\n" + "Number: " + self.number


    def next_weekday(self, d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)


def calculatePriority(person):
    FRONT_LINE_WEIGHT = 0
    if person.front_line == "Yes":
        FRONT_LINE_WEIGHT = 10000
    AGE_CALC_WEIGHT = AGE_WEIGHT / (1 + b * math.pow(math.e, -k * (int(person.age) - 40)))
    calculated = [a*b for a,b in zip(person.vul_list, WEIGHT_LIST)]
    return (AGE_CALC_WEIGHT + sum(calculated)) + FRONT_LINE_WEIGHT


class Providers:
    def __init__(self, address, stock):
        self.address = address
        self.stock = int(stock)

    def __str__(self):
        return "Address: " + self.address + "\n" + "Stock: " + str(self.stock)

