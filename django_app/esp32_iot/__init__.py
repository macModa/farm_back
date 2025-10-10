from mongoengine import connect, disconnect

# Déconnecte si une connexion existe déjà
disconnect(alias='default')

# Reconnecte proprement
connect(
    db='esp32_iot_data',
    host='mongodb+srv://jesssser93_db_user:FydCbJAO4CqguvLu@cluster0.5y36wng.mongodb.net/farmdb?retryWrites=true&w=majority&tls=true'
)

print("✅ MongoDB connected successfully!")
