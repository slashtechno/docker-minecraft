import os

# Request user input
print("In order to remotly access the console of the Minecraft server, rcon needs to be setup\n")
password = input("What is the password you would like to set for rcon?\n")
# port=input("\nWhat is the port you would like to use for rcon?\n")
print("\nEditing files\n")

# Read original_server.properties
with open ("original_server.properties", "r") as original_config_file:
    original_config = original_config_file.read()
    original_config_file.close
new_config = original_config.replace("rcon.password=", "rcon.password="+password)
# Write to server.properties
with open ("server.properties", "w") as server_config:
    server_config.write(new_config)
    server_config.close