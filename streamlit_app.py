
import openai
import streamlit as st
import os
from PIL import Image
import IPython
from IPython.display import Audio

MAX_TEXT = 500 # Max number of ChatGPT answer's text'
MAX_MESSAGE = 10 # Max number of messages sending to ChatGPT

ss = st.session_state

######################
#  st.session_state  #
######################
if "title" not in ss:  # title
    ss.title = ""
if "image" not in ss:  # Upload image
    ss.image = None
if "uploaded_txt" not in ss:    # Upload text
    ss.uploaded_txt = None
if "uploaded_voices" not in ss:  # Upload voice
    ss.uploaded_voices = []
if "names" not in ss: # name list of family member
    ss.names = []
if "num" not in ss: # number of family member
    ss.num = []
if "selected_speaker" not in ss: # Detect change of selected speaker
    ss.selected_speaker = None
if "topics" not in ss: # Inputed topics
    ss.topics = []
if "assists" not in ss: # Inputed assists
    ss.assists = []
if "dialogues" not in ss: # Inputed dialogues
    ss.dialogues = []
if "prompt_name" not in ss: # My name is {My_name}
    ss.prompt_name = ""
if "messages" not in ss: # Messages to send to AI
    ss.messages = []
if "voice_gender" not in ss: # select voice_gender
    ss.voice_gender = "Woman"

ok_message_voices = "Reading voice files are OK." # OK message for input voice files
ng_message_voices = "Reading voice file is NG."  # Ng message for input voice files

######################
# define of function #
######################
def chk_inputs(input_values, ng_message, ok_message):
    error_detected = False
    for input_value in input_values:
        if not input_value:  # In case of empty
            st.error(ng_message)
            error_detected = True
            break  # if there is any error, then break out of loop.
    if not error_detected:
        st.success(ok_message)

def inpt_speakers():
    example_name = [':man-frowning: Dad',':woman-frowning: Mom', ':man-pouting: TOM', ':woman-pouting: ALICE']
    ng_message = "Input name is wrong."
    ok_message = "All inputs are OK."

    number_of_fields = st.number_input("Input number of names to be registered.", min_value=1, value=1, step=1)
    num = int(number_of_fields)
    # dynamic generation of text input fields
    names = []
    for i in range(num):
        text_input = st.text_input(f'No.{i + 1}: input name Example: {example_name[i % 4]}', key=f"input_{i}")
        names.append(text_input)
    # Check input fields
    chk_inputs(names, ng_message, ok_message)
    return num, names

def inpt_topics():
    # Topic message
    topic1 = 'Talk about memories of Sally to build bonds'
    topic2 = 'Asking AI to talk about short stories'
    topic3 = 'Consulting AI about everything like health'
    example_topic = [topic1, topic2, topic3]
    # Send message for AI's role
    assist1 = "I have a fun conversation with you about our beloved dog, Sally."\
                  "I take turns playing the role of Sally and share memories to deepen our bond with her."
    assist2 = "I am a professional storyteller who will entertain you with heartwarming stories"\
                  " based on the themes you provide."
    assist3 = "I am a professional consultant who will answer your questions politely and make good advices."
    example_assist = [assist1, assist2, assist3]
    # Send dialogue's example
    dialogue1 = "Example: Sally's favorite things, places, and foods"
    dialogue2 = "Example theme: loyal dog, success story, story of overcoming hardships"
    dialogue3 = "Example question: Tell me how to take medicine surely."
    example_dialogue = [dialogue1, dialogue2, dialogue3]
    # Message for input check
    ok_message_topics = "All topics are OK."
    ng_message_topics = "Input of topic is wrong."
    ok_message_assists = "All messages for AI's role are OK."
    ng_message_assists = "Input of message for AI's role is wrong."
    ok_message_dialogues = "All dialogue's examples are OK."
    ng_message_dialogues = "Dialogue's example is wrong."

    number_of_fields = st.number_input("Input number of topics to be registered.", min_value=1, value=1, step=1)
    num = int(number_of_fields)
    # dynamic generation of text input fields
    topics = []
    assists = []
    dialogues = []
    for i in range(num):
        with st.container():
            st.markdown(f"No.{i + 1} input set")  # セットのラベルを表示
            text_input0 = st.text_input(f"{i + 1}.1: Input topic", example_topic[i % 3], key=f"txt_input0_{i}")
            topics.append(text_input0)
            text_input1 = st.text_input(f"{i + 1}.2: Input message for AI's role", example_assist[i % 3], key=f"txt_input1_{i}")
            assists.append(text_input1)
            text_input2 = st.text_input(f"{i + 1}.3: Input example of dialogue", example_dialogue[i % 3], key=f"txt_input2_{i}")
            dialogues.append(text_input2)
    # Check input fields of topics, assists, and dialogues
    chk_inputs(topics, ng_message_topics, ok_message_topics)
    chk_inputs(assists, ng_message_assists, ok_message_assists)
    chk_inputs(dialogues, ng_message_dialogues, ok_message_dialogues)

    return topics, assists, dialogues

# Code body
# OpenAI KEY
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key is already provided!', icon='✅')
        openai.api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

with st.sidebar:
    with st.expander("Configuration"):
        # title input
        default_value = "🐶 Let's talk about memories of our dog Sally with AI. 😃"
        ss.title = st.text_input("Enter title of this game.", default_value)

        # Image file upload
        uploaded_image = st.file_uploader("Upload image file for header")
        if uploaded_image is not None:
            ss.image = Image.open(uploaded_image)
            st.success('Image has been uploaded')
        # Additional information upload
        ss.uploaded_txt = st.file_uploader("Upload additoinal information for AI", type=['txt'])
        if ss.uploaded_txt is not None:
            st.success('Additional information for AI has been uploaded')
        # member registration
        ss.num, ss.names = inpt_speakers()
        # Upload voice files
        if ss.names:
            ss.uploaded_voices = []
            for i in range(ss.num):
                voice_input = st.file_uploader(f'Upload voice file for speaker No.{i + 1}', key=f"voice_{i}")
                ss.uploaded_voices.append(voice_input)
            # Check download voice files
            chk_inputs(ss.uploaded_voices, ng_message_voices, ok_message_voices)
        # topic registration
        ss.topics, ss.assists, ss.dialogues = inpt_topics()
        # select voice for AI
        ss.voice_gender = st.selectbox("Select voice for AI's answer:", ["Woman", "Man"])


    if ss.title:
        st.title(ss.title)

    assist_content1, assist_content2 = "", "" # Message for AI's role
    # Select one of speakers
    my_name = st.radio('Select speaker. 😉',[name for name in ss.names], index = None, key = "myname")
    if my_name:
        id = ss.names.index(my_name)
        # Read of voice_message(id)
        if ss.uploaded_voices[id] is not None:
            audio_bytes = ss.uploaded_voices[id].read()
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.error("Please upload a voice file.")
        # Check of first selection
        if my_name != ss.selected_speaker:
            ss.selected_speaker = my_name
            ss.prompt_name = f"My name is {my_name}."
    # Select one of topics
    selected_topic = st.radio('Select topic. 😉',[topic for topic in ss.topics], index = None, key = "topic")
    if selected_topic:
        id = ss.topics.index(selected_topic)
        st.markdown(f"<span style='color: blue;'>{ss.dialogues[id]}</span>", unsafe_allow_html=True)
        if id == 0: # Additional information uploded is used in topic(id=0).
            if ss.uploaded_txt is not None:
                information = ''
                for line in ss.uploaded_txt:
                    # Convert bytes to str
                    information += line.decode('utf-8')
                assist_content1 = information.replace("\n", "")
            # Define role of ChatGPT
            assist_content2 = ss.assists[id]
        else:
            assist_content1 = ss.assists[id]

    if assist_content1:
        ss.messages.append({"role": "assistant", "content": assist_content1})
    if assist_content2:
        ss.messages.append({"role": "assistant", "content": assist_content2})

# Main page
if ss.image is not None:
    st.image(ss.image)
# Select voice
if ss.voice_gender == "Woman":
    selected_voice = 'nova'
elif ss.voice_gender == "Man":
    selected_voice = 'alloy'
# Write message history
if len(ss.messages):
    message = ss.messages[-1]
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input( "Input sentence like the examples on the lower left."):
    ss.messages.append({"role": "user", "content": ss.prompt_name + prompt})

    with st.chat_message("user"):
        st.markdown(ss.prompt_name + prompt)

    ss.prompt_name = ""   # Reset after usage

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in ss.messages], stream=True):
            if response.choices[0].delta.content is not None:
                full_response += response.choices[0].delta.content
            else:
                full_response += ""
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Make voices: From text to voice file
    response = openai.audio.speech.create(
        model="tts-1",
        voice = selected_voice,
        input= full_response
    )
    audio_bytes = response.content
    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")

    # Long responses are't appended for capacity of ss.messages
    if len(full_response) < MAX_TEXT:
        ss.messages.append({"role": "assistant", "content": full_response})
    if len(ss.messages) > MAX_MESSAGE:
            del ss.messages[0]
