""" SMS Utils
"""


def twillo_sms_send(account_id, auth_token, to_number, message, from_number="+16888726748"):
    """ @note: to use this routine, you need to install the Twillo Py API

        :return both t/f for a match, and the index of the word where the match occurred
         depends upon the textblob NLP library for 'spellcheck suggestions and words'
    """
    from twilio.rest import Client

    # the following line needs your Twilio Account SID and Auth Token
    client = Client(account_id, auth_token)
    client.messages.create(to=to_number,
                           from_=from_number,
                           body=message)

