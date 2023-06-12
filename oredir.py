import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse, urlunparse
import requests
import threading

def modify_url(url):
    parsed_url = urlparse(url)
    modified_params = []
    params = parsed_url.query.split('&')

    for param in params:
        parts = param.split('=')
        if len(parts) == 2:
            key, value = parts
            modified_params.append(f"{key}=https://evil.com")

    modified_url = urlunparse(parsed_url._replace(query='&'.join(modified_params)))
    return modified_url

def modify_urls():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as file:
            urls = file.readlines()

        root = tk.Tk()
        root.title("Open Redirect Tester")
        root.geometry("800x400")

        title_label = tk.Label(root, text="Open Redirect Tester", font=("Arial", 16, "bold"))
        title_label = tk.Label(root, text="Focus On red color output", font=("Arial", 10, "bold"))
        title_label.pack(pady=10)

        output_frame = tk.Frame(root, bg="black")
        output_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(output_frame, width=400, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_frame = tk.Frame(output_frame, width=400, bg="black")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        left_text = tk.Text(left_frame, yscrollcommand=scrollbar.set, bg="black", fg="white", font=("Arial", 12))
        left_text.pack(fill=tk.BOTH, expand=True)

        right_text = tk.Text(right_frame, yscrollcommand=scrollbar.set, bg="black", fg="white", font=("Arial", 12))
        right_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=left_text.yview)

        def process_urls(index):
            if index >= len(urls):
                # Notify completion with a popup box
                messagebox.showinfo("Complete", "URL processing completed.")
                return

            url = urls[index]
            modified_url = modify_url(url.strip())

            # Use threading to perform the request in the background
            thread = threading.Thread(target=send_request, args=(modified_url, left_text, right_text))
            thread.start()

            # Call process_urls again with the next index
            root.after(10, process_urls, index + 1)

        def send_request(url, left_text, right_text):
            response = requests.get(url)
            content_length = response.headers.get('Content-Length')
            status_code = response.status_code
            html_title = get_html_title(response.text)

            # Update the text widgets from the main thread using the `after()` method
            if status_code == 200:
                root.after(0, update_output, left_text, url, content_length, status_code, html_title)
            else:
                root.after(0, update_output, right_text, url, content_length, status_code, html_title)

        def get_html_title(html):
            # Use a simple regular expression to extract the HTML title
            import re
            match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            if match:
                return match.group(1)
            else:
                return "N/A"

        def update_output(text_widget, url, content_length, status_code, html_title):
            text_widget.insert(tk.END, f"{url}\n")
            text_widget.insert(tk.END, f"Content Length: {content_length}\n")
            text_widget.insert(tk.END, f"Status Code: {status_code}\n")
            text_widget.insert(tk.END, f"Title: {html_title}\n")
            text_widget.insert(tk.END, f"\n{'#' * 15}\n\n")

            if html_title == "Evil.Com - We get it...Daily.":
                text_widget.tag_configure("red", foreground="red")
                text_widget.insert(tk.END, "Here may be an open redirect. Please check manually.\n", "red")
            else:
                text_widget.tag_configure("green", foreground="green")
                text_widget.insert(tk.END, "Here may not be an open redirect, but please check manually.\n", "green")

        # Start processing URLs from index 0
        process_urls(0)

        footer_label = tk.Label(root, text="Copyright - Dipen_Luitel\nWebsite: dipenluitel30.com.np")
        footer_label.pack(side=tk.BOTTOM, pady=10)

        root.mainloop()

def open_file():
    threading_enabled = threading_value.get()
    if threading_enabled and threading_value.get() <= 50:
        threading.Thread(target=modify_urls).start()
    elif threading_enabled and threading_value.get() > 50:
        messagebox.showerror("Error", "Maximum threading value is 50.")
    else:
        modify_urls()

root = tk.Tk()
root.title("Open Redirect Tester")
root.geometry("300x150")

title_label = tk.Label(root, text="Open Redirect Tester", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

threading_value = tk.IntVar()
threading_checkbutton = tk.Checkbutton(root, text="Enable Threading (Max 50)", variable=threading_value)
threading_checkbutton.pack()

open_file_button = tk.Button(root, text="Open File Containing URLs", command=open_file)
open_file_button.pack()

root.mainloop()
