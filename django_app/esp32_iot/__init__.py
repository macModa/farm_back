# This will make Python treat the directories as containing packages
from mongoengine import connect
import certifi

connect(
    host="mongodb+srv://jesssser93_db_user:FydCbJAO4CqguvLu@cluster0.5y36wng.mongodb.net/farmdb?retryWrites=true&w=majority&tls=true",
    tlsCAFile=certifi.where()
)
print("✅ MongoDB connected successfully!")
