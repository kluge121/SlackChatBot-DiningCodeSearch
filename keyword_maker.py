from konlpy.tag import Kkma
from keyword_data import KeywordData


class KeywordMaker:
    # 입력된 문장 분석 클래스
    def __init__(self):
        pass

    # 클래스 사용 인터페이스 함수
    def get_search_tuple(self, input_sentence):
        split_sentence = self.__sentence_splinter(input_sentence)
        print("자른문장 : " + str(split_sentence))
        data = KeywordData()
        location_list = data.find_location(split_sentence)
        category_list = data.find_category(split_sentence)
        franchise_list = data.find_franchise(split_sentence)
        return location_list, category_list, franchise_list


    # 문장 분리
    def __sentence_splinter(self, input_sentence):
        spliter = Kkma()
        spliter_sentence = spliter.nouns(input_sentence)
        return spliter_sentence
