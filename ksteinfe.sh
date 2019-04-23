### Using labels only
python train.py \
--name '190423_bushwick' \
--dataroot '/media/ksteinfe/DATA/TEMP/bushwick' \
--label_nc 0 \
--no_instance \
--loadSize 512 \
--save_epoch_freq 5 \
--load_pretrain /home/ksteinfe/GitHub/pix2pixHD/checkpoints/190228_adamspoint
#--continue_train \
#--which_epoch 50 \

# --lr 0.0008




#python test.py \
#--name '190213_blijdorp' \
#--dataroot '/media/ksteinfe/DATA/TEMP/_sample_depthmaps' \
#--label_nc 0 \
#--no_instance \
#--loadSize 512 \
