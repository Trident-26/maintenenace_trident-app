import pandas as pd

# lire fichier Excel
df = pd.read_excel("journal.xlsx")

print("=== COLONNES ===")
print(df.columns.tolist())

# 1. équipements HS
hs = df[df["Statut opérationnel"] == "HS"]

print("\n=== EQUIPEMENTS EN PANNE ===")
print(hs[["Date", "Equipement", "Plateforme", "Type d'opération"]])

# 2. machines arrêtées
arrets = df[df["Arrêt de la  machine (Accidentel/Volontaire/Pas d'arrêt)"] != "Pas d'arrêt"]

print("\n=== MACHINES ARRETEES ===")
print(arrets[["Equipement", "Arrêt de la  machine (Accidentel/Volontaire/Pas d'arrêt)"]])

# 3. temps d'arrêt élevé (> 2h)
df["Temps d'arrêt hh:mm:ss"] = pd.to_timedelta(df["Temps d'arrêt hh:mm:ss"], errors='coerce')

long_arret = df[df["Temps d'arrêt hh:mm:ss"] > pd.Timedelta(hours=2)]

print("\n=== ARRETS LONGS (>2h) ===")
print(long_arret[["Equipement", "Temps d'arrêt hh:mm:ss"]])