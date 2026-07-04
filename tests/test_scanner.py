from processors.folder_scanner import FolderScanner

# CHANGE THIS TO YOUR TRAINING ROOT FOLDER
ROOT_FOLDER = "/Users/praxsenghani/Desktop/Al Nasr Training Files"

scanner = FolderScanner(ROOT_FOLDER)

results = scanner.scan()

total = 0

print("\nHistoric Training Records")
print("-" * 40)

for month in results:

    print(f"\n📁 {month['month']}")

    for folder in month["folders"]:

        print(
            f"   {folder['type']:<28} {folder['pdfs']} PDFs"
        )

        total += folder["pdfs"]

print("\n" + "-" * 40)
print(f"Total PDFs : {total}")