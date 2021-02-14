from __future__ import print_function
import pickle
import os.path
import os
from twilio.rest import Client
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Hackathon.Hack2021.venv.vaccines import Person, calculatePriority, Providers


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.

SAMPLE_SPREADSHEET_ID = '1SYJYsfrHLIITrNiAxIiEZGu5W8bzZJ8fKf5pYB8CcrA'
SAMPLE_RANGE_NAME = 'Form Responses 1!B2:O'

account_sid = "AC022c08bee628caada3c82ae493341465"
auth_token = "ef65f47815859fd42718888ecff2aa4d"
client = Client(account_sid, auth_token)

PROVIDERS_SPREADSHEET_ID = "1sKkRAzhqrQmeLxIB0sQQMr5sZsRspjNyh1gzwc-yLuw"
PROVIDERS_RANGE_NAME = "Form Responses 1!A2:C"

person_list = []


def sendMessages(list_of_people):
    for x in list_of_people:
        if x.assignment == "":
            try:
                message = client.messages.create(
                    body= x.first + " " + x.last + ": " + "No valid day or provider could be found for your vaccine appointment. Please resubmit the form and try again later. Thank you.",
                    #constant Twilio account number from which we send our message
                    from_="+15312345711",
                    #variable number - ONLY VERIFIED ACCOUNTS ON TWILIO (UPGRADE TO SEND OUT AGGREGATED)
                    to="+1" + x.number
                )
            except:
                pass
        else:
            try:
                message = client.messages.create(
                    body= x.first + " " + x.last + ": " + "Your vaccine appointment is on " + x.appointment_day + " (" + str(x.true_vaccine_assignment) + ") between " + str(x.appointment_time[0]) + ":00-" + str(x.appointment_time[1]) + ":00. Your assigned local healthcare provider is located at " + x.assignment,
                    #constant Twilio account number from which we send our message
                    from_="+15312345711",
                    #variable number - ONLY VERIFIED ACCOUNTS ON TWILIO (UPGRADE TO SEND OUT AGGREGATED)
                    to="+1" + x.number
                )
            except:
                print("Non-valid number for {} {}".format(x.first, x.last))

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    providers_result = sheet.values().get(spreadsheetId=PROVIDERS_SPREADSHEET_ID,
                                range=PROVIDERS_RANGE_NAME).execute()
    providers_values = providers_result.get('values', [])
    values = result.get('values', [])

    """
        CONSUMER RESPONSES!!!
    """

    if not values:
        print('No data found.')
    else:
        for row in values:
            if row == []:
                pass
            else:
                try:
                    first = row[0].split()[0]
                    last = row[0].split()[1]
                except:
                    first = row[0]
                    last = ""
                number = row[1]
                address = row[2]
                travel_distance = row[3]
                times = row[4:11]
                front_line = row[11]
                vulnerabilities = row[12]
                try:
                    age = row[13]
                except:
                    age = 0
                person_list.append(Person(first, last, age, address, number, travel_distance, times, front_line, vulnerabilities))
    person_list.sort(key=calculatePriority, reverse=True)


    """
        PROVIDERS STOCK RESPONSES!
    """
    providers_list = []
    if not providers_values:
        print("no data found")
    else:
        for row in providers_values:
            if row == []:
                pass
            else:
                if providers_list == []:
                    providers_list.append(Providers(row[1], row[2]))
                else:
                    list_length = len(providers_list)
                    bool = True
                    for x in providers_list:
                        if row[1] in x.address:
                            x.stock = x.stock + int(row[2])
                            bool = False
                    if len(providers_list) == list_length and bool:
                        providers_list.append(Providers(row[1], row[2]))


    for x in person_list:
        for viable_address in x.health_care_providers:
            for providers in providers_list:
                if viable_address in providers.address and providers.stock != 0 and x.assignment == "":
                    providers.stock = providers.stock - 1
                    x.assignment = providers.address
                    break

    for x in person_list:
        print(x)
        print(x.health_care_providers)
        # print(x.assignment)

    for i in providers_list:
        print(i)

    #comment out below function to stop spamming the numbers
    sendMessages(person_list)

# print(person_list)
if __name__ == '__main__':
    main()

