import openpyxl
import re
data = openpyxl.load_workbook('data.xlsx')
ws = data.get_sheet_by_name("sheet1")


# 엑셀에서 행정 구역 읽어오기
# with open("location_data.txt","w") as file:
#     for row in ws.rows:
#         p = re.compile("[^0-9]")
#         tmp = str(row[1].value)+","
#         tmp = tmp.replace("·","")
#         file.write("".join(p.findall(tmp)))

# 테스트 코드
# with open("location_data.text", "rw") as file:
#     str = file.read()
#     p = re.compile("[^0-9]")
#     result = "".join(p.findall(str))
#     print(result)

