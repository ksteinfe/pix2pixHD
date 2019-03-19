import os, shutil, argparse
import torch
from options.test_options import TestOptions
from models.pix2pixHD_model import InferenceModel
from data.base_dataset import get_params, get_transform
import util.util as util
import torchvision.transforms as transforms
from PIL import Image
from io import BytesIO

from dominate.util import raw
from dominate.tags import *
from util import html

pth_dest = r"C:\Users\ksteinfe\Desktop\TEMP\pix2pix_pano_results"
pth_src_mdls = r"X:\Box Sync\RRSYNC\190225_pix2pix_savedmodels"
pth_src_imgs = r"X:\Box Sync\RRSYNC\190225_pix2pix_savedmodels\depth_adamspt"
fmtsrc = "png"
fmtdst = "jpg"
limit = False

def main():
    webpage = html.HTML(pth_dest,"title")
    with webpage.doc.head: raw(html_jscript)
    with webpage.doc.body: raw(html_button)
    image_data = load_images(pth_src_imgs, fmtsrc, limit)

    mdl = init_model()
    mdl_fnames = [file[:-4] for file in os.listdir(pth_src_mdls) if file.lower().endswith(".pth")]
    print("Found {} models.".format(len(mdl_fnames)))

    print("-------------- generating")
    viz_dict = {}
    for imgname in image_data:
        fname = "{}.{}".format(imgname,fmtsrc)
        s,d = os.path.join(pth_src_imgs,fname), os.path.join(pth_dest,"images",fname)
        shutil.copy(s,d)
        viz_dict[imgname] = [fname]

    for mdlname in mdl_fnames:
        print("-----\t{}".format(mdlname))
        mdl.netG.load_state_dict(torch.load(os.path.join(pth_src_mdls,"{}.pth".format(mdlname))))

        for imgname, A_tensor in image_data.items():
            print(imgname)
            fname = "{}_{}.{}".format(imgname,mdlname,fmtdst)
            viz_dict[imgname].append(fname)
            generate_image(mdl,A_tensor).save(os.path.join(pth_dest,"images",fname))

    for srcname, imgs in viz_dict.items():
        #print("{}\t{}".format(srcname,len(imgs)))
        add_images(webpage, srcname, imgs)

    webpage.save()

def generate_image(mdl, A_tensor):
    generated = mdl.inference(A_tensor, torch.tensor([0]), torch.tensor([0]))
    return Image.fromarray(util.tensor2im(generated.data[0]))

def load_images(pth, fmtsrc, limit=False):
    print("-------------- loading images")
    fnames = [file for file in os.listdir(pth) if file.lower().endswith(fmtsrc)]
    if len(fnames)==0:
        print("No files with .{} extension found in directory {}".format(fmtsrc,pth))
        return False

    print("Found {} source images.".format(len(fnames)))
    tens = []
    trans = transforms.Compose([transforms.ToTensor()])
    if limit: fnames = fnames[:limit]
    for fname in fnames:
        img = Image.open(os.path.join(pth,fname))
        img = img.resize((512,512), Image.ANTIALIAS)
        #b = BytesIO()
        #Image.open(os.path.join(pth,fname)).save(b,format="jpeg")
        #img = Image.open(b)
        tens.append(trans(img.convert('RGB')))

    #A_tensor = torch.stack(tens)
    #return A_tensor
    return dict( zip([f[:-4] for f in fnames], [t.unsqueeze(0) for t in tens] ) )

def init_model():
    print("-------------- initializing model")

    opt = TestOptions().parse(save=False)
    opt.label_nc = 0  # no lables
    opt.no_instance = True  # no lables
    opt.loadSize = 512

    model = False
    try:
        model = InferenceModel()
        model.initialize(opt)
    except:
        print("model intialization did not complete because saved model is not where we expected. that's fine.")

    return model

def add_images(wp, name, ims):
    wp.add_table()
    with wp.t:
        with tr():
            with td():
                raw('<input type="checkbox" id="{}" name="cbox" value="{}" style="width:50px;height:50px;">'.format(name,name))
            for n, im in enumerate(ims):
                width = 512
                if n==0: width = 128
                with td(style="word-wrap: break-word;", halign="center", valign="middle"):
                    with p():
                        img(style="width:%dpx" % (width), src=os.path.join('images', im))
                        #with a(href=os.path.join('images', im)): img(style="width:%dpx" % (width), src=os.path.join('images', im))
                        br()
                        if n!=0: p(im)

html_button = '''<button id="btn_test" type="button" style="font-size: 2em;" onclick="getSelectedCheckboxes('cbox')">download cherrypick CSV</button>'''

html_jscript = '''
<script type="text/javascript">
function getSelectedCheckboxes(chkboxName) {
  var checkbx = [];
  var chkboxes = document.getElementsByName(chkboxName);
  var nr_chkboxes = chkboxes.length;
  for(var i=0; i<nr_chkboxes; i++) {
    if(chkboxes[i].type == 'checkbox' && chkboxes[i].checked == true) checkbx.push(chkboxes[i].value);
  }
  checkbx.toString();
  var dummy = document.createElement("input");
  document.body.appendChild(dummy);
  dummy.setAttribute("id", "dummy_id");
  document.getElementById("dummy_id").value=checkbx;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(checkbx));
  element.setAttribute('download', 'cherrypick.csv');

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
</script>
'''


if __name__ == '__main__':
    """Checks if a path is an actual directory"""
    def is_dir(pth):
        if not os.path.isdir(pth):
            msg = "{0} is not a directory".format(pth)
            raise argparse.ArgumentTypeError(msg)
        else:
            return os.path.abspath(os.path.realpath(os.path.expanduser(pth)))

    '''
    # create main parser
    parser = argparse.ArgumentParser()
    parser.add_argument('modelpath', help="Directory in which to find a bunch of saved models (.pth files)", type=is_dir)
    parser.add_argument('imagepath', help="Directory in which to find a bunch of images (.jpg or .png files)", type=is_dir)
    parser.add_argument('destpath', help="Directory in which to save results", type=is_dir)
    parser.add_argument('--limit', type=int, default=-1, help="Limits the number of panos processed for debugging purposes. A value of -1 (default) indicates no limit.")
    parser.add_argument('--fmtsrc', type=str, default="jpg", help="image file type for source images")
    parser.add_argument('--fmtdst', type=str, default="jpg", help="image file type for generated images")

    ARGS = parser.parse_args()

    if ARGS.limit <0: ARGS.limit = False
    '''
    main()
