import json
import random
import decimal

def random_num():
    return decimal.Decimal(random.randrange(1000, 50000))/100


def get_session_attributes(intent_request):
    return intent_request.get('sessionState', {}).get('sessionAttributes', {}).copy()


def set_slots_from_payment_session(slots, session_attributes):
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
    return slots


def MakePaymentFulfillment(intent_request):
    session_attributes = get_session_attributes(intent_request)

    session_attributes.pop('savedAmount', None)
    session_attributes.pop('savedAccount', None)

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_request['sessionState']['intent']['name'],
                "state": "Fulfilled",
                "slots": {
                    "amount": None,
                    "account": None
                }
            },
            "sessionAttributes": session_attributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Payment complete. What else would you like to do today?"
            }
        ],
        "sessionId": intent_request['sessionId']
    }


def MakePayment(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = intent_request['sessionState']['intent']['slots']
    confirmation = intent_request['sessionState']['intent'].get('confirmationState')

    if confirmation == 'Denied':
        # clear only some session attributes
        session_attributes.pop('savedAmount', None)
        session_attributes.pop('savedAccount', None)

        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent_request['sessionState']['intent']['name'],
                    "state": "Fulfilled",
                    "slots": {
                        "amount": None,
                        "account": None
                    }
                },
                "sessionAttributes": session_attributes
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Okay, no problem. What would you like to do next?"
                }
            ],
            "sessionId": intent_request['sessionId']
        }
        
    set_slots_from_payment_session(slots, session_attributes)
        
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

def CheckBalance(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = intent_request['sessionState']['intent']['slots']

    accountType = slots['account']['value']['interpretedValue']
    balance = str(random_num())
    text = f"Your {accountType} balance is ${balance}."
    message = {
        "contentType": "PlainText",
        "content": text
    }
    fulfillment_state = "Fulfilled"
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_request['sessionState']['intent']['name'],
                "slots": slots,
                "state": fulfillment_state
            },
            "sessionAttributes": session_attributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": text + " What else would you like to do today?"
            }
        ],
        "sessionId": intent_request['sessionId']
    }


def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    invocation_source = intent_request.get('invocationSource')

    if intent_name == 'MakePayment':
        if invocation_source == 'FulfillmentCodeHook':
            return MakePaymentFulfillment(intent_request)
        else:
            return MakePayment(intent_request)

    elif intent_name == 'CheckBalance':
        if invocation_source == 'FulfillmentCodeHook':
            return CheckBalance(intent_request)

    raise Exception(f"Unsupported intent: {intent_name}")


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event, indent=2))
    return dispatch(event)
