
def sentence_split(before_sentences: str, after_sentences: str) -> dict:

    def split_sentences(text: str) -> list[str]:
        if not isinstance(text, str):
            return []

        sentences = []
        current = ""
        i = 0

        while i < len(text):
            char = text[i]
            current += char

            if char == "。":
                next_i = i + 1
                if next_i < len(text) and text[next_i] in ("(", "（"):
                    open_bracket = text[next_i] # next_iは「( 」だよ。
                    close_bracket = ")" if open_bracket == "(" else "）" # 全角対応
                    current += open_bracket # ) はcurrentで追跡
                    j = next_i + 1
                    while j < len(text):
                        current += text[j]
                        if text[j] == close_bracket: #とじかっこに当たった
                            j += 1
                            break
                        j += 1
                    i = j
                    if current.strip():
                        sentences.append(current)
                    current = ""
                else: #普通に「。」で切れる場合
                    if current.strip():
                        sentences.append(current)
                    current = "" # 空に戻す
                    i += 1
            else:
                i += 1

        if current.strip():
            sentences.append(current)

        return sentences

    before_list = split_sentences(before_sentences)
    after_list = split_sentences(after_sentences)

    return {
        "before_list": before_list,
        "after_list": after_list,
    }