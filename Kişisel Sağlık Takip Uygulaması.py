# -*- coding: utf-8 -*-

import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QListWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl

class Kullanici:
    def __init__(self, ad, soyad, yas, cinsiyet):
        self.ad = ad
        self.soyad = soyad
        self.yas = yas
        self.cinsiyet = cinsiyet
        self.saglik_kayitlari = []

    def kayit_ekle(self, saglik_kaydi):
        self.saglik_kayitlari.append(saglik_kaydi)

    def egzersiz_ekle(self, egzersiz):
        yeni_kayit = SaglikKaydi()
        yeni_kayit.egzersiz_ekle(egzersiz)
        self.kayit_ekle(yeni_kayit)

    def rapor_olustur(self):
        rapor = "Sağlık Raporu:\n"
        rapor += f"Ad: {self.ad} {self.soyad}, Yaş: {self.yas}, Cinsiyet: {self.cinsiyet}\n"
        rapor += "Sağlık Kayıtları:\n"
        for kayit in self.saglik_kayitlari:
            rapor += kayit.rapor_olustur()
        return rapor

class SaglikKaydi:
    def __init__(self, egzersizler=None):
        if egzersizler is None:
            self.egzersizler = []
        else:
            self.egzersizler = egzersizler

    def egzersiz_ekle(self, egzersiz):
        self.egzersizler.append(egzersiz)

    def rapor_olustur(self):
        rapor = ""
        for egzersiz in self.egzersizler:
            rapor += f"Egzersiz: {egzersiz.ad}, Süre: {egzersiz.sure} {egzersiz.sure_birimi}, Tekrar: {egzersiz.tekrar}\n"
        return rapor

class Egzersiz:
    def __init__(self, ad, sure, sure_birimi, tekrar):
        self.ad = ad
        self.sure = sure
        self.sure_birimi = sure_birimi
        self.tekrar = tekrar

class Arayuz(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kişisel Sağlık Takip Uygulaması")
        self.kullanici = None

        self.initUI()

        # SQLite3 veritabanı bağlantısını oluştur
        self.create_connection()

        # SQLite3 tablolarını oluştur
        self.create_tables()

        # Uygulama başladığında kaydedilmiş verileri yükle
        self.load_saved_data()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 800, 600)  

        self.network_manager = QNetworkAccessManager()
        url = QUrl("https://www.stilfon.com/wp-content/uploads/2022/02/B172.jpg")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(self.on_image_download_finished)

        self.result_label = QLabel()
        self.result_label.setStyleSheet("color: green; font-weight: bold;")

        kullanici_groupbox = self.create_kullanici_groupbox()
        egzersiz_ekle_groupbox = self.create_egzersiz_ekle_groupbox()
        saglik_kaydi_groupbox = self.create_saglik_kaydi_groupbox()
        rapor_olustur_groupbox = self.create_rapor_olustur_groupbox()

        main_layout = QVBoxLayout()
        main_layout.addWidget(kullanici_groupbox)
        main_layout.addWidget(egzersiz_ekle_groupbox)
        main_layout.addWidget(saglik_kaydi_groupbox)
        main_layout.addWidget(rapor_olustur_groupbox)
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)

    def on_image_download_finished(self):
        reply = self.sender()
        if reply.error():
            print("Image download failed:", reply.errorString())
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.background.setPixmap(pixmap)
            self.background.setScaledContents(True)

    def create_kullanici_groupbox(self):
        groupbox = QWidget()
        layout = QHBoxLayout()
        groupbox.setLayout(layout)

        ad_label = QLabel("Ad:")
        self.ad_entry = QLineEdit()
        layout.addWidget(ad_label)
        layout.addWidget(self.ad_entry)

        soyad_label = QLabel("Soyad:")
        self.soyad_entry = QLineEdit()
        layout.addWidget(soyad_label)
        layout.addWidget(self.soyad_entry)

        yas_label = QLabel("Yaş:")
        self.yas_combobox = QComboBox()
        for i in range(18, 61):
            self.yas_combobox.addItem(str(i))
        layout.addWidget(yas_label)
        layout.addWidget(self.yas_combobox)

        cinsiyet_label = QLabel("Cinsiyet:")
        self.cinsiyet_combobox = QComboBox()
        self.cinsiyet_combobox.addItems(["Erkek", "Kız"])
        layout.addWidget(cinsiyet_label)
        layout.addWidget(self.cinsiyet_combobox)

        kullanici_ekle_button = QPushButton("Kullanıcı Ekle")
        kullanici_ekle_button.clicked.connect(self.kullanici_ekle)
        layout.addWidget(kullanici_ekle_button)

        return groupbox

    def create_egzersiz_ekle_groupbox(self):
        groupbox = QWidget()
        layout = QHBoxLayout()
        groupbox.setLayout(layout)

        egzersizler = [
            "Squat (Çökme)",
            "Deadlift",
            "Bench Press (Bench Press)",
            "Pull-up (Çinbarı)",
            "Push-up (Şınav)",
            "Lunges (İleri Atış)",
            "Plank",
            "Burpee",
            "Jumping Jack",
            "Side Lunge"
        ]

        egzersiz_label = QLabel("Egzersiz Adı:")
        self.egzersiz_combobox = QComboBox()
        self.egzersiz_combobox.addItems(egzersizler)
        layout.addWidget(egzersiz_label)
        layout.addWidget(self.egzersiz_combobox)

        sure_label = QLabel("Süre:")
        self.sure_entry = QLineEdit()
        layout.addWidget(sure_label)
        layout.addWidget(self.sure_entry)

        sure_birimi_label = QLabel("Birim:")
        self.sure_birimi_combobox = QComboBox()
        self.sure_birimi_combobox.addItems(["Dakika", "Saat"])
        layout.addWidget(sure_birimi_label)
        layout.addWidget(self.sure_birimi_combobox)

        tekrar_label = QLabel("Tekrar:")
        self.tekrar_combobox = QComboBox()
        self.tekrar_combobox.addItems(["1", "2", "3", "4", "5"])
        layout.addWidget(tekrar_label)
        layout.addWidget(self.tekrar_combobox)

        egzersiz_ekle_button = QPushButton("Egzersiz Ekle")
        egzersiz_ekle_button.clicked.connect(self.egzersiz_ekle)
        layout.addWidget(egzersiz_ekle_button)

        return groupbox

    def create_saglik_kaydi_groupbox(self):
        groupbox = QWidget()
        layout = QVBoxLayout()
        groupbox.setLayout(layout)

        self.saglik_kaydi_listwidget = QListWidget()
        layout.addWidget(self.saglik_kaydi_listwidget)

        return groupbox

    def create_rapor_olustur_groupbox(self):
        groupbox = QWidget()
        layout = QHBoxLayout()
        groupbox.setLayout(layout)

        rapor_olustur_button = QPushButton("Rapor Oluştur")
        rapor_olustur_button.clicked.connect(self.rapor_olustur)
        layout.addWidget(rapor_olustur_button)

        return groupbox

    def egzersiz_ekle(self):
        if self.kullanici is None:
            self.result_label.setText("Lütfen önce kullanıcı bilgilerini girin.")
            return

        egzersiz_ad = self.egzersiz_combobox.currentText()
        sure = self.sure_entry.text()
        sure_birimi = self.sure_birimi_combobox.currentText()
        tekrar = self.tekrar_combobox.currentText()

        egzersiz = Egzersiz(egzersiz_ad, sure, sure_birimi, tekrar)
        self.kullanici.egzersiz_ekle(egzersiz)
        self.update_saglik_kaydi_listwidget()
        # Egzersiz eklenince veriyi kaydet
        self.save_data()

    def rapor_olustur(self):
        if self.kullanici is None:
            self.result_label.setText("Lütfen önce kullanıcı bilgilerini girin.")
            return

        rapor = self.kullanici.rapor_olustur()
        self.result_label.setText(rapor)

    def kullanici_ekle(self):
        ad = self.ad_entry.text()
        soyad = self.soyad_entry.text()
        yas = self.yas_combobox.currentText()
        cinsiyet = self.cinsiyet_combobox.currentText()

        if ad.strip() == "" or soyad.strip() == "":
            self.result_label.setText("Lütfen ad ve soyad bilgilerini girin.")
            return

        self.kullanici = Kullanici(ad, soyad, yas, cinsiyet)
        self.result_label.setText("Kullanıcı başarıyla eklendi.")
        # Kullanıcı eklenince veriyi kaydet
        self.save_data()

    def update_saglik_kaydi_listwidget(self):
        if self.kullanici is None:
            return

        self.saglik_kaydi_listwidget.clear()
        for kayit in self.kullanici.saglik_kayitlari:
            rapor = kayit.rapor_olustur()
            self.saglik_kaydi_listwidget.addItem(rapor)

    def create_connection(self):
        self.connection = sqlite3.connect('veritabani.db')
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ad TEXT,
                            soyad TEXT,
                            yas INTEGER,
                            cinsiyet TEXT
                            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS egzersizler (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            kullanici_id INTEGER,
                            ad TEXT,
                            sure INTEGER,
                            sure_birimi TEXT,
                            tekrar INTEGER,
                            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
                            )''')

        self.connection.commit()

    def save_data(self):
        if self.kullanici is None:
            return

        # Kullanıcıyı kaydet
        self.cursor.execute('''INSERT INTO kullanicilar (ad, soyad, yas, cinsiyet)
                            VALUES (?, ?, ?, ?)''',
                            (self.kullanici.ad, self.kullanici.soyad, self.kullanici.yas, self.kullanici.cinsiyet))
        kullanici_id = self.cursor.lastrowid

        # Egzersiz kayıtlarını kaydet
        for kayit in self.kullanici.saglik_kayitlari:
            for egzersiz in kayit.egzersizler:
                self.cursor.execute('''INSERT INTO egzersizler (kullanici_id, ad, sure, sure_birimi, tekrar)
                                    VALUES (?, ?, ?, ?, ?)''',
                                    (kullanici_id, egzersiz.ad, egzersiz.sure, egzersiz.sure_birimi, egzersiz.tekrar))

        self.connection.commit()

    def load_saved_data(self):
        self.cursor.execute('''SELECT * FROM kullanicilar''')
        kullanici_verileri = self.cursor.fetchall()

        for kullanici_verisi in kullanici_verileri:
            kullanici = Kullanici(kullanici_verisi[1], kullanici_verisi[2], kullanici_verisi[3], kullanici_verisi[4])

            self.cursor.execute('''SELECT * FROM egzersizler WHERE kullanici_id=?''', (kullanici_verisi[0],))
            egzersiz_verileri = self.cursor.fetchall()

            saglik_kaydi = SaglikKaydi()
            for egzersiz_verisi in egzersiz_verileri:
                egzersiz = Egzersiz(egzersiz_verisi[2], egzersiz_verisi[3], egzersiz_verisi[4], egzersiz_verisi[5])
                saglik_kaydi.egzersiz_ekle(egzersiz)

            kullanici.kayit_ekle(saglik_kaydi)

            self.kullanici = kullanici
            self.update_saglik_kaydi_listwidget()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Arayuz()
    ex.show()
    sys.exit(app.exec_())
