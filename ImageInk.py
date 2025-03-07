import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pytesseract
import pyperclip
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

languages = {
    "English": "eng",
    "Myanmar": "mya"
}


def change_language(event=None):
    messagebox.showinfo("Language Changed", f"Language changed to {selectedLanguage.get()}")


def openImage():
    filepath = filedialog.askopenfilename(filetypes=[('Image Files', '*.png *.jpg *.jpeg')])
    if filepath:
        display_image(filepath)
        extracted_text = extract_text(filepath)
        update_text_output(extracted_text)


def display_image(filepath):
    try:
        image = Image.open(filepath)
        image.thumbnail((400, 300))  # Resize image
        img_tk = ImageTk.PhotoImage(image)
        image_label.configure(image=img_tk)
        image_label.image = img_tk
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")


def preprocess_image(image):
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    image = image.filter(ImageFilter.GaussianBlur(radius=1))
    image = image.point(lambda p: p > 128 and 255)

    return image


def extract_text(filepath):
    try:
        selected_lang = languages[selectedLanguage.get()]
        image = Image.open(filepath)

        processed_image = preprocess_image(image)

        text = pytesseract.image_to_string(processed_image, lang=selected_lang)
        return text.strip()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract text: {e}")
        return ""


def update_text_output(text):
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, text)


def copyText():
    text_to_copy = text_output.get(1.0, tk.END).strip()
    if text_to_copy:
        pyperclip.copy(text_to_copy)
        messagebox.showinfo("Copied", "Text copied to clipboard!")
    else:
        messagebox.showwarning("Empty Text", "There is no text to copy.")


def capture_image():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Real-Time Scanner - Press SPACE to Capture", frame)
        key = cv2.waitKey(1)
        if key == 32:  # Press SPACE to capture
            cv2.imwrite("captured_image.png", frame)
            cap.release()
            cv2.destroyAllWindows()
            process_captured_image("captured_image.png")
            break
        elif key == 27:  # Press ESC to exit
            cap.release()
            cv2.destroyAllWindows()
            break


def process_captured_image(filepath):
    display_image(filepath)
    extracted_text = extract_text(filepath)
    update_text_output(extracted_text)

root = tk.Tk()
root.configure(background="#FEF9E1")
root.title("ImageInk")
root.geometry("700x500")
root.resizable(True, True)

custom_font = ("Helvetica", 12)

selectedLanguage = tk.StringVar(value="English")
tk.Label(root, text="Select Language:", font=custom_font, bg="#FEF9E1", fg="black").grid(row=0, column=0, padx=10,
                                                                                         pady=10, sticky="w")
language_dropdown = ttk.Combobox(root, textvariable=selectedLanguage, values=list(languages.keys()), state="readonly",
                                 font=custom_font)
language_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
language_dropdown.bind("<<ComboboxSelected>>", change_language)

tk.Button(root, text="Open Image", command=openImage, font=custom_font, bg="#C7B491", fg="#344351").grid(row=1,
                                                                                                         column=0,
                                                                                                         padx=10,
                                                                                                         pady=10,
                                                                                                         sticky="ew")
tk.Button(root, text="Real-Time Scan", command=capture_image, font=custom_font, bg="#C7B491", fg="#344351").grid(row=1,
                                                                                                                 column=1,
                                                                                                                 padx=10,
                                                                                                                 pady=10,
                                                                                                                 sticky="ew")

image_label = tk.Label(root, bg="#FEF9E1")
image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

text_output = tk.Text(root, height=10, width=50, font=custom_font)
text_output.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Button(root, text="Copy to Clipboard", command=copyText, font=custom_font, bg="#C1C5CB", fg="black").grid(row=4,
                                                                                                             column=0,
                                                                                                             columnspan=2,
                                                                                                             padx=10,
                                                                                                             pady=10,
                                                                                                             sticky="ew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)

root.mainloop()