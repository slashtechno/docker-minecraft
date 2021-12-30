import os
import json
# Set up docker container


# Set up rcon 
# Request user input
print("In order to remotly access the console of the Minecraft server, rcon needs to be setup\nrcon is a protcol for remotely managing game servers")
print("This program will ask for authentication in order to use sudo\n")
password = input("What is the password you would like to set for rcon?\n")
# port=input("\nWhat is the port you would like to use for rcon?\n")
print("\nEditing files\n")
# Read original_server.properties
with open ("original_server.properties", "r") as original_config_file:
    original_config = original_config_file.read()
    original_config_file.close()
new_config = original_config.replace("rcon.password=", "rcon.password="+password)
# new_config = original_config.replace("rcon.port=25575", "rcon.port="+port)
# Write to server.properties
with open ("server.properties", "w") as server_config:
    server_config.write(new_config)
    server_config.close()

# Remove server.properties
print("Removing server.properties in container\n")
os.system("sudo docker exec docker-minecraft-container rm -rf /root/minecraft/server.properties")
# Copy server.properties to /root/minecraft/server.properties
print("Copying server.properties to the container")
os.system("sudo docker cp server.properties docker-minecraft-container:/root/minecraft/server.properties")
# Restart the docker container
print("Retarting the container\n")
os.system("sudo docker restart docker-minecraft-container")

"""
NOTES:
If this program evolves into a setup script for the Docker container itself, it would be favorable to adjust the amount of RAM allocated depending on the amount of RAM accessible.     
"""