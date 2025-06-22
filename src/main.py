from src.hh_handler import HhHandler

if __name__ == '__main__':
    my_hh = HhHandler()
    my_hh.get_employers_info()
    for emp in my_hh.employers:
        print(emp)
        input()

