
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch
from .base import LLM
#   ---------千问模型:获取分词器和模型结构-------------------
class Qwen(LLM):
    def __init__(self,checkpoint):
        self.file_path = checkpoint
        self.setup()
    
    def setup(self):    
        self.tokenizer = AutoTokenizer.from_pretrained(self.file_path, trust_remote_code=True)
        generation_config = GenerationConfig.from_pretrained(self.file_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
                     self.file_path, device_map="auto", trust_remote_code=True).eval()
        self.model.generation_config = generation_config
        self.model.generation_config.do_sample = False
        # self.model.generation_config.top_k = 4
        # self.model.generation_config.top_p = 0.5

    def text_completion(self, input_text: str, stop_words = []) -> str:  # 作为一个文本续写模型来使用
        im_end = '<|im_end|>'
        if im_end not in stop_words:
            stop_words = stop_words + [im_end]
        stop_words_ids = [self.tokenizer.encode(w) for w in stop_words]
        input_ids = torch.tensor([self.tokenizer.encode(input_text)]).to(self.model.device)
        output = self.model.generate(input_ids, stop_words_ids=stop_words_ids)
        output = output.tolist()[0]
        output = self.tokenizer.decode(output, errors="ignore")
        assert output.startswith(input_text)
        output = output[len(input_text) :].replace('<|endoftext|>', '').replace(im_end, '')
        for stop_str in stop_words:
            idx = output.find(stop_str)
            if idx != -1:
                output = output[: idx + len(stop_str)]
        return output  # 续写 input_text 的结果，不包含 input_text 的内容
    
    def generate(self,query,history = []):
        answer, _ = self.model.chat(    tokenizer = self.tokenizer,
                                        query = query ,
                                        history = history,
                                        append_history = False)
        return answer
    def stream_generate(self,query,history):
        answer = self.model.chat_stream(tokenizer = self.tokenizer,
                                        query = query ,
                                        history = history
                                        ) 
        return answer
    
if  __name__ == '__main__':
    checkpoint = "/data/lly/model/Qwen-7B-Chat"
    qwen = Qwen(checkpoint)
    qwen.stream_generate('天气多么好',[])

    
