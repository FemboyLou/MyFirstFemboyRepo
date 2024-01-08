
# Importing necessary libraries and modules
from moviepy.config import change_settings  # Change settings for moviepy library
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Set the path for ImageMagick binary

import ffmpeg  # Library for handling multimedia files
import speech_recognition as sr  # Library for speech recognition
import pyttsx3  # Library for text-to-speech conversion
from googletrans import Translator  # Library for translation using Google Translate API
from pydub import AudioSegment  # Library for audio processing
from tqdm import tqdm  # Library for creating progress bars
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip  # Library for video editing

import os




# Fonction pour extraire le son d'une vidéo
def extraire_audio(chemin_video):
    # Function to extract audio from a video file
    chemin_audio = 'audio_original.wav'
    # Set the output audio file path
    ffmpeg.input(chemin_video).output(chemin_audio).run()
    # Use ffmpeg to input the video file and output the audio file
    return chemin_audio
    # Return the path of the extracted audio file

def decouper_audio(chemin_audio, duree_segment=10000):
    # Function to split audio into segments
    audio = AudioSegment.from_wav(chemin_audio)
    # Load the audio file
    longueur = len(audio)
    # Get the length of the audio in milliseconds
    segments = []
    # Initialize an empty list to store the segments
    temps_debut = 0
    # Initialize the starting time of the segment
    for i in range(0, longueur, duree_segment):
        # Iterate over the audio in segments of specified duration
        segment = audio[i:i+duree_segment]
        # Extract the segment from the audio
        segments.append((segment, temps_debut, len(segment)))
        # Append the segment along with its starting time and duration to the list
        temps_debut += len(segment)
        # Update the starting time for the next segment
    return segments
    # Return the list of segments

def traduire_texte(texte, langue_cible):
    # Function to translate text to the target language
    traducteur = Translator()
    # Create an instance of the Translator class
    traduction = traducteur.translate(texte, dest=langue_cible)
    # Translate the text to the target language
    return traduction.text
    # Return the translated text

def generer_audio(texte, index, taux_parole=150):  # You can adjust the speech rate according to your needs
    # 150 words per minute. Lower than 150 will decrease the speech rate.
    # Higher than 150 will increase the speech rate.
    chemin_audio = f"segment_traduit_{index}.wav"  # Path for the generated audio file
    moteur_tts = pyttsx3.init()  # Initialize the text-to-speech engine
    moteur_tts.setProperty('rate', taux_parole)  # Adjust the speech rate
    moteur_tts.save_to_file(texte, chemin_audio)  # Save the synthesized speech to an audio file
    moteur_tts.runAndWait()  # Wait for the speech synthesis to complete
    return chemin_audio  # Return the path of the generated audio file


def combiner_audio(segments_traduits):
    audio_combiné = AudioSegment.silent(duration=0)
    # Create a silent audio segment with a duration of 0 to start with
    for seg, _, temps_debut, durée in segments_traduits:
        # Iterate over the translated segments
        silence = AudioSegment.silent(duration=temps_debut - len(audio_combiné))
        # Create a silent audio segment with a duration equal to the time gap between the current segment and the end of the combined audio
        audio_traduit = AudioSegment.from_wav(seg)[:durée]
        # Load the translated audio segment and trim it to the specified duration
        audio_combiné += silence + audio_traduit
        # Concatenate the silence segment, translated audio segment, and the combined audio
    audio_combiné.export("audio_final.wav", format="wav")
    # Export the final combined audio as a WAV file


def traiter_segments(segments):
    segments_traduits = []
    reconnaissance_vocale = sr.Recognizer()  # Initialize the speech recognition engine

    for i, (segment, temps_debut, durée) in tqdm(enumerate(segments), total=len(segments), desc="Traitement des segments", unit="segment"):
        segment.export(f"segment_{i}.wav", format="wav")  # Export the audio segment as a WAV file
        try:
            with sr.AudioFile(f"segment_{i}.wav") as source:  # Open the audio file for speech recognition
                audio = reconnaissance_vocale.record(source)  # Record the audio from the file
                texte = reconnaissance_vocale.recognize_google(audio, language='en-US')  # Perform speech recognition on the audio using Google Speech Recognition API
                texte_traduit = traduire_texte(texte, 'fr')  # Translate the recognized text to French
                chemin_audio_traduit = generer_audio(texte_traduit, i)  # Generate audio for the translated text
                segments_traduits.append((chemin_audio_traduit, texte_traduit, temps_debut, durée))  # Save the path of the generated audio file and the translated text
        except sr.UnknownValueError:
            print(f"Segment {i} non compris, passage au suivant...")  # Handle unknown speech segments
        except sr.RequestError as e:
            print(f"Erreur de requête pour le segment {i}: {e}")  # Handle request errors

    return segments_traduits

def remplacer_audio_video(chemin_video, chemin_audio):
    # Function to replace the audio of a video with a new audio file
    video = VideoFileClip(chemin_video)  # Load the video file
    audio = AudioFileClip(chemin_audio)  # Load the audio file
    video_final = video.set_audio(audio)  # Set the audio of the video to the new audio file
    video_final.write_videofile("video_modifiee.mp4", codec="libx264", audio_codec="aac")
    # Write the modified video file with the new audio, using the specified video and audio codecs


def diviser_texte_en_lignes(texte, longueur_max=40):
    """ Divise un texte en lignes de longueur maximale """
    # Split a text into lines of maximum length
    mots = texte.split()
    # Split the text into individual words
    lignes = []
    # Create an empty list to store the lines
    ligne_actuelle = mots[0]
    # Initialize the current line with the first word

    for mot in mots[1:]:
        # Iterate over the remaining words
        if len(ligne_actuelle) + len(mot) + 1 <= longueur_max:
            # Check if adding the current word to the current line exceeds the maximum length
            ligne_actuelle += " " + mot
            # Add the current word to the current line
        else:
            lignes.append(ligne_actuelle)
            # Add the current line to the list of lines
            ligne_actuelle = mot
            # Start a new line with the current word
    lignes.append(ligne_actuelle)
    # Add the last line to the list of lines

    return "\n".join(lignes)
    # Return the lines as a single string separated by newline characters


def main():
    # Path to the video file
    chemin_video = 'C:/Users/X7/Downloads/video test/ZZZ.mp4'
    
    # Extract audio from the video file
    chemin_audio = extraire_audio(chemin_video)
    
    # Split the audio into segments
    segments = decouper_audio(chemin_audio)
    
    # Process the audio segments (e.g., translate)
    segments_traduits = traiter_segments(segments)
    
    # Combine the translated audio segments
    combiner_audio(segments_traduits)

    # Load the original video without audio
    video = VideoFileClip(chemin_video).without_audio()

    # Load the translated and combined audio
    audio_traduit = AudioFileClip("audio_final.wav")

    # Create subtitle clips
#    clips_sous_titres = []
#   for chemin_audio, texte, temps_debut, durée in segments_traduits:
        # Split the text into lines
#        texte_multi_lignes = diviser_texte_en_lignes(texte)
        
        # Create a subtitle clip for each segment
        # Create a subtitle clip with the translated text
#        sous_titre = TextClip(texte_multi_lignes, font='Arial', fontsize=35, color='white', bg_color='rgba(0,0,0,0.5)')
        
        # Set the position of the subtitle clip to be centered at the bottom of the video
#        sous_titre = sous_titre.set_position(('center', 'bottom'))
        
        # Set the duration of the subtitle clip based on the segment duration
#        sous_titre = sous_titre.set_duration(durée/1000)
        
        # Set the start time of the subtitle clip based on the segment start time
#       sous_titre = sous_titre.set_start(temps_debut/1000)
        
        # Add the subtitle clip to the list of subtitle clips
#        clips_sous_titres.append(sous_titre)

    # Create a composite video with subtitles and translated audio
#    video_final = CompositeVideoClip([video] + clips_sous_titres).set_audio(audio_traduit)
    video_final = video.set_audio(audio_traduit)
    # Combine the original video and the subtitle clips, and set the translated audio as the audio of the composite video
#    video_final.write_videofile("video_avec_sous_titres.mp4", codec="libx264", audio_codec="aac")
    video_final.write_videofile("video_modifiee.mp4", codec="libx264", audio_codec="aac")
    # Write the composite video with subtitles and translated audio to a new video file

    # Cleaning temporary files
    nettoyer_fichiers_temporaires()


def nettoyer_fichiers_temporaires():
    # List of file extensions to delete
    extensions_a_supprimer = ['.wav', '.mp4', '.txt']  # Add or remove extensions depending on the files you generate

    # Get all files in current directory
    fichiers_dans_repertoire = os.listdir()

    # Browse all files in the directory
    for fichier in fichiers_dans_repertoire:
        # Get file extension
        extension = os.path.splitext(fichier)[1]
        # Check whether the file extension is in the list of extensions to be deleted
        if extension in extensions_a_supprimer and fichier != "video_modifiee.mp4":
            # Supprimer le fichier
            os.remove(fichier)


# Check if the current module is the main module
if __name__ == '__main__':
    # Call the main function if the current module is the main module
    main()
