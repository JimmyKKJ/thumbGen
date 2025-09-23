from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QColorDialog, QFileDialog, QRadioButton,
)
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QPixmap
from PySide6.QtCore import Qt
from enum import Enum
from utils import misc, img, gui
import pathlib

class ImageSelector(QWidget):
    """ 画像ファイル選択用ウィジェット """
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.__label_file = QLabel("元画像", self)

        self.__input_file = QLineEdit(
            self, placeholderText="ファイルパス", readOnly=True
        )
        self.__input_file.setFixedWidth(200)
        self.__input_file.editingFinished.connect(
            lambda: self.__check_file(parent)
        )

        self.__btn_file = QPushButton("ファイルを開く", self)
        self.__btn_file.setFixedWidth(100)
        self.__btn_file.clicked.connect(
            lambda: self.__file_dialog(parent)
        )

        vbox = QVBoxLayout()
        vbox.addWidget(self.__label_file)

        hbox = QHBoxLayout()
        hbox.addWidget(self.__input_file)
        hbox.addWidget(self.__btn_file)
        vbox.addLayout(hbox)

        self.setLayout(vbox)


    def __file_dialog(self, parent):
        """ファイルを選択するダイアログを表示する"""
        caption = "画像を選択"
        dir = ''
        filter = "Image Files (*.png *.jpg *.bmp)"
        selectedFilter = ''
        fileName = QFileDialog.getOpenFileName(
            None, caption, str(dir), filter, selectedFilter
        )
        file = fileName[0]
        print(file)
        self.__input_file.setText(file)
        self.__check_file(parent)


    def __check_file(self, parent):
        """選択されたファイルが存在するか確認する"""
        file = self.__input_file.text()
        if not pathlib.Path(file).is_file():
            print("ファイルが存在しません")
            self.__input_file.setText("")
            parent.file_info.setText("ファイルが存在しません")
            parent.file_info.setStyleSheet(
                WarningIndicatorStyle.WARNING.value
            )
        else:   
            parent.file_info.setText("画像が選択されました")
            parent.file_info.setStyleSheet(
                WarningIndicatorStyle.SUCCESS.value
            )
            parent.update_preview()

    
    def get_path(self) -> str:
        """選択されたファイルのパスを取得する

        Returns:
            str: ファイルのパス
        """
        return str(pathlib.Path(self.__input_file.text()))

        

class ColorSelector(QWidget):
    """ 色選択用ウィジェット """
    def __init__(self, parent: 'gui.MainWindow'):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        super().__init__(parent)

        # 矩形の色
        self.__label_color = QLabel("矩形の色", self)

        # 色プレビュー
        self.__preview_rect = RectangleWidget(self)
        self.__preview_rect.setFixedSize(40, 20)

        # 色入力欄 RGB
        self.__label_red = QLabel("R", self)
        self.__label_green = QLabel("G", self)
        self.__label_blue = QLabel("B", self)
        self.__label_alpha = QLabel("A", self)

        self.__input_red = RGBLineEdit('0', self)
        self.__input_green = RGBLineEdit('110', self)
        self.__input_blue = RGBLineEdit('79', self)
        self.__input_alpha = RGBLineEdit('255', self)
        
        self.__input_red.editingFinished.connect(lambda: self.__set_color_rgba(parent))
        self.__input_green.editingFinished.connect(lambda: self.__set_color_rgba(parent))
        self.__input_blue.editingFinished.connect(lambda: self.__set_color_rgba(parent))
        self.__input_alpha.editingFinished.connect(lambda: self.__set_color_rgba(parent))

        # 色入力欄 HEX
        self.__label_hash = QLabel("#", self)

        self.__input_hex = LineEditClickable(
            self, placeholderText='006E4F', maxLength=6,
            inputMask='HHHHHH;'
        )
        self.__input_hex.setFixedWidth(80)
        self.__input_hex.editingFinished.connect(lambda: self.__set_color_hex(parent))

        self.__label_opacity = QLabel("不透明度", self)
        self.__label_percent = QLabel("%", self)

        self.__input_opacity = LineEditClickable(
            self, placeholderText='100', maxLength=3,
            inputMask='000;'
        )
        self.__input_opacity.setFixedWidth(40)
        self.__input_opacity.setText('100')
        self.__input_opacity.editingFinished.connect(lambda: self.__set_color_hex(parent))

        # 色選択ボタン
        self.__btn_color = QPushButton("色を選択")
        self.__btn_color.clicked.connect(lambda: self.__color_dialog(parent))

        # レイアウト
        vbox = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(self.__label_color)
        top.addWidget(self.__preview_rect)

        mid = QHBoxLayout()
        mid.addWidget(self.__label_red)
        mid.addWidget(self.__input_red)
        mid.addWidget(self.__label_green)
        mid.addWidget(self.__input_green)
        mid.addWidget(self.__label_blue)
        mid.addWidget(self.__input_blue)
        mid.addWidget(self.__label_alpha)
        mid.addWidget(self.__input_alpha)
        mid.addStretch()

        bottom = QHBoxLayout()
        bottom.addWidget(self.__label_hash)
        bottom.addWidget(self.__input_hex)
        bottom.addWidget(self.__label_opacity)
        bottom.addWidget(self.__input_opacity)
        bottom.addWidget(self.__label_percent)
        bottom.addStretch()
        bottom.addWidget(self.__btn_color)

        vbox.addLayout(top)
        vbox.addLayout(mid)
        vbox.addLayout(bottom)

        self.setLayout(vbox)


    def __color_dialog(self, parent: 'gui.MainWindow'):
        """色を選択するダイアログを表示する

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name().strip('#').upper()
            self.__input_hex.setText(hex_color)
            self.__set_color_hex(parent)


    def __set_color_hex(self, parent: 'gui.MainWindow'):
        """色を設定する (HEX)

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        color = self.__input_hex.text() # 先頭の#は含まない
        opacity = int(self.__input_opacity.text() or '100') / 100.0
        self.__input_hex.setText(color)

        # RGB値の更新
        r, g, b = misc.rgb(color)
        a = int(opacity * 255)
        self.__input_red.setText(str(r))
        self.__input_green.setText(str(g))
        self.__input_blue.setText(str(b))
        self.__input_alpha.setText(str(a))

        self.__check_color(parent)
        self.__preview_rect.set_color((r, g, b, a))

    
    def __set_color_rgba(self, parent: 'gui.MainWindow'):
        """色を設定する (RGBA)
        
        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        r = self.__input_red.text() or '0'
        g = self.__input_green.text() or '0'
        b = self.__input_blue.text() or '0'
        a = self.__input_alpha.text() or '255'

        try:
            r_int, g_int, b_int, a_int = [int(c) for c in (r, g, b, a)]
        except: return

        self.__check_color(parent)
        hex = f'{r_int:02X}{g_int:02X}{b_int:02X}' # '#'を含まない
        self.__input_hex.setText(hex)
        self.__preview_rect.set_color((r_int, g_int, b_int, a_int))

    
    def __check_color(self, parent: 'gui.MainWindow'):
        """色を確認する

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        try:
            r = int(self.__input_red.text())
            g = int(self.__input_green.text())
            b = int(self.__input_blue.text())
            a = int(self.__input_alpha.text())
        except:
            parent.color_info.setText('色が正しく設定されていません')
            parent.color_info.setStyleSheet(
                WarningIndicatorStyle.WARNING.value
            )
            return

        if not all(0 <= c <= 255 for c in (r, g, b, a)):
            parent.color_info.setText('色が正しく設定されていません')
            parent.color_info.setStyleSheet(
                WarningIndicatorStyle.WARNING.value
            )
            return
        
        parent.color_info.setText('視認性の高い色であるかを確認してください')
        parent.color_info.setStyleSheet(
            WarningIndicatorStyle.INFO.value
        )
        


    def get_rgba(self) -> tuple[int, int, int, int]:
        """入力したRGB

        Returns:
            tuple[int, int, int, int]: RGBAの組
        """
        try:
            r = int(self.__input_red.text())
            g = int(self.__input_green.text())
            b = int(self.__input_blue.text())
            a = int(self.__input_alpha.text())
        except:
            r = g = b = 0
            a = 255
        return (r, g, b, a)
    

    def get_hex(self) -> str:
        """入力したHEXコード

        Returns:
            str: HEXコード (例: 'FF0000' for red)
        """
        hex = self.__input_hex.text() or '000000'
        if len(hex) != 6:
            hex = '000000'
        return hex



class OffsetSelector(QWidget):
    """ オフセット選択用ウィジェット """
    
    def __init__(self, parent: 'gui.MainWindow'):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        super().__init__(parent)
        self.__offset = 0

        self.__label_offset = QLabel("オフセット", self)
        self.__btn_minus100 = OffsetButton(-100)
        self.__btn_minus10 = OffsetButton(-10)
        self.__btn_minus1 = OffsetButton(-1)
        self.__btn_plus1 = OffsetButton(1)
        self.__btn_plus10 = OffsetButton(10)
        self.__btn_plus100 = OffsetButton(100)
        
        self.__btn_minus100.clicked.connect(lambda: self.__change_offset(-100))
        self.__btn_minus10.clicked.connect(lambda: self.__change_offset(-10))
        self.__btn_minus1.clicked.connect(lambda: self.__change_offset(-1))
        self.__btn_plus1.clicked.connect(lambda: self.__change_offset(1))
        self.__btn_plus10.clicked.connect(lambda: self.__change_offset(10))
        self.__btn_plus100.clicked.connect(lambda: self.__change_offset(100))
        
        self._input_offset = LineEditClickable(
            self, text='0', alignment=Qt.AlignmentFlag.AlignRight,
            inputMask='#0009;'
        )
        
        self._input_offset.setFixedWidth(50)
        self._input_offset.editingFinished.connect(self.__set_offset)
        
        layout = QVBoxLayout()
        layout.addWidget(self.__label_offset)
        
        b_left = QVBoxLayout()
        b_left.addWidget(self.__btn_minus1)
        b_left.addWidget(self.__btn_minus10)
        b_left.addWidget(self.__btn_minus100)

        b_right = QVBoxLayout()
        b_right.addWidget(self.__btn_plus1)
        b_right.addWidget(self.__btn_plus10)
        b_right.addWidget(self.__btn_plus100)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addLayout(b_left)
        bottom.addSpacing(10)
        bottom.addWidget(self._input_offset)
        bottom.addSpacing(10)
        bottom.addLayout(b_right)
        bottom.addStretch()

        layout.addLayout(bottom)
        
        self.setLayout(layout)
            
    def __change_offset(self, delta: int): 
        self.__offset += delta
        self._input_offset.setText(str(self.__offset))
        # self.__check_offset(parent)
    
    
    def __set_offset(self):
        offset = self._input_offset.text()
        try:
            self.__offset = int(offset)
        except ValueError:
            self.__offset = 0
        # self.__check_offset(parent)


    # def __check_offset(self, parent):
    #     path = str(pathlib.Path("output/thumbnail.png"))
    #     if img.is_transparent(path):
    #         parent.offset_info.setText("透明な部分がある可能性があります")
    #         parent.offset_info.setStyleSheet(
    #             WarningIndicatorStyle.WARNING.value
    #         )
    #     else:
    #         parent.offset_info.setText("透明な部分はありません")
    #         parent.offset_info.setStyleSheet(
    #             WarningIndicatorStyle.SUCCESS.value
    #         )

    
    def get_offset(self) -> int:
        """オフセット値を取得する

        Returns:
            int: オフセット値 (負なら下に，正なら上にずれる)
        """
        return self.__offset



class OffsetButton(QPushButton):
    """オフセット変更用のボタン"""
    def __init__(self, delta: int):
        """初期化関数

        Args:
            delta (int): 押されたときに変化させるオフセットの値
        """
        str_delta = f"{delta:+}"
        super().__init__(str_delta)
        self.__delta = delta
        self.setFixedWidth(50)



class LogoColorSelector(QWidget):
    """ ロゴの色選択用ウィジェット """
    def __init__(self, parent: 'gui.MainWindow'):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        super().__init__(parent)

        self.__label_logo_color = QLabel("ロゴの色", self)

        self.__radio_white = QRadioButton("白", self)
        self.__radio_black = QRadioButton("黒", self)
        self.__radio_white.setChecked(True)

        layout = QHBoxLayout()
        layout.addWidget(self.__label_logo_color)
        layout.addStretch()
        layout.addWidget(self.__radio_white)
        layout.addWidget(self.__radio_black)

        self.setLayout(layout)


    def get_logo_color(self) -> img.LogoColor:
        """選択されたロゴの色を取得する

        Returns:
            img.LogoColor: ロゴの色 (img.LogoColor.WHITE or img.LogoColor.BLACK)
        """
        if self.__radio_white.isChecked():
            return img.LogoColor.WHITE
        else:
            return img.LogoColor.BLACK
            


class RectangleWidget(QWidget):
    """色プレビュー用の矩形ウィジェット"""
    def __init__(self, parent: 'ColorSelector'):
        """初期化関数

        Args:
            parent (ColorSelector): 親ウィジェット(ColorSelector)
        """
        super().__init__(parent)
        self.__color = QColor('#000000')


    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__color)


    def set_color(self, rgba: tuple[int, int, int, int]):
        """色を設定する

        Args:
            rgba (tuple[int, int, int, int]): RGBAの組
        """
        self.__color = QColor(*rgba)
        self.update()



class LineEditClickable(QLineEdit):
    """クリック可能なQLineEdit"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def mousePressEvent(self, event):
        self.selectAll()



class RGBLineEdit(LineEditClickable):
    def __init__(self, placeholder: str, parent: 'ColorSelector'):
        """初期化関数

        Args:
            placeholder (str): プレースホルダー
            parent (ColorSelector): 親ウィジェット(ColorSelector)
        """
        super().__init__(
            parent, inputMask='000;', 
            maxLength=3, placeholderText=placeholder
        )
        self.setFixedWidth(40)



class ThumbnailPreview(QLabel):
    def __init__(self, parent: 'gui.MainWindow'):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        super().__init__(parent)
        pixmap = QPixmap(str(pathlib.Path(misc.base_dir() / "img/wakato.jpg")))
        pixmap = pixmap.scaled(480, 270, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.resize(480, 270)


    def update_preview(
            self, image_path: str, offset: int,
            rgba: tuple[int, int, int, int],
            logo_color: img.LogoColor = img.LogoColor.WHITE
            ):
        """プレビューを更新する

        Args:
            image_path (str): 元画像のパス
            offset (int): 画像の縦方向のオフセット. 負なら下に，正なら上にずれる.
            rgba (tuple[int, int, int, int]): 長方形の色(R, G, B, A)
            logo_color (img.LogoColor, optional): ロゴの色. Defaults to img.LogoColor.WHITE.
        """
        try:
            img.generate_thumbnail(image_path, offset, rgba, logo_color)
            path = pathlib.Path(image_path).parent / 'thumbnail.png'
            pixmap = QPixmap(str(path)).scaled(
                480, 270, Qt.AspectRatioMode.KeepAspectRatio
            )
            self.setPixmap(pixmap)
            self.resize(480, 270)
        except Exception as e:
            print(f"プレビューの更新に失敗: {e}")



class WarningIndicatorStyle(Enum):
    NONE = "color: black;"
    INFO = "color: blue;"
    SUCCESS = "color: green; font-weight: bold;"
    WARNING = "color: red; font-weight: bold;"
    ERROR = "color: red; font-weight: bold;"



class WarningIndicator(QLabel):
    """警告表示用ウィジェット"""
    def __init__(
            self, parent: 'gui.MainWindow', text: str = "", 
            style: WarningIndicatorStyle = WarningIndicatorStyle.NONE
            ):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
            text (str, optional): 表示するテキスト. Defaults to "".
            style (WarningIndicatorStyle, optional): スタイル. Defaults to WarningIndicatorStyle.NONE.
        """
        super().__init__(parent, text=text, wordWrap=True)
        self.setStyleSheet(style.value)
        self.setFixedWidth(480)
        


class GenerateButton(QPushButton):
    """サムネイル生成ボタン"""
    def __init__(self, parent: 'gui.MainWindow'):
        """初期化関数

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        super().__init__("作成", parent)
        self.setDefault(True)
        self.setFixedWidth(100)
        self.clicked.connect(lambda: self.__on_click(parent))


    def __on_click(self, parent: 'gui.MainWindow'):
        """クリック時の処理(サムネイルの作成)

        Args:
            parent (gui.MainWindow): 親ウィジェット(MainWindow)
        """
        print("サムネイルを生成")
        try:
            image_path = parent.get_img_path()
            offset = parent.get_offset()
            rgba = parent.get_rgba()
            logo_color = parent.get_logo_color()
            
            img.generate_thumbnail(image_path, offset, rgba, logo_color)
            parent.update_preview()
        except Exception as e:
            print(f"Error: {e}")
            print("画像の生成に失敗しました。")

