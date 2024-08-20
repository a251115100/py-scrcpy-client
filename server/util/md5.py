import hashlib


def md5(text: str) -> str:
    # 创建一个 MD5 对象
    instance = hashlib.md5()
    # 更新对象以包含要加密的数据
    instance.update(text.encode('utf-8'))
    # 获取十六进制表示的哈希值
    return instance.hexdigest()
