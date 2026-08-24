import csv
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

CONSOLIDATED = r"c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_clientes_full.csv"

with open(CONSOLIDATED, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total registros cargados desde {CONSOLIDATED}: {len(rows)}")
print(f"Columnas ({len(reader.fieldnames)}): {reader.fieldnames}")

# Let's check statistics
emails = [r['Email'] for r in rows if r['Email']]
phones = [r['telefono'] or r['Telefono1'] or r['Celular'] for r in rows if (r['telefono'] or r['Telefono1'] or r['Celular'])]
rfcs = [r['rfc'] for r in rows if r['rfc'] and r['rfc'] != 'N/A' and r['rfc'] != 'XAXX010101000']
addresses = [r['Direccion'] for r in rows if r['Direccion'] and r['Direccion'] != 'N/A']
dates = [r['fecha_creacion'] for r in rows if r['fecha_creacion'] and r['fecha_creacion'] != '0000-00-00 00:00:00']

print("\n--- ESTADÍSTICAS ---")
print(f"Total registros: {len(rows)}")
print(f"Registros con Email: {len(emails)}")
print(f"Registros con Teléfono: {len(phones)}")
print(f"Registros con RFC real: {len(rfcs)}")
print(f"Registros con Dirección física: {len(addresses)}")
print(f"Registros con fecha_creacion válida: {len(dates)}")
if dates:
    print(f"Fecha mínima fecha_creacion: {min(dates)}")
    print(f"Fecha máxima fecha_creacion: {max(dates)}")

# Let's select 20 rich sample records:
# Mix of recent 2026/2025 records and records with complete address PII
samples_recent = [r for r in rows if r['fecha_creacion'].startswith('2026') or r['fecha_creacion'].startswith('2025')]
samples_full_addr = [r for r in rows if r['Direccion'] and r['Direccion'] != 'N/A' and r['Telefono1'] and len(r['Telefono1']) >= 7]

selected_samples = []
# Pick some from full addr
for r in samples_full_addr[:10]:
    selected_samples.append(r)
# Pick some from recent
for r in samples_recent[-10:]:
    if r not in selected_samples:
        selected_samples.append(r)

# If not yet 20, fill up
if len(selected_samples) < 20:
    for r in rows:
        if r not in selected_samples and r['Email']:
            selected_samples.append(r)
            if len(selected_samples) == 20:
                break

print(f"\n--- MUESTRA DE {len(selected_samples)} REGISTROS SELECCIONADOS ---")
for idx, s in enumerate(selected_samples[:20], 1):
    full_name = f"{s['Nombre']} {s['Apellido_Paterno']} {s['Apellido_Materno']}".strip()
    phone = s['Telefono1'] or s['Celular'] or s['telefono'] or s['telefono_telmex'] or 'N/A'
    addr = f"{s['Direccion']}, {s['Colonia']}, {s['Ciudad']}, {s['Estado']} CP {s['Codigo_Postal']}" if s['Direccion'] and s['Direccion'] != 'N/A' else 'Sin dirección registrada'
    print(f"{idx:02d}. ID: {s['Id']} | Nombre: {full_name} | Email: {s['Email']} | Tel: {phone} | RFC: {s['rfc']} | Fecha: {s['fecha_creacion']} | Ubicación: {addr}")
