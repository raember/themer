from themur import get_monitor_resolution
from themur.source import PicsumLorem


def main():
    w, h = get_monitor_resolution()
    picsum = PicsumLorem()
    img, path, meta = picsum.get_img(width=w, height=h)
    img.show()
    img2, path2, meta2 = picsum.get_img()
    img2.show()
    img3, path3, meta3 = picsum.redo_img(grayscale=True)
    img3.show()
    img4, path4, meta4 = picsum.get_last()
    img4.show()
    print('Done')


if __name__ == '__main__':
    main()
