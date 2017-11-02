""" SMS Utils
"""

DEF_FROM_NUM = "+16888726748"  # ott.tra.nsit bogus number


def twillo_sms_send(account_id, auth_token, to_number, message, from_number=DEF_FROM_NUM):
    """ @note: to use this routine, you need to install the Twillo Py API
    """
    from twilio.rest import Client

    # the following line needs your Twilio Account SID and Auth Token
    client = Client(account_id, auth_token)
    client.messages.create(to=to_number,
                           from_=from_number,
                           body=message)


def main():
    import argparse

    parser = argparse.ArgumentParser(prog='twillo-sms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--account_id',  '-a', help='Twillo Account (e.g., )')
    parser.add_argument('--auth_token',  '-u', help='Twillo Auth Token (e.g., )')
    parser.add_argument('--from_number', '-f', help='Number you are texting')
    parser.add_argument('--to_number',   '-t', help='Number you are texting from', default=DEF_FROM_NUM)
    parser.add_argument('msg', help='message you want to send', default='Hello from OTT')
    args = parser.parse_args()
    twillo_sms_send(args.account_id, args.auth_token, args.to_number, args.msg, args.from_number)

if __name__ == "__main__":
    main()
