
def loadVokabelsToArray(filePath):
    vokabels = []
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    vokabels.append((parts[0].strip(), parts[1].strip()))
    except FileNotFoundError:
        print(f"Error: The file at {filePath} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return vokabels


def addVokabelsToFile(filePath, englisch, german):
    try:
        with open(filePath, 'a', encoding='utf-8') as file:
            file.write(f"{englisch},{german}\n")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def removeVokabelFromFile(filePath, englisch):
    try:
        vokabels = loadVokabelsToArray(filePath)
        vokabels = [v for v in vokabels if v[0] != englisch]
        with open(filePath, 'w', encoding='utf-8') as file:
            for v in vokabels:
                file.write(f"{v[0]},{v[1]}\n")
    except Exception as e:
        print(f"An error occurred while removing the vocabulary: {e}")