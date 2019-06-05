import requests
import argparse
import json
import time
import threading


def getConfig(branch, stack):
    url = "https://raw.githubusercontent.com/Azure-App-Service/blessedimagepipelineconfig/" + branch + "/" + stack + ".json"
    headers = {
        'cache-control': "no-cache"
        }
    response = requests.request("GET", url, headers=headers)
    return response.content


def appendPR(buildRequest, pullRepo, pullId):
    if (pullRepo != False):
        buildRequest.update( { "pullRepo": pullRepo } )
        buildRequest.update( { "pullId": pullId } )
    print(buildRequest)
    return buildRequest

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


# parser = argparse.ArgumentParser()
# parser.add_argument('--code', help='code')
# parser.add_argument('--pullId', help='pullId')
# parser.add_argument('--pullRepo', help='pullRepo')
# args = parser.parse_args()

# code = args.code
f = open("secret.txt", "r")
code = f.read()
# pullId = args.pullId
# pullRepo = args.pullRepo
pullId = "7"
pullRepo = "https://github.com/Azure-App-Service/ruby-template.git"
stack = "ruby"
branch = "dev"

buildRequests = getConfig(branch, stack)
for br in json.loads(buildRequests):
    br = appendPR(br, pullRepo, pullId)
    t = threading.Thread(target=buildImage, args=((json.dumps(br), code)))
    t.start()
    t.join()
    time.sleep(60)

print("done")
exit(0)

