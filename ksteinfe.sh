### Using labels only
python train.py \
--name '190312_clarkkerr' \
--dataroot '/media/ksteinfe/DATA/TEMP/clarkkerr' \
--label_nc 0 \
--no_instance \
--loadSize 512 \
--save_epoch_freq 5 
#--continue_train \
#--which_epoch 55 \

# --lr 0.0008

#--load_pretrain /home/ksteinfe/GitHub/pix2pixHD/checkpoints/190228_adamspoint

#python test.py \
#--name '190213_blijdorp' \
#--dataroot '/media/ksteinfe/DATA/TEMP/_sample_depthmaps' \
#--label_nc 0 \
#--no_instance \
#--loadSize 512 \
