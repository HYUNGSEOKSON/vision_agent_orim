import cv2 as cv
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog
)


class Orim(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("오림")
        self.setGeometry(200, 200, 700, 200)

        # 버튼 생성
        fileButton = QPushButton("파일", self)
        paintButton = QPushButton("페인팅", self)
        cutButton = QPushButton("오림", self)
        incButton = QPushButton("+", self)
        decButton = QPushButton("-", self)
        saveButton = QPushButton("저장", self)
        quitButton = QPushButton("나가기", self)

        # 버튼 위치 설정
        fileButton.setGeometry(10, 10, 100, 30)
        paintButton.setGeometry(110, 10, 100, 30)
        cutButton.setGeometry(210, 10, 100, 30)
        incButton.setGeometry(310, 10, 50, 30)
        decButton.setGeometry(360, 10, 50, 30)
        saveButton.setGeometry(410, 10, 100, 30)
        quitButton.setGeometry(510, 10, 100, 30)

        # 버튼 기능 연결
        fileButton.clicked.connect(self.fileOpenFunction)
        paintButton.clicked.connect(self.paintFunction)
        cutButton.clicked.connect(self.cutFunction)
        incButton.clicked.connect(self.incFunction)
        decButton.clicked.connect(self.decFunction)
        saveButton.clicked.connect(self.saveFunction)
        quitButton.clicked.connect(self.quitFunction)

        self.BrushSiz = 5  # 페인팅 붓의 크기
        self.LColor, self.RColor = (255, 0, 0), (0, 0, 255)  # 파란색 물체, 빨간색 배경

    # 파일 열기
    def fileOpenFunction(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open file", "./")
        if not fname:
            print("파일 선택을 취소했습니다.")
            return
        self.img = cv.imread(fname)
        if self.img is None:
            print("파일을 찾을 수 없거나 열 수 없습니다.")
            return
        
        self.img_show = np.copy(self.img)  # 표시용 영상
        cv.imshow("Painting", self.img_show)

        self.mask = np.zeros((self.img.shape[0], self.img.shape[1]), np.uint8)
        self.mask[:, :] = cv.GC_PR_BGD  # 모든 화소를 배경일 것 같음으로 초기화

    # 페인팅 모드 활성화
    def paintFunction(self):
        if not hasattr(self, 'img_show'):
            print("먼저 이미지를 열어야 합니다.")
            return
        cv.setMouseCallback("Painting", self.painting)

    # 페인팅 콜백 함수
    def painting(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            cv.circle(self.img_show, (x, y), self.BrushSiz, self.LColor, -1)
            cv.circle(self.mask, (x, y), self.BrushSiz, cv.GC_FGD, -1)
        elif event == cv.EVENT_RBUTTONDOWN:
            cv.circle(self.img_show, (x, y), self.BrushSiz, self.RColor, -1)
            cv.circle(self.mask, (x, y), self.BrushSiz, cv.GC_BGD, -1)
        elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_LBUTTON:
            cv.circle(self.img_show, (x, y), self.BrushSiz, self.LColor, -1)
            cv.circle(self.mask, (x, y), self.BrushSiz, cv.GC_FGD, -1)
        elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_RBUTTON:
            cv.circle(self.img_show, (x, y), self.BrushSiz, self.RColor, -1)
            cv.circle(self.mask, (x, y), self.BrushSiz, cv.GC_BGD, -1)

        cv.imshow("Painting", self.img_show)

    # 오림 기능 (grabCut)
    def cutFunction(self):
        if not hasattr(self, 'img') or not hasattr(self, 'mask'):
            print("먼저 이미지를 열어야 합니다.")
            return

        background = np.zeros((1, 65), np.float64)
        foreground = np.zeros((1, 65), np.float64)
        cv.grabCut(self.img, self.mask, None, background, foreground, 5, cv.GC_INIT_WITH_MASK)
        mask2 = np.where((self.mask == 2) | (self.mask == 0), 0, 1).astype("uint8")
        self.grabImg = self.img * mask2[:, :, np.newaxis]
        cv.imshow("Scissoring", self.grabImg)

    # 브러시 크기 증가
    def incFunction(self):
        self.BrushSiz = min(20, self.BrushSiz + 1)
        print(f"브러시 크기 증가: {self.BrushSiz}")

    # 브러시 크기 감소
    def decFunction(self):
        self.BrushSiz = max(1, self.BrushSiz - 1)
        print(f"브러시 크기 감소: {self.BrushSiz}")

    # 오려낸 이미지 저장
    def saveFunction(self):
        if not hasattr(self, 'grabImg'):
            print("오려낸 이미지가 없습니다.")
            return
        fname, _ = QFileDialog.getSaveFileName(self, "파일 저장", "./", "Images (*.png *.xpm *.jpg)")
        if fname:
            cv.imwrite(fname, self.grabImg)
            print("파일이 저장되었습니다.")

    # 프로그램 종료
    def quitFunction(self):
        cv.destroyAllWindows()
        QApplication.quit()


# 애플리케이션 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Orim()
    win.show()
    sys.exit(app.exec())
