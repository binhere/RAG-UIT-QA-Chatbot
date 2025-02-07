from llama_index.llms.gemini import Gemini
from llama_index.core import PromptTemplate
from prompts import *

def prepare_context_str(nodes) -> str:
    context_str = "\n\n".join([f'tài liệu {id+1}: {node.metadata['article']}, {node.metadata['document']}, {node.get_content()}' for id, node in enumerate(nodes)])
    return context_str

def filter_query(template_filter, query, llm : Gemini) -> str:
    prompt_template = PromptTemplate(template_filter)
    formatted_prompt = prompt_template.format(query_str=query)
    response = llm.complete(formatted_prompt)
    return response

def answer_query(template_answer, query, context_str, llm : Gemini) -> str:
    prompt_template = PromptTemplate(template_answer)
    formatted_prompt = prompt_template.format(query_str=query, context_str=context_str)
    response = llm.complete(formatted_prompt)
    return response


TEMPLATE_RESPONSE_ABUSE = "Câu hỏi của bạn có vẻ như là lạm dụng hệ thống của chúng tôi. Bạn vui lòng đặt câu hỏi khác để nhận được trợ giúp."
TEMPLATE_RESPONSE_NOT_VIETNAMESE = "Câu hỏi của bạn không phải là tiếng Việt. Bạn vui lòng đặt câu hỏi bằng tiếng Việt để nhận được trợ giúp. \nYour question is not in Vietnamese. Please ask questions in Vietnamese for support."
TEMPLATE_RESPONSE_OUT_OF_DOMAIN = "Câu hỏi của bạn không nằm trong phạm vi tuyển sinh của UIT. Bạn vui lòng đặt câu hỏi khác để nhận được trợ giúp."
TEMPLATE_RESPONSE_NO_INFORMATION = "Không tìm thấy thông tin cho câu hỏi của bạn trong cơ sở dữ liệu. Vui lòng đặt lại câu hỏi hoặc liên hệ với phòng tư vấn tuyển sinh"