import argparse, json, time, os, re
from pathlib import Path
import fitz  
from sentence_transformers import SentenceTransformer, util

RE_NUMBERING = re.compile(r"^(\d+[\.\)]?)+(\s+|$)")
FALSE_POS = {"abstract", "keywords", "references", "bibliography", "index", "appendix"}

def clean(txt: str) -> str:
    return re.sub(r"\s+", " ", txt).strip()

def extract_outline(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    elems = []
    
    for pno, page in enumerate(doc, 1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    t = span["text"].strip()
                    if not t or t.lower() in FALSE_POS or t.isdigit():
                        continue
                    elems.append({
                        "text": clean(t),
                        "page": pno,
                        "size": span["size"],
                        "flags": span["flags"],
                        "y0": span["bbox"][1]
                    })
    doc.close()
    
    if not elems:
        return {"title": "Untitled Document", "outline": []}

    p1 = [e for e in elems if e["page"] == 1]
    if p1:
        big = max(e["size"] for e in p1)
        title = sorted([e for e in p1 if e["size"] >= big*0.95],
                      key=lambda e: (e["y0"], -len(e["text"])))[0]["text"]
    else:
        title = elems[0]["text"]

    body = max(set(e["size"] for e in elems), key=[e["size"] for e in elems].count)
    cands = []
    for e in elems:
        larger = e["size"] > body*1.1
        bold = bool(e["flags"] & 16)
        caps = e["text"].istitle() or e["text"].isupper()
        numbered = bool(RE_NUMBERING.match(e["text"]))
        score = 3*larger + 2*bold + caps + 2*numbered
        if score >= 3:
            cands.append(e)

    sizes = sorted({c["size"] for c in cands}, reverse=True)[:3]
    s2lvl = {s: f"H{i+1}" for i, s in enumerate(sizes)}

    outline, seen = [], set()
    for c in sorted(cands, key=lambda x: (x["page"], x["y0"])):
        if c["text"].lower() in seen:
            continue
        seen.add(c["text"].lower())
        outline.append({
            "level": s2lvl.get(c["size"], "H3"),
            "text": c["text"], 
            "page": c["page"]
        })
    
    return {"title": title, "outline": outline}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--input_json", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--model_dir", required=True)
    args = parser.parse_args()

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    with open(args.input_json, encoding="utf-8") as f:
        meta = json.load(f)["metadata"]
    
    persona = meta["persona"]
    job = meta["job_to_be_done"]
    pdfs = meta["input_documents"]

    model = SentenceTransformer(args.model_dir, device="cpu")
    query_emb = model.encode(f"{persona}: {job}", convert_to_tensor=True)

    extracted, subsections = [], []
    rank = 1

    for pdf in pdfs:
        pdf_path = Path(args.input_dir) / pdf
        if not pdf_path.exists():
            print(f"Missing: {pdf}")
            continue

        outline = extract_outline(str(pdf_path))
        h1s = [o for o in outline["outline"] if o["level"] == "H1"]
        if not h1s:
            h1s = [{"text": outline["title"], "page": 1}]

        doc = fitz.open(pdf_path)
        ptext = {i+1: doc[i].get_text() for i in range(len(doc))}
        doc.close()

        blobs, infos = [], []
        for sec in h1s:
            snippet = ptext.get(sec["page"], "")[:800]
            blobs.append(sec["text"] + "\n" + snippet)
            infos.append(sec)

        sims = util.pytorch_cos_sim(
            model.encode(blobs, convert_to_tensor=True),
            query_emb
        ).squeeze(1).tolist()

        for score, info in sorted(zip(sims, infos), reverse=True):
            extracted.append({
                "document": pdf,
                "section_title": info["text"],
                "importance_rank": rank,
                "page_number": info["page"]
            })

            sents = [s.strip() for s in re.split(r'[.!?]', ptext.get(info["page"], "")) if s.strip()]
            summary = ". ".join(sents[:3]) + ('.' if sents else '')
            
            subsections.append({
                "document": pdf,
                "refined_text": summary or "Summary not available.",
                "page_number": info["page"]
            })
            rank += 1

    result = {
        "metadata": {
            "documents": pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "extracted_sections": extracted,
        "subsection_analysis": subsections
    }

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    out_file = Path(args.output_dir) / "round1b_result.json"
    
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {out_file}")

if __name__ == "__main__":
    main()
