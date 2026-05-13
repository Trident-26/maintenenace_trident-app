import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

# ===== ANALYSE =====
def analyser():
    try:
        df = pd.read_excel("journal.xlsx")

        # filtre date
        if date_debut.get() and date_fin.get():
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            df = df[(df["Date"] >= date_debut.get()) & (df["Date"] <= date_fin.get())]

        hs = df[df["Statut opérationnel"] == "HS"]

        df["Temps d'arrêt hh:mm:ss"] = pd.to_timedelta(df["Temps d'arrêt hh:mm:ss"], errors='coerce')
        long_arret = df[df["Temps d'arrêt hh:mm:ss"] > pd.Timedelta(hours=2)]

        # vider tableau
        for row in tree.get_children():
            tree.delete(row)

        # afficher données
        for _, row in hs.iterrows():
            tree.insert("", "end", values=(row["Date"], row["Equipement"], "HS"))

        for _, row in long_arret.iterrows():
            tree.insert("", "end", values=(row["Date"], row["Equipement"], "Arrêt long"))

        # KPI
        total = len(df)
        texte.set(f"Total: {total} | HS: {len(hs)} | Arrêts longs: {len(long_arret)}")

    except Exception as e:
        messagebox.showerror("Erreur Analyse", str(e))


# ===== EXPORT =====
def exporter():
    try:
        df = pd.read_excel("journal.xlsx")

        hs = df[df["Statut opérationnel"] == "HS"]

        df["Temps d'arrêt hh:mm:ss"] = pd.to_timedelta(df["Temps d'arrêt hh:mm:ss"], errors='coerce')
        long_arret = df[df["Temps d'arrêt hh:mm:ss"] > pd.Timedelta(hours=2)]

        with pd.ExcelWriter("rapport_maintenance.xlsx") as writer:
            hs.to_excel(writer, sheet_name="Pannes", index=False)
            long_arret.to_excel(writer, sheet_name="Arrets_longs", index=False)

        messagebox.showinfo("Succès", "Rapport exporté avec succès !")

    except Exception as e:
        messagebox.showerror("Erreur Export", str(e))


# ===== GRAPHIQUE =====
def graphique():
    try:
        df = pd.read_excel("journal.xlsx")

        hs = df[df["Statut opérationnel"] == "HS"]

        top = hs["Equipement"].value_counts().head(5)

        plt.figure()
        top.plot(kind="bar")
        plt.title("Top 5 équipements en panne")
        plt.ylabel("Nombre de pannes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Erreur Graphique", str(e))


# ===== INTERFACE =====
fenetre = tk.Tk()
fenetre.title("📊 Smart Maintenance Dashboard Trident-Ogx")
fenetre.geometry("850x550")

# filtre date
frame_filtre = tk.Frame(fenetre)
frame_filtre.pack(pady=5)

tk.Label(frame_filtre, text="Début de l'opération (hh:mm):").pack(side="left")
date_debut = tk.Entry(frame_filtre)
date_debut.pack(side="left", padx=5)

tk.Label(frame_filtre, text="Fin de l'opération (hh:mm):").pack(side="left")
date_fin = tk.Entry(frame_filtre)
date_fin.pack(side="left", padx=5)

# KPI
texte = tk.StringVar()
texte.set("Dashboard prêt")

label = tk.Label(fenetre, textvariable=texte, font=("Arial", 12))
label.pack(pady=10)

# boutons
frame_boutons = tk.Frame(fenetre)
frame_boutons.pack()

tk.Button(frame_boutons, text="Analyser", command=analyser).pack(side="left", padx=10)
tk.Button(frame_boutons, text="Exporter", command=exporter).pack(side="left", padx=10)
tk.Button(frame_boutons, text="Graphique", command=graphique).pack(side="left", padx=10)

# tableau
colonnes = ("Date", "Equipement","Plateforme", "Statut")
tree = ttk.Treeview(fenetre, columns=colonnes, show="headings")

for col in colonnes:
    tree.heading(col, text=col)

tree.pack(fill="both", expand=True)

fenetre.mainloop()