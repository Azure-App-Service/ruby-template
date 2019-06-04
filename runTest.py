import requests
import argparse
import json
import time
import threading


def getConfig(branch, stack):
    url = "https://raw.githubusercontent.com/Azure-App-Service/blessedimagepipelineconfig/" + branch + "/" + stack + ".json"
    headers = {
        'cache-control': "no-cache",
        'Postman-Token': "8025abcb-297a-4f9b-b1df-50b3338d7722"
        }
    response = requests.request("GET", url, headers=headers)
    return response.content


def triggerBuild(buildRequests, code):
    url = "https://appsvcbuildfunc-test.azurewebsites.net/api/HttpBuildPipeline_HttpStart"
    querystring = {"code": code}
    payload = buildRequests
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache"
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    return response.content


def getStatusQueryGetUri(jsonResponse):
    return json.loads(jsonResponse)["statusQueryGetUri"]


def pollPipeline(statusQueryGetUri):
    url = statusQueryGetUri
    headers = {
        'cache-control': "no-cache"
        }
    response = requests.request("GET", url, headers=headers)
    return response.content


def buildImage(br, code):
    statusQueryGetUri = getStatusQueryGetUri(triggerBuild(br, code))
    while True:
        content = pollPipeline(statusQueryGetUri)
        print(content)
        runtimeStatus = json.loads(content)["runtimeStatus"]
        if runtimeStatus == "Completed":
            output = json.loads(content)["output"]
            status = json.loads(output)["status"]
            if (status == "success"):
                print("pass")
                break
            else:
                print("failed on")
                print(br)
                exit(1)
        elif runtimeStatus == "Running":
            time.sleep(60)
            continue
        else:
            print("failed on")
            print(br)
            exit(1)


parser = argparse.ArgumentParser()
parser.add_argument('--code', help='code')
parser.add_argument('--pull', help='pull')
args = parser.parse_args()

code = args.code
#f = open("secret.txt", "r")
#code = f.read()
pull = args.pull
stack = "ruby"
branch = "dev"

print(code)
print(pull)

buildRequests = getConfig(branch, stack)
for br in json.loads(buildRequests):
    t = threading.Thread(target=buildImage, args=((json.dumps(br), code)))
    t.start()
    t.join()
    time.sleep(60)

print("done")
exit(0)