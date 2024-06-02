import datetime
import os
import shutil
import sys
from tkinter import PhotoImage
import customtkinter as ctk
import model
import logging



def config(appearance: str = 'system', color_scheme :str = 'dark-blue', stayOnTop : bool = True, width : int = 250, height : int = 280, resizable : bool = False):
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    icon_path = model.resource_path(os.path.join('icons', 'icon_leevai_logo_circle.ico'))
    
    ctk.set_appearance_mode(appearance)
    ctk.set_default_color_theme(color_scheme)

    root = ctk.CTk()
    root.iconbitmap(icon_path)
    if stayOnTop:
        root.call('wm', 'attributes', '.', '-topmost', '1')

    ws = root.winfo_screenwidth()  # width of the screen

    root.title('Note Taker')
    root.geometry('%dx%d+%d+%d' % (width, height, ws - (width * 1.5), 30))
    if not resizable:
        root.resizable(width=False, height=False)
    return root
    
def set_main_image(frame, path: str):
    img = PhotoImage(file=path)
    ctk.CTkLabel(master=frame, image=img, text="").pack(pady=10, padx=10)

def set_bottom_label(frame, text: str = ''):
    label = ctk.CTkLabel(master=frame, text=text, font=('Roboto', 18))
    label.pack(pady=12, padx=10)
    return label

def update_bottom_label(label, text: str = ''):
    label.configure(text=text)

def prepare(just_began):

    if just_began:
        model.tts('Everything has been setup. Let\'s begin')
    else:
        model.tts('What would you like me to look at next?')

  #  root.after(100, prepare, root, frame, img_path, folder_path, just_began)


def listen(audio_file):
    model.record_audio(audio_file)
  #  root.after(100, listen, root, label, audio_file)

def transcribe(audio_file):
    user_input = model.transcribe(audio_file)
    print('Query: ', user_input)
    logging.info(f'Query: {user_input}')
    os.remove(audio_file)  
  #  root.after(100, transcribe, root, label, audio_file)
    return user_input

def termination_handle(user_input):
    response = model.gpt_handle(f'{user_input}. \nThe above statement is a user prompt. If you think the prompt is suggesting the program must be exited or that they have no further queries respond with QUIT else respond with CONTINUE. Only respond with one word, either QUIT or CONTINUE based on the above mentioned condition and nothing else')
    print(f'response: {response}')
    logging.info(f'Interpreted response (QUIT command): {response}')
    if 'QUIT' in response.upper():
        
    #    root.after(100, termination_handle, root, label, user_input)
        return True
    else:
        return False
    
def take_screenshot(folder_path, user_input):
    feedback = model.gpt_handle(f"User query: {user_input}. \n Also note that you are part of a program that allows you to look at the screenshot of the screen corresponding to the user query and the screenshot is taken automatically during the query.\nAcknowledge the user's query and inform them briefly on next steps which will involving you analyzing the image and taking notes")
    model.tts(feedback)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_pth = model.resource_path(os.path.join(folder_path, f"screenshot_{timestamp}.png"))

    
    model.take_screenshot(screenshot_pth)
   # root.after(100, take_screenshot, root, user_input)
    return screenshot_pth

def analyze_screenshot(screenshot_pth, user_input):
    
    screenshot_text = model.analyze_image(screenshot_pth, user_input)
    print(screenshot_text)
    logging.info(f'Screenshot content: \n{screenshot_text}')
   # root.after(100, analyze_screenshot, root, label, screenshot_pth, user_input)
    return screenshot_text

def screenshot_response(screenshot_pth, screenshot_text, user_input):
    notes = model.gpt_handle(f'Text from screenshot : {screenshot_text}.\nWrite down concise and structured notes for the text above. Make customizations to your note taking style based on the user\'s query as follows: {user_input}.')

    if notes.split().pop(0) == 'YES':
        model.tts('Note that I will be ignoring the terminal on the screen as it is used to control the program. If you would like me to include it, please specify next time.')

    if not os.path.exists(model.resource_path('notes')):
        os.makedirs(model.resource_path('notes'))
        # save notes
    notes_path = model.resource_path(os.path.join('notes', 'notes.txt'))
    with open(notes_path, 'a') as notes_file:
        notes_file.write(notes + "\n")
        
        shutil.copyfile(notes_path, model.resource_path(os.path.join("notes", "notes.md")))
        model.tts('Cleaning up your notes for readability... Almost there')

    os.remove(screenshot_pth)
   # root.after(100, screenshot_response, root, label, screenshot_pth, screenshot_text)  
    return notes

def final_response(notes):
    feedback = model.gpt_handle(f'Notes : {notes}\n Those are the notes you wrote down, tell the user in 50 words or less about the notes taken.Keep it brief (NO MORE THAN 50 WORDS)')
    
    model.tts(feedback)
   # root.after(100, final_response, root, label, notes)  


def main():
    root = config()

    audio_file_pth = model.resource_path('temp_recording.wav')
    img_path = model.resource_path(os.path.join('icons', 'leevai_logo_circle.png'))
    folder_path = model.resource_path('images')
    os.makedirs(folder_path, exist_ok=True)
    just_began = True

    logging.info(f'Looking for AUDIO_FILE at {audio_file_pth} \nLooking for MAIN_IMAGE at: {img_path} \nLooking for SCREENSHOT_STORAGE at: {folder_path} \n')

    # Create a frame
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    set_main_image(frame, img_path)
    label = set_bottom_label(frame, 'Getting ready')
    root.update()

    prepare(just_began=just_began)
    
    update_bottom_label(label, 'Listening...')
    root.update()
    listen(audio_file=audio_file_pth)
    
    update_bottom_label(label, 'Thinking...')
    root.update()
    user_input = transcribe(audio_file=audio_file_pth)
    
    is_quit = termination_handle(user_input=user_input)

    if is_quit:
        update_bottom_label(label, 'Finished')
        root.update()
        return 
    
    update_bottom_label(label, 'Let me take a look')
    root.update()
    screenshot_pth = take_screenshot(folder_path=folder_path, user_input=user_input)
    
    update_bottom_label(label, 'Analyzing...')
    root.update()
    screenshot_text = analyze_screenshot(screenshot_pth=screenshot_pth, user_input=user_input)
    
    #in case of no text on screen
    if screenshot_text is None:
        update_bottom_label(label, 'No text on screen')
        root.update()
        model.tts('Sorry. I didn\'t see any text on the screen. Please try again')
        print('Could not find any text')
        logging.info('Screenshot did not contain text. No text was found in the screenshot.')
        sys.exit()
    

    update_bottom_label(label, "Formatting...")
    root.update()
    notes = screenshot_response(screenshot_pth=screenshot_pth, screenshot_text=screenshot_text, user_input=user_input)
    
    update_bottom_label(label, 'Done')
    root.update()
    final_response(notes=notes)

    
    # Start the main event loop
    just_began = False
    root.mainloop()

if __name__ == '__main__':
    main()
