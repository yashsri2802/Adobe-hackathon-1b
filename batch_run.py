import subprocess
from pathlib import Path

cases = ["case1", "case2", "case3"]

for case in cases:
    print(f"\nProcessing {case}...")
    
    cmd = [
        "python", "main.py",
        "--input_dir", f"{case}/input",
        "--input_json", f"{case}/input.json", 
        "--output_dir", f"{case}/output",
        "--model_dir", "models/all-MiniLM-L6-v2"
    ]
    
    subprocess.run(cmd, check=True)
    print(f"{case} completed!")

print("\nAll cases processed!")
