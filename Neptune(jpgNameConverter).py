import sys
from sys import argv
from os.path import join, dirname, abspath

# Main Dialog
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from os import chdir, getcwd, mkdir
from cv2 import IMREAD_GRAYSCALE, IMREAD_COLOR, imdecode, imwrite, getRotationMatrix2D, warpAffine
from numpy import fromfile, uint8

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relative_path)
form = resource_path("jpgConverter.ui")
mainDlg_class = uic.loadUiType(form)[0]

# mainDlg_class = uic.loadUiType("ui/jpgConverter.ui")[0]

class jpgConverter(QMainWindow, mainDlg_class):
    def __init__(self):
        super(jpgConverter, self).__init__()
        self.setupUi(self)

        # Make directory to save result files
        try:
            mkdir('./result')
        except:
            pass

        self.default_path = getcwd()
        self.rotateAngle = 0

        self.loadState = 'loading..\n'
        self.loadList = []

        self.loadBtn.clicked.connect(self.loadBtnFunction)
        self.startBtn.clicked.connect(self.startBtnFunction)
        self.resetBtn.clicked.connect(self.resetBtnFunction)

        self.err_code = None

    def loadBtnFunction(self):
        self.progressBar.setValue(0)

        filenames = QFileDialog.getOpenFileNames(self, 'Load jpg files', "",
                                            "All Files(*);; jpg Files(*.jpg);;", '/home')
        if filenames[0]:
            filenames = list(filenames)
            # filenames.reverse()           # 파일 선택 역순 정렬
            filenames.pop()
            filenames = filenames[0]

            self.progressBar.setMaximum(len(filenames))

            filecnt = 0

            for i, filename in enumerate(filenames):
                filecnt += 1
                self.loadList.append(filename)
                self.progressBar.setValue(filecnt)

                temp = filename.split('/')
                self.loadState = self.loadState + str(i) + '... ' + temp[-1] + '\n'
                self.textEdit_jpgList.setText(self.loadState)

            self.loadState = self.loadState + 'Load Complete!'
            self.textEdit_jpgList.setText(self.loadState)
            self.startBtn.setEnabled(True)

        else:
            pass

    def startBtnFunction(self):
        try:
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(len(self.loadList))
            filecnt = 0

            if str(self.textEdit_targetName.toPlainText()) != '':
                self.targetName = str(self.textEdit_targetName.toPlainText())
            else:
                self.err_code = 0
                raise ValueError

            if str(self.textEdit_rotate.toPlainText()) != '':
                self.rotateAngle = float(self.textEdit_rotate.toPlainText())

            currentState = 'converting..\n'
            chdir(self.default_path)

            for i, name in enumerate(self.loadList):
                temp = name.split('/')
                oldName = temp[-1]
                newName = self.targetName + '_' + str(i) + '.jpg'
                currentState = currentState + str(i) + ' : ' + oldName + ' => ' + newName + '\n'

                if self.checkBox_gray.isChecked():
                    ff = fromfile(name, uint8)  # 한글경로 변환
                    img = imdecode(ff, IMREAD_GRAYSCALE)  # gray Scale로 변환, img = array
                    height, width = img.shape
                else:
                    ff = fromfile(name, uint8)  # 한글경로 변환
                    img = imdecode(ff, IMREAD_COLOR)  # img = array
                    height, width, channel = img.shape

                if self.rotateAngle != 0:
                    matrix = getRotationMatrix2D((width / 2, height / 2), self.rotateAngle, 1)
                    img = warpAffine(img, matrix, (width, height))

                imwrite('./result/' + newName, img)

                self.textEdit_jpgList.setText(currentState)

                filecnt += 1
                self.progressBar.setValue(filecnt)

            currentState = currentState + 'Finish!'
            self.textEdit_jpgList.setText(currentState)
            self.loadState = 'loading..\n'
            self.loadList = []

            self.startBtn.setEnabled(False)

            reply = QMessageBox.question(self, 'Message', 'Do you want to convert more files?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                pass
            else:
                sys.exit()
        except Exception as e:
            if self.err_code == 0:
                QMessageBox.critical(self, "ERROR!!", "Set Target Name!")
            else:
                QMessageBox.critical(self, str(e))
            self.err_code = None

    def resetBtnFunction(self):
        self.textEdit_targetName.setText('')
        self.textEdit_rotate.setText('')
        self.startBtn.setEnabled(False)
        self.checkBox_gray.setChecked(False)
        self.rotateAngle = None
        self.loadList = []
        self.jpgList = []
        self.progressBar.setValue(0)

if __name__ == "__main__":
    app = QApplication(argv)
    win = jpgConverter()
    win.show()
    app.exec_()
