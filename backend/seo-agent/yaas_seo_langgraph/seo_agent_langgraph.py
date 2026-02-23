from langgraph import Graph
from langgraph.state import State
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Define state to store workflow data
class SEOState(State):
    data: dict = None
    keywords: list = None
    metadata: dict = None

# Node 1: Authenticate and Fetch YouTube Data
def fetch_data(state):
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    flow.redirect_uri = "http://localhost:8080/"
    credentials = flow.run_local_server(port=8080)
    youtube = build("youtube", "v3", credentials=credentials)
    request = youtube.search().list(part="snippet", q="python tutorials", maxResults=10)
    state.data = request.execute()
    return state

# Node 2: AI Analysis (Mock Mistral)
def ai_analysis(state):
    state.keywords = ["python", "tutorial", "2025"]  # Replace with real Mistral response
    return state

# Node 3: Optimize Metadata
def optimize_metadata(state):
    state.metadata = {
        "title": f"Top {state.keywords[0]} {state.keywords[1]} - {state.data['items'][0]['snippet']['title']}",
        "tags": state.keywords
    }
    return state

# Build and run the graph
workflow = Graph()
workflow.add_node("fetch", fetch_data)
workflow.add_node("analyze", ai_analysis)
workflow.add_node("optimize", optimize_metadata)
workflow.add_edge("fetch", "analyze")
workflow.add_edge("analyze", "optimize")
workflow.set_entry_point("fetch")

if __name__ == "__main__":
    initial_state = SEOState()
    result = workflow.run(initial_state)
    print(result.metadata)
