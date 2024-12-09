import json
import os
import tempfile

import string
import spacy
import speech_recognition as sr
from gtts import gTTS
from quart import Quart, request
from dataModels import QuestionObj

app = Quart(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "Interview Automate Python Backend Server is running!"

def convert_all_question_tts(selectedDomain):
    with open(f"C:\\Users\\Lenovo\\AppData\\Local\\Temp\\interAutomateFiles\\questions\\{selectedDomain}_questions.json",
              encoding='utf-8') as file:
        questions = json.load(file)
    questions_list = []
    for item in questions["questions"]:
        question_object = QuestionObj(item['id'], item['question'])
        questions_list.append(question_object)
    print("Implementing Text to Speech on Questions individually.")
    for question in questions_list:
        print(str(question.question))
        convert_to_mp3(question.question,
                       f"C:\\Users\\Lenovo\\AppData\\Local\\Temp\\interAutomateFiles\\questions\\{selectedDomain}audio_questions\\question{question.id}.mp3")
    print("Done Converting Text to Speech")

def convert_to_mp3(text, path):
    tts = gTTS(text, lang='en')
    output_file = path
    tts.save(output_file)

@app.route('/init', methods=['POST'])
async def handle_post_request():
    data = await request.get_json()
    #print("Data:" + str(data))
    selectedDomain = data.get("selectedDomain", "")  # Assuming 'selectedDomain' is part of the request data
    convert_all_question_tts(selectedDomain)
    response_data = {"convertedAllQuestions": "yes"}
    response = app.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )
    return response

async def convert_speech_to_text(audio_file_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Error occurred during speech recognition: {e}"

@app.route('/getSpeechToText', methods=['POST'])
async def get_speech_to_text():
    data = await request.get_json()
    print("Data:" + str(data))
    converted_text = await convert_speech_to_text(data['audioFilePath'])
    print("---------------------------")
    print("Converted Text : " + str(converted_text))
    print("---------------------------")

    resp = {"convertedText": converted_text}
    response = app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

def calculate_similarity(text1, text2):
    nlp = spacy.load("en_core_web_md")
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    similarity_score = doc1.similarity(doc2)
    return similarity_score

def get_answer_from_json(id, data):
    for answer in data["answers"]:
        print("Iterating at:"+str(answer))
        if answer["id"] == id:
            return answer['answer']
    return "Answer for id not found"

@app.route('/getFinalResults', methods=['POST'])
async def get_final_results():
    data = await request.get_json()
    print("Data:" + str(data))
    selectedDomain = data.get("selectedDomain", "")
    questions_list = data["questionsList"]
    print("questionsList", questions_list)

    temp_path = tempfile.gettempdir()
    print("Temp File Path" + temp_path)
    submitted_answers_dir = os.path.join(temp_path, "interAutomateFiles", "answers", "Submitted_answers")
    answers_json = os.path.join(temp_path, "interAutomateFiles", "answers", f"{selectedDomain}_answers.json")
    print(answers_json)
    with open(answers_json, encoding="utf-8") as f:
        answer_data = json.load(f)
    print(answer_data)

    submitted_answers_list = os.listdir(submitted_answers_dir)
    print("Submitted Answers List length:" + str(len(submitted_answers_list)))

    final_score = 0

    for file in submitted_answers_list:
        full_file_path = os.path.join(submitted_answers_dir, file)
        print(file)
        converted_text = await convert_speech_to_text(full_file_path)
        print("CONVERTED TEXT =>" + str(converted_text))
        file_name = str(file)
        id = file_name.split(".")[0]
        print("working on" + str(id))
        answer_text = get_answer_from_json(id, answer_data)
        print("Answer =>" + answer_text)
        current_score = calculate_similarity(converted_text, answer_text)
        print("currentScore:", current_score)
        final_score += current_score
    
    final_score /= len(submitted_answers_list)
    print("------------------------------")
    print("Final Score:", final_score)

    candidate_selected = final_score >= 0.50  # 50% overall accuracy threshold
    result = {"finalScore": final_score, "candidateSelected": candidate_selected}

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '_main_':
    app.run(debug=True)
# CODE FOR Speechto text


# import spacy


# audioFilePath = "C:\\Users\\shubh\\AppData\\Local\\Temp\\test.flac"


# Specify the path to your WAV file
# result = convert_speech_to_text(audioFilePath)
# print("Speech to text:")
# print(result)



# # Example usage
# # text1 = "I like cats"
# # text2 = "I love felines"
# # similarity = calculate_similarity(text1, text2)
# # print("Similarity score:", similarity)




