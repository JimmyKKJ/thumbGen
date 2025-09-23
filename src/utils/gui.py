from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt
from utils import custom_widgets as cwidgets
from utils import img


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("thumbGen")

        # 画像ファイル選択
        self.__image_selector = cwidgets.ImageSelector(self)

        # 色選択
        self.__color_selector = cwidgets.ColorSelector(self)

        # オフセット
        self.__offset_selector = cwidgets.OffsetSelector(self)

        # ロゴの色
        self.__logo_color_selector = cwidgets.LogoColorSelector(self)

        # サムネイル表示
        self.__pic = cwidgets.ThumbnailPreview(self)

        # 警告表示
        WIS = cwidgets.WarningIndicatorStyle
        self.file_info = cwidgets.WarningIndicator(
            self, "画像が選択されていません",
            WIS.WARNING
        )
        self.color_info = cwidgets.WarningIndicator(
            self, "色が選択されていません",
            WIS.WARNING
        )
        self.offset_info = cwidgets.WarningIndicator(
            self, "透明な部分がないように注意してください",
            WIS.INFO
        )
        self.logo_color_info = cwidgets.WarningIndicator(
            self, "見やすいロゴの色を選択してください", 
            WIS.NONE
        )


        # サムネイル生成ボタン
        self.__btn_generate = cwidgets.GenerateButton(self)


        # レイアウト配置
        top = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(self.__image_selector)
        # left.addWidget(self.__dir_selector)
        left.addWidget(self.__color_selector)
        left.addWidget(self.__offset_selector)
        left.addWidget(self.__logo_color_selector)
        left.addStretch()
        top.addLayout(left)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self.__pic)
        right.addWidget(self.file_info)
        right.addWidget(self.color_info)
        right.addWidget(self.offset_info)
        right.addWidget(self.logo_color_info)
        right.addStretch()
        top.addLayout(right)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(self.__btn_generate)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top)
        main_layout.addLayout(bottom)

        container = self.centralWidget() or QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    
    def get_img_path(self) -> str:
        """選択されている画像ファイルのパスを取得する

        Returns:
            str: 画像ファイルのパス
        """
        return self.__image_selector.get_path()
        

    def get_hex(self) -> str:
        """選択されている色のHEXコードを取得する

        Returns:
            str: HEXコード (例: 'FF0000' for red)
        """
        return self.__color_selector.get_hex()
    

    def get_rgba(self) -> tuple[int, int, int, int]:
        """選択されている色のRGBA値を取得する

        Returns:
            tuple[int, int, int, int]: RGBAの組 (例: (255, 0, 0, 255) for red)
        """
        r, g, b, a = self.__color_selector.get_rgba()
        return (r, g, b, a)
    
    
    def get_offset(self) -> int:
        """オフセット値を取得する

        Returns:
            int: オフセット値 (負なら下に，正なら上にずれる)
        """
        return self.__offset_selector.get_offset()
    

    def get_logo_color(self) -> img.LogoColor:
        """選択されているロゴの色を取得する

        Returns:
            img.LogoColor: ロゴの色
        """
        return self.__logo_color_selector.get_logo_color()

    
    def update_preview(self):
        """プレビューを更新する"""
        try:
            image_path = self.get_img_path()
            offset = self.get_offset()
            color = self.get_rgba()
            logo_color = self.get_logo_color()
            self.__pic.update_preview(image_path, offset, color, logo_color)
        except Exception as e:
            print(f"プレビューの更新に失敗: {e}")
