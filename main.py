from themur.source import PicsumLorem


def main():
    picsum = PicsumLorem()
    img, path, meta = picsum.get_img(width=1200, height=920)
    img.show()
    img2, path2, meta2 = picsum.get_img(width=1200, height=920)
    img2.show()
    img3, path3, meta3 = picsum.redo_img(grayscale=True)
    img3.show()
    img4, path4, meta4 = picsum.get_last()
    img4.show()
    print('Done')


if __name__ == '__main__':
    main()
