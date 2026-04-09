"""
Brief: New analysis of a predefined string (word count, longest word, odd words).
Lab: 3 (LR3), Task: 4 
Author: Anastasiya Sushkevich
Date: 2026-03-25
"""

def run_task():
    source_text = (
        "«So she was considering in her own mind, as well as she could, "
        "for the hot day made her feel very sleepy and stupid, whether the "
        "pleasure of making a daisy-chain would be worth the trouble of "
        "getting up and picking the daisies, when suddenly a White Rabbit "
        "with pink eyes ran close by her.»"
    )

    print("\n--- Task 4: String Analysis ---")
    print("Text :",source_text)
    
    # 1. Очищаем строку от кавычек и заменяем запятые на пробелы
    clean_text = source_text.replace('«', '').replace('»', '').replace(',', ' ')

    words = clean_text.split()
    
    # а) Количество слов
    print(f"a) Total words in string: {len(words)}")
    
    # б) Самое длинное слово и его номер
    longest_word = ""
    longest_index = 0
    
    for i, w in enumerate(words):
        if len(w) > len(longest_word):
            longest_word = w
            longest_index = i + 1 # Порядковый номер (с единицы)
            
    print(f"b) Longest word: '{longest_word}' (Position: {longest_index})")
    
    # в) Каждое нечетное слово
    odd_words = words[0::2]
    print("\nc) Odd words (1st, 3rd, 5th...):")
    print(", ".join(odd_words)) 