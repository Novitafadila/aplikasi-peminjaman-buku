import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3

class PerpustakaanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Peminjaman Buku - SQLite")
        self.root.geometry("700x500")
        self.root.configure(bg="#121212")

        self.bg_color = "#121212"
        self.primary = "#00C853"
        self.secondary = "#2979FF"
        self.text_color = "#EEEEEE"
        self.late_color = "#FF5252"
        self.font = ("Segoe UI", 10)

        self.daftar_buku = [
            "Bahasa dan Budaya",
            "IPA",
            "IPS",
            "Sejarah",
            "Pendidikan Agama",
            "Matematika",
        ]

        self.koneksi_database()

        frame_input = tk.Frame(self.root, bg=self.bg_color)
        frame_input.pack(pady=10)

        self._add_label_entry(frame_input, "Nama Peminjam:", 0)
        self.nama_entry = self._get_entry(frame_input, 0)

        self._add_label_entry(frame_input, "Cari Buku:", 1)
        self.cari_entry = self._get_entry(frame_input, 1)
        self.cari_entry.bind("<KeyRelease>", self.cari_buku)

        tk.Label(frame_input, text="Pilih Buku:", bg=self.bg_color, fg=self.text_color, font=self.font).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.buku_var = tk.StringVar()
        self.buku_combobox = ttk.Combobox(frame_input, textvariable=self.buku_var, values=self.daftar_buku, state="readonly", font=self.font)
        self.buku_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.buku_combobox.current(0)

        self.btn_pinjam = tk.Button(self.root, text="📖 Pinjam Buku", font=self.font, bg=self.primary, fg="black", command=self.pinjam_buku)
        self.btn_pinjam.pack(pady=10)

        self.listbox_peminjaman = tk.Listbox(self.root, width=95, height=10, font=self.font, bg="#1E1E1E", fg=self.text_color, selectbackground="#333", selectforeground="white")
        self.listbox_peminjaman.pack(pady=10)

        self.btn_kembalikan = tk.Button(self.root, text="↩️ Kembalikan Buku", font=self.font, bg=self.secondary, fg="white", command=self.kembalikan_buku)
        self.btn_kembalikan.pack(pady=5)

        self.tampilkan_data()

    def koneksi_database(self):
        self.conn = sqlite3.connect("peminjaman.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peminjaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                buku TEXT NOT NULL,
                batas_kembali TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _add_label_entry(self, frame, text, row):
        tk.Label(frame, text=text, bg=self.bg_color, fg=self.text_color, font=self.font).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        entry = tk.Entry(frame, font=self.font, bg="#1E1E1E", fg=self.text_color, insertbackground=self.text_color)
        entry.grid(row=row, column=1, padx=5, pady=5)

    def _get_entry(self, frame, row):
        return frame.grid_slaves(row=row, column=1)[0]

    def cari_buku(self, event):
        keyword = self.cari_entry.get().lower()
        hasil = [b for b in self.daftar_buku if keyword in b.lower()]
        self.buku_combobox['values'] = hasil
        if hasil:
            self.buku_combobox.current(0)

    def pinjam_buku(self):
        nama = self.nama_entry.get().strip()
        buku = self.buku_var.get()
        if not nama:
            messagebox.showwarning("⚠️ Peringatan", "Masukkan nama peminjam!")
            return
        batas = datetime.now() + timedelta(days=7)
        batas_str = batas.strftime("%d-%b-%Y")
        self.cursor.execute("INSERT INTO peminjaman (nama, buku, batas_kembali) VALUES (?, ?, ?)", (nama, buku, batas_str))
        self.conn.commit()
        self.nama_entry.delete(0, tk.END)
        self.tampilkan_data()

    def tampilkan_data(self):
        self.listbox_peminjaman.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM peminjaman")
        for row in self.cursor.fetchall():
            id_, nama, buku, batas = row
            tampil = f"{id_} | {nama} meminjam buku '{buku}' (Kembali: {batas})"
            self.listbox_peminjaman.insert(tk.END, tampil)
        self.perbarui_warna()

    def kembalikan_buku(self):
        index = self.listbox_peminjaman.curselection()
        if not index:
            messagebox.showwarning("⚠️ Peringatan", "Pilih item untuk dikembalikan.")
            return
        data = self.listbox_peminjaman.get(index)
        try:
            id_ = int(data.split("|")[0].strip())
            self.cursor.execute("DELETE FROM peminjaman WHERE id = ?", (id_,))
            self.conn.commit()
            self.tampilkan_data()
        except Exception as e:
            messagebox.showerror("❌ Gagal", f"Gagal menghapus data.\n{e}")

    def perbarui_warna(self):
        for i in range(self.listbox_peminjaman.size()):
            item = self.listbox_peminjaman.get(i)
            if "(Kembali:" in item:
                try:
                    tanggal_str = item.split("(Kembali:")[1].strip(" )")
                    batas = datetime.strptime(tanggal_str, "%d-%b-%Y")
                    if datetime.now() > batas:
                        self.listbox_peminjaman.itemconfig(i, foreground=self.late_color)
                    else:
                        self.listbox_peminjaman.itemconfig(i, foreground=self.text_color)
                except:
                    continue

if __name__ == "__main__":
    root = tk.Tk()
    app = PerpustakaanApp(root)
    root.mainloop()
