from pathlib import Path

print("sample started")
Path("/tmp/sandboxed-script-analyzer.txt").write_text("hello from sandbox\n", encoding="utf-8")
print("sample finished")
