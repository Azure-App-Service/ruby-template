import requests
import argparse
import json
import time
import threading


def getConfig():
    f = open("blessedImageConfig.json", "r")
    return f.read()


def appendPR(buildRequest, pullRepo, pullId):
    if (pullRepo != False):
        buildRequest.update( { "pullRepo": pullRepo } )
        buildRequest.update( { "pullId": pullId } )
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
    return response.content.decode('utf-8')


def getStatusQueryGetUri(jsonResponse):
    return json.loads(jsonResponse)["statusQueryGetUri"]


def pollPipeline(statusQueryGetUri):
    url = statusQueryGetUri
    headers = {
        'cache-control': "no-cache"
        }
    response = requests.request("GET", url, headers=headers)
    return response.content.decode('utf-8')


def buildImage(br, code):
    tries = 0
    success = False
    while tries < 3:
        tries = tries + 1
        statusQueryGetUri = getStatusQueryGetUri(triggerBuild(br, code))
        while True:
            content = pollPipeline(statusQueryGetUri)
            runtimeStatus = json.loads(content)["runtimeStatus"]
            if runtimeStatus == "Completed":
                output = json.loads(content)["output"]
                status = json.loads(output)["status"]
                if (status == "success"):
                    print("pass")
                    success = True
                    break
                else:
                    print("failed on")
                    print(br)
                    break
            elif runtimeStatus == "Running":
                print("running")
                time.sleep(60)
                continue
            else:
                print("failed on")
                print(br)
                break
        if success:
            exit(0)
        else:
            print("trying again")
            time.sleep(60)
            continue
    if success:
        exit(0)
    else:
        exit(1)


parser = argparse.ArgumentParser()
parser.add_argument('--code', help='code')
parser.add_argument('--pullId', help='pullId')
parser.add_argument('--pullRepo', help='pullRepo')
args = parser.parse_args()

code = args.code
pullId = args.pullId
pullRepo = args.pullRepo

threads = []
buildRequests = getConfig()
for br in json.loads(buildRequests):
    br = appendPR(br, pullRepo, pullId)
    print(br)
    t = threading.Thread(target=buildImage, args=((json.dumps(br), code)))
    threads.append(t)
    t.start()
    time.sleep(60)

# Wait for all of them to finish
for t in threads:
    t.join()

print("done")
exit(0)

