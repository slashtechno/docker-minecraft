from ubuntu:latest
WORKDIR /root

#MAINTAINER slashtechno
# Update System
RUN apt-get update
RUN apt-get upgrade -y

# Set timezone
RUN echo "America/New_York" > /etc/timezone

# Install software
RUN DEBIAN_FRONTEND=noninteractive apt-get install git curl wget openjdk-17-jdk -y

RUN cd /root
RUN mkdir /root/minecraft
RUN cd /root/minecraft
RUN wget -O /root/minecraft/BuildTools.jar https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar
RUN cd /root/minecraft/; java -Xmx2024M -jar /root/minecraft/BuildTools.jar --rev 1.18.1
RUN cd /root/minecraft/; java -Xms512M -Xmx2024M -jar /root/minecraft/spigot* nogui
RUN rm /root/minecraft/eula.txt
RUN wget -O /root/minecraft/eula.txt https://raw.githubusercontent.com/slashtechno/docker-minecraft/master/eula.txt 
# Download service
# RUN wget -O /etc/systemd/system/mc-server.service https://raw.githubusercontent.com/slashtechno/docker-minecraft/master/mc-server.service
# RUN systemctl enable mc-server.service 
# RUN systemctl start mc-server.service
CMD ["cd","/root/minecraft/","java","-Xms512M","-Xmx2024M","-jar","/root/minecraft/spigot*","nogui"]