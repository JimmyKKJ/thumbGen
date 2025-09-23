from PIL import Image
from enum import Enum
from utils import misc
import pathlib

class LogoColor(Enum):
    BLACK = 0
    WHITE = 1


class LogoShape(Enum):
    BANNER = 0
    TRAPEZOID = 1
    SOFT_TRAPEZOID = 2
    SOFT_RECTANGLE = 3


def generate_thumbnail(
        input_path: str, offset: int, 
        rgba: tuple[int, int, int, int],
        logo_color: LogoColor = LogoColor.WHITE,
        logo_shape: LogoShape = LogoShape.BANNER) -> None:
    """サムネイルを生成する

    Args:
        input_path (str): 元画像のパス
        offset (int): 画像の縦方向のオフセット. 負なら下に，正なら上にずれる.
        rgba (tuple[int, int, int, int]): 長方形の色(R, G, B, A)
        logo_color (LogoColor, optional): ロゴの色. Defaults to LogoColor.WHITE.
        logo_shape (LogoShape, optional): ロゴの形. Defaults to LogoShape.BANNER.
    """
    image = Image.open(input_path).copy()
    image = resize(image, offset)

    canvas = Image.new('RGB', (1920, 1080), (255, 255, 255))
    canvas.paste(image, (0, 0))
    canvas = put_banner(canvas, rgba, logo_shape)
    canvas = put_logo(canvas, logo_color)
    
    save_path = str(pathlib.Path(input_path).parent / 'thumbnail.png')
    canvas.save(save_path)



def resize(image: Image.Image, offset: int = 0) -> Image.Image:
    """画像をフルHD(横長，1920x1080)にリサイズする（縦横比は保つ，あふれた部分は切り取る）

    Args:
        image (Image.Image): リサイズするPIL Imageオブジェクト
        offset (int, optional): 画像の縦方向のオフセット. デフォルトは0. 負なら下に，正なら上にずれる.

    Returns:
        Image.Image: リサイズされたPIL Imageオブジェクト
    """
    after_aspect_ratio = 1920 / 1080  # フルHDの縦横比に合わせる
    image_aspect_ratio = image.width / image.height
    center = ((1080 + offset) // 2, 1920 // 2)

    if image_aspect_ratio > after_aspect_ratio:
        # 画像が横長すぎる場合
        image = image.resize((1080 * image_aspect_ratio, 1080))
    else:
        # 画像が縦長すぎる場合
        image = image.resize((1920, int(1920 // image_aspect_ratio)))

    left = center[1] - 1920 / 2
    top = center[0] - 1080 / 2
    right = center[1] + 1920 / 2
    bottom = center[0] + 1080 / 2


    # 切り取りとリサイズを実行
    image = image.crop((left, top, right, bottom))
    return image



def put_banner(
        image: Image.Image,
        rgba: tuple[int, int, int, int],
        shape: LogoShape = LogoShape.BANNER
        ) -> Image.Image:
    """画像の下に長方形を描画する
    Args:
        image (Image.Image): 長方形を描画するPIL Imageオブジェクト
        rgba (tuple[int, int, int, int]): 長方形の色(R, G, B, A)
        shape (LogoShape, optional): 長方形の形. Defaults to LogoShape.BANNER.
    Returns:
        Image.Image: 長方形が描画されたPIL Imageオブジェクト
    """
    from PIL import ImageDraw

    # RGBAに変換
    image = image.convert('RGBA')
    # 長方形を描画するためのImageDrawオブジェクトを作成
    temp = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(temp, 'RGBA')
    # 長方形を描画
    IMG_H = 1080
    IMG_W = 1920
    RADIUS = 45
    match shape:
        case LogoShape.BANNER:
            draw.rectangle(
                [(0, IMG_H - 180), (IMG_W, IMG_H)], 
                fill=rgba
            )
        case LogoShape.TRAPEZOID:
            draw.polygon(
                [(0, IMG_H - 180),
                 (0, IMG_H),
                 (840, IMG_H),
                 (720, IMG_H - 180)],
                fill=rgba
            )
        case LogoShape.SOFT_TRAPEZOID:
            draw.rounded_rectangle(
                [(0, IMG_H - 180), (720, IMG_H)], 
                radius=RADIUS, fill=rgba
            )
            draw.rectangle(
                [(0, IMG_H - 180), (RADIUS, IMG_H)],
                fill=rgba
            )
            draw.rectangle(
                [(720 - RADIUS, IMG_H - RADIUS), (720, IMG_H)],
                fill=rgba
            )
            draw.polygon(
                [(720 - RADIUS + (3 / (13**(1/2))) * RADIUS, IMG_H),
                 (840, IMG_H),
                 (720 - RADIUS + (3 / (13**(1/2))) * RADIUS,
                  IMG_H - 180 + RADIUS - (2 / (13**(1/2))) * RADIUS)],
                fill=rgba
            )
        case LogoShape.SOFT_RECTANGLE:
            draw.rounded_rectangle(
                [(0, IMG_H - 180), (720, IMG_H)], 
                radius=RADIUS, fill=rgba
            )
            draw.rectangle(
                [(0, IMG_H - 180), (RADIUS, IMG_H)],
                fill=rgba
            )
            draw.rectangle(
                [(720 - RADIUS, IMG_H - RADIUS), (720, IMG_H)],
                fill=rgba
            )
        case _:
            draw.rectangle((0, image.height * 5 / 6, image.width, image.height), fill=rgba)
    # 元の画像と長方形を合成
    image = Image.alpha_composite(image, temp)

    return image



def put_logo(image: Image.Image, bw: LogoColor) -> Image.Image:
    """画像の左下にロゴを描画する

    Args:
        image (Image.Image): ロゴを描画するPIL Imageオブジェクト
        bw (LogoColor): ロゴの色

    Returns:
        Image.Image: ロゴが描画されたPIL Imageオブジェクト
    """
    from PIL import Image

    # ロゴ画像のパスを決定
    if bw == LogoColor.BLACK:
        logo_path = str(pathlib.Path(misc.base_dir() / 'img/logo_black.png'))
    elif bw == LogoColor.WHITE:
        logo_path = str(pathlib.Path(misc.base_dir() / 'img/logo_white.png'))
    else:
        raise ValueError('Invalid logo color')

    # ロゴ画像を開く
    logo = Image.open(logo_path).convert('RGBA')
    # ロゴのサイズを決定（画像の高さの1/6に合わせる）
    LOGO_H = 120
    logo_w = int(logo.width * (LOGO_H / logo.height)) # approx. 570
    logo = logo.resize((logo_w, LOGO_H))

    IMG_H = 1080
    IMG_W = 1920
    # ロゴを画像の左下に貼り付ける
    image.paste(logo, (75, IMG_H - LOGO_H - 30), logo)
    return image



# def is_transparent(path: str) -> bool:
#     """画像に透明部分が含まれているかを判定する

#     Args:
#         path (str): 画像ファイルのパス

#     Returns:
#         bool: 透明部分が含まれている場合はTrue，含まれていない場合はFalse
#     """
#     image = Image.open(path).copy()

#     if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
#         alpha = image.convert('RGBA').split()[-1]
#         if isinstance(alpha.getextrema, tuple):
#             if alpha.getextrema()[0] < 255: return True
#         else:
#             for pixel in alpha.getdata():
#                 if pixel < 255:
#                     return True
#     return False
