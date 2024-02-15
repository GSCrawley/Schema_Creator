import config
import pyTigerGraph as tg
from spellchecker import SpellChecker
import uuid, json, datetime, threading
import pandas as pd
from tigerGraph.eventGraph import event_snapshot

host = config.tg_host
graphname = config.tg_graph_name
username = config.tg_username
password = config.tg_password
secret = config.tg_secret

conn = tg.TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)
conn.apiToken = conn.getToken(secret)


# This is where we are going to create the actual Tigergraph Schema - the code that represents each Vertex node (Entity), each Edge Node (Interaction), and each Event (relationship)
def create_new_user_vertex(first_name, last_name, username, password, email, DOB):
    unique_id = uuid.uuid4()
    user_id = f"P{str(unique_id)[:8]}"
    date_of_birth = int(DOB)
    attributes = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password": password,
        "email": email,
        "DOB": DOB,
    }
    print(attributes)
    conn.upsertVertex("", user_id, attributes)
    return(user_id)

def user_login(email, password):
    result = conn.runInstalledQuery("authenticateUser", {"email": email, "password": password})
    # print('RESULT: ', result[0]['User'])
    return result[0]

def get_user_profile(id_value):
    result = conn.runInstalledQuery("getProfile", {"id_value": id_value})
    # print("RESULT: ", result)
    return result

def create_new_pdf_vertex(pdf_name, pdf_path):
    unique_id = uuid.uuid4()
    pdf_id = f"P{str(unique_id)[:8]}"
    attributes = {
        "pdf_name": pdf_name,
        "pdf_path": pdf_path
    }
    conn.upsertVertex("PDF", pdf_id, attributes)
    return(pdf_id)

def create_event(vertex1_id_list, vertex2_id_list, send_vertex, receive_vertex, send_edge_name, receive_edge_name, action):
    unique_id = uuid.uuid4()
    event_id = f"E{str(unique_id)[:8]}"
    timestamp = datetime.datetime.now()
    attributes = {
        "date_time": timestamp.isoformat(),
        "sensor": vertex1_id_list,
        "actuator": vertex2_id_list,
        "action": action
    }
    conn.upsertVertex("Event", f"{event_id}", attributes)

    # Use send/receive vertex to upsert event data
    # Get event data from vertex

    for id in vertex1_id_list:
        if id == "genesis":
            break
        properties = {"weight": 5}
        conn.upsertEdge(f"Event", f"{event_id}", f"{send_edge_name}", f"{send_vertex}", f"{id}", f"{properties}")
        add_event_to_vertex(id, timestamp, event_id, send_vertex)

    
    for id in vertex2_id_list:
        properties = {"weight": 5}
        conn.upsertEdge(f"Event", f"{event_id}", f"{receive_edge_name}", f"{receive_vertex}", f"{id}", f"{properties}")
        add_event_to_vertex(id, timestamp, event_id, receive_vertex)
    
    # event_snapshot(event_id, timestamp, action, vertex1_id_list, vertex2_id_list, send_vertex, receive_vertex, send_edge_name, receive_edge_name)
    event_thread = threading.Thread(target=event_snapshot, args=(event_id, timestamp, action, vertex1_id_list, vertex2_id_list, send_vertex, receive_vertex, send_edge_name, receive_edge_name))
    event_thread.start()

    return("hi")

def add_event_to_vertex(id, timestamp, event_id, vertex):
    data = conn.getVerticesById(vertex, id)

    data = data[0]['attributes']['event']
    # print("QUERY: ", data)
    keylist = []
    valuelist = []
    for key, value in data.items():
        keylist.append(key)
        valuelist.append(value)
    
    keylist.append(timestamp.isoformat())
    valuelist.append(event_id)
    # print("KEYS", keylist)
    # print("VALUES", valuelist)

    # get event history from vertex
    event_attributes = {
        "event": {
            "keylist": keylist,
            "valuelist": valuelist,
        }
    }

    conn.upsertVertex(f"{vertex}", f"{id}", event_attributes)