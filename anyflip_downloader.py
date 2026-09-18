import os
import sys
import re
import time
import random
import tempfile
import threading
import platform
import subprocess
import requests
import img2pdf
import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from PIL import Image
import fitz  # PyMuPDF

class AnyFlipDownloaderApp(ctk.CTk):
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("AnyFlip PDF Downloader & Compressor")
        self.geometry("700x550")
        self.resizable(False, False)
        
        try:
            self.iconbitmap(self.resource_path("app_icon.ico"))
        except:
            pass
        
        # Modern Dark Mode UI
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State variables
        self.is_downloading = False
        self.is_compressing = False
        self.est_size = 0
        self.total_pages = 0
        
        self.setup_ui()

    def setup_ui(self):
        # Application Title
        self.title_label = ctk.CTkLabel(self, text="AnyFlip PDF Toolkit", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(15, 5))
        
        # Footer
        self.footer_label = ctk.CTkLabel(self, text="© 2026 PM.Taratorn Hongcharoen | Licensed under MIT", font=ctk.CTkFont(size=12), text_color="gray")
        self.footer_label.pack(side="bottom", pady=5)
        
        self.tabview = ctk.CTkTabview(self, width=650, height=450)
        self.tabview.pack(padx=20, pady=10)
        
        self.tab_down = self.tabview.add("AnyFlip Downloader")
        self.tab_comp = self.tabview.add("PDF Compressor")
        
        self.setup_downloader_tab()
        self.setup_compressor_tab()
        
    def setup_downloader_tab(self):
        # URL Input Section
        self.url_frame = ctk.CTkFrame(self.tab_down, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=20, pady=5)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="AnyFlip URL:", font=ctk.CTkFont(size=14))
        self.url_label.pack(anchor="w")
        
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="https://online.anyflip.com/xxxxx/xxxx/mobile/", height=35)
        self.url_entry.pack(fill="x", pady=(5, 0))
        
        # Quality & Estimation Section
        self.qual_est_frame = ctk.CTkFrame(self.tab_down, fg_color="transparent")
        self.qual_est_frame.pack(fill="x", padx=20, pady=10)
        
        self.qual_label = ctk.CTkLabel(self.qual_est_frame, text="Quality:", font=ctk.CTkFont(size=14))
        self.qual_label.pack(side="left")
        
        self.qual_var = ctk.StringVar(value="Lossless")
        self.qual_dropdown = ctk.CTkOptionMenu(self.qual_est_frame, variable=self.qual_var, 
                                               values=["Lossless", "High", "Medium", "Low"], width=100)
        self.qual_dropdown.pack(side="left", padx=(10, 20))
        
        self.est_btn = ctk.CTkButton(self.qual_est_frame, text="Check Size", width=100, command=self.check_size)
        self.est_btn.pack(side="left")
        
        self.est_label = ctk.CTkLabel(self.qual_est_frame, text="Estimated Size: Unknown", font=ctk.CTkFont(size=14, weight="bold"))
        self.est_label.pack(side="right")
        
        # Save Location Section
        self.save_frame = ctk.CTkFrame(self.tab_down, fg_color="transparent")
        self.save_frame.pack(fill="x", padx=20, pady=5)
        
        self.save_label = ctk.CTkLabel(self.save_frame, text="Save To:", font=ctk.CTkFont(size=14))
        self.save_label.pack(anchor="w")
        
        self.save_path_var = ctk.StringVar()
        self.save_entry = ctk.CTkEntry(self.save_frame, textvariable=self.save_path_var, state="readonly", height=35)
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(self.save_frame, text="Browse...", width=100, height=35, command=self.browse_location_down)
        self.browse_btn.pack(side="right")
        
        # Status and Progress Bar
        self.status_label_down = ctk.CTkLabel(self.tab_down, text="Ready", font=ctk.CTkFont(size=14))
        self.status_label_down.pack(pady=(15, 5))
        
        self.progress_bar_down = ctk.CTkProgressBar(self.tab_down, mode="indeterminate", width=400)
        self.progress_bar_down.pack(pady=(0, 15))
        self.progress_bar_down.set(0)
        
        # Start Download Button
        self.start_btn = ctk.CTkButton(self.tab_down, text="Start Download", font=ctk.CTkFont(size=16, weight="bold"), 
                                       height=40, fg_color="#107C41", hover_color="#0b5c30", command=self.start_download)
        self.start_btn.pack(pady=5)

    def setup_compressor_tab(self):
        # Input PDF Section
        self.in_pdf_frame = ctk.CTkFrame(self.tab_comp, fg_color="transparent")
        self.in_pdf_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.in_pdf_label = ctk.CTkLabel(self.in_pdf_frame, text="Select PDF to Compress:", font=ctk.CTkFont(size=14))
        self.in_pdf_label.pack(anchor="w")
        
        self.in_pdf_var = ctk.StringVar()
        self.in_pdf_entry = ctk.CTkEntry(self.in_pdf_frame, textvariable=self.in_pdf_var, state="readonly", height=35)
        self.in_pdf_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_in_btn = ctk.CTkButton(self.in_pdf_frame, text="Browse...", width=100, height=35, command=self.browse_input_pdf)
        self.browse_in_btn.pack(side="right")
        
        # Quality Section
        self.comp_qual_frame = ctk.CTkFrame(self.tab_comp, fg_color="transparent")
        self.comp_qual_frame.pack(fill="x", padx=20, pady=10)
        
        self.comp_qual_label = ctk.CTkLabel(self.comp_qual_frame, text="Target Quality:", font=ctk.CTkFont(size=14))
        self.comp_qual_label.pack(side="left")
        
        self.comp_qual_var = ctk.StringVar(value="Medium")
        self.comp_qual_dropdown = ctk.CTkOptionMenu(self.comp_qual_frame, variable=self.comp_qual_var, 
                                                    values=["High", "Medium", "Low"], width=120)
        self.comp_qual_dropdown.pack(side="left", padx=10)
        
        # Warning label
        self.warn_label = ctk.CTkLabel(self.tab_comp, text="Note: Text-based PDFs will be converted to images and lose text searchability.", 
                                       font=ctk.CTkFont(size=12, slant="italic"), text_color="#FFA500")
        self.warn_label.pack(pady=(10, 20))
        
        # Status and Progress Bar
        self.status_label_comp = ctk.CTkLabel(self.tab_comp, text="Ready", font=ctk.CTkFont(size=14))
        self.status_label_comp.pack(pady=(15, 5))
        
        self.progress_bar_comp = ctk.CTkProgressBar(self.tab_comp, mode="indeterminate", width=400)
        self.progress_bar_comp.pack(pady=(0, 15))
        self.progress_bar_comp.set(0)
        
        # Start Compress Button
        self.comp_btn = ctk.CTkButton(self.tab_comp, text="Compress PDF", font=ctk.CTkFont(size=16, weight="bold"), 
                                       height=40, fg_color="#D83B01", hover_color="#A80000", command=self.start_compression)
        self.comp_btn.pack(pady=5)

    def browse_location_down(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Select Save Location"
        )
        if filepath:
            self.save_path_var.set(filepath)

    def browse_input_pdf(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PDF Documents", "*.pdf")],
            title="Select PDF to Compress"
        )
        if filepath:
            self.in_pdf_var.set(filepath)

    def update_status_safe_down(self, text):
        self.after(0, lambda: self.status_label_down.configure(text=text))

    def update_status_safe_comp(self, text):
        self.after(0, lambda: self.status_label_comp.configure(text=text))

    def show_error_safe(self, title, message):
        self.after(0, lambda: messagebox.showerror(title, message))
        self.after(0, self.reset_ui)

    def show_success_safe(self, filepath):
        self.after(0, self.reset_ui)
        self.after(0, lambda: self.status_label_down.configure(text="Download Complete!"))
        self.after(0, lambda: self.status_label_comp.configure(text="Compression Complete!"))
        
        def ask_open():
            result = messagebox.askyesno(
                "Success", 
                f"Operation completed successfully!\n\nLocation: {filepath}\n\nDo you want to open the containing folder?"
            )
            if result:
                self.open_folder(filepath)
                
        self.after(0, ask_open)

    def reset_ui(self):
        self.is_downloading = False
        self.is_compressing = False
        
        self.url_entry.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.start_btn.configure(state="normal", text="Start Download")
        self.est_btn.configure(state="normal")
        self.qual_dropdown.configure(state="normal")
        self.progress_bar_down.stop()
        self.progress_bar_down.set(0)
        
        self.in_pdf_entry.configure(state="normal")
        self.browse_in_btn.configure(state="normal")
        self.comp_qual_dropdown.configure(state="normal")
        self.comp_btn.configure(state="normal", text="Compress PDF")
        self.progress_bar_comp.stop()
        self.progress_bar_comp.set(0)

    def set_downloading_state(self):
        self.is_downloading = True
        self.url_entry.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.est_btn.configure(state="disabled")
        self.qual_dropdown.configure(state="disabled")
        self.start_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar_down.start()
        
    def set_compressing_state(self):
        self.is_compressing = True
        self.in_pdf_entry.configure(state="disabled")
        self.browse_in_btn.configure(state="disabled")
        self.comp_qual_dropdown.configure(state="disabled")
        self.comp_btn.configure(state="disabled", text="Compressing...")
        self.progress_bar_comp.start()

    def open_folder(self, filepath):
        folder = os.path.dirname(filepath)
        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def parse_anyflip_url(self, url):
        parsed = urlparse(url)
        if "anyflip.com" not in parsed.netloc:
            return None
        path = parsed.path
        path = re.sub(r'(mobile/index\.html|mobile/|index\.html)$', '', path, flags=re.IGNORECASE)
        if not path.endswith('/'):
            path += '/'
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    def check_size(self):
        if self.is_downloading or self.is_compressing:
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter an AnyFlip URL.")
            return
            
        base_url = self.parse_anyflip_url(url)
        if not base_url:
            messagebox.showwarning("Input Error", "Invalid URL. It must be a valid anyflip.com domain.")
            return

        self.est_btn.configure(state="disabled", text="Checking...")
        self.est_label.configure(text="Checking size...")
        
        thread = threading.Thread(target=self.size_worker, args=(base_url,), daemon=True)
        thread.start()

    def size_worker(self, base_url):
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Referer": base_url
        })
        
        page_count = 0
        
        # 1. Fetch config.js for total pages
        try:
            config_url = f"{base_url}mobile/javascript/config.js"
            res = session.get(config_url, timeout=10)
            if res.status_code == 200:
                match = re.search(r'"pageCount":\s*(\d+)', res.text)
                if match:
                    page_count = int(match.group(1))
            if page_count == 0:
                config_url_alt = f"{base_url}javascript/config.js"
                res = session.get(config_url_alt, timeout=10)
                if res.status_code == 200:
                    match = re.search(r'"pageCount":\s*(\d+)', res.text)
                    if match:
                        page_count = int(match.group(1))
        except Exception:
            pass

        if page_count == 0:
            self.after(0, lambda: self.est_label.configure(text="Size: Unknown (Cannot read config)"))
            self.after(0, lambda: self.est_btn.configure(state="normal", text="Check Size"))
            return

        # 2. Get HEAD of first image
        possible_paths = [
            "files/large/1.jpg", "files/large/1.webp",
            "files/mobile/1.jpg", "files/mobile/1.webp"
        ]
        
        img_size = 0
        for path in possible_paths:
            try:
                head_res = session.head(f"{base_url}{path}", timeout=10)
                if head_res.status_code == 200 and 'content-length' in head_res.headers:
                    img_size = int(head_res.headers['content-length'])
                    break
            except Exception:
                continue
                
        if img_size == 0:
            self.after(0, lambda: self.est_label.configure(text="Size: Unknown (Cannot fetch image)"))
            self.after(0, lambda: self.est_btn.configure(state="normal", text="Check Size"))
            return
            
        # Calculate size in MB
        lossless_mb = (img_size * page_count) / (1024 * 1024)
        
        # Estimate based on selected quality
        qual = self.qual_var.get()
        if qual == "High":
            est_mb = lossless_mb * 0.7
        elif qual == "Medium":
            est_mb = lossless_mb * 0.4
        elif qual == "Low":
            est_mb = lossless_mb * 0.2
        else:
            est_mb = lossless_mb
            
        self.after(0, lambda: self.est_label.configure(text=f"Estimated Size: ~{est_mb:.1f} MB"))
        self.after(0, lambda: self.est_btn.configure(state="normal", text="Check Size"))

    def start_download(self):
        if self.is_downloading or self.is_compressing:
            return
            
        url = self.url_entry.get().strip()
        save_path = self.save_path_var.get().strip()
        quality = self.qual_var.get()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter an AnyFlip URL.")
            return
            
        base_url = self.parse_anyflip_url(url)
        if not base_url:
            messagebox.showwarning("Input Error", "Invalid URL. It must be a valid anyflip.com domain.")
            return
            
        if not save_path:
            messagebox.showwarning("Input Error", "Please select a save location.")
            return

        self.set_downloading_state()
        thread = threading.Thread(target=self.download_worker, args=(base_url, save_path, quality), daemon=True)
        thread.start()

    def start_compression(self):
        if self.is_downloading or self.is_compressing:
            return
            
        in_pdf = self.in_pdf_var.get().strip()
        quality = self.comp_qual_var.get()
        
        if not in_pdf or not os.path.exists(in_pdf):
            messagebox.showwarning("Input Error", "Please select a valid input PDF.")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Select Save Location for Compressed PDF"
        )
        
        if not save_path:
            return
            
        self.set_compressing_state()
        thread = threading.Thread(target=self.compression_worker, args=(in_pdf, save_path, quality), daemon=True)
        thread.start()

    def process_image(self, img_path, quality):
        """Resizes and compresses an image based on quality settings."""
        if quality == "Lossless":
            return img_path
            
        try:
            with Image.open(img_path) as img:
                # Convert to RGB to ensure JPEG compatibility
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                width, height = img.size
                
                if quality == "High":
                    scale = 0.8
                    jpeg_quality = 80
                elif quality == "Medium":
                    scale = 0.6
                    jpeg_quality = 60
                else: # Low
                    scale = 0.4
                    jpeg_quality = 40
                    
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                new_path = img_path + "_comp.jpg"
                img.save(new_path, "JPEG", quality=jpeg_quality, optimize=True)
                return new_path
        except Exception as e:
            print(f"Image processing error: {e}")
            return img_path # Fallback to original

    def download_worker(self, base_url, save_path, quality):
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Referer": base_url
        })

        page = 1
        image_paths = []
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                while True:
                    self.update_status_safe_down(f"Fetching page {page}...")
                    
                    possible_paths = [
                        f"files/large/{page}.jpg", f"files/large/{page}.webp",
                        f"files/mobile/{page}.jpg", f"files/mobile/{page}.webp"
                    ]
                    
                    success = False
                    for path in possible_paths:
                        img_url = f"{base_url}{path}"
                        try:
                            response = session.get(img_url, timeout=15)
                            if response.status_code == 200:
                                success = True
                                break
                        except requests.exceptions.RequestException as e:
                            self.show_error_safe("Network Error", f"Failed to fetch page {page}:\n{str(e)}")
                            return

                    if not success:
                        if page == 1:
                            self.show_error_safe("Download Error", "Could not find valid image for page 1. Document may be protected.")
                            return
                        else:
                            break
                            
                    ext = img_url.split('.')[-1]
                    raw_img_path = os.path.join(temp_dir, f"raw_{page:04d}.{ext}")
                    with open(raw_img_path, 'wb') as f:
                        f.write(response.content)
                        
                    # Process image based on quality
                    processed_path = self.process_image(raw_img_path, quality)
                    image_paths.append(processed_path)
                    
                    time.sleep(random.uniform(0.1, 0.3))
                    page += 1

                if not image_paths:
                    self.show_error_safe("Download Error", "No pages found.")
                    return

                self.update_status_safe_down(f"Compiling {len(image_paths)} pages into PDF...")
                
                try:
                    pdf_bytes = img2pdf.convert(image_paths)
                    with open(save_path, "wb") as f:
                        f.write(pdf_bytes)
                except Exception as e:
                    self.show_error_safe("PDF Compilation Error", f"Failed to compile PDF:\n{str(e)}")
                    return

                self.show_success_safe(save_path)
                
        except Exception as e:
            self.show_error_safe("Unexpected Error", str(e))

    def compression_worker(self, in_pdf, save_path, quality):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                doc = fitz.open(in_pdf)
                total_pages = len(doc)
                image_paths = []
                
                if quality == "High":
                    dpi = 150
                    jpeg_quality = 80
                elif quality == "Medium":
                    dpi = 100
                    jpeg_quality = 60
                else: # Low
                    dpi = 72
                    jpeg_quality = 40
                
                for i in range(total_pages):
                    self.update_status_safe_comp(f"Processing page {i+1} of {total_pages}...")
                    page = doc.load_page(i)
                    
                    # Render page to an image pixmap
                    pix = page.get_pixmap(dpi=dpi, alpha=False)
                    img_path = os.path.join(temp_dir, f"page_{i:04d}.jpg")
                    
                    # Convert to PIL Image for better JPEG compression control
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(img_path, "JPEG", quality=jpeg_quality, optimize=True)
                    
                    image_paths.append(img_path)
                    
                doc.close()
                
                self.update_status_safe_comp(f"Compiling {total_pages} compressed pages into PDF...")
                
                try:
                    pdf_bytes = img2pdf.convert(image_paths)
                    with open(save_path, "wb") as f:
                        f.write(pdf_bytes)
                except Exception as e:
                    self.show_error_safe("PDF Compilation Error", f"Failed to compile PDF:\n{str(e)}")
                    return
                    
                self.show_success_safe(save_path)

        except Exception as e:
            self.show_error_safe("Unexpected Error", str(e))


if __name__ == "__main__":
    app = AnyFlipDownloaderApp()
    app.mainloop()
