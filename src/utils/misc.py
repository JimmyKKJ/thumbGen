import sys
from pathlib import Path

def rgb(hex: str) -> tuple[int, int, int]:
    """HEXからRGBに変換する

    Args:
        hex (str): HEXコード (赤はFF0000)

    Returns:
        tuple[int, int, int]: RGBの組
    """
    if hex:
        r = int(hex[0:2], 16) or 0
        g = int(hex[2:4], 16) or 0
        b = int(hex[4:6], 16) or 0
    else:
        r = g = b = 0
    return (r, g, b)



def base_dir() -> Path:
    """ベースディレクトリを取得する

    Returns:
        Path: ベースディレクトリ
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore
    else:
        return Path('.')
    

