import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import tensorflow as tf
import sys
sys.path.append("../..")
from Util.training import cherry_pick
from Util.utils import *
config=tf.compat.v1.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction=0.5
config.gpu_options.allow_growth = True  # 设置动态分配GPU内存
sess=tf.compat.v1.Session(config=config)
# gpus = tf.config.experimental.list_physical_devices('GPU')
# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)

def process_all_data(pre_model_path, code, embed_arg, cls, doc_path, rank_file, K_fold, mul_bin_flag, retrain):
    pre_model_path = pre_model_path + "src_ckpt/model.pickle"
    model = pickle.load(open(pre_model_path, "rb"))
    # print(model["("])
    all_vec_part, all_label_part = prepare_data(doc_path, model, embed_arg["voc_size"],
                                                embed_arg["sentence_length"], code, rank_file, K_fold,
                                                mul_bin_flag)
    del model
    gc.collect()
    print("load finished!")
    return all_vec_part, all_label_part

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cls', '-c', help='data category')
    parser.add_argument('--code', '-d', help='code category')
    parser.add_argument('--fold', '-k', help='the number of data of every fold')
    parser.add_argument("--retrain", "-r")
    parser.add_argument('--split_test', '-s')
    parser.add_argument('--gpu', '-g')
    parser.add_argument('--neural', '-n')
    args = parser.parse_args()

    K_fold = int(args.fold)
    sard_binary_doc_path = "../../pickle_object/sard/detect/src/"
    sard_binary_rank_file = "../../pickle_object/sard/detect/rank/"

    spot_multiclass_doc_path = "../../pickle_object/spotbugs/detect_mul/" + args.code + "/"
    spot_multiclass_rank_file = "../../pickle_object/spotbugs/detect_mul/rank/"
    spot_binary_doc_path = "../../pickle_object/spotbugs/detect_bin_sample_15000/" + args.code + "/"
    spot_binary_rank_file = "../../pickle_object/spotbugs/detect_bin_sample_15000/rank/"
    # spot_binary_doc_path = "../../pickle_object/spotbugs/test/" + args.code + "/"
    # spot_binary_rank_file = "../../pickle_object/spotbugs/test/rank/"
    sard_pre_model_path = "../../pre_train_def/sard/elmo/"
    spotbugs_pre_model_path = "../../pre_train_def/spotbugs/elmo/"

    oop_binary_doc_path, oop_pre_model_path, oop_binary_rank_file = "../../pickle_object/oopsla/detect_bin/" + args.code + "/", \
                                                                    "../../pre_train_def/oopsla/elmo/", \
                                                                    "../../pickle_object/oopsla/detect_bin/rank/"

    prodim_range = [128*2]
    dropout_range = [0.1]
    n_epochs_range = [10]
    batchsize_range = [128]

    sentence_length_range = [200]

    # batch_size_range = [32]
    batch_size_range = [32, 128, 256]
    # epochs_d_range = [20]
    epochs_d_range = [40]
    # lstm_unit_range = [16, 32, 64]     #fixed
    lstm_unit_range = [16, 32]     #fixed
    optimizer_range = ["Adam"] #fixed
    # optimizer_range = ["Adam"] #fixed
    layer_range = [2]    #fixed
    # drop_out_range = [0.1]
    drop_out_range = [0.5]
    # learning_rate_range = [0.001]
    learning_rate_range = [0.0003, 0.001, 0.005]
    gru_unit_range = [64, 128, 256]
    dense_unit_range = [32, 64, 128]
    pool_size_range = [10, 15, 20]
    kernel_size_range = [3, 5, 10]
    #########

    if args.cls == "sard_bin":
        mul_bin_flag, doc_path, pre_model_path, rank_file = 0, sard_binary_doc_path, sard_pre_model_path, sard_binary_rank_file
    elif args.cls == "spot_bin":
        mul_bin_flag, doc_path, pre_model_path, rank_file = 0, spot_binary_doc_path, spotbugs_pre_model_path, spot_binary_rank_file
    elif args.cls == "oop_bin":
        mul_bin_flag, doc_path, pre_model_path, rank_file = 0, oop_binary_doc_path, oop_pre_model_path, oop_binary_rank_file
    elif args.cls == "spot_mul":
        mul_bin_flag, doc_path, pre_model_path, rank_file = 1, spot_multiclass_doc_path, spotbugs_pre_model_path, spot_multiclass_rank_file
    else:
        print("no category!")
        exit(0)
    if not os.path.isdir(args.cls):
        os.mkdir(args.cls)
    save_base = args.cls + "/" + args.code + "_elmo_" + args.neural
    if not os.path.isdir(save_base):
        os.mkdir(save_base)
    # args_range = dict(sg_range=sg_range,min_count_range=min_count_range, voc_size_range=voc_size_range,
    #                   sentence_length_range=sentence_length_range, negative_range=negative_range,
    #                   sample_range=sample_range, hs_range=hs_range, batch_size_range=batch_size_range,
    #                   epochs_d_range=epochs_d_range, lstm_unit_range=lstm_unit_range, optimizer_range=optimizer_range,
    #                   layer_range=layer_range, drop_out_range=drop_out_range, iter_range=iter_range, window_range=window_range)
    # print("preparing for data...")
    # w2v.train(args.cls, code, pre_model_path)
    # model = KeyedVectors.load(pre_model_path, mmap="r")
    # all_vec_part, all_label_part = prepare_data(doc_path, model, args_range["voc_size_range"][0],
    #                                             args_range["sentence_length_range"], code, rank_file, K_fold, mul_bin_flag)
    #
    # start = time.time()
    # for times in range(K_fold-1):
    #     print("**************************" + str(times) + " time training**************************")
    #     # x_train, y_train, x_test, y_test = split_dataset(all_vec_part, all_label_part, 2, times)
    #     Word2vec.word2vec_lstm.cherry_pick(all_vec_part, all_label_part, args_range, code, times, args.cls, K_fold, flag=mul_bin_flag)
    #     # print("length:", x_train)
    # end = time.time()
    # print("total time:", end - start)

    detect_arg = dict(batch_size_range=batch_size_range, epochs_d_range=epochs_d_range,
                      lstm_unit_range=lstm_unit_range, optimizer_range=optimizer_range,
                      layer_range=layer_range, drop_out_range=drop_out_range,
                      learning_rate_range = learning_rate_range, gru_unit_range=gru_unit_range,
                      dense_unit_range=dense_unit_range, pool_size_range=pool_size_range,
                      kernel_size_range=kernel_size_range)
    # times = 0
    print("tf.test.is_gpu_available():", tf.test.is_gpu_available())
    for vec_dim in prodim_range:
        for epoch in n_epochs_range:
            for batch in batchsize_range:
                print("preparing for data...")
                embed_arg = dict(voc_size = vec_dim, dropout_range = dropout_range[0], n_epochs_range = epoch, batchsize_range = batch, sentence_length=sentence_length_range[0])
                all_vec_part, all_label_part = process_all_data(pre_model_path, args.code, embed_arg, args.cls, doc_path, rank_file, K_fold, mul_bin_flag, args.retrain)
                if args.split_test == "True":
                    num = K_fold - 1
                elif args.split_test == "False":
                    num = K_fold
                for times in range(num):
                    start = time.time()
                    print("**************************" + str(times) + " time training**************************")
                    cherry_pick(all_vec_part, all_label_part, embed_arg, detect_arg, times, args.split_test,
                                K_fold, mul_bin_flag, args.neural, args.code, save_base)
                    end = time.time()
                    print("total time:", end - start)
                del all_vec_part
                del all_label_part
                gc.collect()
