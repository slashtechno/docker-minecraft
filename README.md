# Docker-Minecraft
#### Easily use Docker to deploy a basic Minecraft server  
### Requirements
* [Basic knowledge](https://www.youtube.com/watch?v=eGz9DS-aIeY) of Docker
* Docker
* Linux

### To use
1. Clone the repo with `git clone https://github.com/slashtechno/docker-minecraft/`
2. Change to the directory with `cd docker-minecraft`
3. Create Docker image with `docker build -t docker-minecraft .`
4. Create container with `docker run -t -d -p 25565:25565 --name docker-minecraft-container docker-minecraft`  
  a. You can change the port that the server uses (outside of the container) by changing the first occurence of 25565.

Done!
