import re

def cleanhtml(raw_html):
#   cleanr = re.compile('<.*?>')
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

print(cleanhtml('<a href="https://thanhnien.vn/thoi-su/khen-thuong-cong-an-da-lat-vi-bat-nhanh-nhom-nu-quai-trom-dien-thoai-du-khach-1378460.html"><img align="left" border="0" hspace="5" src="https://image.thanhnien.vn/180/uploaded/lamvien/2021_05_04/h5_ixfj.jpg" width="180px" /></a><p>Chủ tịch tỉnh Lâm Đồng Trần Văn Hiệp khen thưởng đột xuất Đội Cảnh sát hình sự (CSHS) Công an TP.Đà Lạt vì đã bắt nhanh nhóm ‘nữ quái’ chuyên trộm điện thoại của du khách ở chợ đêm Đà Lạt.</p>'))