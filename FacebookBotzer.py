import sys, json, requests
from flask import Flask, request
import pyowm
from pyowm import OWM

app = Flask(__name__)


#facebook page access_token
PAT = 'EAANm5eOM8bwBAHvT8mTIoiG06QZAp7S2ig4yrqMBO9JEfw3Trn8ZBSLYLBQUcbb6latpQFe9FiQOR3QzKeOIMbPsA5Nj6oQtrf7Aq976fBCPloX26MZAINZBs3jSvniNSZAwbVJrfZBYub1icLBLIUUGxDLSuijyQLYsEkZA36qaAZDZD'

#webhook verification_token
VERIFY_TOKEN = 'TESTINGTOKEN'

@app.route('/', methods=['GET'])
def handle_verification():

    #Verify FB webhook subscription.
    #Validate Verify_token is same as token sent by facebook app
   
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):     
        print("succefully verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
  
    #Handle messages sent by facebook messenger to the applicaiton
 
    data = request.get_json()
    print('JSON for message coming from facebook==',data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  

                    sender_id = messaging_event["sender"]["id"]   
                    print('SENDER ID==',sender_id)
                    recipient_id = messaging_event["recipient"]["id"]  
                    print('Recipient id==',recipient_id)
                    message_text = messaging_event["message"]["text"]  
                    print('Message==',message_text)
                    send_message_response(sender_id, parse_user_message(message_text)) 

    return "ok"


def send_message(sender_id, message_text):
  
    #Sending response back to the user using facebook graph API
   
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": PAT},

        headers={"Content-Type": "application/json"}, 

        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))


def parse_user_message(user_text):
    
    URL = "https://aibaba.powerupcloud.com/bmpapi/getNLPResponse"
    headers = {
                'Content-Type': 'application/json'
              }
    data = {
            "botId": "2c9faf60724bb353017250b999d40036",
            "type": "FAQ",
            "textInputUtterance": user_text,
            #"sessionId": From[9:],
            "channel":"whatsapp"
            }
    json_string = json.dumps(data)
    response = requests.request("POST", URL, headers=headers, data=json_string)
    nlpresponse = response.json()  
    result = nlpresponse['elements'][0]['data']['text']
    #cleanr = re.compile('<.*?>')
    #result = re.sub(cleanr, '', result)
    print(result)
    #resp = MessagingResponse()
    #resp.message(result)

    return str(result)
    
    

    '''
    #The bot response is appened with weaher data fetched from open weather map client
    
    weather_report = ''
    #sample_responses = ["Hi ! This is Botzer :)","Hello My name is Botzer. I'm a chatbot"]
    #api_access_key
    owm = OWM('38d1fd63f2a68fecca7b765d2cbf36ef')  

# Search for current weather in London (Great Britain)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place('London,GB')
    w = observation.weather
    print(w)                                       
    detailed_status = str(w.detailed_status) 
    print(detailed_status)
    weather_report='Weather forecast for the London City is : '+detailed_status 
    print(weather_report)
    return (weather_report)  
    '''


def send_message_response(sender_id, message_text):

    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
    
    for message in messages:
        send_message(sender_id, message)

if __name__ == '__main__':
    app.run()