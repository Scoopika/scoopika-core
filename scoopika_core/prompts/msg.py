from typing import Dict


def user_msg(content: str) -> Dict:
	return {"role": "user", "content": content}

def system_msg(content: str) -> Dict:
	return {"role": "system", "content": content}