from pydub import AudioSegment,silence
from array import *
import pandas as pd
import os
import re
import plotly.graph_objects as go

game = 4
load = False
rootdir = f'AmongUsGames/Game {game}'
T = [] 
imposters = [["Khalid", "Hakan"], ["Tim", "Abri"], ["Tim", "Gianni"], ["Hakan", "Gianni"], ["Gianni", "Bilal"], ["Hakan", "Abri"], ["Khalid", "Gianni"], ["Gianni", "Bilal"]]

print("Game #" + str(game) + " with imposters: " + imposters[game - 1][0] + " and " + imposters[game - 1][1])
print()

if not load:
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file and file[0] != '.': #discarding files that should be ignored
                tempre = re.sub( r"([A-Z]|[\\.])", r" \1", file).split() #regex to identify name and meeting
                print("Loading file: " + file)
                sound = AudioSegment.from_file(rootdir + "/" + file, format="wav") #load audio

                dBFS=sound.dBFS #using Decibels relative to full scale for way better results to identify speaking thresholds
                duration = sound.duration_seconds #duration of recording

                silencetest = silence.detect_silence(sound, min_silence_len=1000, silence_thresh=dBFS-16) #detecting silence with minimum of 1 sec duration
                silencetest = [((stop/1000)-(start/1000)) for start,stop in silencetest] #populating array with silence durations

                totalsilence = sum(silencetest) #total duration of silence
                speakingfor = 1 - totalsilence/duration #how long the person is speaking relative to the sound segment duration.

                T.append([tempre[2], speakingfor])
                print(tempre[2] + " spoke for " + str(speakingfor) + "% of " + tempre[1])
                print()

    df = pd.DataFrame(T, columns=['Name', 'SpokenFor']) #convert list to dataframe
    df.to_pickle(f'data/game {game}.pkl')
else:
    df = pd.read_pickle(f'data/game {game}.pkl')

df['avg'] = df.Name.apply(lambda name: df[df.Name == name].SpokenFor.mean()) #create and populate column with each player's average speaking %
df['is_imposter'] = df.Name.apply(lambda name: name in imposters[game - 1]) #create and populate column with imposter boolean value
df.drop_duplicates(subset=['Name'], inplace=True)

imposters_df = df[df.is_imposter == True] #data frame with just the imposters of the game
crew_df = df[df.is_imposter == False] #data frame with just the crewmates of the game
totalmean = df.SpokenFor.mean() #the average of the mean % speaking time of each player in the game

for index, row in imposters_df.iterrows(): 
    df3 = row['avg'] - crew_df['avg'] #difference between the imposter's % speaking and each crewmate's % speaking
    print(df3)

fig = go.Figure(data=[
    go.Bar(name='Crew', x=crew_df['Name'], y=crew_df['avg']),
    go.Bar(name='Imposters', x=imposters_df['Name'], y=imposters_df['avg'])
    ])
fig.add_hline(y=totalmean)
fig.update_layout(
    title= f"Game {game}",
    xaxis_title= "Names",
    yaxis_title= "Average"
)
    
fig.show()


print(f"""
Game: {game}
=======
Mean: {totalmean:0.4f}
"""
)
