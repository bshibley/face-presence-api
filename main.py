from fastapi import FastAPI, File
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict
from lru import LRU
import cv2
import face_recognition
import numpy as np
import os
import chromadb

class Session(BaseModel):
    user_id: int
    distances: dict[int, float]
    baseline_embedding: np.ndarray
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

class SessionResult(BaseModel):
    session_id: str
    user_id: int
    pct_present: float
    avg_distance: float
    std_distance: float

id_threshold = 0.3

# If chroma db doesn't exist, create it
if not os.path.exists('chroma'):
    os.makedirs('chroma')

# Load chroma database of known face embeddings
chroma_dir = 'chroma'
chroma_client = chromadb.PersistentClient(path=chroma_dir)
chroma_collection = chroma_client.get_or_create_collection(name="user_embeddings")

app = FastAPI()

# Using LRU dictionary as cache - consider using redis or memcached for production
app.cache = LRU(1024)

@app.post("/sessions")
async def post_session_image(session_id: str, user_id: int, timestamp: int, file: bytes = File(...)):
    if session_id not in app.cache:
        # Fetch baseline encoding from database
        baseline_embedding = chroma_collection.get(ids=[str(user_id)],include=['embeddings'],)["embeddings"]
        # Add new session to cache
        app.cache[session_id] = Session(user_id=user_id, distances={}, baseline_enmbedding=baseline_embedding)
    # Ensure user ID matches the session's user ID
    if user_id != app.cache[session_id].user_id:
        return 'User ID does not match session ID'
    # Convert file bytes to RGB numpy array
    img_array = cv2.imdecode(np.frombuffer(file, dtype=np.uint8), cv2.IMREAD_COLOR)
    session_face_embeddings = face_recognition.face_encodings(img_array)
    # Save the distance of the nearest face in the uploaded image
    min_distance = 1
    for face_embedding in session_face_embeddings:
        distance = np.linalg.norm(np.array(app.cache[session_id].baseline_embedding) - face_embedding, axis=1)/2
        min_distance = min(min_distance, distance)
    app.cache[session_id].distances[timestamp] = min_distance
    return 'Image received'

@app.get("/sessions/{session_id}")
async def get_session_results(session_id: str):
    if session_id in app.cache:
        # Return the minimum distance from the session
        return SessionResult(
          session_id=session_id,
          user_id=app.cache[session_id].user_id,
          pct_present=len(dict((k, v) for k, v in app.cache[session_id].distances.items() if v <= id_threshold))/len(app.cache[session_id].distances),
          avg_distance=np.mean(list(app.cache[session_id].distances.values())),
          std_distance=np.std(list(app.cache[session_id].distances.values()))
        )
    else:
        return 'Session not found'

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id in app.cache:
        del app.cache[session_id]
        return 'Session deleted'
    else:
        return 'Session not found'

@app.get("/users/{user_id}")
async def get_user_embedding(user_id: int):
    # Fetch user's face encoding from database
    user_embedding = chroma_collection.get(ids=[str(user_id)],include=['embeddings'],)["embeddings"]
    return user_embedding

@app.put("/users/{user_id}")
async def set_user_image(user_id: int, file: bytes = File(...)):
    # Convert file bytes to RGB numpy array
    img_array = cv2.imdecode(np.frombuffer(file, dtype=np.uint8), cv2.IMREAD_COLOR)
    id_face_embeddings = face_recognition.face_encodings(img_array)
    # Ensure only one face is found in the photo
    if len(id_face_embeddings) == 1:
        id_face_embedding = id_face_embeddings[0].tolist()
        # Insert the user's face encoding into the database
        chroma_collection.add(ids=[str(user_id)], embeddings=[id_face_embedding])
        return 'Image successfully added to the database'
    elif len(id_face_embeddings) == 0:
        return 'No face found in the photo'
    else:
        return 'More than one face found in the photo'

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    # Delete the user's face encoding from the database
    chroma_collection.delete(ids=[str(user_id)])
    return 'User successfully deleted'

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    # Delete the user's face encoding from the database
    chroma_collection.delete(ids=[str(user_id)])
    return 'User successfully deleted'

@app.get("/", response_class=PlainTextResponse)
async def root():
    return """
                     .....:::::..                                                       
               .:==--+#%@%%%%%%%*:...                                                   
              ..###%%%%########%%@%#*=..                                                
            ..:*@######%######%#*****#%+..                                              
          ..-%%#########%#####@********#%:..                                            
        ..-#%###+=+*#########%#**#******#@+.........                                    
       ..*%##+=#*+++#########@**##-=#%***%%@=:@@@#:                                     
       .+%####=++*+*+*######%%+*#*---=#***@*%@*...                                      
      ..+%*++*+#*+#####%@@@@%*=======-##**@%@%*.                                        
       .-##**++*###%@#++#%*+==============#@**%:.                      .....            
       ..+%#++###%%+-+#*=+*+=============%%+**#%=...               ..-*%#**%*:.         
         :####%%+==*%#*+==++============%@+==+**#%+..       ....:=#%#=:...*==#*..       
         .-%@*=-=#%*=+*+==============+%@+======+*#+..  ...-+%%#++***+:.....-*%*.       
       ..=#+=--*#+++=+*+==========+#%@@@#========*#+..-*###+++**+==+*+=:....-=**..      
     ..-*+---+%+======++=====+#%@@@@@@@@*=======+*%%###++***==+*+===+===-..-=*#-.       
    .:+*=----#%=========+#%#@@@@%##%@@@@@+======*#%***+==+**===++=========+##=..        
  ..:*+--+#*++%====+#%@@@@*#*-:+...=*+@@@+=====+#%#**+====**========++*#%#=:..          
  ..=%**+=::*@@#%@@@@@@@#**==*H..:=#**%@@*===+*#%***+=====++=====++*#%#=:..             
   ..:....+@@@@@@@@@%#*===+*A*::-==++*#%@%*++*#%#**+===========++*###=:...               
         .+@#:.+@@#+=++==*N*++==+++++#%#***%%#**+==========++*##*=...      ......       
          .-%+*#**+====*N*****+===+#%#**#%%*+++==========+*#%*-..        .:=****+:..    
          ..*%+==+===*I**********##*+*#%#++=-...-======+*##-...        .-#+:....-*-.    
          .=#*+====*A********#%%*==+#%*+==+:.....-=====+##.          ..=#::.....:*-.    
          .+#++==*R******##@@%++**##+==---:..   .:====+*%-.          ..%==:.---**-..    
          .:#+=*T****##%%#**#*+======----...    ..:===+*@:.          .-#=====+*..       
           ..*#+=+**##***++++====--:.:::-..     ..:-===+%=.          ..%+===+#-.        
             ..+%%***%%#*++===-:....:::::...     ..:===+#%.          ..+#***+*+.        
               .......+%***+=:::...::--:...       .:====+@-..          .%*++**#:.       
                      :*#*+==:.:-::::-:..         .:-====#%...         .+#====*+.       
                      -#*====::=-===:...          ..-=====%@:.         .-@**+=**.       
                    ..**=====::-----=-...         ..-======@%#:.       .*%***+**.       
                   .:**======---===--=-..         .:=======*@*#%+:.  ..##===+***..      
                  .-##*======-:--+=-:--...       ..-======+**%***##%%%#**====+#-.       
                ..-#+=++=====-:.:--:-=-..    ....:==========+%%****+==+**+===*+.        
                .+%*=========-:----==-:.....::--============+*%#****+==+*==+#+..        
               .=%***++====================================**++%%#***+==+##=:.          
               .**==+++====================++**================*%#=+**+=-:..            
               .*#+=================+*#%%%%@%#*+=============+***%+..                   
               .=%***++++=======+##*+-:.....:=+#%%#*++=======++***%+..                  
               .:#++++++=====+#*=:..          ...:=+#%%#**++++*****%+..                 
                .-%*+=======##....                  ..:=#%#*********%+..                
                ..=%***+===*%+.                         .:*%#********%+..               
                 .:+*:==:-:++@-.                          .:%+-=--:-:.*#-.              
                ..:*+:-=:..-=*%.                            -#....:=:-=:%:.             
                .:*=-=:==..-==@.                            :#-::::*+:#-#=..            
                .:*=++-+-.:=+*%.                            ..-==++++++=-.              
                ..-***####*+-.                                                          
    """