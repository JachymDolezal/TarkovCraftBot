FROM  python:latest

RUN pip3 install discord.py
RUN pip3 install pandas
RUN pip3 install numpy

COPY TarkovBot.py /opt/tarkovpump/Discordbot/TarkovBot.py
COPY config_bot.py /opt/tarkovpump/Discordbot/config_bot.py

WORKDIR /opt/tarkovpump/Discordbot

CMD ["python3", "TarkovBot.py"]

