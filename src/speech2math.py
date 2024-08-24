import os
import pandas as pd
import numpy as np
import speech_recognition as sr
import re
import streamlit as st
import io
from pydub import AudioSegment
from audiorecorder import audiorecorder

# Load data
df_c = pd.read_csv(r"https://raw.githubusercontent.com/swamilalit/Speech2Match/main/data/data.csv")

# Function to print n choose k
def print_n_choose_k(n, k):
    # Convert n and k to superscript and subscript characters
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    
    # Return the result
    return f"{n_str}P{k_str}"

def print_combi(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    
    # Return the result
    return f"{n_str}C{k_str}"

def print_integral(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(subscript_digits)
    k_str = str(k).translate(superscript_digits)
    
    # Return the result
    return f"{n_str}{chr(0x222B)}{k_str}"

def print_d_integral(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(subscript_digits)
    k_str = str(k).translate(superscript_digits)
    
    # Return the result
    return f"{n_str}{chr(0x222B)}{chr(0x222B)}{k_str}"

# Function to escape special characters
def escape_special_characters(text):
    # Escape special characters for regular expressions
    escaped_text = re.escape(text)
    return escaped_text

# Function to convert audio to equation
def from_audio_equation(audio_file):
    r = sr.Recognizer()
    audio_file_path = "temp_audio_file.wav"
    with open(audio_file_path, "wb") as f:
        f.write(audio_file.getbuffer())
    with sr.AudioFile(audio_file_path) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text)
            st.write("Recognized Text:", text)
            st.write("Converting into mathematical equation:")
            text_lower = text.lower().split()  # Split the recognized text into words

            equation = ''
            skip_next_words = False
            
            # Loop through each word in the recognized text
            i = 0
            while i < len(text_lower):
                word = text_lower[i]
                escaped_word = escape_special_characters(word)
                if df_c['Name'].str.contains(escaped_word, case=False).any():
                    remaining_text = ' '.join(text_lower[i:])
                    
                    # Check if the remaining text matches any name in the DataFrame
                    for j in range(len(remaining_text.split()), 0, -1):
                        str_to_check = ' '.join(remaining_text.split()[:j])
                        if str_to_check in df_c['Name'].str.lower().values:
                            if str_to_check == "to the power":
                                i = i + 3
                                if text_lower[i] == "2":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                elif text_lower[i] == "3":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                else:
                                    equation +=  (chr(0x2070 + int(text_lower[i])))
                                i = i + 1
                            elif str_to_check == "raised to" :
                                i = i + 2
                                if text_lower[i] == "2":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                elif text_lower[i] == "3":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                else:
                                    equation +=  (chr(0x2070 + int(text_lower[i])))
                                i = i + 1
                            elif str_to_check == "square":
                               
                                equation +=  (chr(0x00B0 + int(2)))
                                i = i + 1
                            elif str_to_check == "cube":
                                equation +=  (chr(0x00B0 + int(3)))
                                i = i + 1
                            elif str_to_check == "permutation":
                                var = print_n_choose_k(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            elif str_to_check == "combination":
                                var = print_combi(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            elif str_to_check == "double integral":
                                var = print_d_integral(equation[-2], text_lower[i+2])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 3
                            elif str_to_check == "integral":
                                var = print_integral(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            else:
                                equation += df_c.loc[df_c['Name'].str.lower() == str_to_check, 'Symbol'].values[0] + ' '
                                i += len(str_to_check.split())
                            skip_next_words = True
                            break
                if not skip_next_words:
                    equation += word + ' '
                    i += 1
                else:
                    skip_next_words = False

            st.write("Equation:", equation.strip())  #Strip trailing whitespace to remove extra space at the end
        except Exception as e:
            st.write("Error:", e)
    #os.remove(audio_file_path)

# Function to convert speech from the microphone
def from_microphone():
    st.write("in mic")
    audio = audiorecorder("Click to record", "Click to stop recording")
    if len(audio)>0:
        st.write("audio")
        st.audio(audio.export().read(), format ='audio/wav') 
        st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")  
        r = sr.Recognizer()
        st.write("Recognizer called")
        audio_file_path = "temp_audio_file.wav"
        with open(audio_file_path, "wb") as f:
            f.write(audio.export().read())
        with sr.AudioFile(audio_file_path) as source:
            audio_text = r.listen(source)
            st.write("audio text recorded")
        try:
            text = r.recognize_google(audio_text)
            st.write("Recognized Text:", text)
            st.write("Converting into mathematical equation:")
            text_lower = text.lower().split()  # Split the recognized text into words

            equation = ''
            skip_next_words = False
            
            # Loop through each word in the recognized text
            i = 0
            while i < len(text_lower):
                word = text_lower[i]
                escaped_word = escape_special_characters(word)
                if df_c['Name'].str.contains(escaped_word, case=False).any():
                    remaining_text = ' '.join(text_lower[i:])
                    
                    # Check if the remaining text matches any name in the DataFrame
                    for j in range(len(remaining_text.split()), 0, -1):
                        str_to_check = ' '.join(remaining_text.split()[:j])
                        if str_to_check in df_c['Name'].str.lower().values:
                            if str_to_check == "to the power":
                                i = i + 3
                                if text_lower[i] == "2":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                elif text_lower[i] == "3":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                else:
                                    equation +=  (chr(0x2070 + int(text_lower[i])))
                                i = i + 1
                            elif str_to_check == "raised to" :
                                i = i + 2
                                if text_lower[i] == "2":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                elif text_lower[i] == "3":
                                    equation +=  (chr(0x00B0 + int(text_lower[i])))
                                else:
                                    equation +=  (chr(0x2070 + int(text_lower[i])))
                                i = i + 1
                            elif str_to_check == "square" :
                                equation +=  (chr(0x00B0 + int(2)))
                                i = i + 1
                            elif str_to_check == "cube":
                                equation +=  (chr(0x00B0 + int(3)))
                                i = i + 1
                            elif str_to_check == "permutation":
                                var = print_n_choose_k(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            elif str_to_check == "combination":
                                var = print_combi(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            elif str_to_check == "integral":
                                var = print_integral(equation[-2], text_lower[i+1])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 2
                            elif str_to_check == "double integral":
                                var = print_d_integral(equation[-2], text_lower[i+2])
                                equation= equation.replace(equation[-2],var,1)
                                i = i + 3
                            else:
                                equation += df_c.loc[df_c['Name'].str.lower() == str_to_check, 'Symbol'].values[0] + ' '
                                i += len(str_to_check.split())
                            skip_next_words = True
                            break
                if not skip_next_words:
                    equation += word + ' '
                    i += 1
                else:
                    skip_next_words = False

            st.write("Equation:", equation.strip())  #Strip trailing whitespace to remove extra space at the end
            st.button("Go back", use_container_width=True)
        except Exception as e:
            st.write("Error:", e)
    st.write("out")

def from_mic():
    audio = audiorecorder("Click to record", "Click to stop recording")

    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.export().read(), format='audio/wav')  
    
        # To get audio properties, use pydub AudioSegment properties:
        #st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
        
        # Export the audio to a bytes buffer
        audio_bytes = audio.export().read()
        
        # Check if the audio_bytes is not empty
        if audio_bytes:
            #st.write("Audio successfully saved in bytes buffer.")
            
            try:
                # Initialize recognizer
                r = sr.Recognizer()
                #st.write("Recognizer called")
                
                # Convert audio bytes to AudioSegment
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
                
                # Export AudioSegment to a WAV format bytes buffer
                wav_buffer = io.BytesIO()
                audio_segment.export(wav_buffer, format='wav')
                wav_buffer.seek(0)
                
                # Use the wav buffer with speech recognition
                with sr.AudioFile(wav_buffer) as source:
                    audio_text = r.record(source)
                    #st.write("Audio text recorded")
    
                    # Recognize speech using Google Speech Recognition
                    text = r.recognize_google(audio_text)
                    st.write("Recognized Text:", text)
                    st.write("Converting into mathematical equation:")
                    text_lower = text.lower().split()  # Split the recognized text into words
                    equation = ''
                    skip_next_words = False
                    
                    # Loop through each word in the recognized text
                    i = 0
                    while i < len(text_lower):
                        word = text_lower[i]
                        if word == "^" :
                            i = i + 1
                            if text_lower[i] == "2":
                                equation +=  (chr(0x00B0 + int(text_lower[i])))
                            elif text_lower[i] == "3":
                                equation +=  (chr(0x00B0 + int(text_lower[i])))
                            else:
                                 equation +=  (chr(0x2070 + int(text_lower[i])))
                            i = i + 1
                            if i < len(text_lower):
                                continue
                            else:
                                break
                        escaped_word = escape_special_characters(word)
                        if df_c['Name'].str.contains(escaped_word, case=False).any():
                            remaining_text = ' '.join(text_lower[i:])
                            # Check if the remaining text matches any name in the DataFrame
                            for j in range(len(remaining_text.split()), 0, -1):
                                str_to_check = ' '.join(remaining_text.split()[:j])
                                if str_to_check in df_c['Name'].str.lower().values:
                                    if str_to_check == "to the power":
                                        i = i + 3
                                        if text_lower[i] == "2":
                                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                                        elif text_lower[i] == "3":
                                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                                        else:
                                            equation +=  (chr(0x2070 + int(text_lower[i])))
                                        i = i + 1
                                    elif str_to_check == "raised to" :
                                        i = i + 2
                                        if text_lower[i] == "2":
                                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                                        elif text_lower[i] == "3":
                                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                                        else:
                                            equation +=  (chr(0x2070 + int(text_lower[i])))
                                        i = i + 1
                                    elif str_to_check == "square" :
                                        equation +=  (chr(0x00B0 + int(2)))
                                        i = i + 1
                                    elif str_to_check == "cube":
                                        equation +=  (chr(0x00B0 + int(3)))
                                        i = i + 1
                                    elif str_to_check == "permutation":
                                        var = print_n_choose_k(equation[-2], text_lower[i+1])
                                        equation= equation.replace(equation[-2],var,1)
                                        i = i + 2
                                    elif str_to_check == "combination":
                                        var = print_combi(equation[-2], text_lower[i+1])
                                        equation= equation.replace(equation[-2],var,1)
                                        i = i + 2
                                    elif str_to_check == "integral":
                                        var = print_integral(equation[-2], text_lower[i+1])
                                        equation= equation.replace(equation[-2],var,1)
                                        i = i + 2
                                    elif str_to_check == "double integral":
                                        var = print_d_integral(equation[-2], text_lower[i+2])
                                        equation= equation.replace(equation[-2],var,1)
                                        i = i + 3
                                    else:
                                        equation += df_c.loc[df_c['Name'].str.lower() == str_to_check, 'Symbol'].values[0] + ' '
                                        i += len(str_to_check.split())
                                    skip_next_words = True
                                    break
                        if not skip_next_words:
                            equation += word + ' '
                            i += 1
                        else:
                            skip_next_words = False
                    st.write("Equation:", equation.strip())
            except Exception as e:
                st.write("Error during speech recognition:", e)



def help_manual():
    st.markdown("<h1 style='text-align: center;'>Help Manual</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'><strong>Table of contents</strong></p>", unsafe_allow_html=True)
    st.markdown("""
                    1. Introduction
                    2. System Requirements
                    3. Getting started
                    4. Supported audio formats
                    5. Commands
                    6. Troubleshooting
                    """)
    st.markdown("<h3>1. Introduction</h3>", unsafe_allow_html=True)
    st.write("Welcome to speech2math, a speech-to-symbol approach designed to make mathematical notation easier through speech recognition. This manual will guide you through the process of using speech2math effectively to convert spoken mathematical expressions into symbolic equations.")
    st.markdown("<h3>2. System requirements</h3>", unsafe_allow_html=True)
    st.write("To use speech2math, you will need:")
    st.markdown("""
                    - A computer or device with a microphone
                    - Internet connection (for online services)
                    - Supported audio file formats: WAV, AIFF, AIFF-C, FLAC
                    """)
    st.markdown("<h3>3. Getting started</h3>", unsafe_allow_html=True)
    st.write("To begin using speech2math, follow these steps:")
    st.markdown("""
                    - Launch the speech2math application on your device.
                    - Choose your preferred input method: microphone or audio file.
                    - Speak clearly and distinctly when giving commands or dictating mathematical expressions.
                    """)
    st.markdown("<h3>4. Supported audio formats</h3>", unsafe_allow_html=True)
    st.write("speech2math supports the following audio file formats for input:")
    st.markdown("""
                    - WAV
                    - AIFF
                    - AIFF-C
                    - FLAC
                    """)
    st.write("To convert your audio files you may use : https://cloudconvert.com/wav-converter")
    st.markdown("<h3>5. Commands</h3>", unsafe_allow_html=True)
    st.write("Here are some commands you can use with speech2math:")
    st.markdown("""
                    1. Square brackets[]: Say "open squared brackets" to open and "closed squared brackets" to close.
                    2. Parenthesis(): Say "open Parenthesis" to open and "closed Parenthesis" to close.
                    3. Permutation ⁿPₖ : Express as "n permutation k" 
                    4. Combination ⁿCₖ : Express as "n combination k" 
                    5. a. Exponents : Use "raised to" or "to the power" to express exponents
                       b. For square and cube, express as number square or number cube. 
                    6. Integration : express as "lower limit integral upper limit" to print ₄∫⁵.
                    7. Double integral : say "double integral" to print double integral without limits. 
                                         for double integral with limits, say the single integral twice.  
                    8. Modulo : say " modulo your expression modulo " for opening and closing.
                    """)
    st.markdown("<h3>6. Troubleshooting</h3>", unsafe_allow_html=True)
    st.write("If you encounter any issues while using speech2math, consider the following troubleshooting steps:")
    st.markdown("""
                    - Check your internet connection (if using online services).
                    - Ensure your microphone is properly connected and configured.
                    - Speak clearly and avoid background noise.
                    - Connect wired headset(with microphone) if there is unavoidable background noise.
                    - Verify that your audio file is in one of the supported formats (WAV, AIFF, AIFF-C, FLAC).
                    """)
    
def about_us():
    st.markdown("<h1 style='text-align: center;'>About us</h1>", unsafe_allow_html=True) 
    st.markdown("<h3>Our mission</h3>", unsafe_allow_html=True)  
    st.write("At speech2math, we are dedicated to revolutionizing the way mathematical notation is expressed and understood. Our mission is to provide a seamless and intuitive platform that enables users to effortlessly convert spoken mathematical expressions into symbolic equations.")
    st.markdown("<h3>Who are we?</h3>", unsafe_allow_html=True)
    st.write("We envision a future where anyone, regardless of mathematical proficiency, can easily communicate and work with mathematical expressions. By leveraging the power of speech recognition technology, we aim to empower students, educators, professionals, and enthusiasts alike to interact with mathematics in a more natural and efficient manner.")
    st.markdown("<h3>Why speech2match?</h3>", unsafe_allow_html=True)
    st.markdown("""
                    - Simplicity: speech2math streamlines the process of converting spoken language into mathematical notation, making it accessible to everyone.
                    - Efficiency: Our platform saves time and effort by eliminating the need for manual transcription of mathematical expressions.
                    - Accessibility: speech2math breaks down barriers to mathematical understanding, enabling users of all skill levels to engage with complex concepts.
                    """)
    
    

# Streamlit app
st.set_page_config(layout="centered", page_title="speech2math", page_icon=":123:",  initial_sidebar_state="expanded")

def main():
    # Render custom CSS using st.markdown
    col1, col2 = st.columns([1.25,5])  # Adjust the ratio as needed

# Display image in the first column
    col1.image(r'https://raw.githubusercontent.com/swamilalit/Speech2Math/main/data/image.png', use_column_width=True)

# Write text in the second column
    col2.header("Speech2Math")
    col2.subheader("A speech to symbol approach")
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Go to", ['Home','Microphone', 'Help', 'About us'])
    if selection:
        st.session_state.page = selection
    # Display content based on user selection
    if st.session_state.page == 'Home':
        st.write("")
        st.write("Upload audio file here.")
        uploaded_file = st.file_uploader("", type=["wav", "mp3"])
        if uploaded_file is not None:
            from_audio_equation(uploaded_file)
        st.write("")
        st.markdown("<p style='text-align: center;'>OR</p>", unsafe_allow_html=True)
        st.write("Click here to use microphone")
        st.write("")
        if st.button('Use Microphone', use_container_width=True):
            st.session_state.page = "Microphone"
        st.write("*Click on the microphone radio button if the button doesn't load a screen")
    elif st.session_state.page == 'Microphone':
        from_mic()
    elif st.session_state.page == 'Help':
        help_manual()
    elif st.session_state.page == 'About us':
        about_us()
        

                  

if __name__ == "__main__":
    main()
