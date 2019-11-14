import json

def msg_to_json(message="None",result=False,label="warning"):
    '''
    .Description --> Return JSON message for the result
    '''
    message = {
        "message":str(message),
        "result":result,
        "type":str(label)
    }
    return message
