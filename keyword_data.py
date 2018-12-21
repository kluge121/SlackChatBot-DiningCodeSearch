class KeywordData:
    __m_category = []

    __m_locations = []

    __m_franchise = []

    # 생성자, 각 텍스트 데이터 입력
    def __init__(self):
        with open("location_data.txt", "r") as file:
            self.__m_locations = file.read().split(",")

        with open("category_data.txt", "r") as file:
            self.__m_category = file.read().split(",")

        with open("franchise_data.txt", "r") as file:
            self.__m_franchise = file.read().split(",")

    # 음식의 카테고리 키워드를 추출
    def find_category(self, sentence_split):
        search_category_list = set([])
        for word in sentence_split:
            if word in self.__m_category:
                search_category_list.add(word)
        return list(search_category_list)

    # 지역 정보 키워드 추출
    def find_location(self, sentence_split):
        search_location_list = set([])
        for word in sentence_split:
            for location in self.__m_locations:
                if word in location:
                    search_location_list.add(word)
        return self.__valid_check_location(search_location_list)

    # 프랜차이즈 상호명 키워드 추출
    def find_franchise(self, sentence_split):
        search_franchise_list = set([])
        for word in sentence_split:
            if word in self.__m_franchise:
                search_franchise_list.add(word)
        return list(search_franchise_list)

    # 지역 정보 유효성 검사
    def __valid_check_location(self, locations):
        units = ["시", "군", "구", "동", "읍", "면", "리"]
        return_list = set([])
        for location in locations:

            if location[-1] not in units:
                for unit in units:
                    tmp = location + unit
                    if tmp in self.__m_locations:
                        return_list.add(location)

            elif location in self.__m_locations:
                return_list.add(location)

        return list(return_list)
