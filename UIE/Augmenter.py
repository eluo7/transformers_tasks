# !/usr/bin/env python3
"""
==== No Bugs in code, just some Random Unexpected FEATURES ====
┌─────────────────────────────────────────────────────────────┐
│┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐│
││Esc│!1 │@2 │#3 │$4 │%5 │^6 │&7 │*8 │(9 │)0 │_- │+= │|\ │`~ ││
│├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┤│
││ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{[ │}] │ BS  ││
│├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤│
││ Ctrl │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│" '│ Enter  ││
│├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────┬───┤│
││ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│Shift │Fn ││
│└─────┬──┴┬──┴──┬┴───┴───┴───┴───┴───┴──┬┴───┴┬──┴┬─────┴───┘│
│      │Fn │ Alt │         Space         │ Alt │Win│   HHKB   │
│      └───┴─────┴───────────────────────┴─────┴───┘          │
└─────────────────────────────────────────────────────────────┘

数据增强器。

Author: pankeyu
Date: 2023/01/16
"""
import copy
import json
import random
import traceback
from typing import List, Union

import jieba
from tqdm import tqdm


class Augmenter(object):
    """
    数据增强类。

    Args:
        object (_type_): _description_
    """

    @staticmethod
    def augment(text:str, methods=[], **args) -> List[str]:
        """
        对一段文本进行数据增强，包含：随机删词、随机替换、随机重复几种方法。

        Args:
            text (str): 原文本, e.g. -> '王宝强是一个演员。'
            methods (list, optional): 数据增强方法，包含 -> ['delete', 'replace', 'repeat']. Defaults to [].
            del_ratio: _description_
            len_threshold (float, Optional): _description_
            delete_aug_counts (int, Optional): _description_
            replace_ratio (float, Optional): _description_
            replace_aug_counts (int, Optional): _description_
            similarity_threhold (float, Optional): _description_
            repeat_ratio (float, Optional): _description_
            repeat_aug_counts (int, Optional): _description_

        Returns:
            List[str]: 增强后的文本, -> ['刘德华是一个演员。', '王宝强强是一个个演员。', ...]
        """
        results = [text]
        for method in methods:
            if method == 'delete':
                del_ratio = 0.2 if 'del_ratio' not in args else args['del_ratio']                # 随机删除指定比例的文字
                len_threshold = 5 if 'len_threshold' not in args else args['len_threshold']      # 执行删除策略的最小长度
                aug_counts = 1 if 'delete_aug_counts' not in args else args['delete_aug_counts'] # 数据增强次数
                del_words_count = int(len(text) * del_ratio)
                if len(text) > len_threshold:
                    for _ in range(aug_counts):
                        temp_res = ''
                        random_del_index = random.sample([i for i in range(len(text))], k=del_words_count)
                        for i, t in enumerate(text):
                            if i not in random_del_index:
                                temp_res += t
                        if temp_res not in results:
                            results.append(temp_res)
            elif method == 'replace':
                import synonyms
                words = jieba.lcut(text)
                replace_ratio = 0.4 if 'replace_ratio' not in args else args['replace_ratio']      # 替换词个数占总数的比例
                aug_counts = 1 if 'replace_aug_counts' not in args else args['replace_aug_counts'] # 数据增强次数
                similarity_threhold = 0.7 if 'similarity_threhold' not in args else args['similarity_threhold'] # 同义词替换时的最低相似度
                replace_words_count = int(replace_ratio * len(words))
                for _ in range(aug_counts):
                    temp_res = []
                    replace_words_index = random.sample([i for i in range(len(words))], k=replace_words_count)
                    for i, w in enumerate(words):
                        if i in replace_words_index:
                            replaced_res = synonyms.nearby(w)
                            candidate = [w for w, p in zip(*replaced_res) if p > similarity_threhold]   # 找到所有大于相似度阈值的替换词
                            if len(candidate) < 2:                                                      # 没有符合要求的同义词则使用原词
                                temp_res.append(w)
                            else:
                                temp_res.append(random.choice(candidate))
                        else:
                            temp_res.append(w)
                    if ''.join(temp_res) not in results:
                        results.append(''.join(temp_res))
            elif method == 'repeat':
                repeat_ratio = 0.32 if 'repeat_ratio' not in args else args['repeat_ratio']        # 随机重复字个数占总数的比例
                aug_counts = 1 if 'repeat_aug_counts' not in args else args['repeat_aug_counts']   # 数据增强次数
                repeat_words_count = int(repeat_ratio * len(text))
                for _ in range(aug_counts):
                    temp_res = ''
                    random_repeat_index = random.sample([i for i in range(len(text))], k=repeat_words_count)
                    for i, w in enumerate(text):
                        if i in random_repeat_index:
                            temp_res += w * 2
                        else:
                            temp_res += w
                    if temp_res not in results:
                        results.append(temp_res)
            else:
                raise ValueError(f'no method called {method}, must in ["add", "delete", "replace", "repeat"].')
        return results

    @staticmethod
    def batch_augment(texts: List[str], methods=[], **args) -> List[str]:
        """
        批量数据增强，用于对一个文本列表里的所有句子做增强。

        Args:
            texts (List[str]): 原文本列表, e.g. -> ['王宝强是一个演员。', ...]
            methods (list, optional): _description_. Defaults to [].

        methods (list, optional): 数据增强方法，包含 -> [
                'delete',
                'replace',
                'repeat'
            ]. Defaults to [].

        Returns:
            List[str]: 增强后的文本, -> ['刘德华是一个演员。', '王宝强强是一个个演员。', ...]
        """
        res = []
        for text in texts:
            res.extend(Augmenter.augment(text, methods, args))
        return res

    @staticmethod
    def add_uie_relation_negative_samples(
        sample: dict, 
        negative_predicates: List[str]
        ) -> List[dict]:
        """
        为UIE添加关系抽取的负例数据。

        Args:
            sample (dict): UIE训练数据样本, e.g. -> {"content": "大明是小明的父亲", "result_list": [{"text": "大明", "start": 0, "end": 2}], "prompt": "小明的父亲"}
            negative_predicates (List[str]): 负例 p 列表, e.g. -> ['母亲', '叔叔', '二姨']

        Returns:
            List[dict]: [
                {"content": "大明是小明的父亲", "result_list": [], "prompt": "小明的母亲"},
                {"content": "大明是小明的父亲", "result_list": [], "prompt": "小明的叔叔"},
                {"content": "大明是小明的父亲", "result_list": [], "prompt": "小明的二姨"},
                ...
            ]
        """
        assert 'prompt' in sample and '的' in sample['prompt'], \
            "key:'prompt' must in @param:sample and sample['prompt'] must contain '的'."
        res = []
        elements = sample['prompt'].split('的')
        subject = '的'.join(elements[:-1])

        for negtive_predicate in negative_predicates:
            res.append({
                'content': sample['content'],
                'result_list': [],
                'prompt': f'{subject}的{negtive_predicate}'
            })
        return res

    @staticmethod
    def auto_add_uie_relation_negative_samples(
        model, 
        tokenizer, 
        samples: Union[List[str], List[dict]],
        negative_samples_file: str,
        inference_func,
        details_file='details.log',
        device='cpu',
        max_seq_len=256,
        batch_size=64
        ):
        """
        自动为UIE添加关系抽取的负例数据。

        Args:
            model (_type_): fine-tuning 好的 UIE 模型
            tokenizer (_type_): tokenizer
            samples (Union(List[str], List[dict])): 数据集文件名列表（自动读取），或样本列表
            inference_func (callable): 模型推理函数
            negative_samples_file (str): 负例文件存放地址
            details_file (str): 详细信息文件存放地址，默认为'details.log'
        """
        predicate_error_dict, summary_dict = Augmenter.auto_find_uie_negative_predicates(
            model,
            tokenizer,
            samples=samples,
            inference_func=inference_func,
            device=device,
            max_seq_len=max_seq_len,
            batch_size=batch_size
        )

        print(predicate_error_dict, file=open(details_file, 'w', encoding='utf8'))
        print('\n-- Error Count of Predicates --\n', file=open(details_file, 'a', encoding='utf8'))
        error_count_dict = dict([(k, v['total_error']) for k, v in predicate_error_dict.items()])
        error_count_dict = dict(sorted(error_count_dict.items(), key=lambda x: x[1], reverse=True))
        print(f'Total Error: {sum(list(error_count_dict.values()))}', file=open(details_file, 'a', encoding='utf8'))
        print(f'{error_count_dict}', file=open(details_file, 'a', encoding='utf8'))
        print('\n-- Summary of Confused Predicates --\n', file=open(details_file, 'a', encoding='utf8'))
        print(summary_dict, file=open(details_file, 'a', encoding='utf8'))
        print(f'[Done] Model Performance details have saved at "{details_file}".')

        if type(samples[0]) == str:                                # 若传入的是文件路径，则读取全部的文件路径
            parse_samples = []
            for sample_file in samples:
                with open(sample_file, 'r', encoding='utf8') as f:
                    for i, line in enumerate(f.readlines()):
                        try:
                            sample = json.loads(line)
                            parse_samples.append(sample)
                        except:
                            print(f'[Error Line {i}] {line}')
                            print(traceback.format_exc())
                            exit()
            samples = parse_samples

        negative_samples = []        
        for sample in samples:
            if not sample['result_list'] or '的' not in sample['prompt']:
                continue
        
            elements = sample['prompt'].split('的')                 # 解析文件宾语
            predicate = elements[-1]
            if predicate in summary_dict:                           # 添加宾语负例
                res = Augmenter.add_uie_relation_negative_samples(sample, summary_dict[predicate])
                negative_samples.extend(res)
        
        negative_samples = [json.dumps(sample, ensure_ascii=False) for sample in negative_samples]
        negative_samples = list(set(negative_samples))
        with open(negative_samples_file, 'w', encoding='utf8') as f:
            for sample in negative_samples:
                f.write(f'{sample}\n')

        print(f'[Done] Negative Samples have saved at "{negative_samples_file}".')
    
    @staticmethod
    def auto_add_uie_relation_positive_samples(
        samples: Union[List[str], List[dict]],
        positive_samples_file: str
        ):
        """
        自动为UIE添加关系抽取的负例数据。

        Args:
            model (_type_): fine-tuning 好的 UIE 模型
            tokenizer (_type_): tokenizer
            samples (Union(List[str], List[dict])): 数据集文件名列表（自动读取），或样本列表
            positive_samples_file (str): 正例文件存放地址
        """
        assert type(samples) == list, '@params:samples must be [list] type.'
        if type(samples[0]) == str:                                        # 若传入的是文件路径，则读取全部的文件路径
            parse_samples = []
            for sample_file in samples:
                with open(sample_file, 'r', encoding='utf8') as f:
                    for i, line in enumerate(f.readlines()):
                        try:
                            sample = json.loads(line)
                            parse_samples.append(sample)
                        except:
                            print(f'[Error Line {i}] {line}')
                            print(traceback.format_exc())
                            exit()
            samples = parse_samples
        
        predicates_sentence_dict = {}                                                  # 将句子按照「predicate」为key的方式存储
        for sample in samples:
            if len(sample['result_list']) == 1 and '的' in sample['prompt']:           # 只处理宾语只有一个答案的样本
                predicate = sample['prompt'].split('的')[-1]
                if predicate not in predicates_sentence_dict:
                    predicates_sentence_dict[predicate] = [sample]
                else:
                    predicates_sentence_dict[predicate].append(sample)
        
        positive_samples, error_num = [], 0
        for _, samples in predicates_sentence_dict.items():
            if len(samples) < 2:
                continue
            for sample in samples:
                candidates = copy.deepcopy(samples)
                candidates.remove(sample)
                candidate = copy.deepcopy(random.choice(candidates))                        # 从同predicate的句子中随机选则一条，将当前的s和o替换过去

                elements = sample['prompt'].split('的')              
                cur_sub = '的'.join(elements[:-1])
                cur_obj = sample['result_list'][0]['text']

                candidate_new_prompt = sample['prompt']
                candidate_text = candidate['content']
                elements = candidate['prompt'].split('的')              
                candidate_sub = '的'.join(elements[:-1])
                candidate_obj = candidate['result_list'][0]['text']

                new_candidate_text = candidate_text.replace(candidate_sub, cur_sub)         # 主语替换
                new_candidate_text = new_candidate_text.replace(candidate_obj, cur_obj)     # 宾语替换
                
                if new_candidate_text.find(cur_obj) != -1:
                    result_list = [{
                        "text": cur_obj,
                        "start": new_candidate_text.find(cur_obj),
                        "end": new_candidate_text.find(cur_obj) + len(cur_obj)
                    }]
                    positive_samples.append({
                        "content": new_candidate_text,
                        "prompt": candidate_new_prompt,
                        "result_list": result_list
                    })
                else:
                    error_num += 1
        # print('error samples in positive augment: ', error_num)
        
        positive_samples = [json.dumps(sample, ensure_ascii=False) for sample in positive_samples]
        positive_samples = list(set(positive_samples))
        with open(positive_samples_file, 'w', encoding='utf8') as f:
            for sample in positive_samples:
                f.write(f'{sample}\n')
        print(f'[Done] Positive Samples have saved at {positive_samples_file}.')

    @staticmethod
    def auto_find_uie_negative_predicates(
        model: str, 
        tokenizer: str, 
        samples: Union[List[str], List[dict]],
        inference_func,
        device='cpu',
        max_seq_len=256,
        batch_size=64
        ) -> tuple:
        """
        根据标注数据集自动找出易混淆的，需要添加负例的predicates。

        Args:
            model (_type_): fine-tuning 好的 UIE 模型
            tokenizer (_type_): tokenizer 存放地址
            samples (List[str], List[dict]): 数据集文件名列表（自动读取），或样本列表
            inference_func (callabel): 模型推理函数

        Returns:
            predicate_error_dict (混淆负例P的详细信息) -> {
                                                        "上级行政区": {
                                                                        "total_error": 3,
                                                                        "confused_predicates": {
                                                                            "地理位置": {
                                                                                "count": 1,
                                                                                "error_samples": [
                                                                                    "content:  邓台村属于哪个镇？大名县大街镇 prompt:邓台村的地理位置 answer:['大名县大街镇']"
                                                                                ]
                                                                            },
                                                                            "所属机构": {
                                                                                "count": 1,
                                                                                "error_samples": [
                                                                                    "content:  邓台村属于哪个镇？大名县大街镇 prompt:邓台村的所属机构 answer:['大名县大街镇']"
                                                                                ]
                                                                            },
                                                                            ...
                                                                        }
                                                                    },
                                                                    ...
                                                    }
            summary_dict (混淆负例P的简要信息) -> {
                                                '上级行政区': ['地理位置', '所属机构', '行政区等级'],
                                                '重量': ['使用材料', '标准'],
                                                '品牌类型': ['档次', '品牌', '企业类型'],
                                                ...
                                            }
        """
        if type(samples[0]) == str:                                # 若传入的是文件路径，则读取全部的文件路径
            parse_samples = []
            for sample_file in samples:
                with open(sample_file, 'r', encoding='utf8') as f:
                    for i, line in enumerate(f.readlines()):
                        try:
                            sample = json.loads(line)
                            parse_samples.append(sample)
                        except:
                            print(f'[Error Line {i}] {line}')
                            print(traceback.format_exc())
                            exit()
            samples = parse_samples
    
        all_predicates = []                                         # 统计所有的谓语列表
        predicates_of_each_sample = {}                              # 通过整个数据集，计算每个句子中包含的全部p
        for sample in samples:
            if '的' in sample['prompt']:                            # 提取prompt中的predicate
                try:
                    elements = sample['prompt'].split('的')
                    predicate = elements[-1]
                except:
                    print(f'[Error Prompt] {sample}')
                    exit()
                if predicate not in all_predicates:
                    all_predicates.append(predicate)
                
                if sample['result_list'] != []:                     # 记录每一个句子都有哪些predicate
                    if sample['content'] not in predicates_of_each_sample:
                        predicates_of_each_sample[sample['content']] = [predicate]
                    else:
                        if predicate not in predicates_of_each_sample[sample['content']]:
                            predicates_of_each_sample[sample['content']].append(predicate)

        predicate_error_dict = {}
        for sample in tqdm(samples):
            if not sample['result_list'] or '的' not in sample['prompt']:
                continue
            
            elements = sample['prompt'].split('的')
            subject = '的'.join(elements[:-1])
            predicate = elements[-1]
            
            sample_predicates = predicates_of_each_sample[sample['content']]                    # 当前样本包含的p
            negative_predictes = [p for p in all_predicates if p not in sample_predicates]      # 当前样本不包含的p
            
            for i in range(0, len(negative_predictes), batch_size):
                new_prompts = [f'{subject}的{p}' for p in negative_predictes[i:i+batch_size]]
                contents = [sample['content']] * len(new_prompts)
                res_list = inference_func(
                        model,
                        tokenizer,
                        device,
                        contents=contents,
                        prompts=new_prompts,
                        max_length=max_seq_len
                    )

                for new_prompt, res, p in zip(new_prompts, res_list, negative_predictes[i:i+batch_size]):
                    origin_answers = [ele['text'] for ele in sample['result_list']]
                    if len(res) and res[0] in origin_answers:                                    # 如果模型通过其余的p抽出了结果，且结果与原始结果相同
                        if predicate not in predicate_error_dict:
                            predicate_error_dict[predicate] = {
                                'total_error': 0,
                                'confused_predicates': {}
                            }
                        predicate_error_dict[predicate]['total_error'] += 1
                        if p not in predicate_error_dict[predicate]['confused_predicates']:      # 记录（p-负例p）的映射关系
                            predicate_error_dict[predicate]['confused_predicates'][p] = {
                                'count': 1,
                                'error_samples': [f"content: {sample['content']} prompt:{new_prompt} answer:{res}"]
                            }                                                                    # 记录（p-负例p）的出错次数、出错样本
                        else:
                            predicate_error_dict[predicate]['confused_predicates'][p]['count'] += 1
                            predicate_error_dict[predicate]['confused_predicates'][p]['error_samples'].append(
                                f"content: {sample['content']} prompt:{new_prompt} answer:{res}"
                            )
        
        predicate_error_sorted_tuple = sorted(predicate_error_dict.items(), key=lambda x: x[1]['total_error'])
        summary_dict = dict([(ele[0], list(ele[1]['confused_predicates'].keys())) for ele in predicate_error_sorted_tuple])
        
        return predicate_error_dict, summary_dict