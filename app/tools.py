from langchain_core.tools import tool
from mock_data import FLIGHTS_DB, HOTELS_DB

# format tiền Việt Nam 1200000 -> 1.200.000đ
def format_vnd(x):
    return f"{x:,}".replace(",", ".") + "đ"

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy chuyến bay, trả về thông báo không có chuyến.
    """

    # Định dạng lại input để tìm kiếm trong cơ sở dữ liệu
    origin = origin.strip().title()
    destination = destination.strip().title()
    
    def format_flight(flight):
        return f"hãng bay: {flight["airline"]}, giờ khởi hành: {flight["departure"]}, giờ đến: {flight["arrival"]}, giá: {format_vnd(flight["price"])}, hạng: {flight["class"]}"

    if (origin, destination) in FLIGHTS_DB:
        return f"Danh sách chuyến bay từ {origin} đến {destination}:\n{',\n'.join([format_flight(flight) for flight in FLIGHTS_DB[(origin, destination)]])}."
    elif (destination, origin) in FLIGHTS_DB:
        return f"Xin lỗi, chúng tôi chỉ tìm thấy danh sách chuyến bay từ {destination} đến {origin}:\n{',\n'.join([format_flight(flight) for flight in FLIGHTS_DB[(destination, origin)]])}."
    else:
        return "Không tìm thấy chuyến bay nào phù hợp."

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    city = city.strip().title()

    def format_hotel(hotel):
        return f"Tên khách sạn: {hotel["name"]}, số sao: {hotel["stars"]}, giá mỗi đêm: {format_vnd(hotel['price_per_night'])}, khu vực: {hotel['area']}, rating: {hotel['rating']}"

    if city in HOTELS_DB:
        hotels = sorted([hotel for hotel in HOTELS_DB[city] if hotel["price_per_night"] <= max_price_per_night], key=lambda x: x["rating"], reverse=True)

        return f"Danh sách khách sạn tại {city} với giá tối đa {format_vnd(max_price_per_night)} mỗi đêm:\n{',\n'.join([format_hotel(hotel) for hotel in hotels])}."
    else:
        return f"Không tìm thấy khách sạn nào tại {city} với giá dưới {format_vnd(max_price_per_night)} mỗi đêm. Hãy thử tăng ngân sách."

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy, định dạng 'tên_khoản: số_tiền' (VD: 'vé_máy_bay:890000, khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    expenses_items = {}

    for item in expenses.split(", "):
        try:
            key, value = item.split(":")
            expenses_items[key] = int(value)
        except ValueError:
            print(f"Invalid format or value: {item}")
            return "Định dạng chi phí không hợp lệ. Vui lòng sử dụng định dạng 'tên_khoản:số_tiền' và cách nhau bằng dấu phẩy."
        except Exception as e:
            print(f"Unexpected error: {item} - {e}")
            return "Định dạng chi phí không hợp lệ. Vui lòng sử dụng định dạng 'tên_khoản:số_tiền' và cách nhau bằng dấu phẩy."

    total_expenses = sum(expenses_items.values())
    remaining_budget = total_budget - total_expenses

    # format table
    def format_expenses(expenses_items):
        return "\n".join([f"- {name.replace('_', ' ')}: {format_vnd(amount)}" for name, amount in expenses_items.items()])

    
    result = f"""
                Bảng chi phí:
                \n{format_expenses(expenses_items)}
                \n---
                \nTổng chi: {format_vnd(total_expenses)}
                \nNgân sách: {format_vnd(total_budget)}
                \nCòn lại: {format_vnd(remaining_budget)}
            """

    if remaining_budget < 0:
        result += f"\nVượt ngân sách {format_vnd(-remaining_budget)}! Cần điều chỉnh."
    
    return result

if __name__ == "__main__":
    print(search_flights("Đà Nẵng", "Hà Nội"))
    print(search_hotels("ĐÀ NẴNG", max_price_per_night=1000000))
    print(calculate_budget(5000000, "vé_máy_bay:, khách_sạn:6500000, ăn_uống:5000000"))