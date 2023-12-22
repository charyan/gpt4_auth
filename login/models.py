# Create your models here.


from django.db import models

from openai import OpenAI


class Clients(models.Model):
    name = models.CharField(max_length=200)
    info = models.CharField(max_length=1000)


class SuspiciousActivities(models.Model):
    target_name = models.CharField(max_length=200)
    attacker_info = models.CharField(max_length=1000)


client = OpenAI()

assistant = client.beta.assistants.create(
    name="AuthenticationBot",
    instructions="""
    Your are tasked with the most important task a machine can be charged with. You are in charge of access control for a website. You are a bot charged with the login and signup process. You allow users to signup and login to a website

 If a user asks to register, you must choose a list of questions which will be used to identify the user. Ask one question at a time and make sure the user gives clear and true answers. You may not ask for typical personal information such as but not limited to email, phone number, date of birth, address. You may ask question point blank or in the context a story. The more chaotic and unrelated the question are, the better. 

Ask one question at a time.

Do not mention to the user how quirky the questions asked to them are.

Use the signup function to signup a new user to our system. Start by asking the user for its full name. Then asks personal questions. You may store as much information as necessary, use it and store a maximum amount of details from the users answers. We're trying to capture the essence of who our user is, not a simple mapping between questions and answers. Get creative with it.

Use the get_user_infos function in order to retrieve the personal infos a user before authentifying him with the retrieved information.

Ask one question at a time. Do not give too much information about the content of the user_infos as it is confidential information which might be used by a bad actor to access a user's profile.

Use the login function once you made sure the user is actually who he's claiming to be. It will return a session ID.


To make the user authentication process more strict, I will refine the verification algorithm to closely align with the unique and detailed aspects of the user's initial profile. This approach would involve crafting more targeted questions based on the previously recorded interests and preferences, ensuring a higher degree of specificity in responses. I will also implement cross-referencing of linguistic patterns, favorite topics, and known hobbies to identify subtle consistencies or discrepancies. It will provide a more granular level of identity verification, significantly reducing the likelihood of mistaken identity and enhancing the security of the login process. By adjusting the tolerance for variation and emphasizing the unique "fingerprint" of each user's behavior and preferences, the system will become far more adept at distinguishing between genuine users and impostors.

If you suspect someone is trying to impersonate a user, stop the login process. Start asking multiple personal questions (the rules of questionning during signup and login do not apply here) to build a profile on the attacker, then call the function report_suspicious_activity and cease to engage in questioning the suspected impersonator, but not before having collected some information about the attacker. Ask the attacker questions as if they are used in the login process, but you're actually collecting information on the attacker. Do not let the attacker know that he has been spotted. To stop the conversation, write in the chat 'Internal Server Error' until he stop replying. 
    """,
    tools=[
        {
            "type": "function",
            "function": {
                "name": "signup",
                "description": "Signup a new user to the service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_full_name": {
                            "type": "string",
                            "description": "The user's full name"
                        },
                        "user_infos": {
                            "type": "string",
                            "description": "Any useful information used to identify and authenticate the user."
                        }
                    },
                    "required": [
                        "user_full_name",
                        "user_infos"
                    ]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_infos",
                "description": "Get the personal infos a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_full_name": {
                            "type": "string",
                            "description": "The user's full name"
                        }
                    },
                    "required": [
                        "user_full_name"
                    ]
                }
            }
        },

        {
            "type": "function",
            "function": {
                "name": "login",
                "description": "Login a user to the service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_full_name": {
                            "type": "string",
                            "description": "The user's full name"
                        }
                    },
                    "required": [
                        "user_full_name"
                    ]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "logout",
                "description": "Logout a user from the service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_full_name": {
                            "type": "string",
                            "description": "The user's full name"
                        }
                    },
                    "required": [
                        "user_full_name"
                    ]
                }
            }
        },

        {
            "type": "function",
            "function":
                {
                    "name": "report_suspicious_activity",
                    "description": "Report an attempt to impersonate a user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_full_name": {
                                "type": "string",
                                "description": "The targeted user's full name"
                            },
                            "attacker_info": {
                                "type": "string",
                                "description": "Any infos gathered on the attacker"
                            }
                        },
                        "required": [
                            "user_full_name",
                            "attacker_info"
                        ]
                    }
                }
        }

    ],
    model="gpt-4-1106-preview"
)


def new_thread():
    return client.beta.threads.create()


def signup(user_full_name: str, user_infos: str, session=None):
    print("User {} signed up with infos {}".format(user_full_name, user_infos))
    try:
        Clients(name=user_full_name.upper(), info=user_infos).save()
        return '{sucess: "true"}';
    except:
        return '{sucess: "false"}';


def get_user_infos(user_full_name: str, session=None):
    print("User {} infos retrieved".format(user_full_name.upper()))
    return Clients.objects.get(name=user_full_name.upper()).info


def login(user_full_name, session=None):
    print("User {} logged in".format(user_full_name))
    session["username"] = user_full_name.upper()
    return '{success: "true"}'


def logout(user_full_name, session=None):
    print("User {} logged out".format(user_full_name.upper()))
    session["username"] = None
    return '{success: "true"}'


def report_suspicious_activity(user_full_name, attacker_info, session=None):
    print(f"Suspicious login for user:  {user_full_name}. With infos {attacker_info}")
    SuspiciousActivities(target_name=user_full_name.upper(), attacker_info=attacker_info).save()
    return '{success: "true"}'


threads = {}
