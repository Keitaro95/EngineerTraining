""""
。で区切る
（）で区切る
前の分割のやり方でやる
git から昔のバージョンを見る
コードを拾う

"""
def sentence_split_curly(before_sentences: str, after_sentences: str) -> dict:
    
    def split_sentences_curly(text: str) -> list[str]:
        if not isinstance(text, str):
            return []

        sentences = []
        current = ""
        i = 0

        while i < len(text):
            char = text[i]
            current += char

            if char == "。":
                # 「。」でチャンクを区切る
                if current.strip():
                    sentences.append(current)
                current = ""
                i += 1

                # 次が（）の場合、（）を別チャンクとして追加
                if i < len(text) and text[i] in ("(", "（"):
                    open_bracket = text[i]
                    close_bracket = ")" if open_bracket == "(" else "）"
                    bracket_chunk = open_bracket
                    i += 1
                    while i < len(text):
                        bracket_chunk += text[i]
                        if text[i] == close_bracket:
                            i += 1
                            break
                        i += 1
                    if bracket_chunk.strip():
                        sentences.append(bracket_chunk)
            else:
                i += 1

        if current.strip():
            sentences.append(current)

        return sentences

    before_list = split_sentences_curly(before_sentences)
    after_list = split_sentences_curly(after_sentences)

    return {
        "before_list": before_list,
        "after_list": after_list,
    }