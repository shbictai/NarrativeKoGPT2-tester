import random
import torch
from torch.utils.data import DataLoader # 데이터로더
from gluonnlp.data import SentencepieceTokenizer
from kogpt2.utils import get_tokenizer
from kogpt2.utils import download, tokenizer
from model.torch_gpt2 import GPT2Config, GPT2LMHeadModel
from util.data import NovelDataset
import gluonnlp

def topkSampling(predict, k, vocab):
  # topk 중 랜덤으로 선택된 값을 반환.
  gen =[]

  probs, indexs = torch.topk(predict, k=k, dim=-1)
  probs = probs.squeeze().tolist()[-1]
  indexs = indexs.squeeze().tolist()[-1]

  for i in range(len(indexs)):
    gen.append((vocab.to_tokens(indexs[i]),probs[i]))
  # print('topk word and value: ', gen)

  rand_num = random.randint(0,k-1)
  gen_word = vocab.to_tokens(indexs[rand_num])

  return gen_word

def get_model_result(tmp_sent):

    ### 1. koGPT2 Config
    ctx= 'cpu'#'cuda' #'cpu' #학습 Device CPU or GPU. colab의 경우 GPU 사용
    cachedir='~/nlp/' # KoGPT-2 모델 다운로드 경로
    epoch =200  # 학습 epoch
    save_path = './checkpoint'
    load_path = './checkpoint/narrativeKoGPT2_checkpoint.tar'
    #use_cuda = True # Colab내 GPU 사용을 위한 값

    pytorch_kogpt2 = {
        'url':
        'https://kobert.blob.core.windows.net/models/kogpt2/pytorch/pytorch_kogpt2_676e9bcfa7.params',
        'fname': 'pytorch_kogpt2_676e9bcfa7.params',
        'chksum': '676e9bcfa7'
    }

    kogpt2_config = {
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "n_ctx": 1024,
        "n_embd": 768,
        "n_head": 12,
        "n_layer": 12,
        "n_positions": 1024,
        "vocab_size": 50000
    }

    ### 2. Vocab 불러오기
    # download vocab
    vocab_info = tokenizer
    vocab_path = download(vocab_info['url'],
                           vocab_info['fname'],
                           vocab_info['chksum'],
                           cachedir=cachedir)

    ### 3. 체크포인트 및 디바이스 설정
    # Device 설정
    device = torch.device(ctx)
    # 저장한 Checkpoint 불러오기
    checkpoint = torch.load(load_path, map_location=device)

    # KoGPT-2 언어 모델 학습을 위한 GPT2LMHeadModel 선언
    kogpt2model = GPT2LMHeadModel(config=GPT2Config.from_dict(kogpt2_config))
    kogpt2model.load_state_dict(checkpoint['model_state_dict'])

    kogpt2model.eval()
    vocab_b_obj = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
                                                         mask_token=None,
                                                         sep_token=None,
                                                         cls_token=None,
                                                         unknown_token='<unk>',
                                                         padding_token='<pad>',
                                                         bos_token='<s>',
                                                         eos_token='</s>')
    ### 4. Tokenizer
    tok_path = get_tokenizer()
    model, vocab = kogpt2model, vocab_b_obj
    tok = SentencepieceTokenizer(tok_path)

    ### 5. Text Generation
    result = []
    usr_sent = tmp_sent
    sent = ''

    for j in range(10):
        if sent == '':
            sent = sent + usr_sent
        else:
            sent = generated_text

        # print(sent) ## print result
        result.append(sent)
        toked = tok(sent)
        count = 0
        generated_text = ''
        input_size = 50

        if len(toked) > 1022:
            break

        while(1):
            input_ids = torch.tensor([vocab[vocab.bos_token], ] + vocab[toked]).unsqueeze(0)
            predicts = model(input_ids)
            pred = predicts[0]
            # print('predicts:', torch.argmax(pred, axis=-1).squeeze())
            # gen = vocab.to_tokens(torch.argmax(pred, axis=-1).squeeze().tolist())[-1]
            gen = topkSampling(pred, 10, vocab)

            if '</s>' in gen:
                gen = gen.replace('</s>', '')
            # if gen == '</s>':
            # print('to_tokens:',vocab.to_tokens(torch.argmax(pred, axis=-1).squeeze().tolist()))
            if '.' in gen or count > input_size:
                sent += gen.replace('▁', ' ').replace('</', '')
                generated_text += gen.replace('▁', ' ').replace('</', '')
                # sent += '\n'
                # generated_text += '\n'
                toked = tok(sent)
                count = 0
                break
                # print('to_tokens:',vocab.to_tokens(torch.argmax(pred, axis=-1).squeeze().tolist()))
            # if count >= input_size:
            #   break
            sent += gen.replace('▁', ' ').replace('<', '')
            generated_text += gen.replace('▁', ' ').replace('<', '')

            toked = tok(sent)
            count += 1
        # print('result:')
        # print(sent)

        split = sent.split('\n')
        # print(split)
        if len(split) > 1:
            # print(split[1])
            if sent == split[1]:
                break
    result = ''.join(result)
    return result
