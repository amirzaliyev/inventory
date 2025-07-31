from utils.visualize import make_df

s = [
    {"name": "Shapka 60 cm", "total_count": 48},
    {"name": "Shapka 40 cm", "total_count": 31},
    {"name": "Rangli shapka 40 cm", "total_count": 19},
    {"name": "Shlakoblok 20x40", "total_count": 35079},
    {"name": "Rangli shapka 60 cm", "total_count": 263737},
    {"name": "Kalods qopqoq", "total_count": 3741},
    {"name": "Rangli shlakoblok 20x40", "total_count": 2538},
    {"name": "Tumba shapka", "total_count": 50252},
    {"name": "Tumba", "total_count": 334},
    {"name": "Rangli tumba shapka", "total_count": 55793},
    {"name": "Rangli tumba", "total_count": 132},
    {"name": "Shlakoblok 16x32", "total_count": 105364},
    {"name": "Kalods 50", "total_count": 4},
    {"name": "Latok", "total_count": 2626},
    {"name": "Kalods 90", "total_count": 5},
]

m = [
    {"name": "Shlakoblok 20x40", "total_count": 119814},
    {"name": "Tumba", "total_count": 1178},
    {"name": "Rangli tumba", "total_count": 123698},
    {"name": "Latok", "total_count": 25},
    {"name": "Kalods 90", "total_count": 6},
    {"name": "Kalods 50", "total_count": 35},
    {"name": "Kalods qopqoq", "total_count": 5},
    {"name": "Tumba shapka", "total_count": 15},
    {"name": "Rangli tumba shapka", "total_count": 10},
    {"name": "Shapka 40 cm", "total_count": 42},
    {"name": "Shapka 60 cm", "total_count": 32},
    {"name": "Rangli shapka 40 cm", "total_count": 28},
    {"name": "Rangli shapka 60 cm", "total_count": 10},
]
s_df = make_df(s)
m_df = make_df(m)
# print(s_df)
# print()
# print(m_df)
# print()
# print(type(s_df))
# print(m_df - s_df)
res = []

a = [
    {
        "branch": "1-seh",
        "date": "12.06.2025",
        "product": "Shlakoblok 20x40",
        "quantity": 1234,
        "price": 3200,
    },
    {
        "branch": "1-seh",
        "date": "12.06.2025",
        "product": "Shlakoblok 16x32",
        "quantity": 1234,
        "price": 2500,
    },
]

a_df = make_df(a)
print()
print(a_df.to_string(index=False))
