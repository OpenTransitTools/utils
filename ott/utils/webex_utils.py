"""
WebEx Teams chat bot fun...
"""


def curl_msg(msg, url, users=None):
    """
    curl a message
    """

    """
    curl -X POST -H "Content-Type: application/json" -d '{"markdown" : "All your base belong to moi, <@personEmail:Zubot@webex.bot|Zubot>."}' https://api.ciscospark.com/v1/webhooks/incoming/Y2lzY29zcGFyazovL3VzL1dFQkhPT0svNGI0Y2Y3ZjgtYTM3MS00ODg1LWJkZDQtMWYxOGU0Zjc3YWNk
    """

    full_msg = msg
    if users:
        full_msg += "\nattn: {}".format(users)
    content = {"markdown" : full_msg}
    # curl full_msg url


def args():
    import argparse

    parser = argparse.ArgumentParser(prog='webex-chat', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--account_id',  '-a', help='Twillo Account (e.g., )')
    parser.add_argument('--auth_token',  '-u', help='Twillo Auth Token (e.g., )')
    parser.add_argument('--from_number', '-f', help='Number you are texting', default=DEF_FROM_NUM)
    parser.add_argument('--to_number',   '-t', help='Number you are texting to')
    parser.add_argument('msg', help='message you want to send', nargs='?', default='Hello from OTT')
    args = parser.parse_args()
    return args


def main():
    pass


if __name__ == "__main__":
    main()
