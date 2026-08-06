import zipfile, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
docx = r"c:\Users\Usuario\OneDrive\Escritorio\OSTIN}\API_KEYS_TR4NSHACK.docx"
with zipfile.ZipFile(docx) as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="replace")
text = re.sub(r"</w:p>", "\n", xml)
text = re.sub(r"<[^>]+>", "", text)
for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")]:
    text = text.replace(a, b)
text = re.sub(r"[ \t]+\n", "\n", text)
text = re.sub(r"\n{3,}", "\n\n", text)
out = r"c:\xampp\htdocs\pentagi\creze_recon\api_keys_extracted.txt"
with open(out, "w", encoding="utf-8") as f:
    f.write(text)
print(text)
print("\n--- WROTE", out, "---")
