# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 10:36:27 2020

@author: rajes
"""
#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import sys, json, requests
import webbrowser
import validators

app = Flask(__name__)
ACCESS_TOKEN = 'EAAmGB4ZAxDxcBAI5Vp0IkKhZBI44EVrPZB8ms91lnFVEZBLfj063cHvbHWJj69ALKUT8u5DrSAsiwbWqB3x45kTIu5FteUZC9XE8eruabwOti42pznwdNiMyoMUtZB3Oni52m1TzEtm7TGVBXZA89MlZCLeTJ7Cs1oQb50mrj1FNtwZDZD'
VERIFY_TOKEN = 'VERIFY_TOKEN'
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route('/', methods=['GET', 'POST'])
def receive_message():
  try:
    if request.method == 'GET': 
        #take token sent by facebook and verify it matches the verify token you sent
        #if they match, allow the request, else return an error 
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
           return request.args.get("hub.challenge")
        return 'Invalid verification token'
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
         # get whatever message a user sent the bot
       output = request.get_json()
       print('--Message JSON from user side===',output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
              recipient_id = message['sender']['id']
              print('recipient_id==',recipient_id)
              typing_on(recipient_id)
              if message['message'].get('quick_reply'):
                  print('--on click payload--')
                  payload = message["message"]["quick_reply"]["payload"]
                  valid=validators.url(payload)
                  if valid==True:
                       webbrowser.open(payload) 
                  else:
                      print("Invalid url")
                      message_text = message["message"]["text"]
                      parameters= message_text +"|" + payload  
                      print('--on testing Message==',parameters)
                      print('--on click Message==',message_text)
                      print('--on click payback value==',payload) 
                      response_sent_text=get_message(parameters)
                      send_message(recipient_id, response_sent_text)
              elif message['message'].get('text'):
                    message_text=[] 
                    message_text.append(message["message"]["text"])
                    print('Text Message from user==',message_text)
                    response_sent_text=get_message(message_text)
                    send_message(recipient_id, response_sent_text)
    return "Message Processed"
  except Exception as e:
    print("--receive_message method Error==",e)
    return "In receive_message Exception" 

#to display typing symbol on bot
def typing_on(recipient_id):
    print("")
    try:
        url = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+ACCESS_TOKEN ,
        
                params={"access_token": ACCESS_TOKEN},
        
                headers={"Content-Type": "application/json"}, 
                            
                data=json.dumps({
          "recipient":{
            "id":recipient_id
          },
          "sender_action":"typing_on"
          }
        
         ))  
    except Exception as e:
        print("--quick_message_two Error==",e)
        return "In Exception" 

def get_message(user_text):
   print('--get_message parameter value==',user_text)
   print(len(user_text))
   actiontype='FAQ'
   Id=''
   id=''
   if (len(user_text))>1:
        parametersArray = user_text.split("|")
        print(parametersArray)
        text_value=parametersArray[0]
        Id=parametersArray[1]
        actiontype=parametersArray[2]
        print('--text_value==',text_value)
        print('--Id==',Id)
        print('--actiontype==',actiontype)
   else:
        text_value=user_text[0]
   try:
        URL = "https://bmp-api.demo.botzer.io/bmpapi/getNLPResponse"
        headers = {
                    'Content-Type': 'application/json'
                  }
        data = {
                "botId": "2c9faf6072a3022c0172a32c80080061",
                 "type":actiontype ,  
                "textInputUtterance": text_value,
                "sessionId": "sessionId",
                "channel":"facebook",
                "data":{
		           "id":Id
	                   }
                }
        json_string = json.dumps(data)
        response = requests.request("POST", URL, headers=headers, data=json_string)
        response = response.json()  
        #print('--get_message method response==',response)   
        return (response)
   except Exception as e:
        print("--get_message Error==",e)
        return "In Exception"  
    
    
def send_message(recipient_id, response):
    #print('--inside quick_message_two--',response)
    data=response['elements'][0]
    first_text = response['elements'][0]['data']['text']
    print('--data==',data)
    print('--length of response==',len(response['elements']))
    buttons=[]
    actionType=[]
    Id=[]
    target=[]
    if (len(response['elements'])>1):
       print('----Inside len response')
       if 'actionType' in data:
           print('list of buttons')
       
           for i in range(0,len(response['elements'])):
             buttons.append(response['elements'][i]['data']['name'])
             actionType.append(response['elements'][i]['actionType'])
             Id.append(response['elements'][i]['id'])
             if "target" in response['elements'][i]:
                 target.append(response['elements'][i]['target'])
             if "target" not in response['elements'][i]:
                    target.insert(i,"")
           print('buttons==',buttons)
           first_text='Choose from below:'  
       elif ('actionType' in response['elements'][1]) and ('data' in response['elements'][0]):
           print('----Inside both condition')
           for i in range(1,len(response['elements'])):
               print(i)
               buttons.append(response['elements'][i]['data']['name'])
               if "id" in response['elements'][i]:
                 Id.append(response['elements'][i]['id'])
               if "id" not in response['elements'][i]:
                    Id.insert(i,"")
               #actionType.append(response['elements'][i]['actionType'])
               if "actionType" in response['elements'][i]:
                 actionType.append(response['elements'][i]['actionType'])
               if "actionType" not in response['elements'][i]:
                    actionType.insert(i,"None")
               if "target" in response['elements'][i]:
                 target.append(response['elements'][i]['target'])
               if "target" not in response['elements'][i]:
                    target.insert(i,"")
               print('---target==',target)
               print('---id==',id)
               print('---actionType==',actionType)
       elif ('data' in response['elements'][1]):
           print('----Inside data[1] condition')
           for i in range(2,len(response['elements'])):
               print(i)
               buttons.append(response['elements'][i]['data']['name'])
               if "id" in response['elements'][i]:
                 Id.append(response['elements'][i]['id'])
               if "id" not in response['elements'][i]:
                    Id.insert(i,"")
               #actionType.append(response['elements'][i]['actionType'])
               if "actionType" in response['elements'][i]:
                 actionType.append(response['elements'][i]['actionType'])
               if "actionType" not in response['elements'][i]:
                    actionType.insert(i,"None")
               if "target" in response['elements'][i]:
                 target.append(response['elements'][i]['target'])
               if "target" not in response['elements'][i]:
                    target.insert(i,"")
           print('---id==',id)
           print('---actionType==',actionType)
           print('---target==',target)
           first_text=response['elements'][0]['data']['text'] +('\n')+ response['elements'][1]['data']['text']
    
    elif 'data' in data:
       print("first data ===")
       bot.send_text_message(recipient_id, first_text)
    
    print('--button array==',buttons)
        
    if(len(buttons)>12):
        length=12
    else: length=len(buttons) 
    buttonJSON=[]
    for j in range(0,length):   
     
         if(target[j]==""):
            payload= Id[j] +"|" + actionType[j]  
         else:
            payload= target[j] 
         
         buttonJSON.append({
            
            "content_type":"text",
            "title":buttons[j],
            "payload": payload
        
          })
    print('---buttonJSON===',buttonJSON)
    try:
        url = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+ACCESS_TOKEN ,
        
                params={"access_token": ACCESS_TOKEN},
        
                headers={"Content-Type": "application/json"}, 
                            
                data=json.dumps({
          "recipient":{
            "id":recipient_id
          },
          "messaging_type": "RESPONSE",
          "message":{
          "text": first_text,
          "quick_replies":buttonJSON
                    }
          }
        
         ))  
    except Exception as e:
        print("--quick_message_two Error==",e)
        return "In Exception" 


if __name__ == "__main__":
    app.run()