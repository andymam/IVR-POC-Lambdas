import json

def get_session_attributes(intent_request):
    return intent_request.get('sessionState', {}).get('sessionAttributes', {}).copy()


def MakePayment(intent_request):
    session_attributes = get_session_attributes(intent_request)
    print("Session Attributes:", json.dumps(session_attributes))
    
    slots = intent_request['sessionState']['intent']['slots']
    print("BEFORE Slots:", json.dumps(slots))
    if session_attributes.get('savedAmount'):
        slots['amount'] = {
            "value": {
                "originalValue": session_attributes['savedAmount'],
                "interpretedValue": session_attributes['savedAmount'],
                "resolvedValues": [session_attributes['savedAmount']]
            },
            "shape": "Scalar"
        }


    if session_attributes.get('savedAccount'):
        slots['account'] = {
            "value": {
                "originalValue": session_attributes['savedAccount'],
                "interpretedValue": session_attributes['savedAccount'],
                "resolvedValues": [session_attributes['savedAccount']]
            },
            "shape": "Scalar"
        }
    
    print("AFTER Slots:", json.dumps(slots))
    print("Amount slot exists:", bool(slots.get('amount')))
    print("Account slot exists:", bool(slots.get('account')))

    # Don't overwrite sessionAttributes — just update them
    # session_attributes['lastIntent'] = 'MakePayment'

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
            },
            "intent": {
                "name": intent_request['sessionState']['intent']['name'],
                "slots": slots,
                "state": "InProgress"
            },
            "sessionAttributes": session_attributes
        },
        "sessionId": intent_request['sessionId']
    }


def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    
    if intent_name == 'MakePayment':
        return MakePayment(intent_request)
    elif intent_name == 'CheckBalance':
        return CheckBalance(intent_request)
    raise Exception(f"Unsupported intent: {intent_name}")


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event, indent=2))
    return dispatch(event)
