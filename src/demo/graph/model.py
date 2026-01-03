from demo.config.config import get_config

config = get_config()
llm = config.create_llm()
