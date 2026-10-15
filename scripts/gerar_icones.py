"""Renderização dos ícones geométricos próprios do CyberCare em PNG (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / 'frontend' / 'public' / 'icons'
root.mkdir(parents=True, exist_ok=True)


def render(size, filename, maskable=False):
    scale = 4
    image = Image.new('RGB', (size * scale, size * scale), '#073F39')
    draw = ImageDraw.Draw(image)
    factor = size * scale / 512
    # Ícone com conteúdo dentro da área segura de ícones adaptáveis.
    shrink = .84 if maskable else 1
    def points(vertices):
        return [((256 + (x - 256) * shrink) * factor, (256 + (y - 256) * shrink) * factor) for x, y in vertices]
    outer = [(256,96),(235,111),(210,126),(183,138),(154,146),(124,148),(124,264),(128,294),(140,323),(161,350),(189,375),(221,398),(256,420),(291,398),(323,375),(351,350),(372,323),(384,294),(388,264),(388,148),(358,146),(329,138),(302,126),(277,111)]
    inner = [(256,132),(230,148),(205,161),(181,170),(159,174),(159,264),(163,287),(173,310),(190,333),(212,354),(238,374),(256,384),(274,374),(300,354),(322,333),(339,310),(349,287),(353,264),(353,174),(331,170),(307,161),(282,148)]
    draw.polygon(points(outer), fill='#E84B18')
    draw.polygon(points(inner), fill='#073F39')
    check = points([(205,258),(242,295),(313,220)])
    width = round(26 * factor * shrink)
    draw.line(check, fill='#FFF8EF', width=width, joint='curve')
    for x, y in check:
        r = width / 2
        draw.ellipse((x-r,y-r,x+r,y+r), fill='#FFF8EF')
    image.resize((size,size), Image.Resampling.LANCZOS).save(root / filename, optimize=True)


for size in [192, 512]:
    render(size, f'icon-{size}.png')
render(512, 'maskable-512.png', True)
render(180, 'apple-touch-icon.png')
print('Quatro ícones de instalação gerados.')
