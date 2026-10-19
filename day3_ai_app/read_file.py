# use with open() to read the contents of a file
try:
    with open("feedback.txt","r", encoding="utf_8") as f:
        contents = f.read()
        print("----file contents can read----")
        print(contents)
except FileNotFoundError:
    print("file not found")