import os, argparse
from PIL import Image, ImageDraw, ImageFont
import cv2, imageio
import numpy as np

ext_whitelist = ['jpg','png']

FNT = ImageFont.truetype("arial.ttf", 80, encoding="unic")

def main(pth_img_upsp, pth_img_dpth, pth_dst):
    if not os.path.exists(pth_dst): os.makedirs(pth_dst)

    fnames_dpth = [f for f in os.listdir(pth_img_dpth) if any([f.endswith('.{}'.format(ext)) for ext in ext_whitelist])]
    for fname_dpth in fnames_dpth:
        print(fname_dpth)
        fnames_upsp = [f for f in os.listdir(pth_img_upsp) if f.startswith(fname_dpth[:-4]) and any([f.endswith('.{}'.format(ext)) for ext in ext_whitelist])]
        dct_imgs = dict( [ (fname_upsp.split('_')[-1][:-4],Image.open(os.path.join(pth_img_upsp,fname_upsp))) for fname_upsp in fnames_upsp] )
        img_dpth = Image.open(os.path.join(pth_img_dpth,fname_dpth))

        mov_animated = animate_images(img_dpth, dct_imgs, os.path.join(pth_dst,"{}.mp4".format(fname_dpth[:-4])))

        img_tiled = tile_five_images(img_dpth, dct_imgs)
        img_tiled.save(os.path.join(pth_dst,"{}.jpg".format(fname_dpth[:-4])))


def animate_images(img_dpth, dct_imgs, pth_out, fps=24):
    secs_per_fade = 2
    secs_per_stil = 2

    def fade(img1, img2, steps):
        imgs = []
        for fad in np.linspace(0,1,steps):
            i1,i2 = np.asarray(img1), np.asarray(img2)
            arr = cv2.addWeighted( i1, 1-fad, i2, fad, 0)
            imgs.append( arr )
        return imgs


    img_tiles = list(dct_imgs.items())
    img_tiles.append(img_tiles[0]) # add list to the end to get smooth loop

    imgs = []
    for img_a, img_b in zip(img_tiles[:-1],img_tiles[1:]):
        img_a, img_b = img_a[1], img_b[1]
        for f in range(int(secs_per_stil/2.0*fps)): imgs.append(np.asarray(img_a))
        imgs.extend( fade(img_a, img_b, secs_per_fade * fps) )
        for f in range(int(secs_per_stil/2.0*fps)): imgs.append(np.asarray(img_b))

    print("writing mp4 with {} frames at {} fps to produce a {}s animation".format(len(imgs),fps,len(imgs)/fps))
    writer = imageio.get_writer(pth_out, fps=fps)
    for im in imgs: writer.append_data(im)
    writer.close()




def tile_five_images(img_dpth, dct_imgs, pd=20):
    img_tiles = list(dct_imgs.items())
    sz = img_tiles[0][1].size

    txt_pad = 100

    img = Image.new('RGB',( (sz[0]*3)+(pd*4), (sz[1]*2)+(pd*3)+(txt_pad*2) ), (255,255,255))
    img_dpth = img_dpth.resize(sz,Image.NEAREST)

    drw = ImageDraw.Draw(img)

    def paste(tup,xy,txt_top):
        nm,im = tup
        x,y = xy
        img.paste(im,(x,y))
        w,h = drw.textsize(nm, font=FNT)
        if txt_top: drw.text((x+sz[0]/2-w/2,y-h*1.25), nm, font=FNT, fill=(0))
        else: drw.text((x+sz[0]/2-w/2,y+sz[1]), nm, font=FNT, fill=(0))


    paste( ("depth", img_dpth) , (pd*1+sz[0]*0,pd*1+sz[1]*0 +txt_pad), True )
    paste( img_tiles[0],          (pd*2+sz[0]*1,pd*1+sz[1]*0 +txt_pad), True )
    paste( img_tiles[1],          (pd*3+sz[0]*2,pd*1+sz[1]*0 +txt_pad), True )

    paste( img_tiles[2],          (pd*1+sz[0]*0,pd*2+sz[1]*1 +txt_pad), False )
    paste( img_tiles[3],          (pd*2+sz[0]*1,pd*2+sz[1]*1 +txt_pad), False )
    paste( img_tiles[4],          (pd*3+sz[0]*2,pd*2+sz[1]*1 +txt_pad), False )

    return img


if __name__ == '__main__':
    '''
    """Checks if a path is an actual directory"""
    def is_dir(pth):
        if not os.path.isdir(pth):
            msg = "{0} is not a directory".format(pth)
            raise argparse.ArgumentTypeError(msg)
        else:
            return os.path.abspath(os.path.realpath(os.path.expanduser(pth)))

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Directory in which to find the cherrypick.csv AND a directory full of images to pick from.", type=is_dir)
    parser.add_argument('-retain', action='store_true', default=False, help="Keep a copy in the source directory?")
    args = parser.parse_args()
    '''
    pth_img_upsp = r"X:\Box Sync\RRSYNC\projects\almost_home\190301_pano_results\cherrypicked_upsampled"
    pth_img_dpth = r"X:\Box Sync\RRSYNC\projects\almost_home\190301_pano_results\cherrypicked\depthmaps"
    pth_dst = r"X:\Box Sync\RRSYNC\projects\almost_home\190301_pano_results\test"

    main(pth_img_upsp, pth_img_dpth, pth_dst)
