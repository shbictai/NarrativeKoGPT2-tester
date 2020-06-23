import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.utils.data import TensorDataset # 텐서데이터셋
from torch.utils.data import Dataset,DataLoader # 데이터로더

from kogpt2.utils import download, tokenizer, get_tokenizer
from gluonnlp.data import SentencepieceTokenizer
import gluonnlp
import numpy as np
import os


def sentencePieceTokenizer():
  tok_path = get_tokenizer()
  sentencepieceTokenizer = SentencepieceTokenizer(tok_path)

  return sentencepieceTokenizer


def koGPT2Vocab():
  cachedir = '~/kogpt2/'

  # download vocab
  vocab_info = tokenizer
  vocab_path = download(vocab_info['url'],
                        vocab_info['fname'],
                        vocab_info['chksum'],
                        cachedir=cachedir)

  koGPT2_vocab = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
                                                             mask_token=None,
                                                             sep_token=None,
                                                             cls_token=None,
                                                             unknown_token='<unk>',
                                                             padding_token='<pad>',
                                                             bos_token='<s>',
                                                             eos_token='</s>')
  return koGPT2_vocab

def toString(list):
  if not list:
    return ''
  result = ''

  for i in list:
    result = result + i
  return result

class NovelDataset(Dataset):
  """web novel dataset"""

  def __init__(self, file_path,vocab,tokenizer):
    self.file_path = file_path
    self.data =[]
    self.vocab =vocab
    self.tokenizer = tokenizer
    file = open(self.file_path, 'r', encoding='utf-8')

    while True:
      line = file.readline()
      if not line:
        break
      toeknized_line = tokenizer(line[:-1])
      index_of_words = [vocab[vocab.bos_token],] + vocab[toeknized_line]+ [vocab[vocab.eos_token]]
      # print(np.shape(index_of_words))
      self.data.append(index_of_words)

    print(np.shape(self.data))

    file.close()

  def __len__(self):
    return len(self.data)
  def __getitem__(self,index):
    item = self.data[index]
    # print(item)
    return item
#
# cachedir='~/kogpt2/'
# print(os.getcwd())
# os.chdir("../")
# file_path = './data/backmyo_novel_1/untokenized_bm_data.txt'
#
# vocab_info = tokenizer
# vocab_path = download(vocab_info['url'],
#                        vocab_info['fname'],
#                        vocab_info['chksum'],
#                        cachedir=cachedir)
# vocab = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
#                                                      mask_token=None,
#                                                      sep_token=None,
#                                                      cls_token=None,
#                                                      unknown_token='<unk>',
#                                                      padding_token='<pad>',
#                                                      bos_token='<s>',
#                                                      eos_token='</s>')
# tok_path = get_tokenizer()
# sentencepieceTokenizer = SentencepieceTokenizer(tok_path)
#
# novel_dataset = NovelDataset(file_path, vocab,sentencepieceTokenizer)
#
# novel_data_loader = DataLoader(novel_dataset, batch_size=128, shuffle=True)
#
# count = 0
# for data in novel_data_loader:
#     if count == 0:
#       # print('No. %s ' %(count) +' data {}'.format(data))
#       for d in data:
#         print(d)
#     count = count+1
