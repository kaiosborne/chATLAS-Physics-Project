import json
 
# Opening JSON file
f = open('generated-data.json.zip',encoding="utf8")
 
# returns JSON object as 
# a dictionary

d = json.loads(f.read().decode("utf-8"))

 
f.close()