import json
import time

from django.shortcuts import render, redirect

from login.models import *


def index(request):
    request.session.save()

    if request.session.session_key not in threads.keys():
        threads[request.session.session_key] = new_thread()
        request.session["messages"] = []
        request.session["username"] = None
        request.session.save()

    return render(request,
                  "base.html", {
                      "messages": request.session.get("messages"),
                      "username": request.session.get("username"),
                      "session_id": request.session.session_key})


def suspicious_activities(request):
    return render(request,
                  "suspicious_activities.html", {
                      "acts": SuspiciousActivities.objects.all()})


def users(request):
    return render(request,
                  "users.html", {
                      "acts": Clients.objects.all()})


def send_message(request):
    thread = threads[request.session.session_key]

    request.session["messages"].append(f">> {request.POST.get('message')}")

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=request.POST.get("message")
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    completed = False

    while completed is False:
        time.sleep(1)

        # Check run status
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        completed = run.status == "completed"

        print("Run status: {}".format(run.status))

        if run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":
            tool_list = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                func_name = tool_call.function.name
                func_params = json.loads(tool_call.function.arguments)
                func_output = globals()[func_name](**func_params, session=request.session)
                tool_list.append((tool_call.id, json.dumps(func_output)))

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": tool[0],
                        "output": tool[1],
                    } for tool in tool_list
                ]
            )

    # Display the assistant's response
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    for message in messages:
        if (message.content[0].text.value not in request.session["messages"]) and (message.role == "assistant"):
            request.session["messages"].append(message.content[0].text.value)

    print(request.session["messages"])
    request.session.save()

    return redirect('/')
