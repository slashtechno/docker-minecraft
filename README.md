# Docker-Minecraft
#### Easily use Docker to deploy a basic Minecraft server  
### Requirements
* [Basic knowledge](https://www.youtube.com/watch?v=eGz9DS-aIeY) of Docker (not needed, but recommended)
* Docker
* Linux

### To use  
1. Clone the repo with `git clone https://github.com/slashtechno/docker-minecraft/`
2. Change to the directory with `cd docker-minecraft`
3. Run the script with `python3 server-manager.py` (you may need to use `python` instead of `python3`)  
Done!  
### Credits  
* [@Glitch752](https://github.com/glitch752)

### Roadmap  
- [X] Migrate from `os.system` to `subprocess.run` (completed in commit f70b5088698210f81304d6bc7fe0fa3d69f7d6ec)  
- [ ] Allow port changes (save current container as an image, and run image with new ports)
- [ ] Use `pathlib` library
