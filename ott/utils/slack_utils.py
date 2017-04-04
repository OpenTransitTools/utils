""" a lot of code borrowed from fullstackpython.com article  
    @see https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""

import time


def get_bot_id(slack_client, bot_name):
    """ @note needs slackclient egg installed locally """
    bot_id = None
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
                bot_id = user.get('id')
                break
    else:
        print("could not find bot user with the name '{}' and token '{}'".format(bot_name, slack_client.token))
    return bot_id


def slack_message_monitor(slack_rtm_output, bot_id):
    """ The Slack Real Time Messaging API is an message event firehose.  This parsing function returns None unless 
        a message is directed at the Bot (@BotName), based on its ID.
        Default @bot_name is the key to responding in this method
    """
    output_list = slack_rtm_output
    at_bot = "<@{}>".format(bot_id)
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and at_bot in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(at_bot)[1].strip().lower(), output['channel']
    return None, None


def slack_bot_responder(slack_client, command, channel):
    """ Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.

        To Add functionality, write you're own handle_command() method with the above parameters,
        and then send a closure to connect_to_slack as the 'process' parameter...
    """
    response = "Not sure what '{}' means...".format(command)
    if command.startswith('do '):
        response = "Sure...write some more code then I can then '{}'!".format(command)
    if "wing" in command or "zero" in command:
        response = "all your base are belong to us, so... {}".format(command)
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def connect_to_slack(slack_client, bot_id, slack_responder=slack_bot_responder, slack_monitor=slack_message_monitor):
    """ creates the client that monitors a slackbot
        'responder' should be over written so you can add functionality to the bot
        'monitor' might be overwritten, but not necessary
    """
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = slack_monitor(slack_client.rtm_read(), bot_id)
            if command and channel:
                slack_responder(slack_client, command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token '{}' or bot ID '{}'?".format(slack_client.token, bot_id))
