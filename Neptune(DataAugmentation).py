import sys
from sys import argv
from os.path import join, dirname, abspath
from os import chdir, getcwd, mkdir
from shutil import copy

# Main Dialog
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon

# Image Control
from cv2 import IMREAD_GRAYSCALE, IMREAD_COLOR, imdecode
from cv2 import getRotationMatrix2D, warpAffine
from cv2 import filter2D, blur, GaussianBlur, medianBlur, bilateralFilter
from cv2 import remap, INTER_CUBIC, BORDER_DEFAULT
from cv2 import cartToPolar, polarToCart, INTER_LINEAR
from cv2 import flip, cvtColor, COLOR_BGR2RGB, COLOR_RGB2BGR
from cv2 import IMWRITE_JPEG_QUALITY, imwrite

from random import randint
from numpy import fromfile, uint8, float32, abs
from numpy import ones, sin, indices
from math import ceil, atan2, sqrt, pow, pi, radians, cos
from math import sin as msin


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relative_path)
form = resource_path("jpgConverter.ui")
mainDlg_class = uic.loadUiType(form)[0]

class jpgConverter(QMainWindow, mainDlg_class):
    def __init__(self):
        super(jpgConverter, self).__init__()
        self.setupUi(self)

        icon = resource_path("neptune.png")
        self.setWindowIcon(QIcon(icon))

        self.default_path = getcwd()
        self.rotateAngle = 0

        self.loadState = 'loading..\n'
        self.loadList = []

        # LPF 기반 bluring default
        self.option = 1
        self.n = 3

        # 삼각함수를 이용한 비선형 리매핑 default
        self.ampVal = 10
        self.waveFreqVal = 32

        # 오목/볼록 렌즈 왜곡 리매핑 default
        self.expVal = 2
        self.scaleVal = 1

        # 이미지 Quality(File Size) 조절 default
        self.qualityVal = 80

        self.loadBtn.clicked.connect(self.loadBtnFunction)
        self.startBtn.clicked.connect(self.startBtnFunction)
        self.preViewBtn.clicked.connect(self.preViewBtnFunction)
        self.resetBtn.clicked.connect(self.resetBtnFunction)

        self.iqdef_rbtn.clicked.connect(self.rBtnCtrl)
        self.quality_rbtn.clicked.connect(self.rBtnCtrl)

        self.checkBox_blur.clicked.connect(self.ChkBoxCtrl)
        self.checkBox_nm.clicked.connect(self.ChkBoxCtrl)
        self.checkBox_ld.clicked.connect(self.ChkBoxCtrl)
        self.checkBox_flip.clicked.connect(self.ChkBoxCtrl)

        # oldName = 'sampleOriginal.jpg'
        # newName = 'sampleResult.jpg'
        self.sampleOriginal = resource_path("sampleOriginal.jpg")
        self.sampleResult = resource_path("sampleResult.jpg")

        self.figOriginal.setPixmap(QPixmap(self.sampleOriginal))
        self.figOriginal.setScaledContents(True)

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
            # Make directory to save result files
            try:
                mkdir('./result')
            except:
                pass

            self.progressBar.setValue(0)
            self.progressBar.setMaximum(len(self.loadList))
            filecnt = 0

            if str(self.textEdit_targetName.toPlainText()) != '':
                self.targetName = str(self.textEdit_targetName.toPlainText())
            else:
                self.targetName = None
                self.err_code = 0
                10/0

            if str(self.textEdit_rotate.toPlainText()) != '':
                self.err_code = 4
                self.rotateAngle = abs(float(self.textEdit_rotate.toPlainText()))
            else:
                self.rotateAngle = 0
            self.err_code = None

            currentState = 'converting..\n'
            chdir(self.default_path)

            for i, name in enumerate(self.loadList):
                temp = name.split('/')
                oldName = temp[-1]
                if self.targetName != None:
                    newName = self.targetName + '_' + str(i) + '.jpg'
                    currentState = currentState + str(i) + ' : ' + oldName + ' => ' + newName + '\n'

                    try:
                        self.oldTxtName = name[:-4] + '.txt'
                        self.newTxtName = './result/' + newName[:-4] + '.txt'
                        copy(self.oldTxtName, self.newTxtName)
                    except:
                        pass

                else:
                    newName = oldName[:-4] + '.jpg'
                    currentState = currentState + str(i) + ' : ' + oldName + ' => ' + newName + '\n'

                ff = fromfile(name, uint8)  # 한글경로 변환

                # gray scale 전환 여부 결정
                if self.gray_rbtn.isChecked():
                    img = imdecode(ff, IMREAD_GRAYSCALE)
                else:
                    img = imdecode(ff, IMREAD_COLOR)

                # LPF 기반 bluring
                if self.checkBox_blur.isChecked():
                    if self.comboBox_blur.currentText() == 'Convolution':
                        self.option = 0
                        self.n=3
                    elif self.comboBox_blur.currentText() == 'Averaging Blurring':
                        self.option = 1
                        self.n=15
                    elif self.comboBox_blur.currentText() == 'Gaussian Blurring':
                        self.option = 2
                        self.n = 15
                    elif self.comboBox_blur.currentText() == 'Median Blurring':
                        self.option = 3
                        self.n = 15
                    elif self.comboBox_blur.currentText() == 'Bilateral Filtering':
                        self.option = 4
                        self.n = 15

                    if self.textEdit_nVal.toPlainText() != '':
                        self.err_code = 1
                        self.n = int(float(self.textEdit_nVal.toPlainText()))
                    self.err_code = None

                    img = self.BlurImage(img=img, option=self.option, n=self.n)

                # 삼각함수를 이용한 비선형 리매핑
                if self.checkBox_nm.isChecked():
                    self.ampVal = 10
                    self.waveFreqVal = 32

                    if self.textEdit_ampVal.toPlainText() != '':
                        self.err_code = 2
                        self.ampVal = float(self.textEdit_ampVal.toPlainText())
                    if self.textEdit_waveFreqVal.toPlainText() != '':
                        self.err_code = 2
                        self.waveFreqVal = float(self.textEdit_waveFreqVal.toPlainText())
                    self.err_code = None

                    img = self.NonlinearMappingImage(img=img, amp=self.ampVal, waveFreq=self.waveFreqVal)

                # 오목/볼록 렌즈 왜곡 리매핑
                if self.checkBox_ld.isChecked():
                    self.expVal = 2
                    self.scaleVal = 1

                    if self.textEdit_expVal.toPlainText() != '':
                        self.err_code = 3
                        self.expVal = float(self.textEdit_expVal.toPlainText())
                    if self.textEdit_scaleVal.toPlainText() != '':
                        self.err_code = 3
                        self.scaleVal = float(self.textEdit_scaleVal.toPlainText())
                    self.err_code = None

                    img = self.LensDistortionImage(img=img, exp=self.expVal, scale=self.scaleVal)

                # 이미지 Rotate
                if self.rotateAngle:
                    img = self.RotateImage(fileName=self.newTxtName, img=img, angle=self.rotateAngle)
                else:
                    pass
                    # self.rotateAngle = 0
                    # img = self.RotateImage(img, self.rotateAngle)

                # Salt & Pepper noise
                if self.checkBox_snp.isChecked():
                    img = self.SaltPepper(img)
                else:
                    pass

                # Flip Image
                if self.checkBox_flip.isChecked():
                    if self.h_rBtn.isChecked():  # 좌우
                        img = self.FlipImage(img, 1)
                    elif self.v_rBtn.isChecked():  # 상하
                        img = self.FlipImage(img, 0)
                    else:  # 상하 좌우
                        img = self.FlipImage(img, -1)

                # 이미지 Quality(File Size) 조절
                if self.checkBox_iq.isChecked():
                    if self.iqdef_rbtn.isChecked():
                        self.qualityVal = 80
                    else:
                        self.qualityVal = float(self.textEdit_qualityVal.toPlainText())

                    imwrite('./result/' + newName, img, [int(IMWRITE_JPEG_QUALITY), self.qualityVal])
                else:
                    imwrite('./result/' + newName, img)

                self.textEdit_jpgList.setText(currentState)

                filecnt += 1
                self.progressBar.setValue(filecnt)

            currentState = currentState + 'Finish!'
            self.textEdit_jpgList.setText(currentState)
            self.loadState = 'loading..\n'
            # self.loadList = []

            reply = QMessageBox.question(self, 'Message', 'Do you want to convert more files?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                pass
            else:
                sys.exit()
        except Exception as e:
            if self.err_code == 0:
                QMessageBox.critical(self, "ERROR!!", "Set Target Name!")
            elif self.err_code == 1:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Bluring)")
            elif self.err_code == 2:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Nonlinear Mapping)")
            elif self.err_code == 3:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Lens Distortion)")
            elif self.err_code == 4:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Rotate)")
                self.textEdit_rotate.setText('')
                self.rotateAngle = 0
            else:
                QMessageBox.critical(self, "ERROR!!", str(e))
            self.err_code = None

    def preViewBtnFunction(self):
        try:
            if str(self.textEdit_rotate.toPlainText()) != '':
                self.err_code = 4
                self.rotateAngle = abs(float(self.textEdit_rotate.toPlainText()))
            else:
                self.rotateAngle = 0
            self.err_code = None

            oldName = self.sampleOriginal
            newName = self.sampleResult

            ff = fromfile(oldName, uint8)  # 한글경로 변환

            # gray scale 전환 여부 결정
            if self.gray_rbtn.isChecked():
                img = imdecode(ff, IMREAD_GRAYSCALE)
            else:
                img = imdecode(ff, IMREAD_COLOR)

            # LPF 기반 bluring
            if self.checkBox_blur.isChecked():
                if self.comboBox_blur.currentText() == 'Convolution':
                    self.option = 0
                    self.n = 3
                elif self.comboBox_blur.currentText() == 'Averaging Blurring':
                    self.option = 1
                    self.n = 15
                elif self.comboBox_blur.currentText() == 'Gaussian Blurring':
                    self.option = 2
                    self.n = 15
                elif self.comboBox_blur.currentText() == 'Median Blurring':
                    self.option = 3
                    self.n = 15
                elif self.comboBox_blur.currentText() == 'Bilateral Filtering':
                    self.option = 4
                    self.n = 15

                if self.textEdit_nVal.toPlainText() != '':
                    self.err_code = 1
                    self.n = int(float(self.textEdit_nVal.toPlainText()))
                self.err_code = None

                img = self.BlurImage(img=img, option=self.option, n=self.n)

            # 삼각함수를 이용한 비선형 리매핑
            if self.checkBox_nm.isChecked():
                self.ampVal = 10
                self.waveFreqVal = 32

                if self.textEdit_ampVal.toPlainText() != '':
                    self.err_code = 2
                    self.ampVal = float(self.textEdit_ampVal.toPlainText())
                if self.textEdit_waveFreqVal.toPlainText() != '':
                    self.err_code = 2
                    self.waveFreqVal = float(self.textEdit_waveFreqVal.toPlainText())
                self.err_code = None

                img = self.NonlinearMappingImage(img=img, amp=self.ampVal, waveFreq=self.waveFreqVal)

            # 오목/볼록 렌즈 왜곡 리매핑
            if self.checkBox_ld.isChecked():
                self.expVal = 2
                self.scaleVal = 1

                if self.textEdit_expVal.toPlainText() != '':
                    self.err_code = 3
                    self.expVal = float(self.textEdit_expVal.toPlainText())
                if self.textEdit_scaleVal.toPlainText() != '':
                    self.err_code = 3
                    self.scaleVal = float(self.textEdit_scaleVal.toPlainText())
                self.err_code = None

                img = self.LensDistortionImage(img=img, exp=self.expVal, scale=self.scaleVal)

            # Image Rotate
            if self.rotateAngle:
                img = self.RotateImage(fileName=None, img=img, angle=self.rotateAngle)
            else:
                pass

            # Salt & Pepper noise
            if self.checkBox_snp.isChecked():
                img = self.SaltPepper(img)
            else:
                pass

            # Flip Image
            if self.checkBox_flip.isChecked():
                if self.h_rBtn.isChecked():  # 좌우
                    img = self.FlipImage(img, 1)
                elif self.v_rBtn.isChecked():  # 상하
                    img = self.FlipImage(img, 0)
                else:  # 상하 좌우
                    img = self.FlipImage(img, -1)

            # 이미지 Quality(File Size) 조절
            if self.checkBox_iq.isChecked():
                if self.iqdef_rbtn.isChecked():
                    self.qualityVal = 80
                else:
                    self.qualityVal = float(self.textEdit_qualityVal.toPlainText())

                imwrite(newName, img, [int(IMWRITE_JPEG_QUALITY), self.qualityVal])
            else:
                imwrite(newName, img)

            self.figResult.setPixmap(QPixmap(self.sampleResult))
            self.figResult.setScaledContents(True)

        except Exception as e:
            if self.err_code == 1:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Bluring)")
            elif self.err_code == 2:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Nonlinear Mapping)")
            elif self.err_code == 3:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Lens Distortion)")
            elif self.err_code == 4:
                QMessageBox.critical(self, "ERROR!!", "Set Number Not text! (Rotate)")
                self.textEdit_rotate.setText('')
                self.rotateAngle = 0
            else:
                QMessageBox.critical(self, "ERROR!!", str(e))
            self.err_code = None

    def resetBtnFunction(self):
        self.textEdit_targetName.setText('')
        self.textEdit_rotate.setText('0')
        self.startBtn.setEnabled(False)

        self.raw_rbtn.setChecked(True)
        self.iqdef_rbtn.setChecked(True)

        self.comboBox_blur.setEnabled(False)
        self.comboBox_blur.setCurrentIndex(1)

        self.checkBox_blur.setChecked(False)
        self.checkBox_iq.setChecked(False)
        self.checkBox_nm.setChecked(False)
        self.checkBox_ld.setChecked(False)

        self.textEdit_nVal.setEnabled(False)
        self.textEdit_qualityVal.setEnabled(False)
        self.textEdit_ampVal.setEnabled(False)
        self.textEdit_waveFreqVal.setEnabled(False)
        self.textEdit_expVal.setEnabled(False)
        self.textEdit_scaleVal.setEnabled(False)

        self.checkBox_flip.setChecked(False)
        self.h_rBtn.setChecked(True)
        self.h_rBtn.setEnabled(False)
        self.v_rBtn.setEnabled(False)
        self.vh_rBtn.setEnabled(False)

        self.textEdit_nVal.setText('15')
        self.textEdit_qualityVal.setText('')
        self.textEdit_ampVal.setText('10')
        self.textEdit_waveFreqVal.setText('32')
        self.textEdit_expVal.setText('2')
        self.textEdit_scaleVal.setText('1')

        self.rotateAngle = None
        self.loadList = []
        self.progressBar.setValue(0)

    def SaltPepper(self, img):
        # Getting the dimensions of the image
        if img.ndim > 2:    # color
            height, width, _ = img.shape
        else:               # gray scale
            height, width = img.shape

        # Randomly pick some pixels in the image
        # Pick a random number between height*width/80 and height*width/10
        number_of_pixels = randint(int(height * width / 100), int(height * width / 10))

        for i in range(number_of_pixels):
            # Pick a random y coordinate
            y_coord = randint(0, height - 1)

            # Pick a random x coordinate
            x_coord = randint(0, width - 1)

            if img.ndim > 2:
                img[y_coord][x_coord] = [randint(0, 255), randint(0, 255), randint(0, 255)]
            else:
                # Color that pixel to white
                img[y_coord][x_coord] = 255

        # Randomly pick some pixels in image
        # Pick a random number between height*width/80 and height*width/10
        for i in range(number_of_pixels):
            # Pick a random y coordinate
            y_coord = randint(0, height - 1)

            # Pick a random x coordinate
            x_coord = randint(0, width - 1)

            if img.ndim > 2:
                img[y_coord][x_coord] = [randint(0, 255), randint(0, 255), randint(0, 255)]
            else:
                # Color that pixel to white
                img[y_coord][x_coord] = 0

        return img

    def BlurImage(self, img, option=0, n=3):
        '''
        :param img: image
        :param option: 0: Convolution, 1: Averaging Blurring, 2: Gaussian Blurring, 3: Median Blurring, 4: Bilateral Filtering
        :param n: size
        '''
        if option == 0:
            # 컨볼루션 계산은 커널과 이미지 상에 대응되는 값끼리 곱한 후, 모두 더하여 구함
            # 이 결과값을 결과 영상의 현재 위치에 기록
            # default 3
            kernel = ones((n, n), float32) / 25
            result = filter2D(img, -1, kernel)
        elif option == 1:
            # 이웃 픽셀의 평균을 결과 이미지의 픽셀값으로하는 평균 블러링
            # 에지 포함해서 전체적으로 블러링
            # default 15
            result = blur(img, (n, n))
        elif option == 2:
            # 모든 픽셀에 똑같은 가중치를 부여했던 평균 블러링과 달리 가우시안 블러링은 중심에 있는 픽셀에 높은 가중치를 부여
            # 캐니(Canny)로 에지를 검출하기전에 노이즈를 제거하기 위해 사용
            # default 15
            result = GaussianBlur(img, (n, n), 0)
        elif option == 3:
            # 관심화소 주변으로 지정한 커널 크기( 5 x 5) 내의 픽셀을 크기순으로 정렬한 후 중간값을 뽑아서 픽셀값으로 사용
            # default 15
            result = medianBlur(img, n)
        elif option == 4:
            # 에지를 보존하면서 노이즈를 감소시킬수 있는 방법
            # default 15
            result = bilateralFilter(img, n, 75, 75)
        return result

    def NonlinearMappingImage(self, img, amp=10, waveFreq=32):
        h, w = img.shape[:2]  # 입력 영상의 높이와 넓이 정보 추출

        # np.indice는 행렬의 인덱스값 x좌표값 y좌표값을 따로따로 행렬의 형태로 변환해줌
        map2, map1 = indices((h, w), dtype=float32)

        # y좌표에 sin함수를 줬는데 파도처럼 꿀렁꿀렁하게 하기 위해서
        # y좌표 값에 10픽셀만큼 꿀렁꿀렁 거릴 수 있도록.
        # sin함수가 x좌표를 이용해서 파도를 만들기 위해 map1을 줌
        # 적당한 값을 나눠서 여러번 꿀렁꿀렁 거리게
        map2 = map2 + amp * sin(map1 / waveFreq)

        # borderMode는 근방의 색깔로 대칭되게 해서 채워줌, 기본값은 빈 공간을 검은색으로 표현
        result = remap(img, map1, map2, INTER_CUBIC, borderMode=BORDER_DEFAULT)

        return result

    def LensDistortionImage(self, img, exp=2, scale=1):
        '''
        :param img: image
        :param exp: 볼록, 오목 지수 (오목 : 0.1 ~ 1, 볼록 : 1.1~) => 1보다 작으면 오목 렌즈 효과를 내고, 1보다 크면 볼록 렌즈 효과
        :param scale: 변환 영역 크기 (0 ~ 1)
        '''
        rows, cols = img.shape[:2]

        # 매핑 배열 생성 ---②
        mapy, mapx = indices((rows, cols), dtype=float32)

        # 좌상단 기준좌표에서 -1~1로 정규화된 중심점 기준 좌표로 변경 ---③
        mapx = 2 * mapx / (cols - 1) - 1
        mapy = 2 * mapy / (rows - 1) - 1

        # 직교좌표를 극 좌표로 변환 ---④
        r, theta = cartToPolar(mapx, mapy)

        # 왜곡 영역만 중심확대/축소 지수 적용 ---⑤
        r[r < scale] = r[r < scale] ** exp

        # 극 좌표를 직교좌표로 변환 ---⑥
        mapx, mapy = polarToCart(r, theta)

        # 중심점 기준에서 좌상단 기준으로 변경 ---⑦
        mapx = ((mapx + 1) * cols - 1) / 2
        mapy = ((mapy + 1) * rows - 1) / 2
        # 재매핑 변환
        result = remap(img, mapx, mapy, INTER_LINEAR)

        return result

    def FlipImage(self, img, mode):
        '''
        :param mode: 1은 좌우 반전, 0은 상하 반전, -1은 상하 좌우 반전
        '''
        # Getting the dimensions of the image
        imgDim = img.ndim
        if imgDim > 2:    # color
            img = cvtColor(img, COLOR_BGR2RGB)
        else:               # gray scale
            pass

        result = flip(img, mode)

        if imgDim > 2:    # color
            result = cvtColor(result, COLOR_RGB2BGR)
        else:               # gray scale
            pass

        return result

    def rBtnCtrl(self):
        if self.quality_rbtn.isChecked():
            self.textEdit_qualityVal.setEnabled(True)
        else:
            self.textEdit_qualityVal.setEnabled(False)

    def ChkBoxCtrl(self):
        if self.checkBox_blur.isChecked():
            self.comboBox_blur.setEnabled(True)
            self.textEdit_nVal.setEnabled(True)
        else:
            self.comboBox_blur.setEnabled(False)
            self.textEdit_nVal.setEnabled(False)

        if self.checkBox_nm.isChecked():
            self.textEdit_ampVal.setEnabled(True)
            self.textEdit_waveFreqVal.setEnabled(True)
        else:
            self.textEdit_ampVal.setEnabled(False)
            self.textEdit_waveFreqVal.setEnabled(False)

        if self.checkBox_ld.isChecked():
            self.textEdit_expVal.setEnabled(True)
            self.textEdit_scaleVal.setEnabled(True)
        else:
            self.textEdit_expVal.setEnabled(False)
            self.textEdit_scaleVal.setEnabled(False)

        if self.checkBox_flip.isChecked():
            self.v_rBtn.setEnabled(True)
            self.h_rBtn.setEnabled(True)
            self.vh_rBtn.setEnabled(True)
        else:
            self.v_rBtn.setEnabled(False)
            self.h_rBtn.setEnabled(False)
            self.vh_rBtn.setEnabled(False)

    # rotate and make txt label
    def RotateImage(self, fileName, img, angle):
        if img.ndim > 2:
            height, width, channel = img.shape
        else:
            height, width = img.shape

        matrix = getRotationMatrix2D((width / 2, height / 2), angle, 1)
        result = warpAffine(img, matrix, (width, height))

        if fileName:
            f_r = open(self.oldTxtName, 'r')
            lines = f_r.readlines()

            for line in lines:  # get each line's point pos
                # line_split[0] : class, [1] : label_rect_center_x, [2] : label_rect_center_y, [3] : label_rect_width, [4] label_rect_height
                # [1] ~ [3] is percent -> multiple with img's size
                line_split_list = line.split(' ')
                line_split = [float(x) for x in line_split_list]

                img_center = width / 2, height / 2
                labelRect_center = line_split[1] * width, line_split[2] * height

                # draw rect center & labelRect
                rect_points = self.createRect(labelRect_center, line_split[3] * width, line_split[4] * height)
                labelRect_status = self.getPointStatus(labelRect_center, rect_points[0])

                # labelRect center movement circle
                labelRect_center_status = self.getPointStatus(img_center, labelRect_center)

                # +180 : status's degree criterion is left to up, but sin/cos criterion is right to down
                RotateRect_center = self.getRotatedPoints(img_center, labelRect_center_status[0],
                                                     (labelRect_center_status[1] + 180 - angle) % 360)

                RotateRect_degree = (
                    (labelRect_status[1] + 180 - angle) % 360,
                    (180 - labelRect_status[1] - angle) % 360,
                    (360 - labelRect_status[1] - angle) % 360,
                    (labelRect_status[1] - angle) % 360
                )

                RotatedRect_points = self.getRotatedPoints(RotateRect_center, labelRect_status[0], RotateRect_degree)

                boundingRect_points = self.getBoundingPoins(RotatedRect_points)

                # for get percent size value, divide with w, h
                boundingRect = (
                    round(RotateRect_center[0] / width, 6),
                    round(RotateRect_center[1] / height, 6),
                    round((boundingRect_points[0][0] - boundingRect_points[1][0]) / width, 6),
                    round((boundingRect_points[0][1] - boundingRect_points[1][1]) / height, 6)
                )
                f_w = open(fileName, 'w')
                f_w.write(str(int(line_split[0])) + ' ' + str(boundingRect[0]) + ' ' + str(boundingRect[1]) + ' ' +
                          str(boundingRect[2]) + ' ' + str(boundingRect[3]) + '\n')
            f_r.close()
            f_w.close()

        return result

    def createRect(self, center, width, height):
        # up-left
        rect_point1 = ceil(center[0] - width / 2), ceil(center[1] - height / 2)
        # down-left
        rect_point2 = ceil(center[0] - width / 2), ceil(center[1] + height / 2)
        # up-right
        rect_point3 = ceil(center[0] + width / 2), ceil(center[1] - height / 2)
        # down-left
        rect_point4 = ceil(center[0] + width / 2), ceil(center[1] + height / 2)

        rect_points = rect_point1, rect_point2, rect_point3, rect_point4

        return rect_points

    def getPointStatus(self, center, point1):
        # center to point1 radius
        point_radius = sqrt(pow(center[0] - point1[0], 2) + pow(center[1] - point1[1], 2))
        point_degree = atan2(center[1] - point1[1], center[0] - point1[0]) * 180 / pi

        point_status = point_radius, point_degree

        return point_status

    def getRotatedPoints(self, center, radius, degree):
        rotated_points = []

        if isinstance(degree, float):
            rotate_radian = radians(degree)
            rotated_points = center[0] + (cos(rotate_radian) * radius), center[1] + (
                        msin(rotate_radian) * radius)

        else:
            for i in range(0, len(degree)):
                rotate_radian = radians(degree[i])

                rect_point = center[0] + (cos(rotate_radian) * radius), center[1] + (
                            msin(rotate_radian) * radius)

                rotated_points.append(rect_point)

        return rotated_points

    def getBoundingPoins(self, points):
        max_x = max(points[0][0], points[1][0], points[2][0], points[3][0])
        max_y = max(points[0][1], points[1][1], points[2][1], points[3][1])

        min_x = min(points[0][0], points[1][0], points[2][0], points[3][0])
        min_y = min(points[0][1], points[1][1], points[2][1], points[3][1])

        start = max_x, max_y
        end = min_x, min_y

        bounding_points = start, end

        return bounding_points


if __name__ == "__main__":
    app = QApplication(argv)
    win = jpgConverter()
    win.show()
    app.exec_()
