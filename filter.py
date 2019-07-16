import json

with open('out.json') as f:
    out = json.load(f)

print(type(out['Items']))

bounce = {""}
lis = []
for li in out["Items"]:
    if li["mailtype"]["S"] == "bounce":
        bounce.add(li["recipients"]["L"][0]["M"]["emailAddress"]["S"])
        lis.append(li["recipients"]["L"][0]["M"]["emailAddress"]["S"])
print(len(bounce))
print(bounce)