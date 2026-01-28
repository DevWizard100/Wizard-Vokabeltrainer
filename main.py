import settingsHandler
import vokabelHandler
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem, QMessageBox, QTabWidget, QTableWidgetItem
from win32mica import ApplyMica, MicaTheme
from PySide6.QtCore import Qt

from PySide6.QtCore import QTimer
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Initialisiert die Basisklasse QMainWindow (Konstruktor)

        # UI-Datei laden
        loader = QUiLoader()  # Erstellt eine Instanz von QUiLoader, um die .ui-Datei zu laden
        ui_file = QFile('main.ui')  # Öffnet die .ui-Datei (die Benutzeroberflächendatei)
        ui_file.open(QFile.ReadOnly)  # Öffnet die Datei im Nur-Lese-Modus
        self.ui = loader.load(ui_file, self)  # Lädt die .ui-Datei und weist sie self.ui zu
        ui_file.close()  # Schließt die .ui-Datei nach dem Laden

        self.uiWidget = QWidget(self)
        self.uiWidget.setAutoFillBackground(True)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        # transparenten background von allen elementen bis auf den fenster hintergrund entfernen
        for child in self.ui.findChildren(QWidget):
            child.setAttribute(Qt.WA_TranslucentBackground, False)
            child.setStyleSheet("background: none;")




        # transparenten background bei tabWidget hinzufügen
        tabWidget = self.ui.findChild(QTabWidget)
        if tabWidget:
            tabWidget.setAttribute(Qt.WA_TranslucentBackground, True)
            tabWidget.setStyleSheet("background: transparent;")


        self.ui.setParent(self.uiWidget)
        self.uiWidget.setLayout(self.ui.layout())
        self.setCentralWidget(self.uiWidget)
        # Setzt das erstellte Widget als zentrales Widget des QMainWindow

        self.resize(750, 580)
        self.setWindowTitle("Wizard Vokabeltrainer")  # Setzt den Fenstertitel


        # Vokabeln aus der Datei laden
        self.vokabeln = vokabelHandler.loadVokabelsToArray("vokabeln.txt")
        self.currentGermanVokabel = ""
        self.currentEnglishVokabel = ""
        self.germanToEnglish = settingsHandler.getGermanToEnglish() # Standardmäßig von Englisch nach Deutsch abfragen


        # UI Daten laden
        self.loadVocabularyTableWidget()  # Vokabeln laden beim Starten der Anwendung
        self.ui.vokabelTableWidget.resizeColumnsToContents()  # Spaltenbreite an den Inhalt anpassen
        self.nextHardVokabel()  # Erste Vokabel für den harten Modus laden
        self.nextEasyVokabel() # Erste Vokabel für den einfachen Modus laden
        self.loadVocableDirectionRadioButtons()
        self.loadLearnedVocabularyTableWidget()


        # UI Events verbinden
        self.ui.nextButton.clicked.connect(self.nextHardVokabel)
        self.ui.addButton.clicked.connect(self.addVocabulary)
        self.ui.answerLineEdit.returnPressed.connect(self.nextHardVokabel)
        self.ui.germanToEnglishRadioButton.toggled.connect(lambda checked: self.setVocableDirection(checked))
        self.ui.englishToGermanRadioButton.toggled.connect(lambda checked: self.setVocableDirection(not checked))
        self.ui.deleteVokabularyButton.clicked.connect(self.removeSelectedVocabularyRow)
        self.ui.finishVokabelButton.clicked.connect(self.removePreviousVokabel)
        self.ui.englishLineEdit.returnPressed.connect(self.addVocabulary)
        self.ui.germanLineEdit.returnPressed.connect(self.addVocabulary)

        # Easy Vokabel Tab
        self.ui.choose1Btn.clicked.connect(lambda: self.nextEasyVokabel(1))
        self.ui.choose2Btn.clicked.connect(lambda: self.nextEasyVokabel(2))
        self.ui.choose3Btn.clicked.connect(lambda: self.nextEasyVokabel(3))

        # Learned Vokabel Tab
        self.ui.restoreWordBtn.clicked.connect(self.restoreLearnedVokabel)

    def loadLearnedVocabularyTableWidget(self):
        self.ui.learnedVokabelTableWidget.setRowCount(0)  # Alle Einträge löschen
        # Vokabeln aus der CSV .txt Datei laden und in die learnedVokabelnTableWidget einfügen
        try:
            with open("learnedVokabeln.txt", "r", encoding="utf-8") as file:
                for line in file:
                    deutsch, englisch = line.strip().split(",")
                    rowPosition = self.ui.learnedVokabelTableWidget.rowCount()
                    self.ui.learnedVokabelTableWidget.insertRow(rowPosition)
                    self.ui.learnedVokabelTableWidget.setItem(rowPosition, 0, QTableWidgetItem(deutsch))
                    self.ui.learnedVokabelTableWidget.setItem(rowPosition, 1, QTableWidgetItem(englisch))
        except FileNotFoundError:
            pass

        # Spaltenbreite an den Inhalt anpassen
        self.ui.learnedVokabelTableWidget.resizeColumnsToContents()

    def restoreLearnedVokabel(self):
        selectedItems = self.ui.learnedVokabelTableWidget.selectedItems()
        if selectedItems:
            selectedRow = selectedItems[0].row()
            englischItem = self.ui.learnedVokabelTableWidget.item(selectedRow, 0)
            deutschItem = self.ui.learnedVokabelTableWidget.item(selectedRow, 1)
            if deutschItem and englischItem:
                deutsch = deutschItem.text()
                englisch = englischItem.text()
                vokabelHandler.addVokabelsToFile("vokabeln.txt", englisch, deutsch)
                vokabelHandler.removeVokabelFromFile("learnedVokabeln.txt", englisch)
                self.loadVocabularyTableWidget()
                self.loadLearnedVocabularyTableWidget()
            # Vokabeln neu laden
            self.vokabeln = vokabelHandler.loadVokabelsToArray("vokabeln.txt")


        else:
            QMessageBox.information(self, "Info", "Bitte wähle eine Vokabel zum Wiederherstellen aus.")

    def setVocableDirection(self, germanToEnglish: bool):
        self.germanToEnglish = germanToEnglish
        settingsHandler.setGermanToEnglish(germanToEnglish)

    def loadVocableDirectionRadioButtons(self):
        if self.germanToEnglish:
            self.ui.germanToEnglishRadioButton.setChecked(True)
        else:
            self.ui.englishToGermanRadioButton.setChecked(True)

    def closeEvent(self, event): # Muss überladen werden das das Programm beim schließen des Hauptfensters auch vollständig beendet wird
        QApplication.quit()


    def addVocabulary(self):
        # Vokabelen aus deutschLineEdit und englischLineEdit holen
        deutsch = self.ui.germanLineEdit.text()
        englisch = self.ui.englishLineEdit.text()

        # Neue Vokabel zur vokabelTableWidget hinzufügen
        rowPosition = self.ui.vokabelTableWidget.rowCount()
        self.ui.vokabelTableWidget.insertRow(rowPosition)
        self.ui.vokabelTableWidget.setItem(rowPosition, 0, QTableWidgetItem(englisch))
        self.ui.vokabelTableWidget.setItem(rowPosition, 1, QTableWidgetItem(deutsch))

        # Eingabefelder leeren
        self.ui.germanLineEdit.setText("")
        self.ui.englishLineEdit.setText("")

        # Vokabel in die vokabeln.txt datei speichern
        vokabelHandler.addVokabelsToFile("vokabeln.txt", englisch, deutsch)
        # Vokabeln neu laden
        self.vokabeln = vokabelHandler.loadVokabelsToArray("vokabeln.txt")

        # Danach englishLineEdit fokussieren
        self.ui.englishLineEdit.setFocus()

    # mit vokabelHanlder und removeVokabelFromFile die ausgewählte Vokabel aus der datei enfernen und zwar die die in vokabelTableWidget ausgewählt ist

    def removeSelectedVocabularyRow(self):
        selectedItems = self.ui.vokabelTableWidget.selectedItems()
        if selectedItems:
            selectedRow = selectedItems[0].row()
            englischItem = self.ui.vokabelTableWidget.item(selectedRow, 0)
            if englischItem:
                englisch = englischItem.text()
                vokabelHandler.removeVokabelFromFile("vokabeln.txt", englisch)
                self.ui.vokabelTableWidget.removeRow(selectedRow)
                self.vokabeln = vokabelHandler.loadVokabelsToArray("vokabeln.txt")
        else:
            QMessageBox.information(self, "Info", "Bitte wähle eine Vokabel zum Löschen aus.")


    def removePreviousVokabel(self):
        englisch = self.ui.previewEnglishLineEdit.text()
        vokabelHandler.removeVokabelFromFile("vokabeln.txt", englisch)
        self.vokabeln = vokabelHandler.loadVokabelsToArray("vokabeln.txt")
        self.loadVocabularyTableWidget()

        # Gelernte Vokabel in LearnedVokabeln.txt speichern
        deutsch = self.ui.previewDeutschLineEdit.text()

        with open("learnedVokabeln.txt", "a", encoding="utf-8") as file:
            file.write(f"{englisch},{deutsch}\n")

        self.loadLearnedVocabularyTableWidget()


        self.ui.previewEnglishLineEdit.setText("")
        self.ui.previewDeutschLineEdit.setText("")






    def loadVocabularyTableWidget(self):
        # loadVocabularyTableWidget löscht zuerst alle einträge in der vokabelTableWidget und lädt dann alle vokabeln aus der vokabeln.txt datei neu
        self.ui.vokabelTableWidget.setRowCount(0)  # Alle Einträge löschen

        # Vokabeln aus der CSV .txt Datei laden und in die vokabelTableWidget einfügen
        try:
            with open("vokabeln.txt", "r", encoding="utf-8") as file:
                for line in file:
                    deutsch, englisch = line.strip().split(",")
                    rowPosition = self.ui.vokabelTableWidget.rowCount()
                    self.ui.vokabelTableWidget.insertRow(rowPosition)
                    self.ui.vokabelTableWidget.setItem(rowPosition, 0, QTableWidgetItem(deutsch))
                    self.ui.vokabelTableWidget.setItem(rowPosition, 1, QTableWidgetItem(englisch))
        except FileNotFoundError:
            pass

    # ich hab jetzt einen anderen Tab dort wird eine Vokabel angezeigt je nachdem ob deutsch-englisch oder englisch-deutsch modus ausgewählt ist und darunter sind 3 buttons und man muss das richtige wort wählen das es weiter geht
    # es gibt eine choose1Btn, choose2Btn, choose3Btn
    # und ein vokabelEasyLabel um die Vokabel anzuzeigen

    def nextEasyVokabel(self, buttonNumber=None):

        # Normalisiere Aufruf (clicked\(\) kann kein Argument oder ein bool liefern)
        if isinstance(buttonNumber, bool) or buttonNumber is None:
            buttonNumber = 0

        # Wenn buttonNumber == 0: Neue Frage generieren
        if buttonNumber == 0:
            if not self.vokabeln:
                QMessageBox.information(self, "Info", "Keine Vokabeln verfügbar. Bitte füge Vokabeln hinzu.")
                return

            vokabel = random.choice(self.vokabeln)
            self.currentGermanVokabel = vokabel[0]
            self.currentEnglishVokabel = vokabel[1]

            if self.germanToEnglish:
                display_text = self.currentEnglishVokabel
                correct_answer = self.currentGermanVokabel
                wrong_answers = [v[0] for v in self.vokabeln if v != vokabel]
            else:
                display_text = self.currentGermanVokabel
                correct_answer = self.currentEnglishVokabel
                wrong_answers = [v[1] for v in self.vokabeln if v != vokabel]

            # Erstelle drei Auswahlmöglichkeiten (wenn möglich)
            wrong_choices = random.sample(wrong_answers, 2) if len(wrong_answers) >= 2 else wrong_answers + [""] * (
                        2 - len(wrong_answers))
            all_choices = wrong_choices + [correct_answer]
            random.shuffle(all_choices)

            # Setze UI
            self.ui.vokabelEasyLabel.setText(display_text)
            self.ui.choose1Btn.setText(all_choices[0])
            self.ui.choose2Btn.setText(all_choices[1])
            self.ui.choose3Btn.setText(all_choices[2])

            # Merken, welche Antwort korrekt ist und dass eine Frage aktiv ist
            self.easy_correct_answer = correct_answer
            self.easy_question_active = True
            self.ui.statusLabel.setText("")
            return

        # Wenn buttonNumber in {1,2,3}: Antwort prüfen
        if not getattr(self, "easy_question_active", False):
            return

        if buttonNumber == 1:
            userAnswer = self.ui.choose1Btn.text()
        elif buttonNumber == 2:
            userAnswer = self.ui.choose2Btn.text()
        elif buttonNumber == 3:
            userAnswer = self.ui.choose3Btn.text()
        else:
            return

        if userAnswer.strip().lower() == self.easy_correct_answer.strip().lower():
            self.ui.statusLabel.setText("Die Vokabel war Richtig.")
            self.ui.statusLabel.setStyleSheet("color: green;")
            self.easy_question_active = False

            # Button farbe kurz grün anzeigen
            if buttonNumber == 1:
                self.ui.choose1Btn.setStyleSheet("background-color: lightgreen;")
            elif buttonNumber == 2:
                self.ui.choose2Btn.setStyleSheet("background-color: lightgreen;")
            elif buttonNumber == 3:
                self.ui.choose3Btn.setStyleSheet("background-color: lightgreen;")


            # Nach kurzer Verzögerung automatisch nächste Frage zeigen
            QTimer.singleShot(300, lambda: self.nextEasyVokabel(0))
            # Button Farbe zurücksetzen
            QTimer.singleShot(300, lambda: self.resetEasyButtonsColors())

        else:
            # Butten deaktivieren
            if buttonNumber == 1:
                self.ui.choose1Btn.setEnabled(False)
            elif buttonNumber == 2:
                self.ui.choose2Btn.setEnabled(False)
            elif buttonNumber == 3:
                self.ui.choose3Btn.setEnabled(False)




    def resetEasyButtonsColors(self):
        self.ui.choose1Btn.setStyleSheet("background-color: none; color: none;")
        self.ui.choose2Btn.setStyleSheet("background-color: none; color: none;")
        self.ui.choose3Btn.setStyleSheet("background-color: none; color: none;")

        # Buttons wieder aktivieren
        self.ui.choose1Btn.setEnabled(True)
        self.ui.choose2Btn.setEnabled(True)
        self.ui.choose3Btn.setEnabled(True)

    def nextHardVokabel(self):
        # Prüfung der vorherigen Antwort (nur, wenn schon eine Frage gestellt wurde)
        if self.ui.vokabelLabel.text() != "Vokabel" and getattr(self, "lastAskedEnglishToGerman", None) is not None:
            userAnswer = self.ui.answerLineEdit.text().strip()
            # Erwartete Antwort richtet sich nach der Richtung, die beim Stellen der Frage galt
            if self.lastAskedEnglishToGerman:
                expected = self.currentGermanVokabel  # Frage: Englisch -> Antwort: Deutsch
            else:
                expected = self.currentEnglishVokabel  # Frage: Deutsch -> Antwort: Englisch

            if userAnswer.lower() == expected.lower():
                self.ui.statusLabel.setText("Die Vokabel war Richtig.")
                self.ui.statusLabel.setStyleSheet("color: lightgreen;")
            else:
                self.ui.statusLabel.setText(f"Die richtige Antwort war: {expected}")
                self.ui.statusLabel.setStyleSheet("color: red;")

            # Status nach 2 Sekunden zurücksetzen
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.ui.statusLabel.setText(""))

            # Vorschau der alten Vokabeln setzen
            self.ui.previewEnglishLineEdit.setText(self.currentGermanVokabel)
            self.ui.previewDeutschLineEdit.setText(self.currentEnglishVokabel)

        # Neue Vokabel auswählen und Frage anzeigen
        if self.vokabeln:
            vokabel = random.choice(self.vokabeln)
            # konsistente Speicherung der Paare
            self.currentGermanVokabel = vokabel[0]
            self.currentEnglishVokabel = vokabel[1]

            # Anzeige richtet sich nach aktuellem Modus self.englishToGerman
            if self.germanToEnglish:
                display_text = self.currentEnglishVokabel  # Frage: Englisch
            else:
                display_text = self.currentGermanVokabel  # Frage: Deutsch

            self.ui.vokabelLabel.setText(display_text)
            self.ui.answerLineEdit.setText("")

            # Merken, in welcher Richtung diese Frage gestellt wurde
            self.lastAskedEnglishToGerman = self.germanToEnglish
        else:
            QMessageBox.information(self, "Info", "Keine Vokabeln verfügbar. Bitte füge Vokabeln hinzu.")


if __name__ == "__main__":
    app = QApplication([])  # Erstellt eine Instanz der QApplication (Hauptanwendung)
    app.setQuitOnLastWindowClosed(False)  # Verhindert, dass die Anwendung beendet wird, wenn das letzte Fenster geschlossen wird
    window = MainWindow()  # Erstellt eine Instanz des Hauptfensters (MainWindow)
    window.show()  # Zeigt das Hauptfenster an

    ApplyMica(window.winId(), MicaTheme.AUTO)


    app.exec()  # Startet die Ereignisschleife der Anwendung