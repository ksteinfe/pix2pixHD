import os, shutil, argparse, csv


def main(pth_src, do_retain=False):
    print("Cherrypicking from {}".format(pth_src))
    pth_imgs = os.path.join(pth_src,"images")
    pth_csv = os.path.join(pth_src,"cherrypick.csv")
    pth_dst = os.path.join(pth_src,"cherrypicked")
    if not os.path.exists(pth_dst): os.makedirs(pth_dst)
    if not os.path.isfile(pth_csv):
        print ("Could not find cherrypick.csv file. Where is it?")
        exit()
    if not os.path.isdir(pth_imgs):
        print ("Could not find images directory. Where is it?")
        exit()

    prefixes = False
    with open(pth_csv, 'r') as f: prefixes = list(csv.reader(f))[0]

    for root, dirs, files in os.walk(pth_imgs):
        for fname in files:
            if any([fname.startswith(prefix) for prefix in prefixes]):
                print(fname)
                if do_retain: shutil.copy(os.path.join(root,fname),os.path.join(pth_dst,fname))
                else: shutil.move(os.path.join(root,fname),os.path.join(pth_dst,fname))

if __name__ == '__main__':
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
    main(args.path, args.retain)
