import os
import sys
import json


image_id = input("Enter Docker IMAGE_ID: ")

with open(sys.argv[1], 'r') as file:
    address_dict = json.load(file)

    for address in address_dict:
        name = address_dict[address]['name']
        chat_id = address_dict[address]['chat_id']
        print(address, name, chat_id)

        command = f"""docker run --shm-size='2g' --detach --name {name} -it {image_id} """ \
                  f"""python3 -m src.individual.scrape {address} {name} {chat_id}"""

        os.system(command)
