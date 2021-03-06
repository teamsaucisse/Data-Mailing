from __future__ import print_function

import base64
import os.path
import pickle
import re
from datetime import datetime

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
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
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # start

    # unread_msgs = service.users().messages().list(userId='me').execute()
    #
    # # We get a dictonary. Now reading values for the key 'messages'
    # mssg_list = unread_msgs['messages']
    #
    # print("Total unread messages in inbox: ", str(len(mssg_list)))
    #
    # final_list = []
    #
    # for mssg in mssg_list:
    #     temp_dict = {}
    #     m_id = mssg['id']  # get id of individual message
    #     message = service.users().messages().get(userId='me', id=m_id).execute()  # fetch the message using API
    #     payld = message['payload']  # get payload of the message
    #     headr = payld['headers']  # get header of the payload
    #
    #     for one in headr:  # getting the Subject
    #         if one['name'] == 'Subject':
    #             msg_subject = one['value']
    #             temp_dict['Subject'] = msg_subject
    #         else:
    #             pass
    #
    #     for two in headr:  # getting the date
    #         if two['name'] == 'Date':
    #             msg_date = two['value']
    #             date_parse = (parser.parse(msg_date))
    #             m_date = (date_parse.date())
    #             temp_dict['Date'] = str(m_date)
    #         else:
    #             pass
    #
    #     for three in headr:  # getting the Sender
    #         if three['name'] == 'From':
    #             msg_from = three['value']
    #             temp_dict['Sender'] = msg_from
    #         else:
    #             pass
    #
    #     temp_dict['Snippet'] = message['snippet']  # fetching message snippet
    #
    #
    #     # Fetching message body
    #     mssg_parts = payld['parts']  # fetching the message parts
    #     part_one = mssg_parts[0]  # fetching first element of the part
    #
    #     print(part_one['body'])
    #
    #     part_body = part_one['body']  # fetching body of the message
    #     part_data = part_body['data']  # fetching data from the body
    #     clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
    #     clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
    #     clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
    #     soup = BeautifulSoup(clean_two, "lxml")
    #     mssg_body = soup.body()
    #     # mssg_body is a readible form of message body
    #     # depending on the end user's requirements, it can be further cleaned
    #     # using regex, beautiful soup, or any other method
    #     temp_dict['Message_body'] = mssg_body
    #
    #     print(temp_dict)

    # Call the Gmail API
    USER_ID = 'me'
    results = service.users().messages().list(userId=USER_ID).execute()

    for i, m in enumerate(results['messages'][0:10]):
        print('MESSAGE #%d\n' % i)
        # message = service.users().messages().get(userId=USER_ID, id=m['id'], format='raw').execute()

        message_full = service\
            .users()\
            .messages()\
            .get(userId=USER_ID, id=m['id'], format='full')\
            .execute()\
            .get('payload', {})
        msg_headers = message_full.get('headers', [])

        #
        # Header
        #

        required_headers = ['From', 'Subject', 'Date']

        headers = {}
        for header in msg_headers:
            name, value = header['name'], header['value']
            if name in required_headers:
                headers[name] = value

        print('headers: ', headers)

        #
        # Attachments
        #

        def parse_content(content, body_, attachments_):
            msg_body = content.get('body', {})
            msg_parts = content.get('parts', [])

            if msg_body == {} and msg_parts == []:
                return body_, attachments_

            # Is attachment?
            att_id = msg_body.get('attachmentId')
            if att_id:
                att = service \
                    .users() \
                    .messages() \
                    .attachments() \
                    .get(userId=USER_ID, messageId=m['id'], id=att_id) \
                    .execute()
                attachments_[content['filename']] = base64.urlsafe_b64decode(att['data'])

            # Is text?
            text = msg_body.get('data')
            if text:
                body_ += str(base64.urlsafe_b64decode(text))

            for part in msg_parts:
                b, c = parse_content(part, body_, attachments_)
                body_ += b
                attachments_.update(c)
            return body_, attachments_

        body, attachments = parse_content(message_full, "", {})
        print('Attachments: ', {(k, v[:50]) for k, v in attachments.items()})
        print('Body: ', body)

        return USER_ID, headers, body, attachments


def find_regex(regex, body):
    search_result = re.compile(regex, 0).search(body)

    if not search_result:
        return None

    return search_result.groups()[0]


if __name__ == '__main__':
    main()