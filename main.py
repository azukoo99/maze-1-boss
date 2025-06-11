import pygame
import sys
import csv
import hashlib
import time
import os

pygame.init()

# Pengaturan layar
LEBAR, TINGGI = 800, 600
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Find Cheeze")
font = pygame.font.SysFont(None, 32)
font_level = pygame.font.SysFont(None, 40)
font_besar = pygame.font.SysFont(None, 48)
jam = pygame.time.Clock()

# Nama file CSV
FILE_PENGGUNA = 'pengguna.csv'
FILE_SKOR = 'skor.csv'

# --- FUNGSI CSV ---
def inisialisasi_csv():
    # Buat file pengguna jika belum ada
    if not os.path.exists(FILE_PENGGUNA):
        with open(FILE_PENGGUNA, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'username', 'password'])
    
    # Buat file skor jika belum ada
    if not os.path.exists(FILE_SKOR):
        with open(FILE_SKOR, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'id_pengguna', 'level', 'waktu'])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validasi_password(password):
    """Validasi password:
    - Minimal 8 karakter
    - Mengandung huruf dan angka
    """
    if len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit

def daftar_pengguna(username, password):
    try:
        # Cek apakah username sudah ada
        with open(FILE_PENGGUNA, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Lewati header
            for row in reader:
                if row[1] == username:
                    return False
        
        # Dapatkan ID baru
        with open(FILE_PENGGUNA, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            id_baru = len(rows)  # ID berdasarkan jumlah baris
        
        # Tambahkan pengguna baru
        with open(FILE_PENGGUNA, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([id_baru, username, hash_password(password)])
        
        return True
    except Exception:
        return False

def masuk_pengguna(username, password):
    try:
        with open(FILE_PENGGUNA, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Lewati header
            for row in reader:
                if row[1] == username and row[2] == hash_password(password):
                    return int(row[0])  # Return id_pengguna
        return None
    except Exception:
        return None

def simpan_skor(id_pengguna, level, waktu):
    try:
        # Dapatkan ID baru
        with open(FILE_SKOR, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            id_baru = len(rows)  # ID berdasarkan jumlah baris
        
        # Tambahkan skor baru
        with open(FILE_SKOR, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([id_baru, id_pengguna, level, waktu])
        
        return True
    except Exception:
        return False

def dapatkan_leaderboard(level, batas=5):
    try:
        # Baca semua skor
        with open(FILE_SKOR, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Lewati header
            skor = [row for row in reader if int(row[2]) == level]
        
        # Baca data pengguna
        with open(FILE_PENGGUNA, 'r') as file:
            reader = csv.reader(file)
            pengguna = {row[0]: row[1] for row in reader}
        
        # Gabungkan data dan sorting berdasarkan waktu
        hasil = []
        for row in skor:
            id_pengguna = row[1]
            if id_pengguna in pengguna:
                hasil.append({
                    'username': pengguna[id_pengguna],
                    'waktu': float(row[3])
                })
        
        # Sorting menggunakan Bubble Sort (bisa diganti dengan algoritma lain)
        n = len(hasil)
        for i in range(n):
            for j in range(0, n-i-1):
                if hasil[j]['waktu'] > hasil[j+1]['waktu']:
                    hasil[j], hasil[j+1] = hasil[j+1], hasil[j]
        
        # Ambil top 5
        return [(item['username'], item['waktu']) for item in hasil[:batas]]
    
    except Exception:
        return []

# --- KELAS INPUTBOX ---
class KotakInput:
    def __init__(self, x, y, lebar, tinggi, teks=''):
        self.rect = pygame.Rect(x, y, lebar, tinggi)
        self.warna_tidak_aktif = pygame.Color('lightskyblue3')
        self.warna_aktif = pygame.Color('dodgerblue2')
        self.warna = self.warna_tidak_aktif
        self.teks = teks
        self.font = pygame.font.Font(None, 32)
        self.permukaan_teks = self.font.render(teks, True, (0,0,0))
        self.aktif = False

    def tangani_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.aktif = not self.aktif
            else:
                self.aktif = False
            self.warna = self.warna_aktif if self.aktif else self.warna_tidak_aktif
        if event.type == pygame.KEYDOWN:
            if self.aktif:
                if event.key == pygame.K_RETURN:
                    return self.teks
                elif event.key == pygame.K_BACKSPACE:
                    self.teks = self.teks[:-1]
                else:
                    self.teks += event.unicode
                self.permukaan_teks = self.font.render(self.teks, True, (255,255,255))
        return None

    def gambar(self, layar):
        layar.blit(self.permukaan_teks, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(layar, self.warna, self.rect, 2)

# --- KELAS TOMBOL ---
class Tombol:
    def __init__(self, x, y, lebar, tinggi, teks):
        self.rect = pygame.Rect(x, y, lebar, tinggi)
        self.warna = pygame.Color('gray')
        self.teks = teks
        self.font = pygame.font.Font(None, 32)
        self.permukaan_teks = self.font.render(teks, True, (0, 0, 0))

    def gambar(self, layar):
        pygame.draw.rect(layar, self.warna, self.rect)
        rect_teks = self.permukaan_teks.get_rect(center=self.rect.center)
        layar.blit(self.permukaan_teks, rect_teks)

    def diklik(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- VARIABEL GAME ---
status_game = 'login'
id_pengguna_sekarang = None
pesan = ''
level_terpilih = 1

# Variabel sistem petunjuk
jalur_petunjuk = []
tampilkan_petunjuk = False
cooldown_petunjuk = 0

gambar_tikus = pygame.image.load("tikus.png").convert_alpha()
gambar_keju = pygame.image.load("keju.png").convert_alpha()

# Definisi maze (disimpan dalam dictionary)
mazes = {
    1: [  # Level 1 - 8x8 (Sangat Mudah - Random sederhana)
        [1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,1],
        [1,1,0,1,1,0,1,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,1,0,1,0,1],
        [1,0,1,0,0,1,0,1],
        [1,0,0,0,1,0,2,1],
        [1,1,1,1,1,1,1,1],
    ],
    
    2: [  # Level 2 - 10x10 (Mudah - Pattern lebih random)
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,1,0,0,0,1,0,0,1],
        [1,0,1,0,1,0,0,0,1,1],
        [1,0,0,0,1,1,0,1,0,1],
        [1,1,0,1,0,0,0,1,0,1],
        [1,0,0,1,0,1,1,0,0,1],
        [1,0,1,0,0,0,1,0,1,1],
        [1,0,1,1,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,2,1],
        [1,1,1,1,1,1,1,1,1,1],
    ],
    
    3: [  # Level 3 - 12x12 (Sedang - Random medium)
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,1,0,0,0,1,0,0,0,1],
        [1,0,1,0,0,1,0,0,1,0,1,1],
        [1,0,1,1,0,1,1,0,1,0,0,1],
        [1,0,0,0,0,0,1,0,0,1,0,1],
        [1,1,0,1,1,0,0,1,0,1,0,1],
        [1,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,1,0,0,0,1,1,0,1,1,1],
        [1,0,1,1,0,1,0,0,0,0,0,1],
        [1,0,0,1,0,1,1,0,1,1,0,1],
        [1,1,0,0,0,0,0,0,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    4: [  # Level 4 - 14x14 (Sedang-Sulit - Pattern acak kompleks)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,1,0,0,0,0,1,0,0,0,0,1],
        [1,1,0,0,0,1,1,0,0,0,1,0,1,1],
        [1,0,0,1,0,0,1,1,0,1,1,0,0,1],
        [1,0,1,1,1,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,1,0,1,1,1,0,0,1,0,1],
        [1,1,0,1,0,0,0,0,1,1,0,0,0,1],
        [1,0,0,1,0,1,0,0,0,1,0,1,0,1],
        [1,0,1,0,0,1,1,1,0,0,0,1,0,1],
        [1,0,1,1,0,0,0,1,1,0,1,0,0,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,1,1],
        [1,1,0,1,1,1,0,1,0,1,0,0,0,1],
        [1,0,0,0,0,0,0,1,0,0,0,1,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    5: [  # Level 5 - 16x16 (Sulit - Random dengan jebakan)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
        [1,0,1,0,0,0,1,1,0,0,0,1,1,0,1,1],
        [1,0,1,1,0,1,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
        [1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,0,1,1,0,1,0,1,1,1,0,0,0,0,1],
        [1,0,1,0,1,0,1,0,0,0,1,1,0,1,1,1],
        [1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,0,0,1,0,1,0,1,1,0,1,0,1,0,1,1],
        [1,1,0,1,0,1,0,0,0,0,1,0,1,0,0,1],
        [1,0,0,0,0,0,1,1,0,1,0,0,0,1,0,1],
        [1,0,1,1,1,0,0,0,0,1,0,1,0,0,0,1],
        [1,0,0,0,1,1,0,1,0,0,0,1,1,0,1,1],
        [1,1,0,0,0,0,0,1,1,0,0,0,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    6: [  # Level 6 - 18x18 (Sulit - Random kompleks)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
        [1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,1,1,1],
        [1,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
        [1,1,0,1,0,0,0,1,0,0,0,0,1,0,0,1,0,1],
        [1,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,1,0,0,0,1,0,1,1,0,1,1,0,1,0,1,1],
        [1,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1],
        [1,0,0,0,1,1,0,1,0,1,1,0,1,0,0,1,0,1],
        [1,1,0,1,0,0,0,1,0,0,1,0,1,1,0,0,0,1],
        [1,0,0,1,0,1,1,0,0,0,0,0,0,1,1,0,1,1],
        [1,0,1,0,0,0,1,0,1,1,0,1,0,0,0,0,0,1],
        [1,0,1,1,0,0,0,1,0,0,0,1,1,0,1,0,1,1],
        [1,0,0,0,1,1,0,0,0,1,0,0,0,0,1,0,0,1],
        [1,1,0,0,0,1,1,0,1,1,1,0,1,0,0,1,0,1],
        [1,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    7: [  # Level 7 - 20x20 (Sangat Sulit - Random organik)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,0,1,1,0,0,0,1,1,0,0,0,0,1,1,0,1,0,1,1],
        [1,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,1,0,0,1],
        [1,1,0,0,0,0,1,0,1,1,0,1,1,0,1,0,0,1,0,1],
        [1,0,0,1,0,1,0,0,0,0,0,0,1,0,1,1,0,0,0,1],
        [1,0,1,1,0,1,0,1,1,0,1,0,0,0,0,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,1,0,1,1,0,1,0,0,0,0,0,1],
        [1,1,0,1,1,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1],
        [1,0,0,0,1,0,1,1,0,1,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,0,0,0,1,0,1,1,0,1,0,1,1,0,0,0,1],
        [1,0,1,1,0,1,0,0,0,0,1,0,1,0,0,1,1,0,1,1],
        [1,0,0,0,0,1,1,0,1,0,0,0,0,1,0,0,0,0,0,1],
        [1,1,0,1,0,0,0,0,1,1,0,1,0,1,1,0,1,1,0,1],
        [1,0,0,1,1,0,1,0,0,0,0,1,0,0,1,0,0,0,0,1],
        [1,0,1,0,0,0,1,1,0,1,1,0,0,0,0,1,0,1,1,1],
        [1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,0,0,0,0,1],
        [1,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,1,0,1,1],
        [1,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    8: [  # Level 8 - 20x20 (Sangat Sulit - Pattern random kompleks)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
        [1,0,1,0,0,1,1,0,0,0,1,1,0,0,0,1,1,0,1,1],
        [1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,1,0,0,0,0,1,0,1,0,0,1,1,0,1,0,1],
        [1,1,0,1,1,1,0,1,0,0,0,1,0,1,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,1,1,0,1,0,0,1,0,1,0,0,0,1],
        [1,0,1,1,0,1,0,0,0,0,1,0,1,0,0,1,1,0,1,1],
        [1,0,0,1,0,1,1,0,1,1,0,0,1,0,1,0,0,0,0,1],
        [1,1,0,0,0,0,0,0,0,1,0,1,0,0,1,0,1,1,0,1],
        [1,0,0,1,1,0,1,1,0,0,0,1,0,1,0,0,0,1,0,1],
        [1,0,1,0,1,0,0,0,1,0,1,0,0,1,1,0,0,0,0,1],
        [1,0,1,0,0,1,0,0,0,0,1,0,1,0,0,1,1,0,1,1],
        [1,0,0,1,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,1],
        [1,1,0,1,1,0,0,0,0,1,0,1,0,0,0,1,0,1,0,1],
        [1,0,0,0,1,1,0,1,1,0,0,0,1,1,0,0,0,1,0,1],
        [1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,1],
        [1,0,1,1,0,1,1,0,0,0,1,1,0,0,0,0,1,1,0,1],
        [1,0,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    9: [  # Level 9 - 22x22 (Expert - Random sangat kompleks)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
        [1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1,1,0,1,1],
        [1,0,1,1,0,1,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1],
        [1,1,0,1,0,0,0,1,0,0,0,1,0,0,1,1,0,0,0,1,0,1],
        [1,0,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,0,1],
        [1,0,1,0,0,0,1,0,1,1,1,0,1,0,0,0,0,1,0,1,0,1],
        [1,0,1,0,1,0,0,0,0,0,0,0,1,1,0,1,0,0,0,1,0,1],
        [1,0,0,0,1,1,0,1,0,1,1,0,0,0,0,1,1,0,1,0,0,1],
        [1,1,0,1,0,0,0,1,0,0,1,1,0,1,0,0,0,0,1,0,1,1],
        [1,0,0,1,0,1,1,0,0,0,0,1,0,1,1,0,1,0,0,0,0,1],
        [1,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,1,0,1,0,1],
        [1,0,1,1,0,0,0,1,0,0,1,0,1,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,1,1,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1],
        [1,1,0,0,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,0,1,1],
        [1,0,0,1,0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,1],
        [1,0,1,1,1,0,1,0,0,0,1,1,0,0,1,0,0,1,0,1,0,1],
        [1,0,0,0,1,0,1,1,0,1,0,0,0,0,1,1,0,0,0,1,0,1],
        [1,1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,0,0,0,1],
        [1,0,0,1,1,0,1,0,1,0,0,0,0,1,0,0,0,0,1,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    
    10: [  # Level 10 - 24x24 (Master - Random organik paling kompleks)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1],
        [1,0,1,1,0,0,0,1,1,0,0,0,0,1,1,0,1,0,0,0,1,0,1,1],
        [1,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,1,1,0,1,0,0,0,1],
        [1,1,0,0,0,0,1,0,1,1,0,1,1,0,1,0,0,0,0,1,0,1,0,1],
        [1,0,0,1,0,1,0,0,0,0,0,0,1,0,1,1,0,1,0,0,0,1,0,1],
        [1,0,1,1,0,1,0,1,1,0,1,0,0,0,0,1,0,1,1,0,1,0,0,1],
        [1,0,0,0,0,0,0,0,1,0,1,1,0,1,0,0,0,0,0,0,1,0,1,1],
        [1,1,0,1,1,0,1,0,0,0,0,1,0,1,1,0,1,1,0,0,0,0,0,1],
        [1,0,0,0,1,0,1,1,0,1,0,0,0,0,0,0,0,1,1,0,1,1,0,1],
        [1,0,1,0,0,0,0,1,0,1,1,0,1,0,1,1,0,0,0,0,0,1,0,1],
        [1,0,1,1,0,1,0,0,0,0,1,0,1,0,0,1,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,1,0,1,0,0,0,0,1,0,0,0,0,1,1,0,1,1,1],
        [1,1,0,1,0,0,0,0,1,1,0,1,0,1,1,0,1,0,0,0,0,0,0,1],
        [1,0,0,1,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,1,1,0,0,1],
        [1,0,1,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1],
        [1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,1,1,0,0,0,0,1],
        [1,0,0,0,1,1,0,1,1,0,0,0,0,1,0,1,0,0,1,1,0,1,0,1],
        [1,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,0,0,1,0,1],
        [1,0,0,1,0,1,1,0,0,0,0,1,1,0,1,0,1,1,0,1,0,0,0,1],
        [1,0,1,1,0,0,1,1,0,1,0,0,0,0,1,0,0,0,0,1,1,0,1,1],
        [1,0,0,0,1,0,0,0,0,1,1,0,1,0,0,1,0,1,0,0,0,0,0,1],
        [1,1,0,0,0,1,0,1,0,0,0,0,1,1,0,0,0,1,1,0,1,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
}

# posisi_pemain = []
# waktu_mulai = 0
# waktu_berjalan = 0
# selesai = False

# --- FUNGSI PENCARIAN JALUR ---
def cari_jalur_bfs(maze, awal, akhir):
    baris = len(maze)
    kolom = len(maze[0]) if baris > 0 else 0
    
    dikunjungi = [[False for _ in range(kolom)] for _ in range(baris)]
    induk = [[None for _ in range(kolom)] for _ in range(baris)]
    
    antrian = [awal] 
    dikunjungi[awal[1]][awal[0]] = True
    
    # Arah: atas, kanan, bawah, kiri
    arah = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    while antrian:
        x, y = antrian.pop(0)
        
        if (x, y) == akhir:
            # Bangun kembali jalur
            jalur = []
            while (x, y) != awal:
                jalur.append((x, y))
                x, y = induk[y][x]
            jalur.reverse()
            return jalur
            
        for dx, dy in arah:
            nx, ny = x + dx, y + dy
            if 0 <= nx < kolom and 0 <= ny < baris:
                if maze[ny][nx] != 1 and not dikunjungi[ny][nx]:
                    dikunjungi[ny][nx] = True
                    induk[ny][nx] = (x, y)
                    antrian.append((nx, ny))
    
    return []  # Tidak ditemukan jalur

# --- FUNGSI GAME ---
def gambar_maze(maze):
    colors = {
        0: (150, 150, 150),  # Path (abu-abu)
        1: (0, 0, 0)          # Wall (hitam)
    }
    ukuran_sel = min(LEBAR // len(maze[0]), TINGGI // len(maze))
    
    for y, baris in enumerate(maze):
        for x, sel in enumerate(baris):
            rect = pygame.Rect(x * ukuran_sel, y * ukuran_sel, ukuran_sel, ukuran_sel)
            
            # Hanya gambar wall dan path
            if sel in colors:
                pygame.draw.rect(layar, colors[sel], rect)
                pygame.draw.rect(layar, (100, 100, 100), rect, 1)
            
            # Gambar keju untuk finish (sel = 2)
            if sel == 2:
                keju_scaled = pygame.transform.scale(gambar_keju, (ukuran_sel, ukuran_sel))
                layar.blit(keju_scaled, rect)
    
    return ukuran_sel

def gambar_pemain(pos, ukuran_sel):
    rect = pygame.Rect(pos[0] * ukuran_sel, pos[1] * ukuran_sel, ukuran_sel, ukuran_sel)
    tikus_scaled = pygame.transform.scale(gambar_tikus, (ukuran_sel, ukuran_sel))
    layar.blit(tikus_scaled, rect)

def gambar_petunjuk(jalur, ukuran_sel):
    for i, (x, y) in enumerate(jalur):
        if i < len(jalur) - 1:  # Jangan gambar panah di finish
            tengah_x = x * ukuran_sel + ukuran_sel // 2
            tengah_y = y * ukuran_sel + ukuran_sel // 2
            
            # Tentukan arah panah
            next_x, next_y = jalur[i+1]
            if next_x > x:  # Kanan
                titik = [(tengah_x + 5, tengah_y), (tengah_x - 5, tengah_y - 5), (tengah_x - 5, tengah_y + 5)]
            elif next_x < x:  # Kiri
                titik = [(tengah_x - 5, tengah_y), (tengah_x + 5, tengah_y - 5), (tengah_x + 5, tengah_y + 5)]
            elif next_y > y:  # Bawah
                titik = [(tengah_x, tengah_y + 5), (tengah_x - 5, tengah_y - 5), (tengah_x + 5, tengah_y - 5)]
            else:  # Atas
                titik = [(tengah_x, tengah_y - 5), (tengah_x - 5, tengah_y + 5), (tengah_x + 5, tengah_y + 5)]
            
            pygame.draw.polygon(layar, (0, 255, 255), titik)

def reset_level(level):
    global posisi_pemain, waktu_mulai, waktu_berjalan, selesai, jalur_petunjuk, tampilkan_petunjuk, cooldown_petunjuk
    posisi_pemain = [1,1]
    waktu_mulai = time.time()
    waktu_berjalan = 0
    selesai = False
    jalur_petunjuk = []
    tampilkan_petunjuk = False
    cooldown_petunjuk = 0

def gerakan_pemain(dx, dy, maze):
    global posisi_pemain, selesai, waktu_berjalan, tampilkan_petunjuk
    x_baru = posisi_pemain[0] + dx
    y_baru = posisi_pemain[1] + dy
    if 0 <= x_baru < len(maze[0]) and 0 <= y_baru < len(maze):
        if maze[y_baru][x_baru] != 1:
            posisi_pemain[0], posisi_pemain[1] = x_baru, y_baru
            tampilkan_petunjuk = False  # Sembunyikan petunjuk saat pemain bergerak
            if maze[y_baru][x_baru] == 2:
                selesai = True
                waktu_berjalan = time.time() - waktu_mulai
                simpan_skor(id_pengguna_sekarang, level_terpilih, waktu_berjalan)

def gambar_teks_tengah(teks, y, warna=(255,255,255)):
    permukaan = font_besar.render(teks, True, warna)
    rect = permukaan.get_rect(center=(LEBAR//2, y))
    layar.blit(permukaan, rect)

def tampilkan_leaderboard(level):
    leaderboard = dapatkan_leaderboard(level)
    layar.fill((0,0,0))
    judul = font_besar.render(f"Papan Peringkat Level {level}", True, (255,255,255))
    layar.blit(judul, (150,20))
    y_awal = 80
    for i, (username, t) in enumerate(leaderboard):
        txt = f"{i+1}. {username} - {t:.2f} detik"
        permukaan = font.render(txt, True, (255,255,255))
        layar.blit(permukaan, (150, y_awal + i*30))
    info = font.render("Tekan ESC untuk kembali", True, (200,200,200))
    layar.blit(info, (180, TINGGI - 40))
    pygame.display.flip()

def menu_utama():
    global status_game, level_terpilih
    pilihan = [f"Level {i}" for i in range(1,11)] + ["Keluar"]
    terpilih = 0
    while True:
        layar.fill((0,0,0))
        judul = font_besar.render("Pilih Level", True, (255,255,255))
        layar.blit(judul, (310, 30))
        for i, opsi in enumerate(pilihan):
            warna = (255, 0, 0) if i == terpilih else (255,255,255)
            permukaan = font_level.render(opsi, True, warna)
            layar.blit(permukaan, (350, 100 + i*40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    terpilih = (terpilih - 1) % len(pilihan)
                elif event.key == pygame.K_DOWN:
                    terpilih = (terpilih + 1) % len(pilihan)
                elif event.key == pygame.K_RETURN:
                    if terpilih == len(pilihan)-1:
                        pygame.quit()
                        sys.exit()
                    else:
                        level_terpilih = terpilih + 1
                        reset_level(level_terpilih)
                        status_game = 'playing'
                        return

def main_level():
    global status_game, selesai, waktu_berjalan, jalur_petunjuk, tampilkan_petunjuk, cooldown_petunjuk
    
    maze = mazes.get(level_terpilih, mazes[1])
    tinggi_maze = len(maze)
    lebar_maze = len(maze[0])
    
    # Cari posisi finish
    posisi_finish = None
    for y in range(tinggi_maze):
        for x in range(lebar_maze):
            if maze[y][x] == 2:
                posisi_finish = (x, y)
                break
        if posisi_finish:
            break
    
    while True:
        layar.fill((0,0,0))
        ukuran_sel = gambar_maze(maze)
        gambar_pemain(posisi_pemain, ukuran_sel)
        
        # Gambar petunjuk jika aktif
        if tampilkan_petunjuk and jalur_petunjuk:
            gambar_petunjuk(jalur_petunjuk, ukuran_sel)
        
        # Tampilkan timer
        if not selesai:
            waktu_elapsed = time.time() - waktu_mulai
        else:
            waktu_elapsed = waktu_berjalan
        permukaan_timer = font.render(f"Waktu: {waktu_elapsed:.2f} detik", True, (255,255,255))
        layar.blit(permukaan_timer, (10, TINGGI - 30))
        
        # Tampilkan info petunjuk
        teks_petunjuk = font.render("Tekan H untuk hint", True, (200, 200, 200))
        layar.blit(teks_petunjuk, (LEBAR - 200, TINGGI - 30))
        
        if cooldown_petunjuk > 0:
            teks_cooldown = font.render(f"Cooldown: {cooldown_petunjuk//30} detik", True, (255, 100, 100))
            layar.blit(teks_cooldown, (LEBAR - 200, TINGGI - 60))
        
        if selesai:
            gambar_teks_tengah("SELAMAT! Tekan ENTER untuk ke menu", TINGGI//2)
        
        pygame.display.flip()
        
        # Update cooldown
        if cooldown_petunjuk > 0:
            cooldown_petunjuk -= 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if selesai:
                    if event.key == pygame.K_RETURN:
                        status_game = 'leaderboard'
                        return
                else:
                    if event.key == pygame.K_h and cooldown_petunjuk == 0:
                        # Generate jalur petunjuk menggunakan BFS
                        awal = (posisi_pemain[0], posisi_pemain[1])
                        jalur_petunjuk = cari_jalur_bfs(maze, awal, posisi_finish)
                        tampilkan_petunjuk = True
                        cooldown_petunjuk = 180  # Cooldown 3 detik (60 FPS * 3)
                    elif event.key == pygame.K_UP:
                        gerakan_pemain(0, -1, maze)
                    elif event.key == pygame.K_DOWN:
                        gerakan_pemain(0, 1, maze)
                    elif event.key == pygame.K_LEFT:
                        gerakan_pemain(-1, 0, maze)
                    elif event.key == pygame.K_RIGHT:
                        gerakan_pemain(1, 0, maze)

def layar_papan_peringkat():
    global status_game
    while True:
        tampilkan_leaderboard(level_terpilih)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    status_game = 'menu_utama'
                    return

# --- ELEMEN UI ---
kotak_username = KotakInput(300, 250, 200, 32)
kotak_password = KotakInput(300, 310, 200, 32)
tombol_login = Tombol(300, 370, 90, 40, 'Login')
tombol_daftar = Tombol(410, 370, 90, 40, 'Daftar')

# Inisialisasi CSV
inisialisasi_csv()

# --- LOOP GAME UTAMA ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if status_game == 'login':
            ret1 = kotak_username.tangani_event(event)
            ret2 = kotak_password.tangani_event(event)

            if tombol_login.diklik(event):
                username = kotak_username.teks.strip()
                password = kotak_password.teks.strip()
                if username == '' or password == '':
                    pesan = 'Username dan password wajib diisi!'
                else:
                    uid = masuk_pengguna(username, password)
                    if uid:
                        id_pengguna_sekarang = uid
                        pesan = 'Login berhasil!'
                        status_game = 'menu_utama'
                    else:
                        pesan = 'Login gagal! Coba lagi.'

            if tombol_daftar.diklik(event):
                username = kotak_username.teks.strip()
                password = kotak_password.teks.strip()
                if username == '' or password == '':
                    pesan = 'Username dan password wajib diisi!'
                elif not validasi_password(password):
                    pesan = 'Password harus 8 karakter dan berisi huruf dan angka!'
                else:
                    if daftar_pengguna(username, password):
                        pesan = 'Registrasi berhasil! Silakan login.'
                    else:
                        pesan = 'Username sudah dipakai.'

            # Gambar layar login
            layar.fill((30,30,30))
            judul = font_besar.render("Login / Daftar", True, (255,255,255))
            layar.blit(judul, (275, 180))

            kotak_username.gambar(layar)
            kotak_password.gambar(layar)

            tombol_login.gambar(layar)
            tombol_daftar.gambar(layar)

            label_user = font.render("Username:", True, (255,255,255))
            label_pass = font.render("Password:", True, (255,255,255))
            layar.blit(label_user, (150, 255))
            layar.blit(label_pass, (150, 315))

            if pesan:
                permukaan_pesan = font.render(pesan, True, (255, 100, 100))
                layar.blit(permukaan_pesan, (150, 285))

            pygame.display.flip()

        elif status_game == 'menu_utama':
            menu_utama()

        elif status_game == 'playing':
            main_level()

        elif status_game == 'leaderboard':
            layar_papan_peringkat()

    jam.tick(30)