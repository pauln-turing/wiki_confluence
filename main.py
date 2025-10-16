from tools.interface_1.get_user import GetUser
from tools.interface_1.get_labels import GetLabels
import json

with open('generated_data/page_labels.json', "r") as database:
    data = json.load(database)

if __name__== "__main__":
    

    tool = GetLabels()
    print(tool.invoke(data=data, action="get", payload={"page_id": "3"}))
