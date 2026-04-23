from apps.graph.queries import get_full_graph_data
try:
    data = get_full_graph_data()
    print("SUCCESS")
    import json
    print(json.dumps(data))
except Exception as e:
    print("ERROR")
    import traceback
    traceback.print_exc()
