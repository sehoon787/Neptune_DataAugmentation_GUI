from sys import argv

# Main Dialog
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QFileDialog
from os import chdir, getcwd, rename, mkdir

mainDlg_class = uic.loadUiType("ui/txtGenerator.ui")[0]

class txtGenerator(QMainWindow, mainDlg_class):
    def __init__(self):
        super(txtGenerator, self).__init__()
        self.setupUi(self)

        # Make directory to save result files
        try:
            mkdir('./result')
        except:
            pass

        self.default_path = getcwd()

        self.loadState = 'loading..\n'
        self.loadList = []

        self.loadBtn.clicked.connect(self.loadBtnFunction)
        self.startBtn.clicked.connect(self.startBtnFunction)
        self.resetBtn.clicked.connect(self.resetBtnFunction)

        # self.textEdit_jpgList # txt만들면서 만들어지는 목록들 보여주기 => 그냥 보기좋으라고 있는거

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
        self.targetName = str(self.textEdit_targetName.toPlainText())
        currentState = 'converting..\n'
        chdir(self.default_path)

        for i, name in enumerate(self.loadList):
            temp = name.split('/')
            oldName = temp[-1]
            newName = self.targetName + '_' + str(i) + '.jpg'
            currentState = currentState + str(i) + ' : ' + oldName + ' => ' + newName + '\n'

            # path = name.replace(oldName, '')
            rename(name, 'result/' + newName)
            self.textEdit_jpgList.setText(currentState)

        currentState = currentState + 'Finish!'
        self.textEdit_jpgList.setText(currentState)
        self.loadState = 'loading..\n'
        self.loadList = []

        self.startBtn.setEnabled(False)

    def resetBtnFunction(self):
        self.startBtn.setEnabled(False)
        self.loadList = []
        self.jpgList = []
        self.progressBar.setValue(0)

if __name__ == "__main__":
    app = QApplication(argv)
    win = txtGenerator()
    win.show()
    app.exec_()
