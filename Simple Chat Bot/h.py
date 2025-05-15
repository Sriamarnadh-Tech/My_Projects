from tkinter import *
from tkinter import simpledialog, filedialog
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from cleaner import clean_corpus
import cv2
import pytesseract
from PIL import Image,ImageTk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CORPUS_FILE = "chat.txt"

chatbot = ChatBot("Chatpot")
trainer = ListTrainer(chatbot)
cleaned_corpus = clean_corpus(CORPUS_FILE)
trainer.train(cleaned_corpus)
trainer.train(["hi","hello","hllo","hey, what's up"])
trainer.train(["what is your name","my name is AVS"])
trainer.train(["what should i call you","you can call me AVS"])
trainer.train(["who are you","i am AVS Chat bot"])
trainer.train(["who created  you","the great ,greater,greatest brilliant fellow sri sri sri amarnadh created me."])
trainer.train(["who made you","the great ,greater,greatest brilliant fellow sri sri sri amarnadh created me and still under development"])
trainer.train(["""what are the libraries made you""","""so many libraries and all ae used by python:
 \nOpenCV (cv2),
 \nTkinter,
 \nPillow (PIL),
 \nChatterbot,
 \nSumy,"""])
trainer.train(["how are you feeling","i am feeling very tensed !!🥵😥😥"])
trainer.train(["i want to give you a rating", "I'm glad you asked How much would you rate me?"])
trainer.train(["who is vyshnavi?","she is a patient escaped from vizag erragadda hospital.!!!!,can be very dangerous because not fully cured."])
trainer.train([""])

exit_conditions = {":q", "quit", "exit", "bye", "goodbye", "see you"}
operators = {"+", "-", "*", "/", "^", "%"}

def ask_for_rating():
    rating = simpledialog.askinteger("Rating", "How much would you rate me? (Enter a number from 1 to 5)", parent=root, minvalue=1, maxvalue=5)
    return rating

def evaluate_math_expression(expression):
    """Evaluate a mathematical expression and return the result."""
    try:
        return eval(expression)
    except Exception:
        return None

def send_message(event=None):
    query = entry.get()
    entry.delete(0, END)

    if query.lower() in exit_conditions:
        root.quit()
        return

    if any(op in query for op in operators):
        result = evaluate_math_expression(query)
        if result is not None:
            messages.insert(END, f"🪴 The answer for {query} is {result}")
            with open("chat_history.txt", "a") as file:
                file.write(f"User: {query}\nAVS: {result}\n\n")
            return

    if query.lower() == "i want to give you a rating":
        user_rating = ask_for_rating()
        if user_rating:
            messages.insert(END, f"🌟 Thank you sir for your rating of {user_rating} out of 5!!!😅😅😁")
    else:
        response = chatbot.get_response(query)
        messages.insert(END, f"🪴 {response}")
        with open("chat_history.txt", "a") as file:
            file.write(f"User: {query}\nAVS: {response}\n\n")

def new_chat():
    messages.delete(0, END)
    chatbot.storage.drop()
    trainer.train(cleaned_corpus)
    trainer.train(["hi", "hey, what's up"])
    trainer.train(["what is your name", "I am AVS."])
    entry.focus_set()

def open_library():
    
    library_window = Toplevel(root)
    library_window.title("Chat Library")

    library_listbox = Listbox(library_window, width=80, height=20, font=("Arial", 12))
    library_listbox.pack(padx=10, pady=10)

    with open("chat_history.txt", "r") as file:
        for chat in file.readlines():
            library_listbox.insert(END, chat)

    close_button = Button(library_window, text="Close", command=library_window.destroy, bg="black", fg="white", font=("Arial", 12))
    close_button.pack(pady=10)

def upload_image():
    
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*")])

    if file_path:
        
        image = cv2.imread(file_path)

        if image is not None:
            return image
        else:
            return None
    else:
        return None
    
def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3) 
    summary_text = "\n".join([str(sentence) for sentence in summary])
    return summary_text

def upload_and_summarize():
    uploaded_image = upload_image()

    if uploaded_image is not None:
        extracted_text = pytesseract.image_to_string(uploaded_image)

        summary = summarize_text(extracted_text)
        messages.insert(END, f"🪴 Image Summary: {summary}")

root = Tk()
root.title("AVS Chat Bot")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

bg_image = Image.open("t3.jpg")
bg_photo = ImageTk.PhotoImage(bg_image)

label = Label(root, image=bg_photo)
label.place( relwidth=1, relheight=1,)

navbar = Frame(root, bg="orange", height=100)
navbar.pack(fill=X)

label = Label(navbar, text="AVS Chat Bot", fg="black", bg="orange", font=("Arial", 16, "bold"))
label.pack(side=LEFT, padx=10, pady=10)

new_chat_button = Button(navbar, text="New Chat", command=new_chat, bg="black", fg="white", font=("Arial", 12))
new_chat_button.pack(side=LEFT, padx=10, pady=10)

library_button = Button(navbar, text="Library", command=open_library, bg="black", fg="white", font=("Arial", 12))
library_button.pack(side=LEFT, padx=10, pady=10)

camera_button = Button(navbar, text="📸", command=upload_and_summarize, bg="black", fg="white", font=("Arial", 12))
camera_button.pack(side=RIGHT, padx=10, pady=10)

scrollbar = Scrollbar(root, orient=HORIZONTAL)
scrollbar.pack(side=BOTTOM, fill=X)

messages = Listbox(root, bg="lightgreen", fg="black", font=("Arial", 15))
messages.pack(expand=True, fill=BOTH, padx=5, pady=5)


entry_frame = Frame(root)
entry_frame.pack(expand=True,fill=X, padx=10, pady=10)

entry = Entry(entry_frame, bg="skyblue", fg="black", font=("Arial", 12), relief="ridge")
entry.pack(side=LEFT, expand=True, fill=BOTH)
entry.bind("<Return>", send_message)

send_button = Button(entry_frame, text="⬆", command=send_message, bg="black", fg="white", font=("Arial", 12))
send_button.pack(side=LEFT, padx=5)

root.mainloop()